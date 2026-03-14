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