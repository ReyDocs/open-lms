from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class CalendarEvent:
    id: UUID
    course_id: UUID
    created_by: UUID
    title: str
    event_datetime: datetime
    source: str  # auto | manual
    description: Optional[str] = None
    assignment_id: Optional[UUID] = None
    created_at: Optional[datetime] = None
