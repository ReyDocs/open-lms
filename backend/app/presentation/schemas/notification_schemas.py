from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class NotificationResponse(BaseModel):
    id: UUID
    user_id: UUID
    type: str
    title: str
    message: str
    is_read: bool
    link: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UnreadCountResponse(BaseModel):
    unread_count: int
