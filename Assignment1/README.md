# Assignment 1: Automated Instance Management Using AWS Lambda and Boto3

## Architechture
![ ](Screenshots/Assignment1.jpg)
---

## STEP 1: Create & Tag EC2 Instances
- **Navigate to:** AWS Console → EC2 → Instances → Launch Instance
- **Instance 1 (Auto-Stop)**
  1. Click **"Launch Instance"**
  2. Fill in the details:
    ```
    Name: AutoStop-Instance
    AMI: Amazon Linux 2023
    Instance type: t2.micro
    ```
    ![ ](<Screenshots/Screenshot 2026-06-05 170010.png>)
  3. Under "Tags" section, click "Add Tag":
    ```
    Key:   Action
    Value: Auto-Stop
    ```
    ![ ](<Screenshots/Screenshot 2026-06-05 170113.png>)
  4. Click "Launch Instance"
    ![ ](<Screenshots/Screenshot 2026-06-05 170150.png>)
    ![ ](<Screenshots/Screenshot 2026-06-05 170203.png>)
    ![ ](<Screenshots/Screenshot 2026-06-05 170214.png>)
- **Instance 2 (Auto-Start)**
  1. Click **"Launch Instance"**
  2. Fill in the details:
    ```
    Name: AutoStart-Instance
    AMI: Amazon Linux 2023
    Instance type: t2.micro
    ```
    ![ ](<Screenshots/Screenshot 2026-06-05 170325.png>)
  3. Under "Tags" section, click "Add Tag":
    ```
    Key:   Action
    Value: Auto-Start
    ```
  4. Click "Launch Instance"
    ![ ](<Screenshots/Screenshot 2026-06-05 170430.png>)
    ![ ](<Screenshots/Screenshot 2026-06-05 170443.png>)
    ![ ](<Screenshots/Screenshot 2026-06-05 170455.png>)

## STEP 2: Create the IAM Policy for Lambda
- **Navigate to:** AWS Console → IAM → Policies → Create Policy
- **Steps:**
  1. Click **"Create Policy"**
  2. Service: `EC2`
  3. In **"Actions allowed"**, search for and attach:
    ```
    DescribeInstances
    StartInstances
    StopInstances
    ```
    ![ ](<Screenshots/Screenshot 2026-06-05 173351.png>)
  4. Click **Next**, give the policy a name:
    ```
    EC2StartStop
    ```
    ![ ](<Screenshots/Screenshot 2026-06-05 173603.png>)
  5. Click **"Create Policy"**
    ![ ](<Screenshots/Screenshot 2026-06-05 173851.png>)

## STEP 3: Create the IAM Role for Lambda
- **Navigate to:** AWS Console → IAM → Roles → Create Role
- **Steps:**
  1. Click **"Create Role"**
  2. Trusted entity type: `AWS Service`
  3. Use case: `Lambda` → Click Next
    ![ ](<Screenshots/Screenshot 2026-06-05 172853.png>)
  4. In **"Add permissions"**, search for and attach:
    ```
    EC2StartStop
    ```
    ![ ](<Screenshots/Screenshot 2026-06-05 174741.png>)
  5. Click **Next**, give the role a name:
    ```
    Lambda-EC2-Manager-Role
    ```
    ![ ](<Screenshots/Screenshot 2026-06-05 174919.png>)
  6. Click **"Create Role"**
    ![ ](<Screenshots/Screenshot 2026-06-05 174951.png>)

## STEP 4: Create the Lambda Function
- **Navigate to:** AWS Console → Lambda → Create Function
- **Setup:**
  1. Choose **"Author from scratch"**
  2. Fill in:
    ```
    Function name: EC2-Instance-Manager
    Runtime:       Python 3.14
    ```
    ![ ](<Screenshots/Screenshot 2026-06-05 191742.png>)
  3. Under **"Custom settings" → "Additional settings" → "General " → "Custom execution role"**:
    - Toggle select **"Custom execution role"**
    - In **"Configure custom execution role"** section that newly opened 
    - Select **"Choose an existing role"**
    - Choose `Lambda-EC2-Manager-Role`
    - Click **"Save"**
    ![ ](<Screenshots/Screenshot 2026-06-05 192809.png>)
  4. Click **"Create Function"**
  ![ ](<Screenshots/Screenshot 2026-06-05 192844.png>)

## STEP 5: Write the Boto3 Python Code
- In the Lambda function editor, replace all existing code with code.
  ![ ](<Screenshots/Screenshot 2026-06-05 193150.png>)
- Click **"Deploy"** to save
  ![ ](<Screenshots/Screenshot 2026-06-05 193237.png>)

## STEP 6: Configure Timeout
By default Lambda times out in `3 seconds`, which may be too short.
- In your Lambda function → Click **"Configuration"** tab
- Click **"General configuration" → Edit**
- Set **Timeout** to `30 seconds`
  ![ ](<Screenshots/Screenshot 2026-06-05 193335.png>)
- Click **Save**
  ![ ](<Screenshots/Screenshot 2026-06-05 193350.png>)

## STEP 7:  Manually Test the Lambda Function
- Check EC2 instances statuses
  ![ ](<Screenshots/Screenshot 2026-06-05 193454.png>)
- In your Lambda function, click the **"Test"** tab
- Click **"Create new event"**:
  ```
  Invocation type: Synchronous
  Event name: ManualTest
  Template:   Hello World (just leave default JSON)
  ```
  ![ ](<Screenshots/Screenshot 2026-06-05 193851.png>)
- Click **"Save"** then click **"Test"**
  ![ ](<Screenshots/Screenshot 2026-06-05 193936.png>)
  ![ ](<Screenshots/Screenshot 2026-06-05 193949.png>)
- Navigate to: EC2 → Instances
  ![ ](<Screenshots/Screenshot 2026-06-05 194013.png>)