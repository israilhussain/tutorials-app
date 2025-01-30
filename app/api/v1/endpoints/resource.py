import asyncio
from typing import Dict, List
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.db.base import get_db, SessionLocal
from app.db.models.lesson import Lesson, LessonResource
from app.db.schemas.lesson import LessonResourceCreate, LessonResourceResponse, PresignedUrlRequest
from app.services.resource_service import create_lesson_resource_service, generate_presigned_url_service

router = APIRouter()

# In-memory notification storage for simplicity
notifications: Dict[str, List[Dict]] = {}
user_id = "12345"

@router.post("/", response_model=LessonResourceResponse)
async def create_lesson_resource(resource_data: LessonResourceCreate, db: Session = Depends(get_db)):
    return await create_lesson_resource_service(resource_data, db)


# @router.post("/generate-presigned-url/")
# async def generate_presigned_url(payload: PresignedUrlRequest):
#     return await generate_presigned_url_service(payload.file_name, payload.lesson_id)

@router.get("/get-video-url")
def get_video_url():
    url = generate_presigned_url_service("fastapi-tutorials", "41bd42c2-b4d6-405c-9037-665a4a23f8e2-videoplayback.mp4")
    return {"url": url}


@router.get("/stream-video")
def stream_video():
    presigned_url = generate_presigned_url_service("fastapi-tutorials", "41bd42c2-b4d6-405c-9037-665a4a23f8e2-videoplayback.mp4")
    return RedirectResponse(url=presigned_url)




# Update the function to manage the database session manually
async def update_lesson_with_resource(lesson_id: int, video_url: str):
    print("update_lesson_with_resource called: ", lesson_id, video_url)
    
    # Manually create a database session
    db: Session = SessionLocal()
    try:
        lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
        print("LESSON:  ", lesson.id)
        # Prepare the resource data
        resource_data: LessonResourceCreate = {
            "lesson_id": 1,
            "resource_type": "video",
            "url": video_url,
            "content": ""
        }

        # Call the service to create the lesson resource
        resource_response = LessonResource(**resource_data)
        db.add(resource_response)
        db.commit()
        db.refresh(resource_response)
        # return resource
        print("resource_response: ", resource_response.lesson_id, resource_response.url)
        # Add a notification for the user
        if user_id not in notifications:
            notifications[user_id] = []

        notifications[user_id].append({
            "lesson_id": 1,
            "resource_url": resource_response.url,
            "status": "uploaded"
        })
        return resource_response
    finally:
        # Ensure the database session is properly closed
        db.close()






# SSE endpoint
@router.get("/sse/{user_id}")
async def sse(user_id: str):
    async def event_stream():
        while True:
            if user_id in notifications and notifications[user_id]:
                # Send all pending notifications for the user
                while notifications[user_id]:
                    data = notifications[user_id].pop(0)
                    yield f"data: {data}\n\n"
            await asyncio.sleep(1)  # Avoid busy looping

    return StreamingResponse(event_stream(), media_type="text/event-stream")
