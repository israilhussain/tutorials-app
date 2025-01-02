import os
from fastapi import FastAPI, HTTPException
import boto3

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_region = os.getenv("AWS_REGION")

# AWS S3 setup
AWS_REGION = aws_region
S3_BUCKET_NAME = "fastapi-tutorials"

s3_client = boto3.client('s3', 
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=aws_region
)

app = FastAPI()

# Function to list all videos from S3 bucket
def get_videos_from_s3():
    try:
        # List objects in the S3 bucket
        response = s3_client.list_objects_v2(Bucket=S3_BUCKET_NAME)
        
        if "Contents" not in response:
            return []

        video_files = []
        for obj in response["Contents"]:
            # Assuming your videos are mp4 files, you can filter based on file extension
            if obj["Key"].endswith(".mp4"):
                s3_url = f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{obj['Key']}"
                video_files.append({
                    "title": obj["Key"].split('/')[-1],  # Extract filename from the S3 object key
                    "s3_url": s3_url
                })
        return video_files
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching videos from S3: {e}")

# FastAPI endpoint to fetch all video URLs from S3
# @app.get("/videos/", response_model=List[Video])
# async def list_videos():
#     videos = get_videos_from_s3()
#     return videos
