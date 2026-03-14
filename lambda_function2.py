import boto3
import json
import time

textract = boto3.client('textract', region_name='us-east-1')
bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('legal-document-summaries')

def lambda_handler(event, context):
    try:
        print("=" * 80)
        print("LAMBDA 2 START")
        print("=" * 80)
        
        print("Getting SNS message...")
        message = json.loads(event['Records'][0]['Sns']['Message'])
        job_id = message['JobId']
        
        print(f"JobId: {job_id}")
        
        print("Getting Textract response...")
        response = textract.get_document_text_detection(JobId=job_id)
        job_status = response.get('JobStatus')
        print(f"Job Status: {job_status}")
        
        if job_status != 'SUCCEEDED':
            print(f"Job failed")
            return {'statusCode': 400, 'body': json.dumps(f'Job failed: {job_status}')}
        
        print("Extracting text...")
        full_text = ""
        for block in response.get('Blocks', []):
            if block['BlockType'] == 'LINE':
                full_text += block['Text'] + " "
        
        print(f"Extracted {len(full_text)} characters")
        print(f"Text preview: {full_text[:200]}")
        
        if not full_text.strip():
            print("No text extracted")
            return {'statusCode': 400, 'body': json.dumps('No text extracted')}
        
        print(f"Sending to Bedrock...")
        summary = summarize_with_bedrock(full_text)
        
        print(f"✓ Summary received")
        
        print(f"Saving to DynamoDB...")
        table.put_item(
            Item={
                'jobId': job_id,
                'timestamp': str(int(time.time())),
                'textLength': len(full_text),
                'summary': summary,
                'fullText': full_text[:500]  # Store first 500 chars
            }
        )
        print(f"✓ Saved to DynamoDB")
        # Call Lambda 3 to extract structured data
        print(f"Calling Lambda 3 for data extraction...")
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        lambda_client.invoke(
        FunctionName='legal_data_extractor',  # Change to your Lambda 3 name
        InvocationType='Event',  # Async call
         Payload=json.dumps({
           'jobId': job_id,
           'fullText': full_text,
           'summary': summary
       })
     )
        print(f"✓ Lambda 3 triggered")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'jobId': job_id,
                'textLength': len(full_text),
                'summary': summary
            })
        }
    
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return {'statusCode': 500, 'body': json.dumps(f'Error: {str(e)}')}

def summarize_with_bedrock(text):
    text_limited = text[:3000]
    
    try:
        print(f"Calling Bedrock...")
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
            inferenceConfig={'maxTokens': 500}
        )
        
        summary = response['output']['message']['content'][0]['text']
        print(f"✓ Bedrock success")
        print(f"\n" + "=" * 80)
        print(f"SUMMARY:")
        print(f"=" * 80)
        print(f"{summary}")
        print(f"=" * 80)
        return summary
    
    except Exception as e:
        print(f"Bedrock error: {str(e)}")
        raise Exception(f"Bedrock error: {str(e)}")
    