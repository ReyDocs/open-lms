from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime, timezone

from app.application.interfaces.repositories.i_calendar_event_repository import ICalendarEventRepository
from app.application.interfaces.repositories.i_course_repository import ICourseRepository
from app.application.dtos.calendar_dtos import (
    CreateCalendarEventDTO, UpdateCalendarEventDTO, CalendarEventResponseDTO
)
from app.domain.entities.calendar_event import CalendarEvent
from app.domain.entities.user import User


class CalendarService:
    def __init__(
        self,
        calendar_repo: ICalendarEventRepository,
        course_repo: ICourseRepository,
    ):
        self.calendar_repo = calendar_repo
        self.course_repo = course_repo

    async def get_course_calendar(self, course_id: UUID) -> List[CalendarEventResponseDTO]:
        events = await self.calendar_repo.list_by_course(course_id)
        course = await self.course_repo.get_by_id(course_id)
        course_title = course.title if course else None
        return [self._to_dto(e, course_title) for e in events]

    async def get_aggregated_calendar(
        self, user_id: UUID, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
    ) -> List[CalendarEventResponseDTO]:
        events = await self.calendar_repo.list_by_user(user_id, start_date, end_date)
        dtos: List[CalendarEventResponseDTO] = []
        for e in events:
            course = await self.course_repo.get_by_id(e.course_id)
            course_title = course.title if course else None
            dtos.append(self._to_dto(e, course_title))
        return dtos

    async def create_manual_event(
        self, dto: CreateCalendarEventDTO, teacher: User
    ) -> CalendarEventResponseDTO:
        course = await self.course_repo.get_by_id(dto.course_id)
        if not course:
            raise ValueError("Course not found")
        if not teacher.is_admin() and course.teacher_id != teacher.id:
            raise PermissionError("Only the course teacher can add calendar events")

        now = datetime.now(timezone.utc)
        event = CalendarEvent(
            id=uuid4(),
            course_id=dto.course_id,
            created_by=teacher.id,
            title=dto.title.strip(),
            description=dto.description.strip() if dto.description else None,
            event_datetime=dto.event_datetime,
            source="manual",
            created_at=now,
        )
        saved = await self.calendar_repo.create(event)
        return self._to_dto(saved, course.title)

    async def update_event(
        self, event_id: UUID, dto: UpdateCalendarEventDTO, teacher: User
    ) -> Optional[CalendarEventResponseDTO]:
        event = await self.calendar_repo.get_by_id(event_id)
        if not event:
            return None
        if event.source != "manual":
            raise ValueError("Cannot edit an automated assignment calendar event directly")
        if not teacher.is_admin() and event.created_by != teacher.id:
            raise PermissionError("Access denied")

        if dto.title is not None:
            event.title = dto.title.strip()
        if dto.description is not None:
            event.description = dto.description.strip()
        if dto.event_datetime is not None:
            event.event_datetime = dto.event_datetime

        updated = await self.calendar_repo.update(event)
        course = await self.course_repo.get_by_id(updated.course_id)
        return self._to_dto(updated, course.title if course else None)

    async def delete_event(self, event_id: UUID, teacher: User) -> bool:
        event = await self.calendar_repo.get_by_id(event_id)
        if not event:
            return False
        if event.source != "manual":
            raise ValueError("Cannot delete an automated assignment calendar event directly")
        if not teacher.is_admin() and event.created_by != teacher.id:
            raise PermissionError("Access denied")

        return await self.calendar_repo.delete(event_id)

    def _to_dto(self, e: CalendarEvent, course_title: Optional[str] = None) -> CalendarEventResponseDTO:
        return CalendarEventResponseDTO(
            id=e.id,
            course_id=e.course_id,
            created_by=e.created_by,
            title=e.title,
            event_datetime=e.event_datetime,
            source=e.source,
            description=e.description,
            assignment_id=e.assignment_id,
            created_at=e.created_at,
            course_title=course_title,
        )
