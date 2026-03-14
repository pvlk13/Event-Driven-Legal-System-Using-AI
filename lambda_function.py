import boto3
import json
import urllib.parse
import email
from email import policy

s3 = boto3.client('s3')
textract = boto3.client('textract')

SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:272183979798:AmazonTextract-LegalSummaries'
ROLE_ARN = 'arn:aws:iam::272183979798:role/TextractServiceRole'

def lambda_handler(event, context):
    try:
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])
        if key.endswith('.pdf'):
           print(f"Skipping PDF: {key}")
           return {'statusCode': 200, 'body': json.dumps('PDF already processed')}
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
                    print(f"✓ Found PDF: {pdf_filename}")
                    break
        
        if not pdf_content:
            print("✗ No PDF found in email")
            return {'statusCode': 400, 'body': json.dumps('No PDF found')}
        
        # Verify it's a real PDF
        if not pdf_content.startswith(b'%PDF'):
            print(f"✗ Not a valid PDF")
            return {'statusCode': 400, 'body': json.dumps('Not a valid PDF')}
        
        print(f"✓ Valid PDF: {len(pdf_content)} bytes")
        
        # Save PDF to S3
        pdf_key = key.replace('.eml', '.pdf') if key.endswith('.eml') else key + '.pdf'
        s3.put_object(
            Bucket=bucket,
            Key=pdf_key,
            Body=pdf_content,
            ContentType='application/pdf'
        )
        
        print(f"✓ Saved PDF to: {pdf_key}")
        
        # Delete original email
        s3.delete_object(Bucket=bucket, Key=key)
        
        # Send to Textract with SNS notifications
        print(f"Sending to Textract with SNS notifications...")
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
        
        return {
            'statusCode': 200,
            'body': json.dumps({'jobId': job_id, 'file': pdf_filename})
        }
    
    except Exception as e:
        print(f"✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return {'statusCode': 500, 'body': json.dumps(f'Error: {str(e)}')}