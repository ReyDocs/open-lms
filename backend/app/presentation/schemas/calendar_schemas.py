from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


class CalendarEventResponse(BaseModel):
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

    class Config:
        from_attributes = True


class CreateCalendarEventRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    event_datetime: datetime
    description: Optional[str] = None


class UpdateCalendarEventRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    event_datetime: Optional[datetime] = None
    description: Optional[str] = None
