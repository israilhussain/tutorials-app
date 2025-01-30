import asyncio
import json
import time
import boto3 # type: ignore
import os
from dotenv import load_dotenv

from app.api.v1.endpoints.resource import update_lesson_with_resource # type: ignore

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
SQS_QUEUE_URL = os.getenv("SQS_QUEUE_URL")
SNS_TOPIC_ARN = os.getenv("SNS_TOPIC_ARN")

sqs_client = boto3.client(
        "sqs",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )


def consume_sqs_messages():
    while True:
        try:
            # Receive messages from SQS
            response = sqs_client.receive_message(
                QueueUrl=SQS_QUEUE_URL,
                MaxNumberOfMessages=10,  # Batch size
                WaitTimeSeconds=10,
            )
            
            messages = response.get("Messages", [])
            print("consume_sqs_messages: ", messages)
            for message in messages:
                # Parse message body
                body = json.loads(message["Body"])
                video_id = body["video_id"]
                s3_url = body["s3_url"]
                print("s3_url", s3_url, video_id)
                # body = message["Body"]
                # event = eval(body)  # Example only, use safer methods like JSON.parse
                # print("consume_sqs_messages: ", body.get("s3_url"))
                # Extract video details
                # file_key = event["Records"][0]["s3"]["object"]["key"]
                # lesson_id = file_key.split("/")[1]
                # video_url = f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{file_key}"
                
                # # Update lesson in "database"
                asyncio.run(update_lesson_with_resource(1, s3_url))
                print("update_lesson_with_resource::::")
                # Delete message from SQS
                sqs_client.delete_message(
                    QueueUrl=SQS_QUEUE_URL,
                    ReceiptHandle=message["ReceiptHandle"],
                )
        except Exception as e:
            print(f"Error processing SQS message: {e}")
        
        time.sleep(5)