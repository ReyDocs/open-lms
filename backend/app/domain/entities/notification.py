from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class Notification:
    id: UUID
    user_id: UUID
    type: str  # announcement | assignment | grade | enrollment | reminder
    title: str
    message: str
    is_read: bool = False
    link: Optional[str] = None
    created_at: Optional[datetime] = None
