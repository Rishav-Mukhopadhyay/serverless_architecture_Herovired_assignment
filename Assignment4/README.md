# Assignment 4: Automatic EBS Snapshot and Cleanup Using AWS Lambda and Boto3

## Architechture
![ ](Screenshots/Assignment4.jpg)
---

## STEP 1: Create an EBS Volume
- **Navigate to:** AWS Console → EC2 → Elastic Block Store → Volumes
- **Steps**
  1. Click **"Create Volume"**
  2. Fill in the details:
    ```
    Volume type: gp3 (General Purpose SSD)
    Size: 1 GiB  (minimum, free-tier friendly)
    Availability Zone: aps1-az1 (ap-south-1a)
    ```
    ![ ](<Screenshots/Screenshot 2026-06-06 114126.png>)
  3. Under "Tags" section, click "Add Tag":
    ```
    Key:   Name
    Value: Lambda-Backup-Volume
    ```
    ![ ](<Screenshots/Screenshot 2026-06-06 114231.png>)
  4. Click "Create Volume"
  ![ ](<Screenshots/Screenshot 2026-06-06 122253.png>)

## STEP 2: Create the IAM Policy for Lambda
- **Navigate to:** AWS Console → IAM → Policies → Create Policy
- **Steps:**
  1. Click **"Create Policy"**
  2. Service: `EC2` in **"Actions allowed"**, search for and attach:
    ```
    CreateTags
    CreateSnapshot
    DescribeSnapshots
    DescribeVolumes
    DeleteSnapshot
    ```
  3. Service: `CloudWatch Logs` in **"Actions allowed"**, search for and attach:
    ```
    CreateLogGroup
    CreateLogStream
    PutLogEvents
    ```
    ![ ](<Screenshots/Screenshot 2026-06-06 120209.png>)
  4. Click **Next**, give the policy a name:
    ```
    EBSSnapshotPolicy
    ```
    ![ ](<Screenshots/Screenshot 2026-06-06 120304.png>)
  5. Click **"Create Policy"**
    ![ ](<Screenshots/Screenshot 2026-06-06 120327.png>)

## STEP 3: Create the IAM Role for Lambda
- **Navigate to:** AWS Console → IAM → Roles → Create Role
- **Steps:**
  1. Click **"Create Role"**
  2. Trusted entity type: `AWS Service`
  3. Use case: `Lambda` → Click Next
    ![ ](<Screenshots/Screenshot 2026-06-06 120507.png>)
  4. In **"Add permissions"**, search for and attach:
    ```
    EBSSnapshotPolicy
    ```
    ![ ](<Screenshots/Screenshot 2026-06-06 120524.png>)
  5. Click **Next**, give the role a name:
    ```
    Lambda-EBS-Snapshot-Manager-Role
    ```
    ![ ](<Screenshots/Screenshot 2026-06-06 120542.png>)
  6. Click **"Create Role"**
    ![ ](<Screenshots/Screenshot 2026-06-06 120603.png>)

## STEP 4: Create the Lambda Function
- **Navigate to:** AWS Console → Lambda → Create Function
- **Setup:**
  1. Choose **"Author from scratch"**
  2. Fill in:
    ```
    Function name: EBS-Snapshot-Manager
    Runtime:       Python 3.14
    ```
    ![ ](<Screenshots/Screenshot 2026-06-06 120850.png>)
  3. Under **"Custom settings" → "Additional settings" → "General " → "Custom execution role"**:
    - Toggle select **"Custom execution role"**
    - In **"Configure custom execution role"** section that newly opened 
    - Select **"Choose an existing role"**
    - Choose `Lambda-EBS-Snapshot-Manager-Role`
    - Click **"Save"**
    ![ ](<Screenshots/Screenshot 2026-06-06 120927.png>)
  4. Click **"Create Function"**
  ![ ](<Screenshots/Screenshot 2026-06-06 121004.png>)

## STEP 5: Write the Boto3 Python Code
- In the Lambda function editor, replace all existing code with code.
  ![ ](<Screenshots/Screenshot 2026-06-06 121754.png>)
- Click **"Deploy"** to save
  ![ ](<Screenshots/Screenshot 2026-06-06 121834.png>)

## STEP 6: Configure Timeout
By default Lambda times out in `3 seconds`, which may be too short.
- In your Lambda function → Click **"Configuration"** tab
- Click **"General configuration" → Edit**
- Set **Memory** to `256 MB`
- Set **Timeout** to `5 minutes`
![ ](<Screenshots/Screenshot 2026-06-06 122031.png>)
- Click **Save**
![ ](<Screenshots/Screenshot 2026-06-06 122045.png>)

## STEP 7:  Manually Test the Lambda Function
- Check EBS
  ![ ](<Screenshots/Screenshot 2026-06-06 122253.png>)
- In your Lambda function, click the **"Test"** tab
- Click **"Create new event"**:
  ```
  Invocation type: Synchronous
  Event name: SnapshotTest
  Template:   Hello World (just leave default JSON)
  ```
  ![ ](<Screenshots/Screenshot 2026-06-06 122440.png>)
- Click **"Save"** then click **"Test"**
  ![ ](<Screenshots/Screenshot 2026-06-06 122524.png>)
  ![ ](<Screenshots/Screenshot 2026-06-06 122551.png>)
- EC2 → Elastic Block Store → Snapshots
  ![ ](<Screenshots/Screenshot 2026-06-06 122640.png>)