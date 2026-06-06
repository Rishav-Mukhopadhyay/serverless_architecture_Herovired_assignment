import boto3
from datetime import datetime, timezone, timedelta

# ============================================================
# CONFIGURATION — Change these values as needed
# ============================================================
BUCKET_NAME = 'my-cleanup-bucket-rishm'
DAYS_THRESHOLD = 30
# ============================================================

def lambda_handler(event, context):
    """
    Scans an S3 bucket and deletes all objects
    that are older than DAYS_THRESHOLD days.
    """

    # Initialize S3 client
    s3 = boto3.client('s3')

    # Get the cutoff date (anything older than this gets deleted)
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=DAYS_THRESHOLD)
    print(f"Cutoff date: {cutoff_date.strftime('%d-%m-%Y %H:%M:%S UTC')}")
    print(f"Files last modified BEFORE this date will be deleted.\n")

    deleted_files  = []   # Track deleted files
    kept_files     = []   # Track kept files
    error_files    = []   # Track any errors

    try:
        # -----------------------------------------------
        # Handle pagination (buckets can have 1000+ files)
        # -----------------------------------------------
        paginator = s3.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=BUCKET_NAME)

        all_objects = []
        for page in pages:
            # 'Contents' key only exists if the bucket has files
            if 'Contents' in page:
                all_objects.extend(page['Contents'])

        if not all_objects:
            print("Bucket is empty. Nothing to clean up.")
            return {
                'statusCode': 200,
                'body': 'Bucket is empty. No files deleted.'
            }

        print(f"Total files found in bucket: {len(all_objects)}\n")
        print("-" * 50)

        # -----------------------------------------------
        # Loop through each file and check its age
        # -----------------------------------------------
        for obj in all_objects:
            file_name      = obj['Key']             # The file's name/path
            last_modified  = obj['LastModified']    # datetime object (UTC)
            file_size      = obj['Size']            # Size in bytes
            age_days       = (datetime.now(timezone.utc) - last_modified).days

            print(f"   File: {file_name}")
            print(f"   Last Modified : {last_modified.strftime('%d-%m-%Y %H:%M:%S UTC')}")
            print(f"   Age           : {age_days} days")
            print(f"   Size          : {file_size} bytes")

            # -----------------------------------------------
            # Decision: Delete or Keep?
            # -----------------------------------------------
            if last_modified < cutoff_date:
                try:
                    s3.delete_object(Bucket=BUCKET_NAME, Key=file_name)
                    deleted_files.append(file_name)
                    print(f"   Status        :   DELETED (older than {DAYS_THRESHOLD} days)\n")
                except Exception as e:
                    error_files.append(file_name)
                    print(f"   Status        :  ERROR deleting - {str(e)}\n")
            else:
                kept_files.append(file_name)
                print(f"   Status        :  KEPT ({age_days} days old, within limit)\n")

        # -----------------------------------------------
        # Print Summary Report
        # -----------------------------------------------
        print("=" * 50)
        print("CLEANUP SUMMARY REPORT")
        print("=" * 50)
        print(f"Files kept    : {len(kept_files)}")
        print(f"Files deleted : {len(deleted_files)}")
        print(f"Errors        : {len(error_files)}")

        if deleted_files:
            print("\nDeleted files:")
            for f in deleted_files:
                print(f"   - {f}")

        if kept_files:
            print("\nKept files:")
            for f in kept_files:
                print(f"   - {f}")

        if error_files:
            print("\nFiles with errors:")
            for f in error_files:
                print(f"   - {f}")

        return {
            'statusCode': 200,
            'body': {
                'total_scanned' : len(all_objects),
                'deleted'       : deleted_files,
                'kept'          : kept_files,
                'errors'        : error_files
            }
        }

    except Exception as e:
        print(f"Fatal error: {str(e)}")
        return {
            'statusCode': 500,
            'body': f'Error during cleanup: {str(e)}'
        }