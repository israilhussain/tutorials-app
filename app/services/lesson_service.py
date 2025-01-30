

from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.db.models.lesson import Course, Lesson
from app.db.schemas.lesson import LessonCreate


async def get_lesson_service(db: Session):
    lesson = db.query(Lesson).all()
    return lesson

async def create_lesson_service(lesson_data: LessonCreate, db: Session):
    course = db.query(Course).filter(Course.id == lesson_data.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    lesson = Lesson(**lesson_data.dict())
    db.add(lesson)
    db.commit()
    db.refresh(lesson)
    return lesson