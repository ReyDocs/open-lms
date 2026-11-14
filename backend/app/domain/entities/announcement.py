from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from uuid import UUID


@dataclass
class AnnouncementAttachment:
    id: UUID
    announcement_id: UUID
    file_url: str
    file_name: str
    file_size: int


@dataclass
class Announcement:
    id: UUID
    course_id: UUID
    author_id: UUID
    title: str
    content: str  # rich text HTML
    created_at: Optional[datetime] = None
    attachments: List[AnnouncementAttachment] = field(default_factory=list)
