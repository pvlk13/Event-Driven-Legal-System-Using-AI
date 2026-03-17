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

        # ✅ Only trigger when fully ready
        if not accident_city or not summary:
            print(f"Skipping {job_id} - incomplete data")
            continue

        # ✅ Prevent duplicate emails
        if already_sent:
            print(f"Skipping {job_id} - already processed")
            continue

        print(f"Triggering Step Function for {job_id}")

        sf.start_execution(
            stateMachineArn=STATE_MACHINE_ARN,
            input=json.dumps({"jobId": job_id})
        )

    return {"status": "done"}