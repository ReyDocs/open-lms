from dataclasses import dataclass
from typing import Optional
from uuid import UUID
from datetime import datetime


@dataclass
class CreateCalendarEventDTO:
    course_id: UUID
    title: str
    event_datetime: datetime
    description: Optional[str] = None


@dataclass
class UpdateCalendarEventDTO:
    title: Optional[str] = None
    event_datetime: Optional[datetime] = None
    description: Optional[str] = None


@dataclass
class CalendarEventResponseDTO:
    id: UUID
    course_id: UUID
    created_by: UUID
    title: str
    event_datetime: datetime
    source: str
    description: Optional[str] = None
    assignment_id: Optional[UUID] = None
    created_at: Optional[datetime] = None
    course_title: Optional[str] = None
