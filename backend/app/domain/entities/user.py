from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class User:
    id: UUID
    email: str
    full_name: str
    role: str  # admin | teacher | student
    avatar_url: Optional[str] = None
    student_id: Optional[str] = None
    google_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def is_admin(self) -> bool:
        return self.role == "admin"

    def is_teacher(self) -> bool:
        return self.role in ("teacher", "admin")

    def is_student(self) -> bool:
        return self.role == "student"
