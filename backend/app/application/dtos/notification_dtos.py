from dataclasses import dataclass
from typing import Optional
from uuid import UUID
from datetime import datetime


@dataclass
class NotificationResponseDTO:
    id: UUID
    user_id: UUID
    type: str
    title: str
    message: str
    is_read: bool
    link: Optional[str] = None
    created_at: Optional[datetime] = None
