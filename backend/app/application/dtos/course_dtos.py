from dataclasses import dataclass
from typing import Optional
from uuid import UUID
from datetime import datetime


@dataclass
class CreateCourseDTO:
    title: str
    code: str
    description: str
    semester: str
    cover_image_url: Optional[str] = None


@dataclass
class UpdateCourseDTO:
    title: Optional[str] = None
    description: Optional[str] = None
    semester: Optional[str] = None
    cover_image_url: Optional[str] = None


@dataclass
class CourseResponseDTO:
    id: UUID
    title: str
    code: str
    description: str
    semester: str
    teacher_id: UUID
    cover_image_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
