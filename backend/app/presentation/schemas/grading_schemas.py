from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


class GradeSubmissionRequest(BaseModel):
    grade: int = Field(..., ge=0)
    feedback: Optional[str] = None


class StudentGradeResponse(BaseModel):
    assignment_id: UUID
    assignment_title: str
    total_points: int
    points_earned: Optional[int]
    percentage: Optional[float]
    feedback: Optional[str]
    submitted_at: Optional[datetime]
    graded_at: Optional[datetime]


class GradebookRow(BaseModel):
    student_id: UUID
    student_name: str
    student_email: str
    grades: Dict[str, Optional[int]]
    total_earned: int
    total_possible: int
    overall_percentage: float


class GradebookResponse(BaseModel):
    course_id: UUID
    assignments: List[Dict[str, Any]]
    students: List[GradebookRow]
