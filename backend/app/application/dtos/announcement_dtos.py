from dataclasses import dataclass
from typing import Optional, List
from uuid import UUID
from datetime import datetime


@dataclass
class AttachmentInputDTO:
    file_url: str
    file_name: str
    file_size: int


@dataclass
class AttachmentResponseDTO:
    id: UUID
    announcement_id: UUID
    file_url: str
    file_name: str
    file_size: int


@dataclass
class CreateAnnouncementDTO:
    title: str
    content: str
    attachments: Optional[List[AttachmentInputDTO]] = None


@dataclass
class UpdateAnnouncementDTO:
    title: Optional[str] = None
    content: Optional[str] = None


@dataclass
class AnnouncementResponseDTO:
    id: UUID
    course_id: UUID
    author_id: UUID
    title: str
    content: str
    created_at: Optional[datetime] = None
    author_name: Optional[str] = None
    attachments: Optional[List[AttachmentResponseDTO]] = None
