from sqlalchemy import Column, Integer, String
from .database import Base



class Video(Base):
    __tablename__ = "videos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    s3_url = Column(String)