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