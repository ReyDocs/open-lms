from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


class AssignmentResponse(BaseModel):
    id: UUID
    title: str
    description: str
    total_points: int
    status: str
    due_date: datetime
    module_id: UUID
    course_id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CreateAssignmentRequest(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    description: str = Field(..., min_length=1)
    total_points: int = Field(..., gt=0)
    due_date: datetime
    status: str = "draft"  # draft | published


class UpdateAssignmentRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = None
    total_points: Optional[int] = Field(None, gt=0)
    due_date: Optional[datetime] = None
    status: Optional[str] = None
