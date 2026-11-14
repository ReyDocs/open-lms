from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, and_
from app.application.interfaces.repositories.i_assignment_repository import IAssignmentRepository
from app.domain.entities.assignment import Assignment
from app.infrastructure.database.models.assignment_model import AssignmentModel
from app.infrastructure.database.models.enrollment_model import EnrollmentModel


class SQLAlchemyAssignmentRepository(IAssignmentRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, assignment_id: UUID) -> Optional[Assignment]:
        stmt = select(AssignmentModel).where(AssignmentModel.id == assignment_id)
        res = await self.session.execute(stmt)
        model = res.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def create(self, assignment: Assignment) -> Assignment:
        model = AssignmentModel(
            id=assignment.id,
            title=assignment.title,
            description=assignment.description,
            total_points=assignment.total_points,
            status=assignment.status,
            due_date=assignment.due_date,
            module_id=assignment.module_id,
            course_id=assignment.course_id,
            created_at=assignment.created_at,
            updated_at=assignment.updated_at,
        )
        self.session.add(model)
        await self.session.flush()
        return self._to_entity(model)

    async def update(self, assignment: Assignment) -> Assignment:
        stmt = select(AssignmentModel).where(AssignmentModel.id == assignment.id)
        res = await self.session.execute(stmt)
        model = res.scalar_one_or_none()
        if not model:
            raise ValueError(f"Assignment {assignment.id} not found")

        model.title = assignment.title
        model.description = assignment.description
        model.total_points = assignment.total_points
        model.status = assignment.status
        model.due_date = assignment.due_date
        model.updated_at = assignment.updated_at
        await self.session.flush()
        return self._to_entity(model)

    async def delete(self, assignment_id: UUID) -> bool:
        stmt = delete(AssignmentModel).where(AssignmentModel.id == assignment_id)
        res = await self.session.execute(stmt)
        await self.session.flush()
        return res.rowcount > 0

    async def list_by_course(self, course_id: UUID, published_only: bool = False) -> List[Assignment]:
        stmt = select(AssignmentModel).where(AssignmentModel.course_id == course_id)
        if published_only:
            stmt = stmt.where(AssignmentModel.status == "published")
        stmt = stmt.order_by(AssignmentModel.due_date.asc())
        models = (await self.session.execute(stmt)).scalars().all()
        return [self._to_entity(m) for m in models]

    async def list_by_module(self, module_id: UUID, published_only: bool = False) -> List[Assignment]:
        stmt = select(AssignmentModel).where(AssignmentModel.module_id == module_id)
        if published_only:
            stmt = stmt.where(AssignmentModel.status == "published")
        stmt = stmt.order_by(AssignmentModel.due_date.asc())
        models = (await self.session.execute(stmt)).scalars().all()
        return [self._to_entity(m) for m in models]

    async def list_upcoming(self, user_id: UUID, days: int = 7) -> List[Assignment]:
        now = datetime.now(timezone.utc)
        future = now + timedelta(days=days)

        enrolled_courses = select(EnrollmentModel.course_id).where(EnrollmentModel.user_id == user_id)

        stmt = (
            select(AssignmentModel)
            .where(
                and_(
                    AssignmentModel.course_id.in_(enrolled_courses),
                    AssignmentModel.status == "published",
                    AssignmentModel.due_date >= now,
                    AssignmentModel.due_date <= future,
                )
            )
            .order_by(AssignmentModel.due_date.asc())
        )
        models = (await self.session.execute(stmt)).scalars().all()
        return [self._to_entity(m) for m in models]

    def _to_entity(self, m: AssignmentModel) -> Assignment:
        return Assignment(
            id=m.id,
            title=m.title,
            description=m.description,
            total_points=m.total_points,
            status=m.status,
            due_date=m.due_date,
            module_id=m.module_id,
            course_id=m.course_id,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )
