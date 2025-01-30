from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.models.lesson import Lesson
from app.db.schemas.course import CourseCreate, CourseResponse
from app.services.course_service import create_course_service, get_courses_service
from app.db.base import get_db


router = APIRouter()

# @router.get("/", response_model=List[CourseResponse])
# async def get_courses(db: Session = Depends(get_db)):
#     return await get_courses_service(db)

@router.get("/")
async def get_courses(db: Session = Depends(get_db)):
    courses = await get_courses_service(db)
    results = []
    for course in courses:
        lessons = db.query(Lesson).filter(Lesson.course_id == course.id).all()

        results.append({
            "id": course.id,
            "title": course.title,
            "lessons": [{"id": lesson.id, "title": lesson.title} for lesson in lessons]
        })

    return results


@router.post("/", response_model=CourseResponse)
async def create_course(course_data: CourseCreate, db: Session = Depends(get_db)):
    return await create_course_service(course_data, db) 
