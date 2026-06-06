# Assignment 3: Monitor Unencrypted S3 Buckets Using AWS Lambda and Boto3

## Architechture
![ ](Screenshots/Assignment3.jpg)
---

## STEP 1: Create S3 Buckets (With & Without Encryption)
- **Navigate to:** AWS Console → S3 → Create Bucket
- **Bucket 1 — NO Bucket Key (Minimum Base level encrytion will be there):**
  1. Click **"Create Bucket"**
  2. Fill in the details:
    ```
    AWS Region: Asia Pacific (Mumbai) ap-south-1
    Bucket type: General purpose
    Bucket namespace: Global namespace
    Bucket name: demo-unencrypted-bucket-01-rishm
    ```
    ![ ](<Screenshots/Screenshot 2026-06-06 025126.png>)
  3. Scroll to **"Default encryption"** section
  4. Select **"Disable"** ← Bucket Key
    ![ ](<Screenshots/Screenshot 2026-06-06 025416.png>)
  5. Click **"Create Bucket"**
    ![ ](<Screenshots/Screenshot 2026-06-06 025521.png>)
- **Bucket 2 — NO Bucket Key (Minimum Base level encrytion will be there):**
  1. Click **"Create Bucket"**
  2. Fill in the details:
    ```
    AWS Region: Asia Pacific (Mumbai) ap-south-1
    Bucket type: General purpose
    Bucket namespace: Global namespace
    Bucket name: demo-unencrypted-bucket-02-rishm
    ```
    ![ ](<Screenshots/Screenshot 2026-06-06 025647.png>)
  3. Scroll to **"Default encryption"** section
  4. Select **"Disable"** ← Bucket Key
    ![ ](<Screenshots/Screenshot 2026-06-06 025719.png>)
  5. Click **"Create Bucket"**
    ![ ](<Screenshots/Screenshot 2026-06-06 025747.png>)
- **Bucket 3 — WITH SSE-S3 Encryption:**
  1. Click **"Create Bucket"**
  2. Fill in the details:
    ```
    AWS Region: Asia Pacific (Mumbai) ap-south-1
    Bucket type: General purpose
    Bucket namespace: Global namespace
    Bucket name: demo-encrypted-sse-s3-rishm
    ```
    ![ ](<Screenshots/Screenshot 2026-06-06 025959.png>)
  3. Scroll to **"Default encryption"** section
  4. **Encryption type** select `Server-side encryption with Amazon S3 managed keys (SSE-S3)`
  5. Select **"Enable"** ← Bucket Key
    ![ ](<Screenshots/Screenshot 2026-06-06 030128.png>)
  6. Click **"Create Bucket"**
    ![ ](<Screenshots/Screenshot 2026-06-06 030201.png>)
- **Bucket 4 — WITH SSE-KMS Encryption:**
  1. Click **"Create Bucket"**
  2. Fill in the details:
    ```
    AWS Region: Asia Pacific (Mumbai) ap-south-1
    Bucket type: General purpose
    Bucket namespace: Global namespace
    Bucket name: demo-encrypted-sse-kms-rishm
    ```
    ![ ](<Screenshots/Screenshot 2026-06-06 030319.png>)
  3. Scroll to **"Default encryption"** section
  4. **Encryption type** select `Server-side encryption with AWS Key Management Service keys (SSE-KMS)`
  5. **AWS KMS key** select `Choose from your AWS KMS keys` choose aws default key
  6. Select **"Enable"** ← Bucket Key
    ![ ](<Screenshots/Screenshot 2026-06-06 030612.png>)
  7. Click **"Create Bucket"**
    ![ ](<Screenshots/Screenshot 2026-06-06 030629.png>)

## STEP 2: Create the IAM Role for Lambda
- **Navigate to:** AWS Console → IAM → Roles → Create Role
- **Steps:**
  1. Click **"Create Role"**
  2. Trusted entity type: `AWS Service`
  3. Use case: `Lambda` → Click Next
    ![ ](<Screenshots/Screenshot 2026-06-06 031157.png>)
  4. In **"Add permissions"**, search for and attach:
    ```
    AmazonS3ReadOnlyAccess
    CloudWatchLogsFullAccess
    ```
    ![ ](<Screenshots/Screenshot 2026-06-06 031229.png>)
  5. Click **Next**, give the role a name:
    ```
    Lambda-S3-Security-Monitor-Role
    ```
    ![ ](<Screenshots/Screenshot 2026-06-06 031255.png>)
  6. Click **"Create Role"**
    ![ ](<Screenshots/Screenshot 2026-06-06 031323.png>)

## STEP 3: Create the Lambda Function
- **Navigate to:** AWS Console → Lambda → Create Function
- **Setup:**
  1. Choose **"Author from scratch"**
  2. Fill in:
    ```
    Function name: S3-Encryption-Monitor
    Runtime:       Python 3.14
    ```
    ![ ](<Screenshots/Screenshot 2026-06-06 031556.png>)
  3. Under **"Custom settings" → "Additional settings" → "General " → "Custom execution role"**:
    - Toggle select **"Custom execution role"**
    - In **"Configure custom execution role"** section that newly opened 
    - Select **"Choose an existing role"**
    - Choose `Lambda-S3-Security-Monitor-Role`
    - Click **"Save"**
    ![ ](<Screenshots/Screenshot 2026-06-06 031636.png>)
  4. Click **"Create Function"**
  ![ ](<Screenshots/Screenshot 2026-06-06 031702.png>)

## STEP 5: Write the Boto3 Python Code
- In the Lambda function editor, replace all existing code with code.
![ ](<Screenshots/Screenshot 2026-06-06 032206.png>)
- Click **"Deploy"** to save
![ ](<Screenshots/Screenshot 2026-06-06 032225.png>)

## STEP 6: Configure Lambda Settings
By default Lambda times out in `3 seconds`, which may be too short.
- In your Lambda function → Click **"Configuration"** tab
- Click **"General configuration" → Edit**
- Set **Timeout** to `1 minutes`
![ ](<Screenshots/Screenshot 2026-06-06 032409.png>)
- Click **Save**
![ ](<Screenshots/Screenshot 2026-06-06 032428.png>)

## STEP 7:  Manually Test the Lambda Function
- Check S3 bucket
  ![ ](<Screenshots/Screenshot 2026-06-06 032538.png>)
- In your Lambda function, click the **"Test"** tab
- Click **"Create new event"**:
  ```
  Invocation type: Synchronous
  Event name: SecurityScanTest
  Template:   Hello World (just leave default JSON)
  ```
  ![ ](<Screenshots/Screenshot 2026-06-06 032643.png>)
- Click **"Save"** then click **"Test"**
  ![ ](<Screenshots/Screenshot 2026-06-06 032755.png>)
  ![ ](<Screenshots/Screenshot 2026-06-06 033334.png>)

Not possible to re-create as currently AWS does not support creating S3 buckets without base level encryption
![alt text](<Screenshots/Screenshot 2026-06-06 033451.png>)