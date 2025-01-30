from pydantic import BaseModel, Field
from typing import Optional, List
from typing import Annotated

from app.db.schemas.lesson import LessonResponse

class CourseCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[bool] = False  # False = draft, True = published


class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[bool] = None



class CourseResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: bool
    lessons: Annotated[list[LessonResponse], Field(...)]

    # Ensure the model is fully defined
    model_config = {
        "from_attributes": True  # Replace `orm_mode` with `from_attributes`
    }

# # Call rebuild explicitly
# CourseResponse.model_rebuild()

# # Example usage with Annotated
# CourseAnnotated = Annotated[CourseResponse, Field(description="Course Response")]
