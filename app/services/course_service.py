


from app.db.models.lesson import Course
from app.db.schemas.course import CourseCreate
from sqlalchemy.orm import Session


async def get_courses_service(db: Session):
    courses = db.query(Course).all()
    return courses

async def create_course_service(course_data: CourseCreate, db: Session):
    course = Course(**course_data.dict())
    db.add(course)
    db.commit()
    db.refresh(course)
    return course