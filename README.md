# ⚖️ Event-Driven Legal System Using AI

<p align="center">
  <b>An AI-powered, event-driven legal intake system for processing accident reports, extracting structured case data, and automating client follow-up.</b>
</p>

<p align="center">
  <img alt="AWS" src="https://img.shields.io/badge/AWS-Serverless-orange?logo=amazonaws" />
  <img alt="Python" src="https://img.shields.io/badge/Python-Backend-blue?logo=python" />
  <img alt="Terraform" src="https://img.shields.io/badge/Terraform-IaC-623CE4?logo=terraform" />
  <img alt="React" src="https://img.shields.io/badge/React-Dashboard-61DAFB?logo=react" />
  <img alt="Streamlit" src="https://img.shields.io/badge/Streamlit-Admin_App-FF4B4B?logo=streamlit" />
  <img alt="Amazon Bedrock" src="https://img.shields.io/badge/Amazon%20Bedrock-LLM-green" />
  <img alt="Textract" src="https://img.shields.io/badge/Amazon%20Textract-OCR-yellow" />
</p>

---

## 📌 Overview

This project is a **serverless legal document intake and case extraction platform** built on AWS.

It automates the full workflow of receiving legal documents by email, extracting PDF attachments, processing those documents with OCR, summarizing and structuring the case content with AI, storing the extracted results, and triggering automated client communication.

The system is especially designed for workflows involving **police accident reports** and related legal intake documents.

---

## 🚀 What This System Does

### 1️⃣ Email Intake
Incoming emails are received through **Amazon SES** and stored in **Amazon S3**.

### 2️⃣ PDF Extraction
A Lambda function reads the raw email file, finds the attached PDF, validates it, and saves it into a processed S3 location.

### 3️⃣ OCR Processing
The extracted PDF is sent to **Amazon Textract** for text detection.

### 4️⃣ AI Summarization
When Textract finishes, another Lambda collects the OCR text and sends it to **Amazon Bedrock** to generate a concise legal summary.

### 5️⃣ Structured Legal Data Extraction
A separate Lambda extracts deeper structured data such as:
- client details
- opposing party details
- accident details
- legal summary
- vehicle damage information
- role classification (driver / pedestrian / bicyclist / occupant)

### 6️⃣ Data Persistence
Processed case data is stored in **Amazon DynamoDB** for retrieval and dashboard use.

### 7️⃣ Automated Follow-Up
A **Step Functions** workflow waits until the case data is ready, then triggers an automated **retainer / next-steps email**.

### 8️⃣ Dashboard & Query Access
The processed case can be viewed via:
- a **React dashboard**
- a **Streamlit dashboard**
- an **API Gateway + Lambda query endpoint**

---

## 🧠 Core Features

- 📥 Email-based legal document intake
- 📄 Automatic PDF extraction from `.eml` files
- 🔍 OCR processing with Amazon Textract
- 🤖 AI-powered legal summarization with Amazon Bedrock
- 🧾 Structured police report data extraction
- 🚗 Vehicle damage interpretation logic
- 👤 Smart client identification logic
- 🗄️ DynamoDB-based case storage
- ⏳ Delayed workflow orchestration with Step Functions
- 📧 Automated retainer / consultation email sending
- 🌐 API endpoint for case retrieval
- 📊 Dashboard support with React and Streamlit

---

## 🚀 Tech Stack

### ☁️ Cloud & Infrastructure
- ☁️ AWS (SES, S3, Lambda, Textract, SNS, DynamoDB, Step Functions, API Gateway)
- 🏗️ Terraform

### 🤖 AI & Backend
- 🐍 Python
- 🔗 Boto3
- 🧠 Amazon Bedrock (Claude 3 Haiku)

### 🎨 Frontend
- ⚛️ React (Dashboard)
- 🚀 AWS Amplify
- 📊 Streamlit

---

## 🏗️ Architecture
<img width="2476" height="1682" alt="image" src="https://github.com/user-attachments/assets/3f752f77-a26e-4c9d-b747-6c929d39647a" />
This is a fully event-driven serverless pipeline. Emails are ingested via SES and stored in S3. A Lambda function extracts PDFs and triggers Textract for OCR. Once processing completes, SNS triggers downstream Lambdas for AI-based data extraction using Bedrock, which is stored in DynamoDB. A Step Function orchestrates delayed workflows like sending retainer emails. The frontend interacts via API Gateway to fetch processed case data

---

## 📂 Project Structure
```bash

Event-Driven-Legal-System-Using-AI/
│
├── lambda/
│   ├── lambda.tf
│   ├── lambda_function.py
│   ├── lambda_function2.py
│   ├── lambda_function3.py
│   ├── lambda_query.py
│   ├── lambda_step.py
│   ├── lambda_function.zip
│   ├── lambda_extractor.zip
│   ├── lambda_query.zip
│
├── legal-dashboard/
│   ├── amplify/
│   ├── public/
│   ├── src/
│   ├── package.json
│   └── README.md
│
├── retainer_email/
│   ├── send_retainer_email.py
│   └── send_retainer_email.zip
│
├── s3/
│   └── s3bucket.tf
│
├── step_function/
│   ├── step_function_definition.json
│   └── start_step_function.zip
│
├── dynamoDB.tf
├── ses.tf
├── sns.tf
├── main.tf
├── logic.py
├── streamlit_app.py
└── requirements.txt
```
---
## 📂 File-by-File Purpose

### ⚙️ `main.tf`

```

provider "aws" {
    region = "us-east-1"
}

```

| 🔹 **Section** | 📖 **Description** |
|--------------|------------------|
| 🎯 **Purpose** | Defines the base Terraform configuration and AWS provider setup for the project |
| 💡 **Why It Matters** | Acts as the entry point for infrastructure deployment and ensures all cloud resources are created in the correct AWS environment |

---

### 🗄️ `dynamoDB.tf`

```
resource "aws_dynamodb_table" "legal_summaries" {
  name           = "legal-document-summaries"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "jobId"
  
  attribute {
    name = "jobId"
    type = "S"
  }
  global_secondary_index {
    name            = "ClientIndex"
    hash_key        = "client_last_name"
    projection_type = "ALL"
  }
  
  attribute {
    name = "client_last_name"
    type = "S"
  }

  # DynamoDB streams
  #  ADD THIS to capture events from table
  stream_enabled   = true
  stream_view_type = "NEW_IMAGE"
}

```
<img width="2982" height="1110" alt="image" src="https://github.com/user-attachments/assets/60a80e3a-6074-48e7-9333-85a9ce4b30bf" />


| 🔹 **Section** | 📖 **Description** |
|--------------|------------------|
| 🎯 **Purpose** | Creates the **Amazon DynamoDB** table used to store extracted legal case data, summaries, and processing metadata |
| 💡 **Why It Matters** | Serves as the system’s main structured data store, allowing processed case information to be saved, queried, and reused by dashboards and workflows |

