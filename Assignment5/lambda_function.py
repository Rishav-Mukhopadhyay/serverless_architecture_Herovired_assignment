import boto3
from datetime import datetime, timezone
from botocore.exceptions import ClientError

# ============================================================
# CONFIGURATION — Customize your auto-tags here
# ============================================================
AUTO_TAGS = {
    'Environment': 'Production',        # Change per environment
    'ManagedBy': 'Lambda-AutoTagger',  # Identifies automated tagging
    'Owner': 'DevOps-Team',        # Your team name
    'CostCenter': 'Engineering',        # For billing reports
    'Compliance': 'Required',           # For compliance tracking
}
# ============================================================


def lambda_handler(event, context):
    """
    Triggered by EventBridge when a new EC2 instance is launched.
    Automatically applies tags to the new instance.

    Event source: EC2 RunInstances via CloudTrail → EventBridge
    """

    print("=" * 65)
    print("EC2 AUTO-TAGGER — TRIGGERED")
    print("=" * 65)

    # -------------------------------------------------------
    # STEP 1: Log the raw event for debugging
    # -------------------------------------------------------
    print(f"\nEvent Source: {event.get('source', 'Unknown')}")
    print(f"Event Detail Type: {event.get('detail-type', 'Unknown')}")
    print(f"Event Region: {event.get('region', 'Unknown')}")
    print(f"Event Time: {event.get('time', 'Unknown')}\n")

    # -------------------------------------------------------
    # STEP 2: Extract instance ID(s) from the event payload
    # -------------------------------------------------------
    instance_ids = extract_instance_ids(event)

    if not instance_ids:
        print("No instance IDs found in event. Exiting.")
        print("This may happen if the event format is unexpected.")
        print(f"Full event: {event}")
        return {'statusCode': 200, 'body': 'No instances to tag.'}

    print(f"🖥️  Instances to tag: {instance_ids}\n")

    # -------------------------------------------------------
    # STEP 3: Initialize EC2 client and apply tags
    # -------------------------------------------------------
    ec2 = boto3.client('ec2', region_name=event.get('region', 'us-east-1'))
    launch_date = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    launch_time = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')

    tagged_instances  = []
    failed_instances  = []

    for instance_id in instance_ids:
        print(f"{'─' * 65}")
        print(f"Tagging instance: {instance_id}")

        # Fetch instance details to enrich tags
        instance_info = get_instance_info(ec2, instance_id)

        # Build the complete tag set for this instance
        tags_to_apply = build_tags(
            instance_id   = instance_id,
            launch_date   = launch_date,
            launch_time   = launch_time,
            instance_info = instance_info,
            event         = event
        )

        # Apply all tags in a single API call
        success = apply_tags(ec2, instance_id, tags_to_apply)

        if success:
            tagged_instances.append(instance_id)
            print(f"\nSuccessfully tagged {instance_id}")
            print(f"Tags applied:")
            for tag in tags_to_apply:
                print(f"{tag['Key']:<20} = {tag['Value']}")
        else:
            failed_instances.append(instance_id)

        print()

    # -------------------------------------------------------
    # STEP 4: Print summary report
    # -------------------------------------------------------
    print("=" * 65)
    print("AUTO-TAGGING SUMMARY")
    print("=" * 65)
    print(f"Successfully tagged : {len(tagged_instances)}")
    print(f"Failed: {len(failed_instances)}")

    if tagged_instances:
        print(f"\nTagged instances:")
        for iid in tagged_instances:
            print(f"     • {iid}")

    if failed_instances:
        print(f"\nFailed instances:")
        for iid in failed_instances:
            print(f"     • {iid}")

    print("\n" + "=" * 65)
    print("AUTO-TAGGER — COMPLETE")
    print("=" * 65)

    return {
        'statusCode': 200,
        'body': {
            'tagged'  : tagged_instances,
            'failed'  : failed_instances
        }
    }


# ============================================================
# HELPER FUNCTION 1 — Extract Instance IDs from Event
# ============================================================
def extract_instance_ids(event):
    """
    Parses the EventBridge/CloudTrail event to find instance IDs.
    EC2 RunInstances events nest instance IDs in:
    event → detail → responseElements → instancesSet → items[]
    """
    instance_ids = []

    try:
        # Standard CloudTrail EC2 launch event structure
        items = (
            event
            .get('detail', {})
            .get('responseElements', {})
            .get('instancesSet', {})
            .get('items', [])
        )

        for item in items:
            iid = item.get('instanceId')
            if iid:
                instance_ids.append(iid)

    except (KeyError, TypeError, AttributeError) as e:
        print(f"Error parsing event for instance IDs: {e}")

    return instance_ids


# ============================================================
# HELPER FUNCTION 2 — Get Instance Details
# ============================================================
def get_instance_info(ec2, instance_id):
    """
    Fetches instance metadata to enrich tags
    (type, AMI, subnet, availability zone, etc.)
    Returns a dict or empty dict on failure.
    """
    try:
        response  = ec2.describe_instances(InstanceIds=[instance_id])
        instances = response['Reservations'][0]['Instances']
        return instances[0] if instances else {}
    except ClientError as e:
        print(f"Could not fetch instance info: {e}")
        return {}


# ============================================================
# HELPER FUNCTION 3 — Build Tag List
# ============================================================
def build_tags(instance_id, launch_date, launch_time, instance_info, event):
    """
    Builds the complete list of tags to apply.
    Combines: fixed config tags + dynamic tags from event/instance data.
    """
    # Dynamic tags — pulled from actual instance/event data
    dynamic_tags = {
        'LaunchDate'        : launch_date,
        'LaunchTime'        : launch_time,
        'InstanceType'      : instance_info.get('InstanceType', 'Unknown'),
        'AmiId'             : instance_info.get('ImageId', 'Unknown'),
        'AvailabilityZone'  : instance_info.get('Placement', {}).get('AvailabilityZone', 'Unknown'),
        'LaunchedBy'        : event.get('detail', {}).get('userIdentity', {}).get('arn', 'Unknown'),
        'Region'            : event.get('region', 'Unknown'),
    }

    # Merge config tags + dynamic tags
    # (dynamic tags take priority if key clash)
    all_tags_dict = {**AUTO_TAGS, **dynamic_tags}

    # Convert dict to AWS tag format: [{'Key': k, 'Value': v}, ...]
    return [{'Key': k, 'Value': str(v)} for k, v in all_tags_dict.items()]


# ============================================================
# HELPER FUNCTION 4 — Apply Tags to Instance
# ============================================================
def apply_tags(ec2, instance_id, tags):
    """
    Calls ec2:CreateTags to apply all tags to the instance.
    Returns True on success, False on failure.
    """
    try:
        ec2.create_tags(
            Resources = [instance_id],
            Tags      = tags
        )
        return True
    except ClientError as e:
        error_code = e.response['Error']['Code']
        print(f"Failed to tag {instance_id}: [{error_code}] {e}")
        return False