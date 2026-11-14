import csv
import io
from typing import List, Optional, Dict
from uuid import UUID
from datetime import datetime, timezone

from app.application.interfaces.repositories.i_submission_repository import ISubmissionRepository
from app.application.interfaces.repositories.i_assignment_repository import IAssignmentRepository
from app.application.interfaces.repositories.i_course_repository import ICourseRepository
from app.application.interfaces.repositories.i_enrollment_repository import IEnrollmentRepository
from app.application.interfaces.repositories.i_user_repository import IUserRepository
from app.application.services.notification_service import NotificationService
from app.application.dtos.grading_dtos import (
    GradeSubmissionDTO, StudentGradeDTO, GradebookResponseDTO, GradebookRowDTO
)
from app.application.dtos.submission_dtos import SubmissionResponseDTO
from app.domain.entities.user import User


class GradingService:
    def __init__(
        self,
        submission_repo: ISubmissionRepository,
        assignment_repo: IAssignmentRepository,
        course_repo: ICourseRepository,
        enrollment_repo: IEnrollmentRepository,
        user_repo: IUserRepository,
        notification_service: Optional[NotificationService] = None,
    ):
        self.submission_repo = submission_repo
        self.assignment_repo = assignment_repo
        self.course_repo = course_repo
        self.enrollment_repo = enrollment_repo
        self.user_repo = user_repo
        self.notification_service = notification_service

    async def grade_submission(
        self, dto: GradeSubmissionDTO, teacher: User
    ) -> SubmissionResponseDTO:
        if not teacher.is_teacher():
            raise PermissionError("Only teachers can grade submissions")

        submission = await self.submission_repo.get_by_id(dto.submission_id)
        if not submission:
            raise ValueError("Submission not found")

        assignment = await self.assignment_repo.get_by_id(submission.assignment_id)
        if not assignment:
            raise ValueError("Assignment not found")

        if dto.grade < 0 or dto.grade > assignment.total_points:
            raise ValueError(f"Grade must be between 0 and total points ({assignment.total_points})")

        submission.grade = dto.grade
        submission.feedback = dto.feedback.strip() if dto.feedback else None
        submission.graded_at = datetime.now(timezone.utc)

        updated = await self.submission_repo.update(submission)

        student = await self.user_repo.get_by_id(submission.student_id)
        student_email = student.email if student else None
        student_name = student.full_name if student else None

        # Notify student
        if self.notification_service and student:
            await self.notification_service.create_notification(
                user_id=student.id,
                notif_type="grade",
                title=f"Assignment Graded: {assignment.title}",
                message=f"You received {dto.grade}/{assignment.total_points} on {assignment.title}.",
                link=f"/courses/{assignment.course_id}/assignments/{assignment.id}",
                recipient_email=student_email,
            )

        return SubmissionResponseDTO(
            id=updated.id,
            assignment_id=updated.assignment_id,
            student_id=updated.student_id,
            file_url=updated.file_url,
            file_name=updated.file_name,
            file_size=updated.file_size,
            submitted_at=updated.submitted_at,
            grade=updated.grade,
            feedback=updated.feedback,
            graded_at=updated.graded_at,
            student_name=student_name,
            student_email=student_email,
        )

    async def get_gradebook(self, course_id: UUID, teacher: User) -> GradebookResponseDTO:
        course = await self.course_repo.get_by_id(course_id)
        if not course:
            raise ValueError("Course not found")
        if not teacher.is_admin() and course.teacher_id != teacher.id:
            raise PermissionError("Only course teacher can access the gradebook")

        assignments = await self.assignment_repo.list_by_course(course_id, published_only=False)
        students = await self.enrollment_repo.list_students_by_course(course_id)

        assignment_list = [
            {"id": str(a.id), "title": a.title, "total_points": a.total_points}
            for a in assignments
        ]

        total_possible = sum(a.total_points for a in assignments)

        rows: List[GradebookRowDTO] = []
        for student in students:
            student_grades: Dict[str, Optional[int]] = {}
            earned_sum = 0
            for a in assignments:
                sub = await self.submission_repo.get_latest_by_student_and_assignment(student.id, a.id)
                if sub and sub.grade is not None:
                    student_grades[str(a.id)] = sub.grade
                    earned_sum += sub.grade
                else:
                    student_grades[str(a.id)] = None

            pct = (earned_sum / total_possible * 100.0) if total_possible > 0 else 0.0

            rows.append(
                GradebookRowDTO(
                    student_id=student.id,
                    student_name=student.full_name,
                    student_email=student.email,
                    grades=student_grades,
                    total_earned=earned_sum,
                    total_possible=total_possible,
                    overall_percentage=round(pct, 2),
                )
            )

        return GradebookResponseDTO(
            course_id=course_id,
            assignments=assignment_list,
            students=rows,
        )

    async def export_gradebook_csv(self, course_id: UUID, teacher: User) -> str:
        gradebook = await self.get_gradebook(course_id, teacher)
        output = io.StringIO()
        writer = csv.writer(output)

        headers = ["Student Name", "Student Email"]
        for a in gradebook.assignments:
            headers.append(f"{a['title']} ({a['total_points']} pts)")
        headers.extend(["Total Earned", "Total Possible", "Overall %"])
        writer.writerow(headers)

        for row in gradebook.students:
            r = [row.student_name, row.student_email]
            for a in gradebook.assignments:
                g = row.grades.get(a["id"])
                r.append(str(g) if g is not None else "-")
            r.extend([str(row.total_earned), str(row.total_possible), f"{row.overall_percentage}%"])
            writer.writerow(r)

        return output.getvalue()

    async def get_my_grades(self, course_id: UUID, student: User) -> List[StudentGradeDTO]:
        if not student.is_student():
            raise PermissionError("Only students can access personal grades")
        course = await self.course_repo.get_by_id(course_id)
        if not course:
            raise ValueError("Course not found")
        if not await self.enrollment_repo.is_enrolled(student.id, course_id):
            raise PermissionError("Student is not enrolled in this course")

        assignments = await self.assignment_repo.list_by_course(course_id, published_only=True)
        results: List[StudentGradeDTO] = []

        for a in assignments:
            sub = await self.submission_repo.get_latest_by_student_and_assignment(student.id, a.id)
            points_earned = sub.grade if sub else None
            percentage = (
                (points_earned / a.total_points * 100.0)
                if points_earned is not None and a.total_points > 0
                else None
            )
            results.append(
                StudentGradeDTO(
                    assignment_id=a.id,
                    assignment_title=a.title,
                    total_points=a.total_points,
                    points_earned=points_earned,
                    percentage=round(percentage, 2) if percentage is not None else None,
                    feedback=sub.feedback if sub else None,
                    submitted_at=sub.submitted_at if sub else None,
                    graded_at=sub.graded_at if sub else None,
                )
            )

        return results
