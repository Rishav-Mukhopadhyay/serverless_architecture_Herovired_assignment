import boto3
from datetime import datetime, timezone, timedelta
from botocore.exceptions import ClientError

# ============================================================
# CONFIGURATION — Update these values
# ============================================================
VOLUME_IDS       = [
    'vol-0b8d87ee1c848968d'
]
RETENTION_DAYS   = 30          # ← Delete snapshots older than this
OWNER_ID         = 'self'      # ← 'self' means your own AWS account
# ============================================================

def lambda_handler(event, context):
    """
    For each EBS volume in VOLUME_IDS:
      1. Creates a new snapshot (backup)
      2. Scans all existing snapshots for that volume
      3. Deletes snapshots older than RETENTION_DAYS
    """

    ec2 = boto3.client('ec2', region_name='ap-south-1')  # ← Match your region

    # Tracking across all volumes
    all_created   = []
    all_deleted   = []
    all_kept      = []
    all_errors    = []

    print("=" * 65)
    print("EBS SNAPSHOT MANAGER — STARTING")
    print(f"Volumes to back up  : {len(VOLUME_IDS)}")
    print(f"Retention period    : {RETENTION_DAYS} days")
    print(f"Cutoff date         : {(datetime.now(timezone.utc) - timedelta(days=RETENTION_DAYS)).strftime('%Y-%m-%d')}")
    print("=" * 65)

    for volume_id in VOLUME_IDS:
        print(f"\n{'─' * 65}")
        print(f"Processing Volume: {volume_id}")
        print(f"{'─' * 65}")

        # ---------------------------------------------------
        # PART 1: Validate volume exists
        # ---------------------------------------------------
        volume_info = get_volume_info(ec2, volume_id)
        if not volume_info:
            all_errors.append({'volume': volume_id, 'error': 'Volume not found'})
            print(f"Volume {volume_id} not found — skipping.\n")
            continue

        vol_name  = get_tag_value(volume_info.get('Tags', []), 'Name') or 'Unnamed'
        vol_size  = volume_info.get('Size', 'Unknown')
        vol_state = volume_info.get('State', 'Unknown')

        print(f"   Volume Name  : {vol_name}")
        print(f"   Volume Size  : {vol_size} GiB")
        print(f"   Volume State : {vol_state}\n")

        # ---------------------------------------------------
        # PART 2: Create a new snapshot
        # ---------------------------------------------------
        snapshot_id = create_snapshot(ec2, volume_id, vol_name)
        if snapshot_id:
            all_created.append({
                'snapshot_id': snapshot_id,
                'volume_id':   volume_id,
                'volume_name': vol_name
            })
        else:
            all_errors.append({'volume': volume_id, 'error': 'Snapshot creation failed'})

        # ---------------------------------------------------
        # PART 3: Clean up old snapshots for this volume
        # ---------------------------------------------------
        deleted, kept, errors = cleanup_old_snapshots(ec2, volume_id)
        all_deleted.extend(deleted)
        all_kept.extend(kept)
        all_errors.extend(errors)

    # ---------------------------------------------------
    # FINAL SUMMARY REPORT
    # ---------------------------------------------------
    print_summary(all_created, all_deleted, all_kept, all_errors)

    return {
        'statusCode': 200,
        'body': {
            'snapshots_created': [s['snapshot_id'] for s in all_created],
            'snapshots_deleted': all_deleted,
            'snapshots_kept':    all_kept,
            'errors':            all_errors
        }
    }


# ============================================================
# HELPER FUNCTION 1 — Get Volume Info
# ============================================================
def get_volume_info(ec2, volume_id):
    """Fetches volume metadata. Returns None if not found."""
    try:
        response = ec2.describe_volumes(VolumeIds=[volume_id])
        volumes  = response.get('Volumes', [])
        return volumes[0] if volumes else None
    except ClientError as e:
        print(f"⚠️  Error fetching volume info: {e}")
        return None


# ============================================================
# HELPER FUNCTION 2 — Create Snapshot
# ============================================================
def create_snapshot(ec2, volume_id, volume_name):
    """
    Creates a new EBS snapshot with a descriptive name and tags.
    Returns the snapshot ID or None on failure.
    """
    timestamp      = datetime.now(timezone.utc).strftime('%d-%m-%Y-%H%M')
    snapshot_desc  = f"AutoBackup-{volume_name}-{timestamp}"

    print(f"📸 Creating snapshot...")
    print(f"   Description: {snapshot_desc}")

    try:
        response    = ec2.create_snapshot(
            VolumeId    = volume_id,
            Description = snapshot_desc,
            TagSpecifications = [{
                'ResourceType': 'snapshot',
                'Tags': [
                    {'Key': 'Name',        'Value': snapshot_desc},
                    {'Key': 'CreatedBy',   'Value': 'Lambda-AutoBackup'},
                    {'Key': 'VolumeId',    'Value': volume_id},
                    {'Key': 'BackupDate',  'Value': timestamp},
                    {'Key': 'Retention',   'Value': f'{RETENTION_DAYS}-days'}
                ]
            }]
        )

        snap_id = response['SnapshotId']
        print(f"Snapshot created: {snap_id}\n")
        return snap_id

    except ClientError as e:
        print(f"Failed to create snapshot: {e}\n")
        return None


