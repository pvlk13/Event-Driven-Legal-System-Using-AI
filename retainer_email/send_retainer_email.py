import os
import boto3
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
s3 = boto3.client("s3", region_name="us-east-1")
ses = boto3.client("ses", region_name="us-east-1")

TABLE_NAME = os.environ["TABLE_NAME"]
SENDER_EMAIL = os.environ["SENDER_EMAIL"]
OFFICE_CALENDLY_LINK = os.environ["OFFICE_CALENDLY_LINK"]
VIRTUAL_CALENDLY_LINK = os.environ["VIRTUAL_CALENDLY_LINK"]

TEST_RECIPIENT_EMAIL = "praveenavijayalakshmi.k@gmail.com"

table = dynamodb.Table(TABLE_NAME)


def safe_str(value, default="N/A"):
    if value is None or value == "":
        return default
    return str(value)


def get_consultation_details():
    month = datetime.now().month

    if 3 <= month <= 8:
        return {
            "consultation_type": "In-Office Meeting",
            "calendly_link": OFFICE_CALENDLY_LINK
        }
    else:
        return {
            "consultation_type": "Virtual Meeting",
            "calendly_link": VIRTUAL_CALENDLY_LINK
        }


def lambda_handler(event, context):
    job_id = event["jobId"]

    response = table.get_item(Key={"jobId": job_id})
    item = response.get("Item")

    if not item:
        raise Exception(f"No DynamoDB item found for jobId={job_id}")

    client_name = f"{safe_str(item.get('client_first_name'), '')} {safe_str(item.get('client_last_name'), '')}".strip()
    opposing_name = f"{safe_str(item.get('opposing_first_name'), '')} {safe_str(item.get('opposing_last_name'), '')}".strip()

    accident_location = safe_str(item.get("accident_location"))
    summary = safe_str(item.get("summary"))
    police_report_number = safe_str(item.get("police_report_number"))

    original_pdf_key = item.get("original_pdf_key")
    original_pdf_bucket = item.get("original_pdf_bucket")

    if not original_pdf_key or not original_pdf_bucket:
        raise Exception(f"Missing original PDF location for jobId={job_id}")

    consultation = get_consultation_details()
    consultation_type = consultation["consultation_type"]
    calendly_link = consultation["calendly_link"]

    # Download original PDF from S3
    s3_obj = s3.get_object(Bucket=original_pdf_bucket, Key=original_pdf_key)
    pdf_bytes = s3_obj["Body"].read()

    subject = "Next Steps for Your Case"

    body_text = f"""Hello {client_name},

We have reviewed the initial police report for your matter.

Case Details
------------
Client: {client_name}
Location: {accident_location}
Opposing Party: {opposing_name}
Police Report Number: {police_report_number}

Summary
-------
{summary}

Consultation
------------
Based on the season, your consultation type is: {consultation_type}

Please book here:
{calendly_link}

The original police report PDF is attached for your reference.

Regards,
Law Office
"""

    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = TEST_RECIPIENT_EMAIL

    msg.attach(MIMEText(body_text, "plain"))

    attachment = MIMEApplication(pdf_bytes)
    attachment.add_header(
        "Content-Disposition",
        "attachment",
        filename=f"police_report_{job_id}.pdf"
    )
    msg.attach(attachment)

    ses.send_raw_email(
        Source=SENDER_EMAIL,
        Destinations=[TEST_RECIPIENT_EMAIL],
        RawMessage={"Data": msg.as_string()}
    )

    table.update_item(
        Key={"jobId": job_id},
        UpdateExpression="SET retainer_sent = :true, retainer_sent_time = :ts, consultation_type = :ct, test_email_sent_to = :to",
        ExpressionAttributeValues={
            ":true": True,
            ":ts": datetime.utcnow().isoformat(),
            ":ct": consultation_type,
            ":to": TEST_RECIPIENT_EMAIL
        }
    )

    return {
        "jobId": job_id,
        "sent_to": TEST_RECIPIENT_EMAIL,
        "consultation_type": consultation_type,
        "original_pdf_key": original_pdf_key,
        "status": "email_sent"
    }