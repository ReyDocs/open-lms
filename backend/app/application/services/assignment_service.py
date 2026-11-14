from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime, timezone

from app.application.interfaces.repositories.i_assignment_repository import IAssignmentRepository
from app.application.interfaces.repositories.i_module_repository import IModuleRepository
from app.application.interfaces.repositories.i_course_repository import ICourseRepository
from app.application.interfaces.repositories.i_calendar_event_repository import ICalendarEventRepository
from app.application.services.notification_service import NotificationService
from app.application.dtos.assignment_dtos import (
    CreateAssignmentDTO, UpdateAssignmentDTO, AssignmentResponseDTO
)
from app.domain.entities.assignment import Assignment
from app.domain.entities.calendar_event import CalendarEvent
from app.domain.entities.user import User


class AssignmentService:
    def __init__(
        self,
        assignment_repo: IAssignmentRepository,
        module_repo: IModuleRepository,
        course_repo: ICourseRepository,
        calendar_repo: Optional[ICalendarEventRepository] = None,
        notification_service: Optional[NotificationService] = None,
    ):
        self.assignment_repo = assignment_repo
        self.module_repo = module_repo
        self.course_repo = course_repo
        self.calendar_repo = calendar_repo
        self.notification_service = notification_service

    async def get_assignment_by_id(self, assignment_id: UUID) -> Optional[AssignmentResponseDTO]:
        assignment = await self.assignment_repo.get_by_id(assignment_id)
        if not assignment:
            return None
        return self._to_dto(assignment)

    async def create_assignment(
        self, module_id: UUID, dto: CreateAssignmentDTO, teacher: User
    ) -> AssignmentResponseDTO:
        module = await self.module_repo.get_by_id(module_id)
        if not module:
            raise ValueError("Module not found")
        course = await self.course_repo.get_by_id(module.course_id)
        if not course or (not teacher.is_admin() and course.teacher_id != teacher.id):
            raise PermissionError("Only the course teacher can create assignments")

        now = datetime.now(timezone.utc)
        assignment = Assignment(
            id=uuid4(),
            title=dto.title.strip(),
            description=dto.description.strip(),
            total_points=dto.total_points,
            status=dto.status,
            due_date=dto.due_date,
            module_id=module_id,
            course_id=course.id,
            created_at=now,
            updated_at=now,
        )
        saved = await self.assignment_repo.create(assignment)

        if saved.status == "published":
            await self._handle_publish_side_effects(saved, course.title)

        return self._to_dto(saved)

    async def update_assignment(
        self, assignment_id: UUID, dto: UpdateAssignmentDTO, teacher: User
    ) -> Optional[AssignmentResponseDTO]:
        assignment = await self.assignment_repo.get_by_id(assignment_id)
        if not assignment:
            return None
        course = await self.course_repo.get_by_id(assignment.course_id)
        if not course or (not teacher.is_admin() and course.teacher_id != teacher.id):
            raise PermissionError("Only the course teacher can update this assignment")

        was_draft = assignment.status == "draft"

        if dto.title is not None:
            assignment.title = dto.title.strip()
        if dto.description is not None:
            assignment.description = dto.description.strip()
        if dto.total_points is not None:
            assignment.total_points = dto.total_points
        if dto.due_date is not None:
            assignment.due_date = dto.due_date
        if dto.status is not None:
            assignment.status = dto.status
        assignment.updated_at = datetime.now(timezone.utc)

        updated = await self.assignment_repo.update(assignment)

        # If it was just published or due date changed
        if was_draft and updated.status == "published":
            await self._handle_publish_side_effects(updated, course.title)
        elif self.calendar_repo and dto.due_date is not None:
            # Update auto calendar event
            await self.calendar_repo.delete_by_assignment(updated.id)
            if updated.status == "published":
                event = CalendarEvent(
                    id=uuid4(),
                    course_id=updated.course_id,
                    created_by=teacher.id,
                    title=f"Due: {updated.title}",
                    description=f"Assignment due date for {updated.title}",
                    event_datetime=updated.due_date,
                    source="auto",
                    assignment_id=updated.id,
                    created_at=datetime.now(timezone.utc),
                )
                await self.calendar_repo.create(event)

        return self._to_dto(updated)

    async def publish_assignment(self, assignment_id: UUID, teacher: User) -> Optional[AssignmentResponseDTO]:
        dto = UpdateAssignmentDTO(status="published")
        return await self.update_assignment(assignment_id, dto, teacher)

    async def delete_assignment(self, assignment_id: UUID, teacher: User) -> bool:
        assignment = await self.assignment_repo.get_by_id(assignment_id)
        if not assignment:
            return False
        course = await self.course_repo.get_by_id(assignment.course_id)
        if not course or (not teacher.is_admin() and course.teacher_id != teacher.id):
            raise PermissionError("Only the course teacher can delete this assignment")

        # Delete calendar event if auto
        if self.calendar_repo:
            await self.calendar_repo.delete_by_assignment(assignment_id)

        return await self.assignment_repo.delete(assignment_id)

    async def list_by_course(self, course_id: UUID, user: User) -> List[AssignmentResponseDTO]:
        # If student, only published assignments
        published_only = not user.is_teacher()
        assignments = await self.assignment_repo.list_by_course(course_id, published_only=published_only)
        return [self._to_dto(a) for a in assignments]

    async def list_by_module(self, module_id: UUID, user: User) -> List[AssignmentResponseDTO]:
        published_only = not user.is_teacher()
        assignments = await self.assignment_repo.list_by_module(module_id, published_only=published_only)
        return [self._to_dto(a) for a in assignments]

    async def list_upcoming_deadlines(self, user_id: UUID, days: int = 7) -> List[AssignmentResponseDTO]:
        assignments = await self.assignment_repo.list_upcoming(user_id, days)
        return [self._to_dto(a) for a in assignments]

    async def _handle_publish_side_effects(self, assignment: Assignment, course_title: str):
        # 1. Create auto calendar event
        if self.calendar_repo:
            await self.calendar_repo.delete_by_assignment(assignment.id)
            event = CalendarEvent(
                id=uuid4(),
                course_id=assignment.course_id,
                created_by=assignment.course_id,  # system / course context
                title=f"Due: {assignment.title}",
                description=f"Assignment due date for {assignment.title}",
                event_datetime=assignment.due_date,
                source="auto",
                assignment_id=assignment.id,
                created_at=datetime.now(timezone.utc),
            )
            await self.calendar_repo.create(event)

        # 2. Notify students
        if self.notification_service:
            await self.notification_service.notify_course_students(
                course_id=assignment.course_id,
                notif_type="assignment",
                title=f"New Assignment: {assignment.title}",
                message=f"A new assignment has been published in {course_title}. Due: {assignment.due_date.strftime('%Y-%m-%d %H:%M')}",
                link=f"/courses/{assignment.course_id}/assignments/{assignment.id}",
            )

    def _to_dto(self, a: Assignment) -> AssignmentResponseDTO:
        return AssignmentResponseDTO(
            id=a.id,
            title=a.title,
            description=a.description,
            total_points=a.total_points,
            status=a.status,
            due_date=a.due_date,
            module_id=a.module_id,
            course_id=a.course_id,
            created_at=a.created_at,
            updated_at=a.updated_at,
        )
