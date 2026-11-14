from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from app.domain.entities.calendar_event import CalendarEvent


class ICalendarEventRepository(ABC):
    @abstractmethod
    async def get_by_id(self, event_id: UUID) -> Optional[CalendarEvent]:
        pass

    @abstractmethod
    async def create(self, event: CalendarEvent) -> CalendarEvent:
        pass

    @abstractmethod
    async def update(self, event: CalendarEvent) -> CalendarEvent:
        pass

    @abstractmethod
    async def delete(self, event_id: UUID) -> bool:
        pass

    @abstractmethod
    async def list_by_course(self, course_id: UUID) -> List[CalendarEvent]:
        pass

    @abstractmethod
    async def list_by_user(self, user_id: UUID, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[CalendarEvent]:
        pass

    @abstractmethod
    async def delete_by_assignment(self, assignment_id: UUID) -> bool:
        pass
