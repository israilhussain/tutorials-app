from fastapi import FastAPI, UploadFile, Depends, HTTPException, BackgroundTasks, Query, Header
from sqlalchemy.orm import Session

from app.listbuckets import get_videos_from_s3
from .database import Base, SessionLocal, engine
from .models import Video
from .schemas import VideoListResponse, VideoResponse
import boto3 # type: ignore
import json
import os
import uuid
import re
import subprocess

from fastapi.responses import Response
from fastapi.requests import Request

from dotenv import load_dotenv # type: ignore

# Load environment variables from .env file
load_dotenv()

# Now, you can access the environment variables like this
# AWS Configuration

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
SQS_QUEUE_URL = os.getenv("SQS_QUEUE_URL")
SNS_TOPIC_ARN = os.getenv("SNS_TOPIC_ARN")

Base.metadata.create_all(bind=engine)

app = FastAPI()



# Initialize AWS clients
# Use the credentials from environment variables
s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

# Example: List S3 Buckets
# response = s3_client.list_buckets()
# print(response)

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


# Dependency to get the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@app.post("/videos/")
async def upload_video(
    title: str,
    file: UploadFile,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    # Generate a unique filename
    sanitized_filename = re.sub(r"[^\w\-.]", "_", file.filename)  # Sanitize filename
    unique_filename = f"{uuid.uuid4()}-{sanitized_filename}"

    # Create a temporary file path
    temp_file_path = f"{unique_filename}"

    # Save the uploaded file temporarily
    try:
        with open(temp_file_path, "wb") as temp_file:
            content = await file.read()
            temp_file.write(content)
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
        # encoded_files = encode_video(temp_file_path)

        # # Step 2: Upload encoded videos to S3 and collect URLs
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



def encode_video(video_path):
    """
    Encode the video into multiple resolutions using FFmpeg.
    """
    resolutions = ["1080p", "720p", "480p", "240p"]
    encoded_files = []

    for resolution in resolutions:
        output_file = f"{video_path.split('.')[0]}_{resolution}.mp4"
        ffmpeg_command = [
            "ffmpeg", "-i", video_path,
            "-vf", f"scale=-2:{resolution.split('p')[0]}",
            output_file
        ]
        subprocess.run(ffmpeg_command, check=True)
        encoded_files.append(output_file)
        print(f"Encoded video at {resolution}: {output_file}")

    return encoded_files



# Endpoint to list all videos
@app.get("/videos/", response_model=VideoListResponse)
async def list_videos():
    videos = get_videos_from_s3()
    return {"videos": videos}






# ########################## STUDY MATERIALS ####################


@app.get("/headers-test")
async def headers_test():
    return {"message": "HTTP Headers are being tested"}


@app.post("/custom-text/")
async def custom_text_response():
    return Response(
        content="Custom text with additional headers",
        media_type="text/plain",
        headers={"X-Custom-Header": "CustomValue"}
    )


# Middleware to allow only GET requests
# @app.middleware("http")
# async def allow_only_get(request: Request, call_next):
#     if request.method != "GET":
#         raise HTTPException(
#             status_code=405, detail="This application only supports GET requests"
#         )
#     return await call_next(request)
import time
# Example endpoints
@app.get("/example1")
def example1():
    print("Before the sleep statement")
    time.sleep(5)
    print("After the sleep statement")
    return {"message": "This is a GET endpoint"}

@app.post("/example2")
async def example2():
    return {"message": "Another GET endpoint"}




# Dependency function to extract and validate parameters
def extract_params(
    param1: str = Query(..., description="Required string parameter"),
    param2: int = Query(42, description="Optional integer parameter with a default value"),
):
    return {"param1": param1, "param2": param2}

# Endpoint using the dependency
@app.get("/items/")
async def get_items(params: dict = Depends(extract_params)):
    return {"extracted_params": params}



def first_dependency(param: int = Query(...)):
    return param * 2

def second_dependency(first_result: int = Depends(first_dependency)):
    return first_result + 10

@app.get("/chained/")
async def chained(dep_result: int = Depends(second_dependency)):
    return {"result": dep_result}


# Dependency to extract and validate headers
def extract_headers(custom_header: str = Header(...)):
    return {"custom_header": custom_header}

# Endpoint using the dependency
@app.get("/headers/")
async def read_headers(headers: dict = Depends(extract_headers)):
    return {"extracted_headers": headers}



# Class to handle parameter extraction
class Extractor:
    def __init__(self, default_value: int):
        self.default_value = default_value

    def __call__(self, param: int = Query(None)):
        return {"param": param or self.default_value}

extractor_instance = Extractor(default_value=100)

@app.get("/class-dependency/")
async def class_dep(params: dict = Depends(extractor_instance)):
    
    return {"params": params}


# 2. Set Secure HTTP Response Headers
# Secure headers help prevent XSS and other attacks by controlling how the browser processes content.

# Key Headers to Prevent XSS:
# Content-Security-Policy (CSP):

# Restricts the sources from which scripts, styles, and other content can be loaded.
# Example CSP: script-src 'self' ensures that only scripts from your domain are allowed.
# X-Content-Type-Options:

# Prevents MIME type sniffing, ensuring that the browser respects the Content-Type.
# Set to nosniff.
# X-XSS-Protection:

# Enables browser-based XSS filters (may be redundant with modern browsers).
# Set to 1; mode=block.
# Referrer-Policy:

# Controls how much referrer information is sent with requests.
# Example: strict-origin-when-cross-origin.
# Setting Secure Headers in FastAPI

from starlette.middleware.base import BaseHTTPMiddleware


class SecureHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = "script-src 'self'"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

# app.add_middleware(SecureHeadersMiddleware)

@app.get("/")
async def read_root():
    return {"message": "Secure headers are set"}



# 1. Validate and Sanitize Headers
# Always validate the headers received from clients to ensure they contain only expected data.
# Avoid directly using header values in dynamic content (e.g., HTML pages) without proper sanitization.
# Example: Validating a Header in FastAPI

@app.get("/")
async def read_headers(custom_header: str = Header(...)):
    if not custom_header.isalnum(): #is alpha numeric
        raise HTTPException(status_code=400, detail="Invalid header value")
    return {"header": custom_header}



# 4. Use Input Sanitization Libraries
# Use libraries like bleach for sanitizing inputs when dealing with potentially malicious data.
# Example: Using bleach for Sanitization

import bleach # type: ignore


@app.get("/")
async def sanitize_header(custom_header: str = Header(...)):
    safe_value = bleach.clean(custom_header)  # Strips unsafe tags
    return {"sanitized_header": safe_value}