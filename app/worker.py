import boto3
import json
import time
import os
import json
import subprocess

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# AWS Configuration

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
SQS_QUEUE_URL = os.getenv("SQS_QUEUE_URL")

# Initialize AWS clients
sqs_client = boto3.client(
    "sqs", 
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)


def encode_video(video_path):
    """
    Encode the video into multiple resolutions using FFmpeg or AWS tools.
    """
    resolutions = ["1080p", "720p", "480p", "240p"]
    for resolution in resolutions:
        # Example command for FFmpeg
        output_file = f"{video_path.split('.')[0]}_{resolution}.mp4"
        ffmpeg_command = [
            "ffmpeg", "-i", video_path,
            "-vf", f"scale=-2:{resolution.split('p')[0]}",
            output_file
        ]
        subprocess.run(ffmpeg_command)
        print(f"Encoded video at {resolution}: {output_file}")

def notify_students(video_id):
    """
    Notify students that the video is ready.
    """
    print(f"Video {video_id} has been processed and is now available!")
    # Add notification logic here (e.g., email, SNS, database update)


def process_video(s3_url, video_id):
    """
    Placeholder for video processing logic.
    """
    print(f"Processing video {video_id} from {s3_url}")
    # Example: Transcode video into multiple resolutions (e.g., 1080p, 720p, 480p)
    # encode_video(s3_url)
    time.sleep(5)  # Simulate processing time
    print(f"Video {video_id} processing completed!")




def process_message(message_body):
    """
    Logic to process the message body.
    """
    print(f"Processing message: {message_body}")

    # Parse message to get video details (e.g., S3 bucket, file path)
    video_details = json.loads(message_body)
    video_path = video_details["file_path"]

    # Video encoding logic (using FFmpeg, AWS Elastic Transcoder, etc.)
    encode_video(video_path)

    # After processing, store the encoded files and notify students
    notify_students(video_details["video_id"])



def poll_sqs():
    while True:
        try:
            response = sqs_client.receive_message(
                QueueUrl=SQS_QUEUE_URL,
                MaxNumberOfMessages=10,  # Batch size
                WaitTimeSeconds=10       # Long polling
            )
            messages = response.get("Messages", [])
            for message in messages:
                # Parse the message
                body = json.loads(message["Body"])
                video_id = body["video_id"]
                s3_url = body["s3_url"]

                # Process the video
                process_video(s3_url, video_id)

                # Delete the message after processing
                sqs_client.delete_message(
                    QueueUrl=SQS_QUEUE_URL,
                    ReceiptHandle=message["ReceiptHandle"]
                )
        except Exception as e:
            print(f"Error processing message: {e}")
        time.sleep(2)  # Avoid overloading the SQS queue

if __name__ == "__main__":
    print("Worker started. Polling SQS...")
    poll_sqs()
