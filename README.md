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
## 🔥 From Email to Insight: Event-Driven Legal AI Pipeline

![Image](https://github.com/user-attachments/assets/cd36d21c-9348-41ac-af7b-51717f24a3a4)

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


| 🔹 **Section** | 📖 **Description** |
|--------------|------------------|
| 🎯 **Purpose** | Reads incoming `.eml` files from S3, extracts PDF attachments, uploads the PDF back to S3, and starts the Textract OCR job |
| 💡 **Why It Matters** | This is the first processing step after email intake and is responsible for converting raw email input into a machine-processable legal document workflow |

---

### 🧠 `lambda/lambda_function2.py`



| 🔹 **Section** | 📖 **Description** |
|--------------|------------------|
| 🎯 **Purpose** | Handles Textract completion notifications, collects OCR text, generates AI summaries using Bedrock, and updates DynamoDB |
| 💡 **Why It Matters** | Transforms raw OCR output into meaningful legal summaries and prepares the document for deeper structured extraction |

---

### ⚖️ `lambda/lambda_function3.py`



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

### 🚀 Frontend Deployment (AWS Amplify)

The frontend for this project is deployed using AWS Amplify, enabling continuous deployment directly from the GitHub repository.

### 🔧 Setup Overview

 - Framework: React (Create React App)

 - Deployment: AWS Amplify Hosting

 - Source: GitHub repository

 - Build configuration: amplify.yml

### ⚙️ Amplify Build Configuration

The project uses a custom build configuration to ensure proper dependency resolution:
```
version: 1
applications:
  - appRoot: legal-dashboard
    frontend:
      phases:
        preBuild:
          commands:
            - npm install --legacy-peer-deps
        build:
          commands:
            - npm run build
      artifacts:
        baseDirectory: build
        files:
          - '**/*'
      cache:
        paths:
          - node_modules/**/*
```
### 📁 Important Notes

 - The frontend resides in:
  ```
  legal-dashboard/
  ```
 - The file aws-exports.js is required for Amplify configuration and must be committed to the repository.
   ```
   legal-dashboard/src/aws-exports.js
   ```
### 🔄 Continuous Deployment

 - Amplify automatically deploys the application on every push to the main branch.

Workflow:   
 ```
 GitHub Push → Amplify Build → Deploy → Live URL
 ```
### 🌐 Live Application

Once deployed, the app is accessible at: 
```
https://<your-amplify-app-id>.amplifyapp.com
```

### 📌 Why Amplify?

 - Fully managed CI/CD

 - Automatic builds and deployments

 - Seamless GitHub integration

 - Scalable hosting for React applications

 <img width="1708" height="694" alt="image" src="https://github.com/user-attachments/assets/dbe3b5ca-9ecd-4b7d-b424-3919ec2bbae4" />


 <img width="2098" height="1070" alt="image" src="https://github.com/user-attachments/assets/462a870e-7a05-4ebe-b336-186f765ab121" />

 <img width="2986" height="1674" alt="image" src="https://github.com/user-attachments/assets/78c87025-9ad8-433c-a980-c661614e88b7" />

 <img width="2730" height="1538" alt="image" src="https://github.com/user-attachments/assets/fe981836-046c-4d78-ba13-4d842d14298e" />

 <img width="1966" height="1130" alt="image" src="https://github.com/user-attachments/assets/7ccabda8-380c-4154-933f-4fcc2f6043ad" />

 <img width="1996" height="710" alt="image" src="https://github.com/user-attachments/assets/ee05eb35-c213-4b5f-b7e7-601b0c471e78" />



### ⚠️ Challenges & Solutions
| #  | Challenge                                          | Root Cause                                | Solution                                                                     |
| -- | -------------------------------------------------- | ----------------------------------------- | ---------------------------------------------------------------------------- |
| 1  | Lambda not triggering from S3                      | Wrong event filter (`.pdf` vs `.eml`)     | Updated S3 trigger to listen for `.eml` files and handled parsing correctly  |
| 2  | Textract not processing PDFs                       | PDF not uploaded to S3 properly           | Extracted PDF from email and ensured it exists in S3 before calling Textract |
| 3  | DynamoDB not fully populated                       | Async pipeline delay (Textract + Bedrock) | Introduced **Step Functions with 5-min wait** to ensure complete data        |
| 4  | Duplicate / incorrect vehicle & pedestrian mapping | Weak extraction prompt logic              | Improved prompt with **strict role mapping (PEDESTRIAN, BICYCLIST, DRIVER)** |
| 5  | Client and opposing vehicle confusion              | AI ambiguity in role linking              | Added **priority-based client selection logic** in prompt                    |
| 6  | Wrong images for pedestrian/bicycle                | UI assumed vehicle always exists          | Added **conditional rendering + person/bicycle placeholder UI**              |
| 7  | Missing original PDF in email Lambda               | PDF key not stored in DB                  | Stored `original_pdf_key` in **Lambda 1 → passed through pipeline**          |
| 8  | Email not sending                                  | Missing SES config / env variables        | Added **Terraform env variables + SES permissions**                          |
| 9  | Step Function not triggering                       | Missing IAM permissions                   | Added `states:StartExecution` permission to Lambda                           |
| 10 | DynamoDB Stream not working                        | Missing stream IAM permissions            | Added `GetRecords`, `DescribeStream`, etc. permissions                       |
| 11 | Step Function definition errors                    | Missing `Next` state / invalid ARN        | Fixed JSON definition and proper Lambda ARN mapping                          |
| 12 | Lambda import errors (`os not defined`)            | Missing imports                           | Added required Python imports (`import os`)                                  |
| 13 | Multiple PDF uploads causing conflicts             | No orchestration                          | Used **Step Functions → each job runs independently**                        |
| 14 | Amplify build failing (dependency conflict)        | React + TypeScript mismatch               | Used `npm install --legacy-peer-deps`                                        |
| 15 | Amplify build failing (`aws-exports` missing)      | File ignored by Git                       | Forced commit of `aws-exports.js`                                            |
| 16 | Git push rejected                                  | Local branch behind remote                | Used `git pull --rebase` before pushing                                      |
| 17 | Lambda not triggering at all                       | Misconfigured S3 notifications            | Verified event mapping + permissions                                         |
| 18 | Wrong damage visualization in UI                   | Poor normalization logic                  | Improved `normalizePart()` mapping logic                                     |
| 19 | Vehicle shown for pedestrian cases                 | UI assumption issue                       | Added `isClientHuman` condition in React                                     |
| 20 | Plate number confusion (same for both)             | AI extraction inconsistency               | Strengthened prompt to separate **client vs opposing vehicle**               |
| 21 | Step Function confusion                            | Lack of orchestration understanding       | Used Step Functions for **delay + reliability + scaling**                    |
| 22 | Handling bulk uploads                              | Sequential processing concern             | Step Functions enabled **parallel independent executions**                   |
| 23 | Frontend only working on localhost                 | Not deployed                              | Used **AWS Amplify for CI/CD deployment**                                    |
| 24 | Understanding architecture flow                    | Complex event-driven system               | Created **visual architecture diagram (draw.io + AWS icons)**                |

### 💡 Key Learnings

 - Event-driven systems require proper orchestration (Step Functions)

 - AI extraction accuracy depends heavily on prompt engineering

 - Frontend must handle real-world edge cases (not just happy path)

 - CI/CD pipelines (Amplify) require repo completeness (no missing files)

### 🔐 Environment Variables
# Lambda

   - TABLE_NAME

   - PDF_BUCKET

   - SENDER_EMAIL

   - OFFICE_CALENDLY_LINK

   - VIRTUAL_CALENDLY_LINK

### 🧪 Testing

  - Send email with PDF attachment to SES email

  - Wait for processing (~5 mins)

  - Open dashboard and search by jobId

### 📈 Future Improvements

  🔍 Confidence scoring for AI extraction

      📂 Multi-document support

      📊 Analytics dashboard

      🤖 Fine-tuned legal LLM

      🖼️ Real image extraction instead of placeholders

### 👩‍💻 Author

      Vijayalakshmi Kurra  
    

  

   


