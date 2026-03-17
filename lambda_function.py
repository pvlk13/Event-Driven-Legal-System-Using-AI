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