---

### 📩 `ses.tf`

```
#ses domain identity
# 1. Create the "Box" (Rule Set)
resource "aws_ses_receipt_rule_set" "main" {
  rule_set_name = "primary-ruleset"
}

# 2. Tell AWS: "This is the box I am currently using"
resource "aws_ses_active_receipt_rule_set" "main" {
  rule_set_name = aws_ses_receipt_rule_set.main.rule_set_name
}
resource "aws_ses_domain_identity" "legal_domain"{
    domain = "vijayalakshmi-kurra-porfolio.website"
}
# receipt rule
resource "aws_ses_receipt_rule" "storage_email" {
  name = "store-to-s3"
  rule_set_name = aws_ses_active_receipt_rule_set.main.rule_set_name
  recipients = [
    "legal@vijayalakshmi-kurra-porfolio.website",
    "intake@vijayalakshmi-kurra-porfolio.website",
    "claims@vijayalakshmi-kurra-porfolio.website"
  ]
  enabled = true
  scan_enabled = true

  s3_action {
    bucket_name = aws_s3_bucket.legal_uploads.id
    position = 1
  }
}

```

| 🔹 **Section** | 📖 **Description** |
|--------------|------------------|
| 🎯 **Purpose** | Configures **Amazon SES** to receive incoming legal intake emails |
| 💡 **Why It Matters** | Acts as the starting point of the entire workflow by allowing users or clients to send documents directly into the system via email |

---

### 📡 `sns.tf`

```
# 1. Create the SNS Topic
resource "aws_sns_topic" "textract_notifications" {
  name = "AmazonTextract-LegalSummaries"
}

# 2. Allow Textract to publish to this topic
resource "aws_sns_topic_policy" "default" {
  arn = aws_sns_topic.textract_notifications.arn

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowTextractToPublish"
        Effect = "Allow"
        Principal = {
          Service = "textract.amazonaws.com"
        }
        Action   = "sns:Publish"
        Resource = aws_sns_topic.textract_notifications.name
      }
    ]
  })
}
# Link SNS to Lambda
resource "aws_sns_topic_subscription" "textract_to_lambda" {
  topic_arn = aws_sns_topic.textract_notifications.arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.results_processor.arn # Your new Lambda B
}

# Give SNS permission to invoke the Lambda
resource "aws_lambda_permission" "allow_sns_invoke" {
  statement_id  = "AllowExecutionFromSNS"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.results_processor.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = aws_sns_topic.textract_notifications.arn
}
```
<img width="2966" height="1212" alt="image" src="https://github.com/user-attachments/assets/aac13048-04e2-4e86-bd44-ead88308d076" />


| 🔹 **Section** | 📖 **Description** |
|--------------|------------------|
| 🎯 **Purpose** | Creates the **Amazon SNS topic** used to receive completion notifications from **Amazon Textract** |
| 💡 **Why It Matters** | Enables an **event-driven workflow** by automatically triggering the next Lambda function after OCR completes — eliminating polling, reducing cost, and improving scalability |

---

### 🪣 `s3/s3bucket.tf`

```
resource "aws_s3_bucket" "legal_uploads" {
    bucket = "legal-intake-uploads-${random_id.id.hex}"  
}
resource "random_id" "id" {
  byte_length = 4
}
# the trigger
resource "aws_s3_bucket_notification" "bucket_notification" {
    bucket = aws_s3_bucket.legal_uploads.id
    lambda_function {
      lambda_function_arn = aws_lambda_function.legal_processor.arn
      events = ["s3:ObjectCreated:*"]
      filter_prefix       = ""
      filter_suffix       = ".eml"  # Only trigger on .eml files
    }
    depends_on = [ aws_lambda_permission.allow_s3 ]
}
resource "aws_s3_bucket_policy" "legal_uploads_policy" {
     bucket = aws_s3_bucket.legal_uploads.id

     policy = jsonencode({
       Version = "2012-10-17"
       Statement = [
         {
           Sid    = "AllowSESPuts"
           Effect = "Allow"
           Principal = {
             Service = "ses.amazonaws.com"
           }
           Action   = "s3:PutObject"
           Resource = "${aws_s3_bucket.legal_uploads.arn}/*"
           Condition = {
             StringEquals = {
               "aws:Referer" = data.aws_caller_identity.current.account_id
             }
           }
         },
         {
           Sid    = "AllowTextractS3Access"
           Effect = "Allow"
           Principal = {
             Service = "textract.amazonaws.com"
           }
           Action   = "s3:GetObject"
           Resource = "${aws_s3_bucket.legal_uploads.arn}/*"
         },
         {
           Sid    = "AllowLambdaS3Access"
           Effect = "Allow"
           Principal = {
             AWS = aws_iam_role.lambda_role.arn
           }
           Action = [
             "s3:GetObject",
             "s3:GetObjectVersion"
           ]
           Resource = "${aws_s3_bucket.legal_uploads.arn}/*"
         }
       ]
     })
   }
# Add this to get your account ID automatically
data "aws_caller_identity" "current" {}
```


<img width="2144" height="1212" alt="image" src="https://github.com/user-attachments/assets/fc9d27b9-3f9f-4a93-9929-4d4ece30a654" />



| 🔹 **Section** | 📖 **Description** |
|--------------|------------------|
| 🎯 **Purpose** | Creates the **Amazon S3 bucket** used to store raw incoming emails and extracted PDF documents |
| 💡 **Why It Matters** | Provides durable document storage and connects file uploads to the processing pipeline through S3-triggered Lambda execution |

---

### 🧩 `lambda/lambda.tf`

