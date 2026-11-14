from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime, timezone

from app.application.interfaces.repositories.i_enrollment_repository import IEnrollmentRepository
from app.application.interfaces.repositories.i_course_repository import ICourseRepository
from app.application.interfaces.repositories.i_user_repository import IUserRepository
from app.application.interfaces.services.i_email_service import IEmailService
from app.application.services.notification_service import NotificationService
from app.application.dtos.user_dtos import UserResponseDTO
from app.domain.entities.enrollment import Enrollment
from app.domain.entities.user import User


class EnrollmentService:
    def __init__(
        self,
        enrollment_repo: IEnrollmentRepository,
        course_repo: ICourseRepository,
        user_repo: IUserRepository,
        email_service: Optional[IEmailService] = None,
        notification_service: Optional[NotificationService] = None,
    ):
        self.enrollment_repo = enrollment_repo
        self.course_repo = course_repo
        self.user_repo = user_repo
        self.email_service = email_service
        self.notification_service = notification_service

    async def enroll_students_from_pool(
        self, course_id: UUID, student_ids: List[UUID], teacher: User
    ) -> List[UserResponseDTO]:
        course = await self.course_repo.get_by_id(course_id)
        if not course:
            raise ValueError("Course not found")
        if not teacher.is_admin() and course.teacher_id != teacher.id:
            raise PermissionError("Only the course teacher can enroll students")

        now = datetime.now(timezone.utc)
        enrolled_students: List[UserResponseDTO] = []

        for student_id in student_ids:
            student = await self.user_repo.get_by_id(student_id)
            if not student:
                continue

            # Check if already enrolled
            is_already = await self.enrollment_repo.is_enrolled(student_id, course_id)
            if not is_already:
                enrollment = Enrollment(
                    id=uuid4(),
                    user_id=student_id,
                    course_id=course_id,
                    method="pool",
                    enrolled_at=now,
                )
                await self.enrollment_repo.enroll(enrollment)
                if self.notification_service:
                    await self.notification_service.create_notification(
                        user_id=student.id,
                        notif_type="enrollment",
                        title=f"Enrolled in {course.code}",
                        message=f"You have been added to {course.title}.",
                        link=f"/courses/{course_id}",
                        recipient_email=student.email,
                    )

            enrolled_students.append(
                UserResponseDTO(
                    id=student.id,
                    email=student.email,
                    full_name=student.full_name,
                    role=student.role,
                    avatar_url=student.avatar_url,
                    student_id=student.student_id,
                    created_at=student.created_at,
                )
            )

        return enrolled_students

    async def invite_student_by_email(
        self, course_id: UUID, email: str, teacher: User
    ) -> UserResponseDTO:
        course = await self.course_repo.get_by_id(course_id)
        if not course:
            raise ValueError("Course not found")
        if not teacher.is_admin() and course.teacher_id != teacher.id:
            raise PermissionError("Only the course teacher can invite students")

        clean_email = email.lower().strip()
        student = await self.user_repo.get_by_email(clean_email)
        now = datetime.now(timezone.utc)

        if not student:
            # Pre-register user
            student = User(
                id=uuid4(),
                email=clean_email,
                full_name=clean_email.split("@")[0].capitalize(),
                role="student",
                created_at=now,
                updated_at=now,
            )
            student = await self.user_repo.create(student)

        # Check existing enrollment
        already_enrolled = await self.enrollment_repo.is_enrolled(student.id, course_id)
        if not already_enrolled:
            enrollment = Enrollment(
                id=uuid4(),
                user_id=student.id,
                course_id=course_id,
                method="invite",
                enrolled_at=now,
            )
            await self.enrollment_repo.enroll(enrollment)

            if self.notification_service:
                await self.notification_service.create_notification(
                    user_id=student.id,
                    notif_type="enrollment",
                    title=f"Enrolled in {course.code}",
                    message=f"You have been enrolled in {course.title}. Sign in with Google to view course materials.",
                    link=f"/courses/{course_id}",
                )

        # Send invite email
        if self.email_service and not already_enrolled:
            invite_html = f"""
            <div style="font-family: sans-serif; padding: 20px;">
                <h2>You've been invited to {course.title}!</h2>
                <p>Teacher {teacher.full_name} has invited you to join <strong>{course.code} - {course.title}</strong> on OpenLMS.</p>
                <p>Please sign in with your Google account ({clean_email}) to access your course materials and assignments.</p>
            </div>
            """
            try:
                await self.email_service.send_email(
                    to=clean_email,
                    subject=f"Course Invitation: {course.code} {course.title}",
                    html_content=invite_html,
                )
            except Exception:
                pass

        return UserResponseDTO(
            id=student.id,
            email=student.email,
            full_name=student.full_name,
            role=student.role,
            avatar_url=student.avatar_url,
            student_id=student.student_id,
            created_at=student.created_at,
        )

    async def list_enrolled_students(
        self, course_id: UUID, user: User
    ) -> List[UserResponseDTO]:
        course = await self.course_repo.get_by_id(course_id)
        if not course:
            raise ValueError("Course not found")
        if user.is_admin():
            pass
        elif user.is_teacher():
            if course.teacher_id != user.id:
                raise PermissionError("Only the course teacher can view the course roster")
        elif not await self.enrollment_repo.is_enrolled(user.id, course_id):
            raise PermissionError("Access denied")

        students = await self.enrollment_repo.list_students_by_course(course_id)
        return [
            UserResponseDTO(
                id=s.id,
                email=s.email,
                full_name=s.full_name,
                role=s.role,
                avatar_url=s.avatar_url,
                student_id=s.student_id,
                created_at=s.created_at,
            )
            for s in students
        ]

    async def remove_student(
        self, course_id: UUID, student_id: UUID, teacher: User
    ) -> bool:
        course = await self.course_repo.get_by_id(course_id)
        if not course:
            raise ValueError("Course not found")
        if not teacher.is_admin() and course.teacher_id != teacher.id:
            raise PermissionError("Only the course teacher can remove students")

        return await self.enrollment_repo.unenroll(student_id, course_id)
