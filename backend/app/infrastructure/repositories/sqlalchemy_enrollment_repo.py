from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, and_
from app.application.interfaces.repositories.i_enrollment_repository import IEnrollmentRepository
from app.domain.entities.enrollment import Enrollment
from app.domain.entities.user import User
from app.infrastructure.database.models.enrollment_model import EnrollmentModel
from app.infrastructure.database.models.user_model import UserModel


class SQLAlchemyEnrollmentRepository(IEnrollmentRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, user_id: UUID, course_id: UUID) -> Optional[Enrollment]:
        stmt = select(EnrollmentModel).where(
            and_(EnrollmentModel.user_id == user_id, EnrollmentModel.course_id == course_id)
        )
        res = await self.session.execute(stmt)
        model = res.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def enroll(self, enrollment: Enrollment) -> Enrollment:
        model = EnrollmentModel(
            id=enrollment.id,
            user_id=enrollment.user_id,
            course_id=enrollment.course_id,
            method=enrollment.method,
            enrolled_at=enrollment.enrolled_at,
        )
        self.session.add(model)
        await self.session.flush()
        return self._to_entity(model)

    async def unenroll(self, user_id: UUID, course_id: UUID) -> bool:
        stmt = delete(EnrollmentModel).where(
            and_(EnrollmentModel.user_id == user_id, EnrollmentModel.course_id == course_id)
        )
        res = await self.session.execute(stmt)
        await self.session.flush()
        return res.rowcount > 0

    async def list_students_by_course(self, course_id: UUID) -> List[User]:
        stmt = (
            select(UserModel)
            .join(EnrollmentModel, EnrollmentModel.user_id == UserModel.id)
            .where(EnrollmentModel.course_id == course_id)
            .order_by(UserModel.full_name.asc())
        )
        models = (await self.session.execute(stmt)).scalars().all()
        return [
            User(
                id=m.id,
                email=m.email,
                full_name=m.full_name,
                avatar_url=m.avatar_url,
                role=m.role,
                student_id=m.student_id,
                google_id=m.google_id,
                created_at=m.created_at,
                updated_at=m.updated_at,
            )
            for m in models
        ]

    async def list_course_ids_by_user(self, user_id: UUID) -> List[UUID]:
        stmt = select(EnrollmentModel.course_id).where(EnrollmentModel.user_id == user_id)
        return (await self.session.execute(stmt)).scalars().all()

    async def is_enrolled(self, user_id: UUID, course_id: UUID) -> bool:
        stmt = select(EnrollmentModel.id).where(
            and_(EnrollmentModel.user_id == user_id, EnrollmentModel.course_id == course_id)
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none() is not None

    def _to_entity(self, m: EnrollmentModel) -> Enrollment:
        return Enrollment(
            id=m.id,
            user_id=m.user_id,
            course_id=m.course_id,
            method=m.method,
            enrolled_at=m.enrolled_at,
        )