```
# the packaging 
data "archive_file" "lambda_zip" {
  type = "zip"
  source_file = "${path.module}/lambda_function.py" # Adding path.module makes it more stable
  output_path = "${path.module}/lambda_function.zip"
}
data "archive_file" "lambda2_zip" {
  type = "zip"
  source_file = "${path.module}/lambda_function2.py" # Adding path.module makes it more stable
  output_path = "${path.module}/results_processor.zip"  
}
# Lambda 3 - Data Extractor
data "archive_file" "lambda_extractor_zip" {
  type        = "zip"
  source_file = "${path.module}/lambda_function3.py"
  output_path = "${path.module}/lambda_extractor.zip"
}
# Lambda Step function
data "archive_file" "start_sf_zip" {
  type        = "zip"
  source_file = "${path.module}/lambda_step.py"
  output_path = "${path.module}/start_step_function.zip"
}
# Package send_retainer_email Lambda
data "archive_file" "send_email_zip" {
  type        = "zip"
  source_file = "${path.module}/send_retainer_email.py"
  output_path = "${path.module}/send_retainer_email.zip"
}

resource "aws_lambda_function" "start_step_function" {
  filename         = data.archive_file.start_sf_zip.output_path
  function_name    = "start-step-function"
  role             = aws_iam_role.lambda_role.arn
  handler          = "lambda_step.lambda_handler"
  runtime          = "python3.9"
  source_code_hash = data.archive_file.start_sf_zip.output_base64sha256

  environment {
    variables = {
      STATE_MACHINE_ARN = aws_sfn_state_machine.retainer_workflow.arn
    }
  }
}

# the Function
resource "aws_lambda_function" "legal_processor" {
    filename = data.archive_file.lambda_zip.output_path
    function_name = "legal_pdf_processor"
    role = aws_iam_role.lambda_role.arn
    handler       = "lambda_function.lambda_handler"
    runtime       = "python3.9"
    source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  
}
resource "aws_lambda_function" "results_processor" {
    filename = data.archive_file.lambda2_zip.output_path
    function_name = "results_processor"
    role = aws_iam_role.lambda_role.arn
    handler       = "lambda_function2.lambda_handler"
    runtime       = "python3.9"
    source_code_hash = data.archive_file.lambda2_zip.output_base64sha256
  
}

 # permission for s3 to invoke lambda
 resource "aws_lambda_permission" "allow_s3" {
    statement_id = "AllowExecutionFromS3Bucket"
    action = "lambda:InvokeFunction"
    function_name = aws_lambda_function.legal_processor.function_name
    principal = "s3.amazonaws.com"
    source_arn = aws_s3_bucket.legal_uploads.arn
   
 }
 resource "aws_lambda_function" "legal_data_extractor" {
  filename         = data.archive_file.lambda_extractor_zip.output_path
  function_name    = "legal_data_extractor"
  role             = aws_iam_role.lambda_role.arn
  handler          = "lambda_function3.lambda_handler"
  runtime          = "python3.9"
  source_code_hash = data.archive_file.lambda_extractor_zip.output_base64sha256
  timeout          = 60
}
# Query Lambda
data "archive_file" "lambda_query_zip" {
  type        = "zip"
  source_file = "${path.module}/lambda_query.py"
  output_path = "${path.module}/lambda_query.zip"
}

resource "aws_lambda_function" "query_function" {
  filename         = data.archive_file.lambda_query_zip.output_path
  function_name    = "legal-query-function"
  role             = aws_iam_role.lambda_role.arn
  handler          = "lambda_query.lambda_handler"
  runtime          = "python3.9"
  source_code_hash = data.archive_file.lambda_query_zip.output_base64sha256
  timeout          = 30
}

# API Gateway
resource "aws_apigatewayv2_api" "legal_api" {
  name          = "legal-case-api"
  protocol_type = "HTTP"
  
  cors_configuration {
    allow_origins = ["*"]
    allow_methods = ["GET", "POST", "OPTIONS"]
    allow_headers = ["*"]
  }
}

# Lambda Integration
resource "aws_apigatewayv2_integration" "lambda" {
  api_id             = aws_apigatewayv2_api.legal_api.id
  integration_type   = "AWS_PROXY"
  integration_method = "POST"
  integration_uri    = aws_lambda_function.query_function.arn
  payload_format_version = "2.0"
}

# Route
resource "aws_apigatewayv2_route" "get_case" {
  api_id    = aws_apigatewayv2_api.legal_api.id
  route_key = "GET /cases/{jobId}"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

# Stage
resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.legal_api.id
  name        = "$default"
  auto_deploy = true
}

# Lambda Permission
resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.query_function.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.legal_api.execution_arn}/*/*"
}
# DynamoDB streams
resource "aws_lambda_event_source_mapping" "ddb_trigger" {
  event_source_arn  = aws_dynamodb_table.legal_summaries.stream_arn
  function_name     = aws_lambda_function.start_step_function.arn
  starting_position = "LATEST"
}

# Arn for stepfunction

resource "aws_sfn_state_machine" "retainer_workflow" {
  name     = "retainer-workflow"
  role_arn = aws_iam_role.step_function_role.arn
  definition = file("step_function_definition.json")
}

resource "aws_lambda_function" "send_retainer_email" {
  filename         = data.archive_file.send_email_zip.output_path
  function_name    = "send_retainer_email"
  role             = aws_iam_role.lambda_role.arn
  handler          = "send_retainer_email.lambda_handler"
  runtime          = "python3.9"
  source_code_hash = data.archive_file.send_email_zip.output_base64sha256
  timeout          = 60

  environment {
    variables = {
      TABLE_NAME            = aws_dynamodb_table.legal_summaries.name
      SENDER_EMAIL          = "legal@vijayalakshmi-kurra-porfolio.website"
      OFFICE_CALENDLY_LINK  = "https://calendly.com/office-consultation"
      VIRTUAL_CALENDLY_LINK = "https://calendly.com/virtual-consultation"
    }
  }
}
# Output API endpoint
output "api_endpoint" {
  value = aws_apigatewayv2_api.legal_api.api_endpoint
  description = "API Gateway endpoint URL"
}

```
<img width="2970" height="926" alt="image" src="https://github.com/user-attachments/assets/2fb6c0d3-2614-4b44-a520-542764601e00" />

<img width="2968" height="830" alt="image" src="https://github.com/user-attachments/assets/40690420-0ec4-4762-8be8-a3fd83d7e99e" />





| 🔹 **Section** | 📖 **Description** |
|--------------|------------------|
| 🎯 **Purpose** | Deploys and configures all AWS Lambda functions, permissions, triggers, API resources, and workflow integrations |
| 💡 **Why It Matters** | Acts as the glue that connects all serverless components together and makes the full legal automation pipeline operational |

---

