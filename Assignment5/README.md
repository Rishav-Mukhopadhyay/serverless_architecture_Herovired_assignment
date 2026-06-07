# Assignment 5: Auto-Tagging EC2 Instances on Launch Using AWS Lambda and Boto3

## STEP 1: Create the IAM Policy for Lambda
- **Navigate to:** AWS Console → IAM → Policies → Create Policy
- **Steps:**
  1. Click **"Create Policy"**
  2. Service: `EC2` in **"Actions allowed"**, search for and attach:
    ```
    CreateTags
    DescribeInstances
    DescribeTags
    ```
  3. Service: `CloudWatch Logs` in **"Actions allowed"**, search for and attach:
    ```
    CreateLogGroup
    CreateLogStream
    PutLogEvents
    ```
    ![ ](<Screenshots/Screenshot 2026-06-07 073544.png>)
  4. Click **Next**, give the policy a name:
    ```
    EC2AutoTaggerPolicy
    ```
    ![ ](<Screenshots/Screenshot 2026-06-07 073708.png>)
  5. Click **"Create Policy"**
    ![ ](<Screenshots/Screenshot 2026-06-07 073734.png>)

## STEP 2: Create the IAM Role for Lambda
- **Navigate to:** AWS Console → IAM → Roles → Create Role
- **Steps:**
  1. Click **"Create Role"**
  2. Trusted entity type: `AWS Service`
  3. Use case: `Lambda` → Click Next
    ![ ](<Screenshots/Screenshot 2026-06-07 073809.png>)
  4. In **"Add permissions"**, search for and attach:
    ```
    EC2AutoTaggerPolicy
    ```
    ![ ](<Screenshots/Screenshot 2026-06-07 073835.png>)
  5. Click **Next**, give the role a name:
    ```
    Lambda-EC2-AutoTagger-Role
    ```
    ![ ](<Screenshots/Screenshot 2026-06-07 073854.png>)
  6. Click **"Create Role"**
    ![ ](<Screenshots/Screenshot 2026-06-07 073921.png>)

## STEP 3: Create the Lambda Function
- **Navigate to:** AWS Console → Lambda → Create Function
- **Setup:**
  1. Choose **"Author from scratch"**
  2. Fill in:
    ```
    Function name: EC2-Auto-Tagger
    Runtime:       Python 3.14
    ```
    ![ ](<Screenshots/Screenshot 2026-06-07 074020.png>)
  3. Under **"Custom settings" → "Additional settings" → "General " → "Custom execution role"**:
    - Toggle select **"Custom execution role"**
    - In **"Configure custom execution role"** section that newly opened 
    - Select **"Choose an existing role"**
    - Choose `Lambda-EC2-AutoTagger-Role`
    - Click **"Save"**
    ![ ](<Screenshots/Screenshot 2026-06-07 074052.png>)
  4. Click **"Create Function"**
  ![ ](<Screenshots/Screenshot 2026-06-07 074125.png>)

## STEP 4: Write the Boto3 Python Code
- In the Lambda function editor, replace all existing code with code.
  ![ ](<Screenshots/Screenshot 2026-06-07 074227.png>)
- Click **"Deploy"** to save
  ![ ](<Screenshots/Screenshot 2026-06-07 074250.png>)

## STEP 5: Configure Timeout
By default Lambda times out in `3 seconds`, which may be too short.
- In your Lambda function → Click **"Configuration"** tab
- Click **"General configuration" → Edit**
- Set **Timeout** to `5 minutes`
![ ](<Screenshots/Screenshot 2026-06-07 074356.png>)
- Click **Save**
![ ](<Screenshots/Screenshot 2026-06-07 074413.png>)

## STEP 6: Set Up EventBridge Rule
This is what connects EC2 launches to your Lambda automatically. CloudWatch Events is re-named to EventBridge
- **Navigate to:** AWS Console → Amazon EventBridge → Rules → Create Rule
- Select advanced builder
- **Step:**
  1. Define rule detail:
    ```
    Name:         EC2-Launch-AutoTagger
    Description:  Triggers Lambda when any EC2 instance is launched
    Event bus:    default
    ```
    ![ ](<Screenshots/Screenshot 2026-06-07 074839.png>)
    Click Next
  2. Build event pattern:
    - Select "AWS events or EventBridge partner events"
    - Event source: AWS services
    - AWS service: EC2
    - Event type: AWS API Call via CloudTrail
    - Select "Specific operations" and type `RunInstances`
    ![ ](<Screenshots/Screenshot 2026-06-07 075033.png>)
    Click Next
  3. Select target:
    - Target type: AWS service
    - Select a target: Lambda function
    - Function: EC2-Auto-Tagger
    ![ ](<Screenshots/Screenshot 2026-06-07 075144.png>)
  Click **Next → Next → "Create Rule"**
![ ](<Screenshots/Screenshot 2026-06-07 075334.png>)

## STEP 7:  Manually Test the Lambda Function
- Launch an EC2 Instance
    - **Navigate to:** EC2 → Launch Instance
    - Launch any t2.micro instance (Amazon Linux, default settings)
    - Do NOT add any tags manually 
    - Click Launch
    - Wait 30–60 seconds
  ![ ](<Screenshots/Screenshot 2026-06-07 080422.png>)
  ![ ](<Screenshots/Screenshot 2026-06-07 080520.png>)
- Verify Tags Were Applied
    **Navigate to:** EC2 → Instances → click your new instance → Tags tab
  ![ ](<Screenshots/Screenshot 2026-06-07 080806.png>)
- Check Lambda Logs
    **Navigate to:** Lambda → EC2-Auto-Tagger → Monitor → View CloudWatch Logs
  ![ ](<Screenshots/Screenshot 2026-06-07 080929.png>)
  ![ ](<Screenshots/Screenshot 2026-06-07 080949.png>)
  ![ ](<Screenshots/Screenshot 2026-06-07 081002.png>)