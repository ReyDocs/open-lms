from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime, timezone

from app.application.interfaces.repositories.i_submission_repository import ISubmissionRepository
from app.application.interfaces.repositories.i_assignment_repository import IAssignmentRepository
from app.application.interfaces.repositories.i_enrollment_repository import IEnrollmentRepository
from app.application.interfaces.repositories.i_user_repository import IUserRepository
from app.application.interfaces.services.i_storage_service import IStorageService
from app.application.dtos.submission_dtos import SubmissionResponseDTO
from app.domain.entities.submission import Submission
from app.domain.entities.user import User
from app.domain.value_objects.file_type import FileType, MAX_FILE_SIZE_BYTES


class SubmissionService:
    def __init__(
        self,
        submission_repo: ISubmissionRepository,
        assignment_repo: IAssignmentRepository,
        enrollment_repo: IEnrollmentRepository,
        user_repo: IUserRepository,
        storage_service: Optional[IStorageService] = None,
    ):
        self.submission_repo = submission_repo
        self.assignment_repo = assignment_repo
        self.enrollment_repo = enrollment_repo
        self.user_repo = user_repo
        self.storage_service = storage_service

    async def submit_assignment(
        self,
        assignment_id: UUID,
        file_bytes: bytes,
        file_name: str,
        content_type: str,
        student: User,
    ) -> SubmissionResponseDTO:
        # Validate assignment
        assignment = await self.assignment_repo.get_by_id(assignment_id)
        if not assignment:
            raise ValueError("Assignment not found")
        if assignment.status != "published":
            raise ValueError("Cannot submit to an unpublished assignment")

        # Validate enrollment
        is_enrolled = await self.enrollment_repo.is_enrolled(student.id, assignment.course_id)
        if not is_enrolled and not student.is_admin():
            raise PermissionError("Student is not enrolled in this course")

        # Check due date
        now = datetime.now(timezone.utc)
        due = assignment.due_date if assignment.due_date.tzinfo else assignment.due_date.replace(tzinfo=timezone.utc)
        if now > due:
            raise ValueError("Assignment is past due. Late submissions are not accepted.")

        # Check file size & type
        if len(file_bytes) > MAX_FILE_SIZE_BYTES:
            raise ValueError("File exceeds maximum allowed size of 25MB")

        ft = FileType(file_name)
        if not ft.is_allowed():
            raise ValueError(f"File type .{ft.extension} is not allowed")

        if not self.storage_service:
            raise RuntimeError("Storage service is unavailable")

        file_url = await self.storage_service.upload_file(
            file_bytes=file_bytes,
            filename=file_name,
            content_type=content_type,
            bucket="submissions",
        )

        submission = Submission(
            id=uuid4(),
            assignment_id=assignment_id,
            student_id=student.id,
            file_url=file_url,
            file_name=file_name,
            file_size=len(file_bytes),
            submitted_at=now,
        )
        saved = await self.submission_repo.create(submission)
        return self._to_dto(saved, student.full_name, student.email)

    async def get_my_submission(
        self, assignment_id: UUID, student: User
    ) -> Optional[SubmissionResponseDTO]:
        sub = await self.submission_repo.get_latest_by_student_and_assignment(student.id, assignment_id)
        if not sub:
            return None
        return self._to_dto(sub, student.full_name, student.email)

    async def list_assignment_submissions(
        self, assignment_id: UUID, teacher: User
    ) -> List[SubmissionResponseDTO]:
        assignment = await self.assignment_repo.get_by_id(assignment_id)
        if not assignment:
            raise ValueError("Assignment not found")
        if not teacher.is_teacher():
            raise PermissionError("Only teachers can view all submissions")

        submissions = await self.submission_repo.list_by_assignment(assignment_id)
        dtos: List[SubmissionResponseDTO] = []
        for s in submissions:
            student = await self.user_repo.get_by_id(s.student_id)
            name = student.full_name if student else None
            email = student.email if student else None
            dtos.append(self._to_dto(s, name, email))
        return dtos

    async def get_submission_by_id(
        self, submission_id: UUID, user: User
    ) -> Optional[SubmissionResponseDTO]:
        sub = await self.submission_repo.get_by_id(submission_id)
        if not sub:
            return None
        if not user.is_teacher() and sub.student_id != user.id:
            raise PermissionError("Access denied")

        student = await self.user_repo.get_by_id(sub.student_id)
        name = student.full_name if student else None
        email = student.email if student else None
        return self._to_dto(sub, name, email)

    def _to_dto(
        self, s: Submission, student_name: Optional[str] = None, student_email: Optional[str] = None
    ) -> SubmissionResponseDTO:
        return SubmissionResponseDTO(
            id=s.id,
            assignment_id=s.assignment_id,
            student_id=s.student_id,
            file_url=s.file_url,
            file_name=s.file_name,
            file_size=s.file_size,
            submitted_at=s.submitted_at,
            grade=s.grade,
            feedback=s.feedback,
            graded_at=s.graded_at,
            student_name=student_name,
            student_email=student_email,
        )