### 📥 `lambda/lambda_function.py`
```
import boto3
import json
import urllib.parse
import email
import os
from email import policy

s3 = boto3.client('s3')
textract = boto3.client('textract')
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('legal-document-summaries')

SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:272183979798:AmazonTextract-LegalSummaries'
ROLE_ARN = 'arn:aws:iam::272183979798:role/TextractServiceRole'


def lambda_handler(event, context):
    try:
        for record in event['Records']:
            bucket = record['s3']['bucket']['name']
            key = urllib.parse.unquote_plus(record['s3']['object']['key'])

            # Only process .eml files
            if key.startswith("processed-pdfs/") or key.lower().endswith('.pdf'):
                 print(f"Skipping generated PDF object: {key}")
                 continue

            print(f"Lambda 1: Processing email: {key}")

            # Download email message
            obj = s3.get_object(Bucket=bucket, Key=key)
            email_content = obj['Body'].read()

            print(f"Email size: {len(email_content)} bytes")

            # Parse email
            msg = email.message_from_bytes(email_content, policy=policy.default)

            print(f"From: {msg.get('From')}")
            print(f"Subject: {msg.get('Subject')}")

            # Extract PDF attachment
            pdf_content = None
            pdf_filename = None

            for part in msg.iter_parts():
                if part.get_content_disposition() == 'attachment':
                    filename = part.get_filename()

                    if filename and filename.lower().endswith('.pdf'):
                        pdf_content = part.get_payload(decode=True)
                        pdf_filename = filename
                        print(f"✓ Found PDF attachment: {pdf_filename}")
                        break

            if not pdf_content:
                print("✗ No PDF found in email")
                continue

            # Verify it's a real PDF
            if not pdf_content.startswith(b'%PDF'):
                print("✗ Attachment is not a valid PDF")
                continue

            print(f"✓ Valid PDF found: {len(pdf_content)} bytes")

            # Save extracted PDF to a separate prefix
            base_name = os.path.splitext(os.path.basename(key))[0]
            pdf_key = f"processed-pdfs/{base_name}.pdf"

            s3.put_object(
                Bucket=bucket,
                Key=pdf_key,
                Body=pdf_content,
                ContentType='application/pdf'
            )

            print(f"✓ Saved PDF to S3: {pdf_key}")

            # Start Textract using the saved PDF
            print("Sending PDF to Textract with SNS notifications...")
            response = textract.start_document_text_detection(
                DocumentLocation={
                    'S3Object': {
                        'Bucket': bucket,
                        'Name': pdf_key
                    }
                },
                NotificationChannel={
                    'SNSTopicArn': SNS_TOPIC_ARN,
                    'RoleArn': ROLE_ARN
                }
            )

            job_id = response['JobId']
            print(f"✓ Textract job started: {job_id}")

            # Save original PDF reference immediately in DynamoDB
            table.update_item(
                 Key={'jobId': job_id},
                 UpdateExpression="""
                        SET original_pdf_bucket = :b,
                            original_pdf_key = :k,
                            original_email_key = :e,
                            pdf_filename = :f
                     """,
                 ExpressionAttributeValues={
                      ':b': bucket,
                      ':k': pdf_key,
                       ':e': key,
                       ':f': pdf_filename
                 }
            )          

            print(f"✓ Stored PDF reference in DynamoDB for jobId: {job_id}")

            # Optional: delete original email after successful extraction
            s3.delete_object(Bucket=bucket, Key=key)
            print(f"✓ Deleted original email: {key}")

        return {
            'statusCode': 200,
            'body': json.dumps('Processing complete')
        }

    except Exception as e:
        print(f"✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }
```

| 🔹 **Section** | 📖 **Description** |
|--------------|------------------|
| 🎯 **Purpose** | Reads incoming `.eml` files from S3, extracts PDF attachments, uploads the PDF back to S3, and starts the Textract OCR job |
| 💡 **Why It Matters** | This is the first processing step after email intake and is responsible for converting raw email input into a machine-processable legal document workflow |

---

### 🧠 `lambda/lambda_function2.py`

```
import boto3
import json
import time

textract = boto3.client('textract', region_name='us-east-1')
bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
lambda_client = boto3.client('lambda', region_name='us-east-1')

table = dynamodb.Table('legal-document-summaries')


def lambda_handler(event, context):
    try:
        print("=" * 80)
        print("LAMBDA 2 START")
        print("=" * 80)

        # Process all SNS messages
        for record in event['Records']:

            print("Getting SNS message...")
            message = json.loads(record['Sns']['Message'])
            job_id = message['JobId']

            print(f"JobId: {job_id}")

            print("Fetching Textract results...")
            blocks = get_textract_blocks(job_id)

            print(f"Total blocks retrieved: {len(blocks)}")

            print("Extracting text...")
            full_text = ""

            for block in blocks:
                if block['BlockType'] == 'LINE':
                    full_text += block['Text'] + " "

            print(f"Extracted {len(full_text)} characters")
            print(f"Text preview: {full_text[:200]}")

            if not full_text.strip():
                print("No text extracted")
                continue

            print("Sending to Bedrock...")
            summary = summarize_with_bedrock(full_text)

            print("✓ Summary received")

            print("Saving to DynamoDB...")
            table.update_item(
                Key={'jobId': job_id},
                UpdateExpression="""
                   SET #ts = :ts,
                   textLength = :tl,
                   summary = :sum,
                   fullText = :ft
                """,
                ExpressionAttributeNames={
                    '#ts': 'timestamp'
                },
                ExpressionAttributeValues={
                   ':ts': str(int(time.time())),
                   ':tl': len(full_text),
                   ':sum': summary,
                   ':ft': full_text[:500]
                  }
                )

            print("✓ Saved to DynamoDB")

            # Trigger Lambda 3 for structured extraction
            print("Calling Lambda 3 for data extraction...")

            lambda_client.invoke(
                FunctionName='legal_data_extractor',
                InvocationType='Event',
                Payload=json.dumps({
                    'jobId': job_id,
                    'fullText': full_text,
                    'summary': summary
                })
            )

            print("✓ Lambda 3 triggered")

        return {
            'statusCode': 200,
            'body': json.dumps('Processing completed')
        }

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }


# -----------------------------
# TEXTRACT PAGINATION HANDLER
# -----------------------------
def get_textract_blocks(job_id):

    all_blocks = []
    next_token = None

    while True:

        if next_token:
            response = textract.get_document_text_detection(
                JobId=job_id,
                NextToken=next_token
            )
        else:
            response = textract.get_document_text_detection(
                JobId=job_id
            )

        all_blocks.extend(response.get('Blocks', []))

        next_token = response.get('NextToken')

        if not next_token:
            break

    return all_blocks


# -----------------------------
# BEDROCK SUMMARIZATION
# -----------------------------
def summarize_with_bedrock(text):

    text_limited = text[:3000]

    try:
        print("Calling Bedrock...")

        response = bedrock_runtime.converse(
            modelId='arn:aws:bedrock:us-east-1:272183979798:application-inference-profile/8ykdxt4a0ds8',
            messages=[
                {
                    'role': 'user',
                    'content': [
                        {
                            'text': f'Summarize this legal document in 3-4 sentences:\n\n{text_limited}'
                        }
                    ]
                }
            ],
            inferenceConfig={
                'maxTokens': 500
            }
        )

        summary = response['output']['message']['content'][0]['text']

        print("✓ Bedrock success")

        print("=" * 80)
        print("SUMMARY:")
        print("=" * 80)
        print(summary)
        print("=" * 80)

        return summary

    except Exception as e:
        print(f"Bedrock error: {str(e)}")
        raise Exception(f"Bedrock error: {str(e)}")
```

