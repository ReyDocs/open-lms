from typing import List, Optional, Tuple
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, delete
from app.application.interfaces.repositories.i_course_repository import ICourseRepository
from app.domain.entities.course import Course
from app.infrastructure.database.models.course_model import CourseModel
from app.infrastructure.database.models.enrollment_model import EnrollmentModel


class SQLAlchemyCourseRepository(ICourseRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, course_id: UUID) -> Optional[Course]:
        stmt = select(CourseModel).where(CourseModel.id == course_id)
        res = await self.session.execute(stmt)
        model = res.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_code(self, code: str) -> Optional[Course]:
        stmt = select(CourseModel).where(func.upper(CourseModel.code) == code.upper().strip())
        res = await self.session.execute(stmt)
        model = res.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def create(self, course: Course) -> Course:
        model = CourseModel(
            id=course.id,
            title=course.title,
            code=course.code.upper().strip(),
            description=course.description,
            semester=course.semester,
            teacher_id=course.teacher_id,
            cover_image_url=course.cover_image_url,
            created_at=course.created_at,
            updated_at=course.updated_at,
        )
        self.session.add(model)
        await self.session.flush()
        return self._to_entity(model)

    async def update(self, course: Course) -> Course:
        stmt = select(CourseModel).where(CourseModel.id == course.id)
        res = await self.session.execute(stmt)
        model = res.scalar_one_or_none()
        if not model:
            raise ValueError(f"Course {course.id} not found")

        model.title = course.title
        model.description = course.description
        model.semester = course.semester
        model.cover_image_url = course.cover_image_url
        model.updated_at = course.updated_at
        await self.session.flush()
        return self._to_entity(model)

    async def delete(self, course_id: UUID) -> bool:
        stmt = delete(CourseModel).where(CourseModel.id == course_id)
        res = await self.session.execute(stmt)
        await self.session.flush()
        return res.rowcount > 0

    async def list_all(self, page: int = 1, per_page: int = 20) -> Tuple[List[Course], int]:
        count_stmt = select(func.count(CourseModel.id))
        total = (await self.session.execute(count_stmt)).scalar() or 0

        stmt = select(CourseModel).order_by(CourseModel.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
        models = (await self.session.execute(stmt)).scalars().all()
        return [self._to_entity(m) for m in models], total

    async def list_by_teacher(self, teacher_id: UUID, page: int = 1, per_page: int = 20) -> Tuple[List[Course], int]:
        count_stmt = select(func.count(CourseModel.id)).where(CourseModel.teacher_id == teacher_id)
        total = (await self.session.execute(count_stmt)).scalar() or 0

        stmt = (
            select(CourseModel)
            .where(CourseModel.teacher_id == teacher_id)
            .order_by(CourseModel.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        models = (await self.session.execute(stmt)).scalars().all()
        return [self._to_entity(m) for m in models], total

    async def list_by_student(self, student_id: UUID, page: int = 1, per_page: int = 20) -> Tuple[List[Course], int]:
        count_stmt = (
            select(func.count(CourseModel.id))
            .join(EnrollmentModel, EnrollmentModel.course_id == CourseModel.id)
            .where(EnrollmentModel.user_id == student_id)
        )
        total = (await self.session.execute(count_stmt)).scalar() or 0

        stmt = (
            select(CourseModel)
            .join(EnrollmentModel, EnrollmentModel.course_id == CourseModel.id)
            .where(EnrollmentModel.user_id == student_id)
            .order_by(CourseModel.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        models = (await self.session.execute(stmt)).scalars().all()
        return [self._to_entity(m) for m in models], total

    async def search(
        self, query: str, user_id: Optional[UUID] = None, page: int = 1, per_page: int = 20
    ) -> Tuple[List[Course], int]:
        filter_expr = or_(
            CourseModel.title.ilike(f"%{query}%"),
            CourseModel.code.ilike(f"%{query}%"),
        )
        stmt = select(CourseModel).where(filter_expr)
        count_stmt = select(func.count(CourseModel.id)).where(filter_expr)

        if user_id:
            # Enrolled courses or taught courses
            enrolled_subq = select(EnrollmentModel.course_id).where(EnrollmentModel.user_id == user_id)
            user_filter = or_(CourseModel.teacher_id == user_id, CourseModel.id.in_(enrolled_subq))
            stmt = stmt.where(user_filter)
            count_stmt = count_stmt.where(user_filter)

        total = (await self.session.execute(count_stmt)).scalar() or 0
        stmt = stmt.order_by(CourseModel.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
        models = (await self.session.execute(stmt)).scalars().all()
        return [self._to_entity(m) for m in models], total

    def _to_entity(self, m: CourseModel) -> Course:
        return Course(
            id=m.id,
            title=m.title,
            code=m.code,
            description=m.description,
            semester=m.semester,
            teacher_id=m.teacher_id,
            cover_image_url=m.cover_image_url,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )
