import boto3

def lambda_handler(event, context):
    """
    Automatically Stop/Start EC2 instances based on their 'Action' tag.
    - Tag 'Action: Auto-Stop'  → Stops the instance
    - Tag 'Action: Auto-Start' → Starts the instance
    """

    # Initialize the EC2 client (Lambda runs in AWS, so no credentials needed)
    ec2 = boto3.client('ec2', region_name='ap-south-1')

    # -------------------------------------------------------
    # PART 1: Stop instances tagged with Action = Auto-Stop
    # -------------------------------------------------------
    print("🔍 Looking for instances tagged 'Auto-Stop'...")

    # Describe (find) all instances with the Auto-Stop tag
    stop_response = ec2.describe_instances(
        Filters=[
            {
                'Name': 'tag:Action',        # Filter by tag key 'Action'
                'Values': ['Auto-Stop']      # Where tag value = 'Auto-Stop'
            },
            {
                'Name': 'instance-state-name',
                'Values': ['running']        # Only target RUNNING instances
            }
        ]
    )

    # Extract instance IDs from the response
    stop_instance_ids = []
    for reservation in stop_response['Reservations']:
        for instance in reservation['Instances']:
            stop_instance_ids.append(instance['InstanceId'])

    # Stop them if any found
    if stop_instance_ids:
        print(f"Stopping instances: {stop_instance_ids}")
        ec2.stop_instances(InstanceIds=stop_instance_ids)
        print(f"Successfully sent STOP signal to: {stop_instance_ids}")
    else:
        print("No running instances found with 'Auto-Stop' tag.")

    # -------------------------------------------------------
    # PART 2: Start instances tagged with Action = Auto-Start
    # -------------------------------------------------------
    print("🔍 Looking for instances tagged 'Auto-Start'...")

    start_response = ec2.describe_instances(
        Filters=[
            {
                'Name': 'tag:Action',
                'Values': ['Auto-Start']     # Where tag value = 'Auto-Start'
            },
            {
                'Name': 'instance-state-name',
                'Values': ['stopped']        # Only target STOPPED instances
            }
        ]
    )

    # Extract instance IDs
    start_instance_ids = []
    for reservation in start_response['Reservations']:
        for instance in reservation['Instances']:
            start_instance_ids.append(instance['InstanceId'])

    # Start them if any found
    if start_instance_ids:
        print(f"Starting instances: {start_instance_ids}")
        ec2.start_instances(InstanceIds=start_instance_ids)
        print(f"Successfully sent START signal to: {start_instance_ids}")
    else:
        print("No stopped instances found with 'Auto-Start' tag.")

    # -------------------------------------------------------
    # PART 3: Return a summary
    # -------------------------------------------------------
    return {
        'statusCode': 200,
        'body': {
            'stopped_instances': stop_instance_ids,
            'started_instances': start_instance_ids
        }
    }