| 🔹 **Section** | 📖 **Description** |
|--------------|------------------|
| 🎯 **Purpose** | Handles Textract completion notifications, collects OCR text, generates AI summaries using Bedrock, and updates DynamoDB |
| 💡 **Why It Matters** | Transforms raw OCR output into meaningful legal summaries and prepares the document for deeper structured extraction |

---

### ⚖️ `lambda/lambda_function3.py`

```
import boto3
import json
import time
import json , re

bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('legal-document-summaries')


EXTRACTION_PROMPT = """You are a legal data entry specialist. Extract ALL data from this police accident report into JSON format.

CRITICAL EXTRACTION RULES:

CRITICAL: Read "VEHICLE 1 DAMAGE CODES" and "VEHICLE 2 DAMAGE CODES" carefully.

For EACH vehicle:
- Box 1 (Point of Impact): severity = "severe", damage_type = "point_of_impact"
- Box 2 (Most Damage): severity = "moderate", damage_type = "most_damage"  
- Additional codes: severity = "minor", damage_type = "other_damage"

DAMAGE CODE MAPPING (NY MV-104A):
01-02: Right Front
03: Center Front (HOOD/GRILLE)
04-05: Left Front
06-08: Left Side (DOORS)
09-10: Left Rear
11: Center Rear (REAR BUMPER/TRUNK)
12-13: Right Rear
14-16: Right Side
17: Entire Vehicle (Demolished)
18: No Damage
19: Other (Undercarriage/Roof)

CRITICAL: In the PDF provided, look at "Officer's Notes". If the notes say "HIT IN THE REAR", ensure the damage_locations reflect the REAR (Code 11) even if the boxes are hard to read.

EXAMPLE from your PDF:
Example: If Box 1 contains '11', the part is 'REAR_BUMPER'. If Box 1 contains '03', the part is 'HOOD'.
→ Extract as:
  "damage_locations": [
    {"part": "REAR", "severity": "severe", "damage_type": "point_of_impact"}
]
CLIENT IDENTIFICATION RULES (VERY IMPORTANT):

First identify all people in the report and classify each one as one of:
- BICYCLIST
- PEDESTRIAN
- DRIVER
- OCCUPANT

Then choose the CLIENT using this strict priority:

1. If any BICYCLIST exists, the CLIENT MUST be the BICYCLIST.
2. If no bicyclist exists but any PEDESTRIAN exists, the CLIENT MUST be the PEDESTRIAN.
3. If neither bicyclist nor pedestrian exists, the CLIENT MUST be DRIVER 1.
4. OCCUPANT can be the CLIENT only if no bicyclist, no pedestrian, and no driver is present.

STRICT RULES:
- NEVER choose OCCUPANT if a BICYCLIST exists.
- NEVER choose OCCUPANT if a PEDESTRIAN exists.
- NEVER invent a motor vehicle for a bicyclist or pedestrian client.
- If the client is a BICYCLIST or PEDESTRIAN, extract that person as the client and keep motor vehicle extraction separate.

Examples:
- If the report labels JOHN GRILLO as BICYCLIST, then JOHN GRILLO is the CLIENT even if drivers or occupants are listed elsewhere.
- If the report labels someone as PEDESTRIAN, that person is the CLIENT unless a BICYCLIST is also present.

Extract the selected CLIENT fields:
- first_name
- last_name
- DOB
- address
- phone
- type
- description

ACCIDENT DETAILS:
- Accident Date: MM/DD/YYYY
- Time: Military time
- Location: Full address with street, city, state, zip
- Intersection: Cross streets
- Weather: (if mentioned)
- Road Condition: (if mentioned)
- SOL Date: Accident Date + 3 years (YYYY-MM-DD)

VEHICLES:
- License Plate
- Vehicle Year, Make, Model
- VIN (if available)
- Insurance Info
- Owner Name
- Damage Description
- Photos Available: Yes/No
- Image URL or reference (if visible in document)

INJURIES:
- Injured Count
- Injury Types (head, knee, jaw, etc.)
- Treatment Provided
- EMT Name/Badge
- Hospital (if applicable)

POLICE REPORT:
- Report Number
- Officer Name
- Badge Number
- Precinct
- Filed Date

IMAGES TO EXTRACT:
- Client Photo: Description of client (facial features, clothing, distinguishing marks)
- Client Vehicle Photo: Year, make, model, color, visible damage areas
- Opposing Party Photo: Description of opposing party
- Opposing Vehicle Photo: Year, make, model, color, visible damage areas

Extract ONLY this JSON:
{
  "client": {
    "first_name": "CASTILLO",
    "last_name": "FAUSTO",
    "dob": "11/12/1976",
    "address": "106 WEST 105 STREET, NEW YORK, NY",
    "type": "PEDESTRIAN",
    "description": "Male, brown skin, approximately 40-50 years old, wearing gray jacket"
  },
  "opposing_party": {
    "first_name": "CHIMIE",
    "last_name": "DORJEE",
    "dob": "08/18/1994",
    "address": "142-001 41 AVENUE, QUEENS, NY 11355",
    "type": "DRIVER",
    "description": "Male, Asian appearance, approximately 25-35 years old, wearing dark shirt"
  },
  "accident": {
    "date": "11/16/2022",
    "time": "20:01",
    "location": "WEST 105 STREET & CENTRAL PARK WEST",
    "city": "NEW YORK",
    "state": "NY",
    "description": "Vehicle struck pedestrian in crosswalk",
    "sol_date": "2025-11-16"
  },
  "vehicles": [
    {
      "vehicle_number": 1,
      "license_plate": "T698783C",
      "year": "2019",
      "make": "CHEVROLET",
      "model": "SEDAN",
      "color": "White",
      "vin": "N/A",
      "owner": "CHIMIE DORJEE",
      "damage_locations": [
        {"part": "REAR_BUMPER", "code": 1, "severity": "severe", "damage_type": "point_of_impact"},
        {"part": "DOORS", "code": 7, "severity": "moderate", "damage_type": "most_damage"}
      ],
      "point_of_impact_code": 3,
      "most_damage_code": 9,
      "other_damage_codes": [12]      
    }
  ],
  "injuries": {
    "injured_count": 1,
    "injury_types": ["HEAD", "JAW", "RIGHT KNEE"],
    "treatment": "Treated by EMT CRUZ"
  }, 
  "police_report": {
    "report_number": "MV-2022-024-000521",
    "officer": "WILLIAM J CLUNE",
    "badge": "970457",
    "precinct": "024",
    "filed_date": "10/02/2025"
  },
  "images": {
    "client_description": "Male, brown skin, 40-50 years, gray jacket",
    "client_vehicle_description": "2019 Chevrolet Sedan, white, front end damage",
    "opposing_party_description": "Male, Asian, 25-35 years, dark shirt",
    "opposing_vehicle_description": "2013 Subaru Sedan, dark color, minor damage"
  }
}
Return ONLY valid JSON, no other text."""

def lambda_handler(event, context):
    try:
        print("Lambda 3: Extracting ALL legal data")
        
        job_id = event.get('jobId')
        full_text = event.get('fullText')
        summary = event.get('summary')
        
        if not full_text:
            return {'statusCode': 400, 'body': json.dumps('No text provided')}
        
        print(f"Extracting data from {len(full_text)} characters...")
        
        legal_data = extract_legal_data(full_text)
        
        print(f"✓ Data extracted")
        
        # Save ALL fields to DynamoDB
        print(f"Saving ALL fields to DynamoDB...")
        table.update_item(
            Key={'jobId': job_id},
            UpdateExpression="""SET 
                client_first_name = :cfn,
                client_last_name = :cln,
                client_dob = :cdob,
                client_address = :caddr,
                client_type = :ctype,
                client_description = :cd,
                client_vehicle_description = :cvd,
                opposing_party_description = :opd,
                opposing_vehicle_description = :ovd,
                opposing_first_name = :opfn,
                opposing_last_name = :opln,
                opposing_dob = :opdob,
                opposing_address = :opaddr,
                opposing_type = :optype,
                accident_date = :ad,
                accident_time = :at,
                accident_location = :aloc,
                accident_city = :acity,
                accident_state = :astate,
                accident_description = :adesc,
                sol_date = :sol,
                vehicles = :veh,
                vehicle_damage_locations = :vdl,
                injured_count = :injc,
                injury_types = :injt,
                injury_treatment = :injtr,
                police_report_number = :prn,
                officer_name = :on,
                badge_number = :bn,
                precinct = :prec,
                filed_date = :fd,
                summary = :sum,
                extracted_data_json = :edj,
                extracted_at = :ts
            """,
            ExpressionAttributeValues={
                ':cfn': legal_data.get('client', {}).get('first_name', 'N/A'),
                ':cln': legal_data.get('client', {}).get('last_name', 'N/A'),
                ':cdob': legal_data.get('client', {}).get('dob', 'N/A'),
                ':caddr': legal_data.get('client', {}).get('address', 'N/A'),
                ':cd': legal_data.get('images', {}).get('client_description', 'N/A'),
                ':cvd': legal_data.get('images', {}).get('client_vehicle_description', 'N/A'),
                ':opd': legal_data.get('images', {}).get('opposing_party_description', 'N/A'),
                ':ovd': legal_data.get('images', {}).get('opposing_vehicle_description', 'N/A'),
                ':ctype': legal_data.get('client', {}).get('type', 'N/A'),
                ':opfn': legal_data.get('opposing_party', {}).get('first_name', 'N/A'),
                ':opln': legal_data.get('opposing_party', {}).get('last_name', 'N/A'),
                ':opdob': legal_data.get('opposing_party', {}).get('dob', 'N/A'),
                ':opaddr': legal_data.get('opposing_party', {}).get('address', 'N/A'),
                ':optype': legal_data.get('opposing_party', {}).get('type', 'N/A'),
                ':ad': legal_data.get('accident', {}).get('date', 'N/A'),
                ':at': legal_data.get('accident', {}).get('time', 'N/A'),
                ':aloc': legal_data.get('accident', {}).get('location', 'N/A'),
                ':acity': legal_data.get('accident', {}).get('city', 'N/A'),
                ':astate': legal_data.get('accident', {}).get('state', 'N/A'),
                ':adesc': legal_data.get('accident', {}).get('description', 'N/A'),
                ':sol': legal_data.get('accident', {}).get('sol_date', 'N/A'),
                ':veh': legal_data.get('vehicles', []),
                ':vdl': legal_data.get('vehicles', []),
                ':injc': legal_data.get('injuries', {}).get('injured_count', 0),
                ':injt': legal_data.get('injuries', {}).get('injury_types', []),
                ':injtr': legal_data.get('injuries', {}).get('treatment', 'N/A'),
                ':prn': legal_data.get('police_report', {}).get('report_number', 'N/A'),
                ':on': legal_data.get('police_report', {}).get('officer', 'N/A'),
                ':bn': legal_data.get('police_report', {}).get('badge', 'N/A'),
                ':prec': legal_data.get('police_report', {}).get('precinct', 'N/A'),
                ':fd': legal_data.get('police_report', {}).get('filed_date', 'N/A'),
                ':sum': summary,
                ':edj': json.dumps(legal_data),
                ':ts': str(int(time.time()))
            }
        )
        
        print(f"✓ ALL fields saved to DynamoDB")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'jobId': job_id,
                'message': 'All data extracted and saved'
            })
        }
    
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return {'statusCode': 500, 'body': json.dumps(f'Error: {str(e)}')}

def extract_legal_data(text):
    text_limited = text[:20000]
    
    try:
        print(f"Calling Bedrock for comprehensive data extraction...")
        response = bedrock_runtime.converse(
            modelId='arn:aws:bedrock:us-east-1:272183979798:application-inference-profile/8ykdxt4a0ds8',
            messages=[{'role': 'user', 'content': [{'text': f'{EXTRACTION_PROMPT}\n\nDocument text:\n\n{text_limited}'}]}],
            inferenceConfig={'maxTokens': 4000}
        )
        
        response_text = response['output']['message']['content'][0]['text']
        print(f"Raw response length: {len(response_text)}")
        
        # 1. Clean markdown backticks
        clean_text = response_text.strip()
        clean_text = re.sub(r'^```json\s*', '', clean_text, flags=re.IGNORECASE)
        clean_text = re.sub(r'^```\s*', '', clean_text, flags=re.IGNORECASE)
        clean_text = re.sub(r'```$', '', clean_text, flags=re.IGNORECASE)
        clean_text = clean_text.strip()
        
        # 2. Find JSON object
        json_match = re.search(r'\{[\s\S]*\}', clean_text)
        if not json_match:
            print("ERROR: No JSON object found in response")
            return {}
        
        json_str = json_match.group()
        
        # 3. Fix common JSON issues
        # Remove trailing commas before closing braces/brackets
        json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
        
        # Fix unquoted keys (though Claude should quote them)
        # Fix incomplete strings
        json_str = re.sub(r':\s*([^",\[\]{}\n]+)([,\]\}])', r': "\1"\2', json_str)
        
        print(f"Cleaned JSON length: {len(json_str)}")
        
        # 4. Parse JSON
        legal_data = json.loads(json_str)
        print(f"✓ JSON parsed successfully")
        return legal_data
        
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        print(f"Error at line {e.lineno}, column {e.colno}")
        # Try to find the problematic part
        lines = response_text.split('\n')
        if len(lines) > e.lineno - 1:
            print(f"Problem line: {lines[e.lineno - 1]}")
        return {}
        
    except Exception as e:
        print(f"Extraction error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {}

def enforce_client_rules(legal_data, full_text):
    text = full_text.upper()

    # Priority 1: Bicyclist
    if "BICYCLIST" in text:
        legal_data["client"]["type"] = "BICYCLIST"

    # Priority 2: Pedestrian
    elif "PEDESTRIAN" in text:
        legal_data["client"]["type"] = "PEDESTRIAN"

    return legal_data
    
```

| 🔹 **Section** | 📖 **Description** |
|--------------|------------------|
| 🎯 **Purpose** | Extracts structured legal information such as party details, accident facts, role classification, and damage information from OCR text |
| 💡 **Why It Matters** | This is the core AI-driven legal intelligence layer of the project, turning unstructured police reports into usable case data |

---

### 🔎 `lambda/lambda_query.py`

```
import boto3
import json

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('legal-document-summaries')

def lambda_handler(event, context):
    try:
        print("Query Lambda: Fetching case data")
        
        # Get jobId from API request
        job_id = event['pathParameters']['jobId']
        
        print(f"Fetching case: {job_id}")
        
        response = table.get_item(Key={'jobId': job_id})
        
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Case not found'})
            }
        
        item = response['Item']
        print(f"✓ Case found")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(item, default=str)
        }
    
    except Exception as e:
        print(f"ERROR: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }
```

| 🔹 **Section** | 📖 **Description** |
|--------------|------------------|
| 🎯 **Purpose** | Provides a query API for retrieving processed legal case data from DynamoDB |
| 💡 **Why It Matters** | Enables dashboards and external applications to fetch case information on demand, making the processed data accessible and useful |

---

### 🔄 `lambda/lambda_step.py`

```
import boto3
import json,os


sf = boto3.client("stepfunctions")

STATE_MACHINE_ARN = os.environ["STATE_MACHINE_ARN"]

def lambda_handler(event, context):

    for record in event["Records"]:

        if record["eventName"] != "MODIFY":
            continue

        new_image = record["dynamodb"]["NewImage"]

        job_id = new_image.get("jobId", {}).get("S")
        accident_city = new_image.get("accident_city", {}).get("S")
        summary = new_image.get("summary", {}).get("S")
        already_sent = new_image.get("retainer_sent", {}).get("BOOL")

        #  Only trigger when fully ready
        if not accident_city or not summary:
            print(f"Skipping {job_id} - incomplete data")
            continue

        #  Prevent duplicate emails
        if already_sent:
            print(f"Skipping {job_id} - already processed")
            continue

        print(f"Triggering Step Function for {job_id}")

        sf.start_execution(
            stateMachineArn=STATE_MACHINE_ARN,
            input=json.dumps({"jobId": job_id})
        )

    return {"status": "done"}
```

| 🔹 **Section** | 📖 **Description** |
|--------------|------------------|
| 🎯 **Purpose** | Monitors DynamoDB stream events and starts the Step Functions workflow when a case record is ready |
| 💡 **Why It Matters** | Ensures downstream automation only runs when the required data is available and helps prevent duplicate or premature email sending |

---

### 📧 `retainer_email/send_retainer_email.py`

```
import os
import boto3
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
s3 = boto3.client("s3", region_name="us-east-1")
ses = boto3.client("ses", region_name="us-east-1")

TABLE_NAME = os.environ["TABLE_NAME"]
SENDER_EMAIL = os.environ["SENDER_EMAIL"]
OFFICE_CALENDLY_LINK = os.environ["OFFICE_CALENDLY_LINK"]
VIRTUAL_CALENDLY_LINK = os.environ["VIRTUAL_CALENDLY_LINK"]

TEST_RECIPIENT_EMAIL = "praveenavijayalakshmi.k@gmail.com"

table = dynamodb.Table(TABLE_NAME)


def safe_str(value, default="N/A"):
    if value is None or value == "":
        return default
    return str(value)


def get_consultation_details():
    month = datetime.now().month

    if 3 <= month <= 8:
        return {
            "consultation_type": "In-Office Meeting",
            "calendly_link": OFFICE_CALENDLY_LINK
        }
    else:
        return {
            "consultation_type": "Virtual Meeting",
            "calendly_link": VIRTUAL_CALENDLY_LINK
        }


def lambda_handler(event, context):
    job_id = event["jobId"]

    response = table.get_item(Key={"jobId": job_id})
    item = response.get("Item")

    if not item:
        raise Exception(f"No DynamoDB item found for jobId={job_id}")

    client_name = f"{safe_str(item.get('client_first_name'), '')} {safe_str(item.get('client_last_name'), '')}".strip()
    opposing_name = f"{safe_str(item.get('opposing_first_name'), '')} {safe_str(item.get('opposing_last_name'), '')}".strip()

    accident_location = safe_str(item.get("accident_location"))
    summary = safe_str(item.get("summary"))
    police_report_number = safe_str(item.get("police_report_number"))

    original_pdf_key = item.get("original_pdf_key")
    original_pdf_bucket = item.get("original_pdf_bucket")

    if not original_pdf_key or not original_pdf_bucket:
        raise Exception(f"Missing original PDF location for jobId={job_id}")

    consultation = get_consultation_details()
    consultation_type = consultation["consultation_type"]
    calendly_link = consultation["calendly_link"]

    # Download original PDF from S3
    s3_obj = s3.get_object(Bucket=original_pdf_bucket, Key=original_pdf_key)
    pdf_bytes = s3_obj["Body"].read()

    subject = "Next Steps for Your Case"

    body_text = f"""Hello {client_name},

We have reviewed the initial police report for your matter.

Case Details
------------
Client: {client_name}
Location: {accident_location}
Opposing Party: {opposing_name}
Police Report Number: {police_report_number}

Summary
-------
{summary}

Consultation
------------
Based on the season, your consultation type is: {consultation_type}

Please book here:
{calendly_link}

The original police report PDF is attached for your reference.

Regards,
Law Office
"""

    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = TEST_RECIPIENT_EMAIL

    msg.attach(MIMEText(body_text, "plain"))

    attachment = MIMEApplication(pdf_bytes)
    attachment.add_header(
        "Content-Disposition",
        "attachment",
        filename=f"police_report_{job_id}.pdf"
    )
    msg.attach(attachment)

    ses.send_raw_email(
        Source=SENDER_EMAIL,
        Destinations=[TEST_RECIPIENT_EMAIL],
        RawMessage={"Data": msg.as_string()}
    )

    table.update_item(
        Key={"jobId": job_id},
        UpdateExpression="SET retainer_sent = :true, retainer_sent_time = :ts, consultation_type = :ct, test_email_sent_to = :to",
        ExpressionAttributeValues={
            ":true": True,
            ":ts": datetime.utcnow().isoformat(),
            ":ct": consultation_type,
            ":to": TEST_RECIPIENT_EMAIL
        }
    )

    return {
        "jobId": job_id,
        "sent_to": TEST_RECIPIENT_EMAIL,
        "consultation_type": consultation_type,
        "original_pdf_key": original_pdf_key,
        "status": "email_sent"
    }
```

| 🔹 **Section** | 📖 **Description** |
|--------------|------------------|
| 🎯 **Purpose** | Generates and sends the retainer or follow-up email to the client, often including the processed case details and original report attachment |
| 💡 **Why It Matters** | Turns the system from a document processor into an action-oriented legal intake platform by automating client communication |

---

### ⏳ `step_function/step_function_definition.json`

```
{
  "Comment": "Retainer workflow test",
  "StartAt": "WaitForData",
  "States": {
    "WaitForData": {
      "Type": "Wait",
      "Seconds": 300,
      "Next": "SendRetainerEmail"
    },
    "SendRetainerEmail": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-1:272183979798:function:send_retainer_email",
      "End": true
    }
  }
}
```

<img width="2766" height="1398" alt="image" src="https://github.com/user-attachments/assets/fcb5a182-c529-4faa-81a4-e809ed4c7958" />

<img width="2902" height="1300" alt="image" src="https://github.com/user-attachments/assets/6b11d2fe-9d73-44da-a6a8-018b5cc627b8" />





| 🔹 **Section** | 📖 **Description** |
|--------------|------------------|
| 🎯 **Purpose** | Defines the AWS Step Functions workflow used to delay and orchestrate the follow-up email process |
| 💡 **Why It Matters** | Adds controlled workflow orchestration to the system, allowing post-processing steps to happen in a reliable and timed sequence |

---

### 🤖 `logic.py`

```
import boto3
import json

