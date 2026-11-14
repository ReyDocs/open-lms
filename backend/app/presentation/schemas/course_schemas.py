from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


class CourseResponse(BaseModel):
    id: UUID
    title: str
    code: str
    description: str
    semester: str
    teacher_id: UUID
    cover_image_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CreateCourseRequest(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    code: str = Field(..., min_length=2, max_length=50)
    description: str = Field(..., min_length=5)
    semester: str = Field(..., min_length=2, max_length=100)
    cover_image_url: Optional[str] = None


class UpdateCourseRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = Field(None, min_length=5)
    semester: Optional[str] = Field(None, min_length=2, max_length=100)
    cover_image_url: Optional[str] = None


class EnrollStudentRequest(BaseModel):
    student_ids: List[UUID]


class InviteStudentRequest(BaseModel):
    email: str
