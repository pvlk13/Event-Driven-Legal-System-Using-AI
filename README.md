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


## 📘 File-by-File Purpose

main.tf
```
provider "aws" {
    region = "us-east-1"
}
```
Purpose:
Sets the AWS provider region for the Terraform deployment.

Why it matters:
This is the Terraform entry point that establishes the base cloud configuration.





