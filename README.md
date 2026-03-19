# ⚖️ Event-Driven-Legal-System-Using-AI

An end-to-end AI-powered legal intake system that automates document processing, extracts structured case data, and generates actionable insights for legal workflows.

---

## 🚀 Overview

Event-Driven-Legal-System-Using-AI automates the intake of legal documents (like police accident reports) by:

- 📩 Receiving emails via AWS SES  
- 📄 Extracting PDFs from emails  
- 🔍 Processing documents using AWS Textract  
- 🧠 Extracting structured legal data using Amazon Bedrock (LLM)  
- 💾 Storing results in DynamoDB  
- 📧 Sending automated client emails  
- 📊 Visualizing case data in a React dashboard  

---

## 🧠 Key Features

- ✅ Automated email-to-case pipeline  
- ✅ AI-based legal data extraction (Bedrock)  
- ✅ Smart client identification (driver / pedestrian / bicyclist)  
- ✅ Vehicle damage visualization  
- ✅ Human vs Vehicle detection in UI  
- ✅ Retainer email automation via SES  
- ✅ Serverless architecture (AWS Lambda + Step Functions)

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