# Initialize the Bedrock Runtime client
bedrock = boto3.client(service_name='bedrock-runtime', region_name='us-east-1')

def get_legal_summary(extracted_text):
    model_id = "anthropic.claude-3-haiku-20240307-v1:0"
    
    # Define the prompt for the AI Agent
    prompt = f"""
    You are a professional legal assistant. Please summarize the following legal document text.
    Extract the following details in JSON format:
    - Case Number
    - Key Parties
    - Primary Legal Issue
    - Summary of Facts
    
    Document Text:
    {extracted_text}
    """

    # Format the request for the Messages API
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "messages": [
            {
                "role": "user",
                "content": [{"type": "text", "text": prompt}]
            }
        ]
    })

    # Call Bedrock
    response = bedrock.invoke_model(body=body, modelId=model_id)
    
    # Parse the response
    response_body = json.loads(response.get('body').read())
    return response_body['content'][0]['text']
```

| 🔹 **Section** | 📖 **Description** |
|--------------|------------------|
| 🎯 **Purpose** | Contains helper logic for summarization and AI-driven legal text processing |
| 💡 **Why It Matters** | Centralizes reusable intelligence logic and supports cleaner separation between orchestration code and AI prompt/processing code |

---

### 📊 `streamlit_app.py`

```
import streamlit as st
import boto3
import pandas as pd
from datetime import datetime

