from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


class AttachmentSchema(BaseModel):
    file_url: str
    file_name: str
    file_size: int


class AttachmentResponse(BaseModel):
    id: UUID
    announcement_id: UUID
    file_url: str
    file_name: str
    file_size: int


class AnnouncementResponse(BaseModel):
    id: UUID
    course_id: UUID
    author_id: UUID
    title: str
    content: str
    created_at: Optional[datetime] = None
    author_name: Optional[str] = None
    attachments: Optional[List[AttachmentResponse]] = []

    class Config:
        from_attributes = True


class CreateAnnouncementRequest(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    content: str = Field(..., min_length=1)
    attachments: Optional[List[AttachmentSchema]] = []


class UpdateAnnouncementRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=255)
    content: Optional[str] = Field(None, min_length=1)