# ============================================================
# HELPER FUNCTION 3 — Cleanup Old Snapshots
# ============================================================
def cleanup_old_snapshots(ec2, volume_id):
    """
    Lists all existing snapshots for a volume.
    Deletes those older than RETENTION_DAYS.
    Returns: (deleted_list, kept_list, error_list)
    """
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=RETENTION_DAYS)
    deleted     = []
    kept        = []
    errors      = []

    print(f"Scanning existing snapshots for {volume_id}...")

    try:
        # List all snapshots owned by this account for this volume
        response  = ec2.describe_snapshots(
            OwnerIds = [OWNER_ID],
            Filters  = [
                {
                    'Name':   'volume-id',
                    'Values': [volume_id]
                },
                {
                    'Name':   'status',
                    'Values': ['completed']  # Only check completed snapshots
                }
            ]
        )

        snapshots = response.get('Snapshots', [])
        print(f"   Found {len(snapshots)} existing snapshot(s)\n")

        if not snapshots:
            print("No existing snapshots to evaluate.\n")
            return deleted, kept, errors

        # Sort by date — oldest first (easier to read in logs)
        snapshots.sort(key=lambda x: x['StartTime'])

        for snap in snapshots:
            snap_id = snap['SnapshotId']
            start_time = snap['StartTime']
            age_days = (datetime.now(timezone.utc) - start_time).days
            snap_size = snap.get('VolumeSize', 'Unknown')
            snap_desc = snap.get('Description', 'No description')

            print(f"Snapshot: {snap_id}")
            print(f"Created: {start_time.strftime('%Y-%m-%d %H:%M UTC')}")
            print(f"Age: {age_days} days")
            print(f"Size: {snap_size} GiB")
            print(f"Description: {snap_desc} GiB")

            if start_time < cutoff_date:
                # Snapshot is too old — delete it
                try:
                    ec2.delete_snapshot(SnapshotId=snap_id)
                    deleted.append(snap_id)
                    print(f"Status: DELETED (exceeded {RETENTION_DAYS}-day retention)\n")
                except ClientError as e:
                    errors.append({'snapshot': snap_id, 'error': str(e)})
                    print(f"Status: DELETE FAILED — {e}\n")
            else:
                # Snapshot is within retention window — keep it
                days_remaining = RETENTION_DAYS - age_days
                kept.append(snap_id)
                print(f"Status: KEPT ({days_remaining} days until expiry)\n")

    except ClientError as e:
        errors.append({'volume': volume_id, 'error': str(e)})
        print(f"Error scanning snapshots: {e}\n")

    return deleted, kept, errors


# ============================================================
# HELPER FUNCTION 4 — Print Summary
# ============================================================
def print_summary(created, deleted, kept, errors):
    print("\n" + "=" * 65)
    print("FINAL SUMMARY REPORT")
    print("=" * 65)
    print(f"Snapshots Created  : {len(created)}")
    print(f"Snapshots Kept     : {len(kept)}")
    print(f"Snapshots Deleted  : {len(deleted)}")
    print(f"Errors             : {len(errors)}")
    print("─" * 65)

    if created:
        print("\nNEWLY CREATED SNAPSHOTS:")
        for s in created:
            print(f"{s['snapshot_id']}  (Volume: {s['volume_id']} — {s['volume_name']})")

    if deleted:
        print(f"\nDELETED SNAPSHOTS (older than {RETENTION_DAYS} days):")
        for snap_id in deleted:
            print(f"   • {snap_id}")

    if kept:
        print("\nRETAINED SNAPSHOTS (within retention window):")
        for snap_id in kept:
            print(f"   • {snap_id}")

    if errors:
        print("\nERRORS ENCOUNTERED:")
        for err in errors:
            print(f"   • {err}")

    print("\n" + "=" * 65)
    print("EBS SNAPSHOT MANAGER — COMPLETE")
    print("=" * 65)


# ============================================================
# UTILITY — Extract tag value by key
# ============================================================
def get_tag_value(tags, key):
    """Returns the value of a specific tag key from a tags list."""
    for tag in tags:
        if tag['Key'] == key:
            return tag['Value']
    return None