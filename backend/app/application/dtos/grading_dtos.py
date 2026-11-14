from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime


@dataclass
class GradeSubmissionDTO:
    submission_id: UUID
    grade: int
    feedback: Optional[str] = None


@dataclass
class StudentGradeDTO:
    assignment_id: UUID
    assignment_title: str
    total_points: int
    points_earned: Optional[int]
    percentage: Optional[float]
    feedback: Optional[str]
    submitted_at: Optional[datetime]
    graded_at: Optional[datetime]


@dataclass
class GradebookRowDTO:
    student_id: UUID
    student_name: str
    student_email: str
    grades: Dict[str, Optional[int]]  # assignment_id -> points_earned
    total_earned: int
    total_possible: int
    overall_percentage: float


@dataclass
class GradebookResponseDTO:
    course_id: UUID
    assignments: List[Dict[str, Any]]  # id, title, total_points
    students: List[GradebookRowDTO]
