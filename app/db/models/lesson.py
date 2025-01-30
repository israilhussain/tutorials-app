from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from app.db.base import Base


class Course(Base):
    __tablename__ = 'courses'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Boolean, default=False)  # True for published, False for draft
    
    # Relationship with Lesson
    lessons = relationship("Lesson", back_populates="course", cascade="all, delete")
    

class Lesson(Base):
    __tablename__ = 'lessons'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    course_id = Column(Integer, ForeignKey('courses.id', ondelete="CASCADE"), nullable=False)

    # Relationship with Course
    course = relationship("Course", back_populates="lessons")
    resources = relationship("LessonResource", back_populates="lesson", cascade="all, delete-orphan")


class LessonResource(Base):
    __tablename__ = 'lesson_resources'
    id = Column(Integer, primary_key=True, autoincrement=True)
    lesson_id = Column(Integer, ForeignKey('lessons.id', ondelete="CASCADE"), nullable=False)
    resource_type = Column(Enum("video", "pdf", "text", name="resource_type"), nullable=False)
    url = Column(String(1024), nullable=True)  # URL for videos or PDFs
    content = Column(Text, nullable=True)  # For text-based content
    lesson = relationship("Lesson", back_populates="resources")
