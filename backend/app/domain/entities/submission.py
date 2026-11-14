from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class Submission:
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

    def is_graded(self) -> bool:
        return self.grade is not None
