import boto3
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    """
    Scans ALL S3 buckets in the AWS account and detects
    which ones do NOT have server-side encryption enabled.
    Outputs a full security report to CloudWatch Logs.
    """

    # Initialize S3 client
    s3 = boto3.client('s3')

    # Tracking lists
    unencrypted_buckets = []   # Buckets with NO encryption
    encrypted_buckets   = []   # Buckets with encryption enabled
    error_buckets       = []   # Buckets we couldn't check

    print("=" * 60)
    print("S3 ENCRYPTION SECURITY MONITOR — STARTING SCAN")
    print("=" * 60)

    # -------------------------------------------------------
    # STEP 1: List ALL S3 buckets in the account
    # -------------------------------------------------------
    try:
        response     = s3.list_buckets()
        all_buckets  = response.get('Buckets', [])

        if not all_buckets:
            print("No S3 buckets found in this account.")
            return {'statusCode': 200, 'body': 'No buckets found.'}

        print(f"\nTotal buckets found: {len(all_buckets)}\n")
        print("-" * 60)

    except ClientError as e:
        print(f"Failed to list buckets: {e}")
        return {'statusCode': 500, 'body': str(e)}

    # -------------------------------------------------------
    # STEP 2: Check encryption config for each bucket
    # -------------------------------------------------------
    for bucket in all_buckets:
        bucket_name = bucket['Name']
        created_on  = bucket['CreationDate'].strftime('%Y-%m-%d')

        print(f"Checking: {bucket_name}  (Created: {created_on})")

        try:
            # This API call returns the encryption config if it exists
            enc_response = s3.get_bucket_encryption(Bucket=bucket_name)

            # Parse the encryption rules
            rules = enc_response['ServerSideEncryptionConfiguration']['Rules']
            encryption_info = parse_encryption_rules(rules)

            encrypted_buckets.append({
                'name':       bucket_name,
                'encryption': encryption_info
            })
            print(f"ENCRYPTED  | Type: {encryption_info}\n")

        except ClientError as e:
            error_code = e.response['Error']['Code']

            if error_code == 'ServerSideEncryptionConfigurationNotFoundError':
                # This specific error = NO encryption configured
                unencrypted_buckets.append(bucket_name)
                print(f"UNENCRYPTED | No encryption configuration found!\n")

            elif error_code == 'AccessDenied':
                # IAM role doesn't have permission to check this bucket
                error_buckets.append({
                    'name':  bucket_name,
                    'error': 'Access Denied'
                })
                print(f"ACCESS DENIED | Cannot read encryption config\n")

            else:
                # Some other unexpected error
                error_buckets.append({
                    'name':  bucket_name,
                    'error': error_code
                })
                print(f"ERROR | {error_code}\n")

    # -------------------------------------------------------
    # STEP 3: Print the full Security Summary Report
    # -------------------------------------------------------
    print("=" * 60)
    print("SECURITY SCAN — FULL REPORT")
    print("=" * 60)
    print(f"Total Buckets Scanned : {len(all_buckets)}")
    print(f"Encrypted          : {len(encrypted_buckets)}")
    print(f"UNENCRYPTED        : {len(unencrypted_buckets)}")
    print(f"Errors / Skipped  : {len(error_buckets)}")
    print("-" * 60)

    # List all unencrypted buckets clearly
    if unencrypted_buckets:
        print("\nUNENCRYPTED BUCKETS — IMMEDIATE ACTION REQUIRED:")
        for i, name in enumerate(unencrypted_buckets, 1):
            print(f"   {i}. {name}")
        print("\nRecommended Fix: Enable SSE-S3 or SSE-KMS encryption")
        print("AWS Console: S3 → Bucket → Properties → Default Encryption")
    else:
        print("\nAll buckets are encrypted. Security posture: GOOD!")

    # List encrypted buckets with their encryption type
    if encrypted_buckets:
        print("\nENCRYPTED BUCKETS:")
        for bucket in encrypted_buckets:
            print(f"{bucket['name']}  [{bucket['encryption']}]")

    # List any access errors
    if error_buckets:
        print("\nBUCKETS WITH ERRORS (review manually):")
        for bucket in error_buckets:
            print(f"   • {bucket['name']}  — Reason: {bucket['error']}")

    print("\n" + "=" * 60)
    print("SCAN COMPLETE")
    print("=" * 60)

    # -------------------------------------------------------
    # STEP 4: Return structured result
    # -------------------------------------------------------
    return {
        'statusCode': 200,
        'body': {
            'total_scanned':       len(all_buckets),
            'encrypted_count':     len(encrypted_buckets),
            'unencrypted_count':   len(unencrypted_buckets),
            'unencrypted_buckets': unencrypted_buckets,
            'error_buckets':       [b['name'] for b in error_buckets]
        }
    }


def parse_encryption_rules(rules):
    """
    Reads the encryption rule and returns a human-readable string.
    Example outputs: 'SSE-S3 (AES256)', 'SSE-KMS (aws/s3)'
    """
    if not rules:
        return "Unknown"

    rule        = rules[0]  # Usually just one rule
    sse_config  = rule.get('ApplyServerSideEncryptionByDefault', {})
    algo        = sse_config.get('SSEAlgorithm', 'Unknown')

    if algo == 'AES256':
        return 'SSE-S3 (AES256)'
    elif algo == 'aws:kms':
        kms_key = sse_config.get('KMSMasterKeyID', 'AWS Managed Key')
        return f'SSE-KMS ({kms_key})'
    else:
        return f'Unknown ({algo})'