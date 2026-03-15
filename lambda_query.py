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