# Configure Streamlit
st.set_page_config(page_title="Legal Case Dashboard", layout="wide")

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('legal-document-summaries')

st.title("⚖️ Legal Case Management Dashboard")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("Search")
    search_type = st.radio("Search by:", ["Job ID", "Client Name", "Case Number"])
    search_query = st.text_input("Enter search term:")

# Main content
if search_query:
    try:
        if search_type == "Job ID":
            response = table.get_item(Key={'jobId': search_query})
            cases = [response['Item']] if 'Item' in response else []
        
        elif search_type == "Client Name":
            response = table.query(
                IndexName='ClientIndex',
                KeyConditionExpression='client_last_name = :cln',
                ExpressionAttributeValues={':cln': search_query}
            )
            cases = response.get('Items', [])
        
        else:  # Case Number
            response = table.scan(
                FilterExpression='case_number = :cn',
                ExpressionAttributeValues={':cn': search_query}
            )
            cases = response.get('Items', [])
        
        if cases:
            for case in cases:
                with st.container():
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("Client Information")
                        st.write(f"**Name:** {case.get('client_first_name', 'N/A')} {case.get('client_last_name', 'N/A')}")
                        st.write(f"**Job ID:** {case.get('jobId', 'N/A')}")
                    
                    with col2:
                        st.subheader("Case Details")
                        st.write(f"**Opposing Party:** {case.get('opposing_party', 'N/A')}")
                        st.write(f"**Accident Date:** {case.get('accident_date', 'N/A')}")
                        st.write(f"**SOL Date:** {case.get('sol_date', 'N/A')}")
                    
                    st.write(f"**Location:** {case.get('location', 'N/A')}")
                    st.write(f"**Document Type:** {case.get('document_type', 'N/A')}")
                    
                    st.subheader("Summary")
                    st.write(case.get('summary', 'No summary available'))
                    
                    if case.get('vehicle_info'):
                        st.subheader("Vehicle Information")
                        for vehicle in case.get('vehicle_info', []):
                            st.write(f"**License Plate:** {vehicle.get('license_plate', 'N/A')}")
                    
                    st.markdown("---")
        else:
            st.warning("No cases found matching your search.")
    
    except Exception as e:
        st.error(f"Error: {str(e)}")

else:
    st.info("👈 Use the sidebar to search for cases")

# Footer
st.markdown("---")
st.markdown("Built with Streamlit | Legal Case Management System")
```

| 🔹 **Section** | 📖 **Description** |
|--------------|------------------|
| 🎯 **Purpose** | Provides a **Streamlit-based dashboard** for searching and viewing processed case data |
| 💡 **Why It Matters** | Offers a simple and fast admin interface for interacting with extracted legal records without needing to directly access AWS services |

---

### 🌐 `legal-dashboard/`



| 🔹 **Section** | 📖 **Description** |
|--------------|------------------|
| 🎯 **Purpose** | Contains the **React frontend dashboard** and related Amplify configuration files |
| 💡 **Why It Matters** | Delivers a more polished user-facing interface for viewing, searching, and managing processed legal cases |

---

### 📦 `requirements.txt`

```
streamlit==1.28.0
boto3==1.26.0
pandas==2.0.0
```

| 🔹 **Section** | 📖 **Description** |
|--------------|------------------|
| 🎯 **Purpose** | Lists all required Python dependencies for running the backend and supporting scripts |
| 💡 **Why It Matters** | Ensures the project environment can be reproduced consistently across local development and deployment setups |

---


