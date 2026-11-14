from dataclasses import dataclass
from typing import Optional
from uuid import UUID
from datetime import datetime


@dataclass
class CreateAssignmentDTO:
    title: str
    description: str
    total_points: int
    due_date: datetime
    status: str = "draft"  # draft | published


@dataclass
class UpdateAssignmentDTO:
    title: Optional[str] = None
    description: Optional[str] = None
    total_points: Optional[int] = None
    due_date: Optional[datetime] = None
    status: Optional[str] = None


@dataclass
class AssignmentResponseDTO:
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
