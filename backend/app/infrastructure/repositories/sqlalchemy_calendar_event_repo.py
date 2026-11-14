from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, and_
from app.application.interfaces.repositories.i_calendar_event_repository import ICalendarEventRepository
from app.domain.entities.calendar_event import CalendarEvent
from app.infrastructure.database.models.calendar_event_model import CalendarEventModel
from app.infrastructure.database.models.enrollment_model import EnrollmentModel
from app.infrastructure.database.models.course_model import CourseModel


class SQLAlchemyCalendarEventRepository(ICalendarEventRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, event_id: UUID) -> Optional[CalendarEvent]:
        stmt = select(CalendarEventModel).where(CalendarEventModel.id == event_id)
        res = await self.session.execute(stmt)
        model = res.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def create(self, event: CalendarEvent) -> CalendarEvent:
        model = CalendarEventModel(
            id=event.id,
            course_id=event.course_id,
            created_by=event.created_by,
            title=event.title,
            description=event.description,
            event_datetime=event.event_datetime,
            source=event.source,
            assignment_id=event.assignment_id,
            created_at=event.created_at,
        )
        self.session.add(model)
        await self.session.flush()
        return self._to_entity(model)

    async def update(self, event: CalendarEvent) -> CalendarEvent:
        stmt = select(CalendarEventModel).where(CalendarEventModel.id == event.id)
        res = await self.session.execute(stmt)
        model = res.scalar_one_or_none()
        if not model:
            raise ValueError(f"Calendar event {event.id} not found")

        model.title = event.title
        model.description = event.description
        model.event_datetime = event.event_datetime
        await self.session.flush()
        return self._to_entity(model)

    async def delete(self, event_id: UUID) -> bool:
        stmt = delete(CalendarEventModel).where(CalendarEventModel.id == event_id)
        res = await self.session.execute(stmt)
        await self.session.flush()
        return res.rowcount > 0

    async def list_by_course(self, course_id: UUID) -> List[CalendarEvent]:
        stmt = (
            select(CalendarEventModel)
            .where(CalendarEventModel.course_id == course_id)
            .order_by(CalendarEventModel.event_datetime.asc())
        )
        models = (await self.session.execute(stmt)).scalars().all()
        return [self._to_entity(m) for m in models]

    async def list_by_user(
        self, user_id: UUID, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
    ) -> List[CalendarEvent]:
        enrolled_courses = select(EnrollmentModel.course_id).where(EnrollmentModel.user_id == user_id)
        taught_courses = select(CourseModel.id).where(CourseModel.teacher_id == user_id)

        stmt = select(CalendarEventModel).where(
            CalendarEventModel.course_id.in_(enrolled_courses.union(taught_courses))
        )
        if start_date:
            stmt = stmt.where(CalendarEventModel.event_datetime >= start_date)
        if end_date:
            stmt = stmt.where(CalendarEventModel.event_datetime <= end_date)

        stmt = stmt.order_by(CalendarEventModel.event_datetime.asc())
        models = (await self.session.execute(stmt)).scalars().all()
        return [self._to_entity(m) for m in models]

    async def delete_by_assignment(self, assignment_id: UUID) -> bool:
        stmt = delete(CalendarEventModel).where(CalendarEventModel.assignment_id == assignment_id)
        res = await self.session.execute(stmt)
        await self.session.flush()
        return res.rowcount > 0

    def _to_entity(self, m: CalendarEventModel) -> CalendarEvent:
        return CalendarEvent(
            id=m.id,
            course_id=m.course_id,
            created_by=m.created_by,
            title=m.title,
            description=m.description,
            event_datetime=m.event_datetime,
            source=m.source,
            assignment_id=m.assignment_id,
            created_at=m.created_at,
        )
