from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.db.models.lesson import Course, Lesson
from app.db.schemas.lesson import LessonCreate, LessonResponse
from app.services.lesson_service import create_lesson_service, get_lesson_service

router = APIRouter()


@router.get("/", response_model=List[LessonResponse])
async def get_lesson(db: Session = Depends(get_db)):
    return await get_lesson_service(db)

@router.post("/", response_model=LessonResponse)
async def create_lesson(lesson_data: LessonCreate, db: Session = Depends(get_db)):
    return await create_lesson_service(lesson_data, db)
