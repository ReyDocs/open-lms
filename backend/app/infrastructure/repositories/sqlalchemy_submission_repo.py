from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.application.interfaces.repositories.i_submission_repository import ISubmissionRepository
from app.domain.entities.submission import Submission
from app.infrastructure.database.models.submission_model import SubmissionModel
from app.infrastructure.database.models.assignment_model import AssignmentModel


class SQLAlchemySubmissionRepository(ISubmissionRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, submission_id: UUID) -> Optional[Submission]:
        stmt = select(SubmissionModel).where(SubmissionModel.id == submission_id)
        res = await self.session.execute(stmt)
        model = res.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def create(self, submission: Submission) -> Submission:
        model = SubmissionModel(
            id=submission.id,
            assignment_id=submission.assignment_id,
            student_id=submission.student_id,
            file_url=submission.file_url,
            file_name=submission.file_name,
            file_size=submission.file_size,
            grade=submission.grade,
            feedback=submission.feedback,
            submitted_at=submission.submitted_at,
            graded_at=submission.graded_at,
        )
        self.session.add(model)
        await self.session.flush()
        return self._to_entity(model)

    async def update(self, submission: Submission) -> Submission:
        stmt = select(SubmissionModel).where(SubmissionModel.id == submission.id)
        res = await self.session.execute(stmt)
        model = res.scalar_one_or_none()
        if not model:
            raise ValueError(f"Submission {submission.id} not found")

        model.grade = submission.grade
        model.feedback = submission.feedback
        model.graded_at = submission.graded_at
        await self.session.flush()
        return self._to_entity(model)

    async def get_latest_by_student_and_assignment(
        self, student_id: UUID, assignment_id: UUID
    ) -> Optional[Submission]:
        stmt = (
            select(SubmissionModel)
            .where(
                and_(
                    SubmissionModel.student_id == student_id,
                    SubmissionModel.assignment_id == assignment_id,
                )
            )
            .order_by(SubmissionModel.submitted_at.desc())
            .limit(1)
        )
        res = await self.session.execute(stmt)
        model = res.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_by_assignment(self, assignment_id: UUID) -> List[Submission]:
        stmt = (
            select(SubmissionModel)
            .where(SubmissionModel.assignment_id == assignment_id)
            .order_by(SubmissionModel.submitted_at.desc())
        )
        models = (await self.session.execute(stmt)).scalars().all()
        return [self._to_entity(m) for m in models]

    async def list_by_student_and_assignment(
        self, student_id: UUID, assignment_id: UUID
    ) -> List[Submission]:
        stmt = (
            select(SubmissionModel)
            .where(
                and_(
                    SubmissionModel.student_id == student_id,
                    SubmissionModel.assignment_id == assignment_id,
                )
            )
            .order_by(SubmissionModel.submitted_at.desc())
        )
        models = (await self.session.execute(stmt)).scalars().all()
        return [self._to_entity(m) for m in models]

    async def list_by_student_and_course(
        self, student_id: UUID, course_id: UUID
    ) -> List[Submission]:
        stmt = (
            select(SubmissionModel)
            .join(AssignmentModel, AssignmentModel.id == SubmissionModel.assignment_id)
            .where(
                and_(
                    SubmissionModel.student_id == student_id,
                    AssignmentModel.course_id == course_id,
                )
            )
            .order_by(SubmissionModel.submitted_at.desc())
        )
        models = (await self.session.execute(stmt)).scalars().all()
        return [self._to_entity(m) for m in models]

    async def list_latest_by_course(self, course_id: UUID) -> List[Submission]:
        stmt = (
            select(SubmissionModel)
            .join(AssignmentModel, AssignmentModel.id == SubmissionModel.assignment_id)
            .where(AssignmentModel.course_id == course_id)
            .order_by(SubmissionModel.submitted_at.desc())
        )
        models = (await self.session.execute(stmt)).scalars().all()
        return [self._to_entity(m) for m in models]

    def _to_entity(self, m: SubmissionModel) -> Submission:
        return Submission(
            id=m.id,
            assignment_id=m.assignment_id,
            student_id=m.student_id,
            file_url=m.file_url,
            file_name=m.file_name,
            file_size=m.file_size,
            submitted_at=m.submitted_at,
            grade=m.grade,
            feedback=m.feedback,
            graded_at=m.graded_at,
        )
