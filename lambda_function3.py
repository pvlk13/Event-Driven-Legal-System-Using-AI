import boto3
import json
from datetime import datetime,timezone

bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('legal-document-summaries')

EXTRACTION_PROMPT = """You are a legal data entry specialist. Extract data into JSON. You must follow these rules:

THE "NAME" RULE:
- Search the text for "Driver Name".
- The name appearing immediately after "Driver Name" is your candidate.
- MANDATORY: If "REGISTRANT" or "OWNER" appears near a name, DISCARD that name.

THE "SOL_DATE" RULE (CRITICAL):
- Extract accident_date in MM/DD/YYYY format.
- Calculate sol_date = accident_date + 3 YEARS.
- Example: If accident_date is 09/22/2020, then sol_date is 2023-09-22 (YYYY-MM-DD format).
- ALWAYS add exactly 3 years to the accident date.

THE "UNIT 2" PRIORITY:
- Scan for "PEDESTRIAN" or "BICYCLIST".
- If found with a name (e.g., CASTILLO or GRILLO), that person is the client.
- If NO pedestrian/bicyclist, use the FIRST "Driver Name" as Client.

THE OPPOSING PARTY:
- If client is Pedestrian → opposing_party is the FIRST "Driver Name".
- If client is Driver 1 → opposing_party is the SECOND "Driver Name".

Extract ONLY this JSON:
{
  "client_first_name": "REQUIRED - First name only",
  "client_last_name": "REQUIRED - Last name only",
  "opposing_party": "REQUIRED - Full name",
  "accident_date": "MM/DD/YYYY format",
  "sol_date": "YYYY-MM-DD format (today + 3 years)",
  "location": "Street address",
  "vehicle_info": [{"license_plate": "Plate or N/A"}],
  "document_type": "Type of document"
}

Return ONLY valid JSON, no other text."""

def lambda_handler(event, context):
    try:
        print("Lambda 3: Extracting structured legal data")
        
        # Get jobId from event (passed from Lambda 2)
        job_id = event.get('jobId')
        full_text = event.get('fullText')
        summary = event.get('summary')
        
        if not full_text:
            return {'statusCode': 400, 'body': json.dumps('No text provided')}
        
        print(f"Extracting structured data from {len(full_text)} characters...")
        
        # Call Claude to extract structured data
        legal_data = legal_data_extractor(full_text)
        
        print(f"✓ Data extracted")
        print(f"Client: {legal_data.get('client_first_name')} {legal_data.get('client_last_name')}")
        
        # Save to DynamoDB with all details
        print(f"Saving to DynamoDB...")
        table.update_item(
            Key={'jobId': job_id},
            UpdateExpression="""SET 
                raw_full_text = :rft,
                client_first_name = :cfn,
                client_last_name = :cln,
                opposing_party = :op,
                accident_date = :ad,
                sol_date = :sol,
                place = :loc,
                vehicle_info = :vi,
                document_type = :dt,
                summary = :sum,
                extracted_data_json = :edj,
                extracted_at = :ts
            """,
            ExpressionAttributeValues={
                ':rft': full_text,  # Save raw text
                ':cfn': legal_data.get('client_first_name', 'N/A'),
                ':cln': legal_data.get('client_last_name', 'N/A'),
                ':op': legal_data.get('opposing_party', 'N/A'),
                ':ad': legal_data.get('accident_date', 'N/A'),
                ':sol': legal_data.get('sol_date', 'N/A'),
                ':loc': legal_data.get('place', 'N/A'),
                ':vi': legal_data.get('vehicle_info', []),
                ':dt': legal_data.get('document_type', 'N/A'),
                ':sum': summary,
                ':edj': json.dumps(legal_data),  # Save entire JSON
                ':ts': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
            }
        )
        
        print(f"✓ Saved to DynamoDB")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'jobId': job_id,
                'legal_data': legal_data,
                'message': 'Data extracted and saved'
            })
        }
    
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return {'statusCode': 500, 'body': json.dumps(f'Error: {str(e)}')}

def legal_data_extractor(text):
    text_limited = text[:4000]
    
    try:
        print(f"Calling Bedrock for data extraction...")
        response = bedrock_runtime.converse(
            modelId='arn:aws:bedrock:us-east-1:272183979798:application-inference-profile/8ykdxt4a0ds8',
            messages=[
                {
                    'role': 'user',
                    'content': [
                        {
                            'text': f'{EXTRACTION_PROMPT}\n\nDocument text:\n\n{text_limited}'
                        }
                    ]
                }
            ],
            inferenceConfig={'maxTokens': 1000}
        )
        
        response_text = response['output']['message']['content'][0]['text']
        
        # Parse JSON from response
        try:
            legal_data = json.loads(response_text)
        except:
            # Try to extract JSON if response has extra text
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                legal_data = json.loads(json_match.group())
            else:
                legal_data = {}
        
        print(f"✓ Extracted data: {legal_data}")
        return legal_data
    
    except Exception as e:
        print(f"Extraction error: {str(e)}")
        return {}