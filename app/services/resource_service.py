import uuid
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.db.models.lesson import Lesson, LessonResource
from app.db.schemas.lesson import LessonResourceCreate
import time
import boto3 # type: ignore
import os
from dotenv import load_dotenv

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
SQS_QUEUE_URL = os.getenv("SQS_QUEUE_URL")
SNS_TOPIC_ARN = os.getenv("SNS_TOPIC_ARN")

s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

async def create_lesson_resource_service(resource_data: LessonResourceCreate, db: Session):
    lesson = db.query(Lesson).filter(Lesson.id == resource_data.lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    resource = LessonResource(**resource_data.dict())
    db.add(resource)
    db.commit()
    db.refresh(resource)
    return resource


# async def generate_presigned_url_service(file_name: str, lesson_id: str):
#     try:
#         # Generate a unique file key
#         file_key = f"lessons/{lesson_id}/{uuid.uuid4()}_{file_name}"
        
#         # Generate pre-signed URL
#         presigned_url = s3_client.generate_presigned_url(
#             "put_object",
#             Params={"Bucket": S3_BUCKET_NAME, "Key": file_key},
#             ExpiresIn=3600,  # 1 hour expiration
#         )
        
#         return {"presigned_url": presigned_url, "file_key": file_key}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
    



def generate_presigned_url_service(bucket_name: str, object_key: str, expiration: int = 3600):
    return s3_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": bucket_name, "Key": object_key, "ResponseContentType": "video/mp4"  # Forces correct Content-Type
        },
        ExpiresIn=expiration
    )