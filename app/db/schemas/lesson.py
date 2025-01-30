from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

class LessonCreate(BaseModel):
    title: str
    course_id: int


class LessonUpdate(BaseModel):
    title: Optional[str] = None


class LessonResponse(BaseModel):
    id: int
    title: str
    course_id: int
    resources: List['LessonResourceResponse'] = [] # type: ignore

    class Config:
        orm_mode = True


# Models for LessonResource

class ResourceType(str, Enum):
    video = "video"
    pdf = "pdf"
    text = "text"

class LessonResourceCreate(BaseModel):
    lesson_id: int
    resource_type: ResourceType
    url: Optional[str] = None  # For video or PDF
    content: Optional[str] = None  # For text content


class LessonResourceUpdate(BaseModel):
    resource_type: Optional[ResourceType] = None
    url: Optional[str] = None
    content: Optional[str] = None


class LessonResourceResponse(BaseModel):
    id: int
    lesson_id: int
    resource_type: ResourceType
    url: Optional[str] = None
    content: Optional[str] = None

    class Config:
        orm_mode = True


class PresignedUrlRequest(BaseModel):
    file_name: str
    lesson_id: str