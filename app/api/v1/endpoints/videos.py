from fastapi import APIRouter, UploadFile, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.services.video_service import upload_video_service
from app.db.base import get_db

router = APIRouter()

@router.get("/")
async def get_videos():
    return {"videos": []}

@router.post("/")
async def upload_video(
    title: str,
    file: UploadFile,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    return await upload_video_service(title, file, background_tasks, db)