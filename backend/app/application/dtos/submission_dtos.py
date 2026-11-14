from dataclasses import dataclass
from typing import Optional
from uuid import UUID
from datetime import datetime


@dataclass
class SubmitAssignmentDTO:
    assignment_id: UUID
    student_id: UUID
    file_url: str
    file_name: str
    file_size: int


@dataclass
class SubmissionResponseDTO:
    id: UUID
    assignment_id: UUID
    student_id: UUID
    file_url: str
    file_name: str
    file_size: int
    submitted_at: datetime
    grade: Optional[int] = None
    feedback: Optional[str] = None
    graded_at: Optional[datetime] = None
    student_name: Optional[str] = None
    student_email: Optional[str] = None
