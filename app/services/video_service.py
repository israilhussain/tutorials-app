import re
import subprocess
import uuid
from fastapi import UploadFile, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.utils.file_utils import save_file
from app.db.models.video import Video
# from app.tasks import process_file_in_background  # Background task logic
import boto3
import os
import json
from dotenv import load_dotenv # type: ignore
# Load environment variables from .env file
load_dotenv()

# AWS Configuration
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
SQS_QUEUE_URL = os.getenv("SQS_QUEUE_URL")
SNS_TOPIC_ARN = os.getenv("SNS_TOPIC_ARN")

s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

# Example: List S3 Buckets
# response = s3_client.list_buckets()

sqs_client = boto3.client(
    "sqs", 
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

sns_client = boto3.client(
    'sns', 
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

async def upload_video_service(
    title: str, 
    file: UploadFile, 
    background_tasks: BackgroundTasks, 
    db: Session
):
    # Sanitize and generate a unique filename
    sanitized_filename = re.sub(r"[^\w\-.]", "_", file.filename)
    unique_filename = f"{uuid.uuid4()}-{sanitized_filename}"

    # Save the uploaded file temporarily
    temp_file_path = f"{unique_filename}"
    try:
        await save_file(temp_file_path, file)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving temporary file: {str(e)}")

    # Process the file in the background
    background_tasks.add_task(
        process_file_in_background, temp_file_path, unique_filename, title, db
    )

    return {"message": "Your file is being processed. You will be notified when it's complete."}



def process_file_in_background(temp_file_path, unique_filename, title, db:Session):
    try:
        # Debug: Log the temp file path
        print(f"Processing file at: {temp_file_path}")

        # # Step 1: Encode video
        # encoded_files = encode_video_with_ffmpeg(temp_file_path)

        # Step 2: Upload encoded videos to S3 and collect URLs
        # s3_urls = {}
        # for file in encoded_files:
        #     s3_key = os.path.basename(file)
        #     with open(file, "rb") as f:
        #         s3_client.upload_fileobj(f, S3_BUCKET_NAME, s3_key)
        #     s3_url = f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"
        #     resolution = s3_key.split('_')[-1].replace('.mp4', '')
        #     s3_urls[resolution] = s3_url
        #     print(f"Uploaded {file} to S3: {s3_url}")


        # Upload the file to S3
        with open(temp_file_path, "rb") as f:
            s3_client.upload_fileobj(f, S3_BUCKET_NAME, unique_filename)

        # Generate the S3 URL
        s3_url = f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{unique_filename}"

        # Save metadata to the database
        # new_video = Video(title=title, s3_url=s3_urls["1080p"])  # Default to highest resolution for display
        new_video = Video(title=title, s3_url=s3_url)
        db.add(new_video)
        db.commit()
        db.refresh(new_video)

        # Push task to SQS queue
        task = {
            "video_id": new_video.id,
            "s3_url": new_video.s3_url
        }
        sqs_client.send_message(
            QueueUrl=SQS_QUEUE_URL,
            MessageBody=json.dumps(task)
        )

        # Notify user via SNS
        sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=json.dumps({
                "default": f"Your video '{title}' has been successfully uploaded and is now being processed.",
                "s3_url": s3_url
            }),
            Subject="Video Upload Completed",
            MessageStructure="json"
        )

        print(f"File processing complete: {new_video.id}")
    except Exception as e:
        print(f"Error in processing file: {e}")
    finally:
        # Safely remove the temporary file
        try:
            os.remove(temp_file_path)
        except Exception as e:
            print(f"Error removing temp file: {e}")


        

# def encode_video(video_path):
#     """
#     Encode the video into multiple resolutions using FFmpeg.
#     """
#     resolutions = ["1080p", "720p", "480p", "240p"]
#     encoded_files = []

#     for resolution in resolutions:
#         output_file = f"{video_path.split('.')[0]}_{resolution}.mp4"
#         ffmpeg_command = [
#             "ffmpeg", "-i", video_path,
#             "-vf", f"scale=-2:{resolution.split('p')[0]}",
#             output_file
#         ]
#         subprocess.run(ffmpeg_command, check=True)
#         encoded_files.append(output_file)
#         print(f"Encoded video at {resolution}: {output_file}")

#     return encoded_files


# def encode_video_in_docker(video_path):
#     """
#     Encode the video into multiple resolutions using FFmpeg inside a Docker container.
#     """
#     resolutions = ["1080p", "720p", "480p", "240p"]
#     encoded_files = []

#     for resolution in resolutions:
#         output_file = f"{video_path.split('.')[0]}_{resolution}.mp4"
#         ffmpeg_command = [
#             "docker", "run", "--rm",
#             "-v", f"{video_path.rsplit('/', 1)[0]}:/videos",  # Mount video directory
#             "jrottenberg/ffmpeg", 
#             "-i", f"/videos/{video_path.rsplit('/', 1)[1]}",  # Input file in container
#             "-vf", f"scale=-2:{resolution.split('p')[0]}",
#             f"/videos/{output_file}"  # Output file in container
#         ]
#         subprocess.run(ffmpeg_command, check=True)
#         encoded_files.append(output_file)
#         print(f"Encoded video at {resolution}: {output_file}")

#     return encoded_files



# def encode_video_in_docker(video_path):
#     resolutions = ["1080p", "720p", "480p", "240p"]
#     encoded_files = []

#     # Use os.path.splitext to safely extract the filename without extension
#     base_name, _ = os.path.splitext(video_path)

#     for resolution in resolutions:
#         output_file = f"{base_name}_{resolution}.mp4"
#         ffmpeg_command = [
#             "jrottenberg/ffmpeg", "-i", video_path,
#             "-vf", f"scale=-2:{resolution.split('p')[0]}",
#             output_file
#         ]
#         subprocess.run(ffmpeg_command, check=True)
#         encoded_files.append(output_file)
#         print(f"Encoded video at {resolution}: {output_file}")

#     return encoded_files

import os
import subprocess

def encode_video_with_ffmpeg(video_path):
    resolutions = ["720", "480"]  # Resolutions as integers (no 'p')
    encoded_files = []

    # Extract the base name and directory of the video file
    base_name, ext = os.path.splitext(video_path)
    # video_dir = os.path.dirname(video_path)

    for resolution in resolutions:
        output_file = f"{base_name}_{resolution}p.mp4"  # Add resolution as a suffix
        ffmpeg_command = [
            "ffmpeg", "-i", video_path, 
            "-vf", f"scale=-2:{resolution}", 
            "-c:v", "libx264", "-crf", "23", "-preset", "fast", 
            output_file
        ]
        
        try:
            print(f"Encoding video to {resolution}p...")
            subprocess.run(ffmpeg_command, check=True)
            encoded_files.append(output_file)
            print(f"Encoded video at {resolution}p: {output_file}")
        except subprocess.CalledProcessError as e:
            print(f"Error encoding {resolution}p: {e}")
    
    return encoded_files
