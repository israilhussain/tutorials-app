from pydantic import BaseModel
from typing import List

class VideoCreate(BaseModel):
    title: str

class VideoResponse(BaseModel):
    id: int
    title: str
    s3_url: str

    class Config:
        orm_mode = True


# Pydantic model for video response
class Video(BaseModel):
    title: str
    s3_url: str



# Response model for the list of videos
class VideoListResponse(BaseModel):
    videos: List[Video]