from dataclasses import dataclass
from typing import Optional, List
from uuid import UUID
from datetime import datetime


@dataclass
class UserResponseDTO:
    id: UUID
    email: str
    full_name: str
    role: str
    avatar_url: Optional[str] = None
    student_id: Optional[str] = None
    created_at: Optional[datetime] = None


@dataclass
class CreateUserDTO:
    email: str
    full_name: str
    role: str = "student"
    student_id: Optional[str] = None
    avatar_url: Optional[str] = None
    google_id: Optional[str] = None


@dataclass
class UpdateUserDTO:
    full_name: Optional[str] = None
    role: Optional[str] = None
    student_id: Optional[str] = None
    avatar_url: Optional[str] = None


@dataclass
class BulkImportResultDTO:
    imported_count: int
    errors: List[str]
