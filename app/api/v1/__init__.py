from fastapi import APIRouter
from app.api.v1.endpoints import videos, course, lesson, resource

api_router = APIRouter()

api_router.include_router(videos.router, prefix="/videos")
api_router.include_router(course.router, prefix="/courses")
api_router.include_router(lesson.router, prefix="/lessons")
api_router.include_router(resource.router, prefix="/lesson-resources")