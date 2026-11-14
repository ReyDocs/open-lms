from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    role: str
    avatar_url: Optional[str] = None
    student_id: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CreateUserRequest(BaseModel):
    email: EmailStr
    full_name: str
    role: str = "student"
    student_id: Optional[str] = None
    avatar_url: Optional[str] = None


class UpdateUserRequest(BaseModel):
    full_name: Optional[str] = None
    role: Optional[str] = None
    student_id: Optional[str] = None
    avatar_url: Optional[str] = None


class BulkImportResponse(BaseModel):
    imported_count: int
    errors: List[str]
