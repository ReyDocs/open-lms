from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime, timezone

from app.application.interfaces.repositories.i_notification_repository import INotificationRepository
from app.application.interfaces.repositories.i_enrollment_repository import IEnrollmentRepository
from app.application.interfaces.services.i_email_service import IEmailService
from app.application.dtos.notification_dtos import NotificationResponseDTO
from app.domain.entities.notification import Notification


class NotificationService:
    def __init__(
        self,
        notif_repo: INotificationRepository,
        enrollment_repo: Optional[IEnrollmentRepository] = None,
        email_service: Optional[IEmailService] = None,
    ):
        self.notif_repo = notif_repo
        self.enrollment_repo = enrollment_repo
        self.email_service = email_service

    async def list_user_notifications(
        self, user_id: UUID, page: int = 1, per_page: int = 20
    ) -> List[NotificationResponseDTO]:
        items = await self.notif_repo.list_by_user(user_id, page, per_page)
        return [self._to_dto(n) for n in items]

    async def mark_as_read(self, notification_id: UUID, user_id: UUID) -> bool:
        return await self.notif_repo.mark_as_read(notification_id, user_id)

    async def mark_all_as_read(self, user_id: UUID) -> int:
        return await self.notif_repo.mark_all_as_read(user_id)

    async def get_unread_count(self, user_id: UUID) -> int:
        return await self.notif_repo.get_unread_count(user_id)

    async def create_notification(
        self,
        user_id: UUID,
        notif_type: str,
        title: str,
        message: str,
        link: Optional[str] = None,
        recipient_email: Optional[str] = None,
    ) -> NotificationResponseDTO:
        now = datetime.now(timezone.utc)
        notification = Notification(
            id=uuid4(),
            user_id=user_id,
            type=notif_type,
            title=title,
            message=message,
            link=link,
            is_read=False,
            created_at=now,
        )
        saved = await self.notif_repo.create(notification)

        # Trigger email if email service is active and recipient email provided
        if self.email_service and recipient_email:
            try:
                html_body = f"""
                <div style="font-family: sans-serif; padding: 20px;">
                    <h2>{title}</h2>
                    <p>{message}</p>
                    {f'<p><a href="{link}">View Details</a></p>' if link else ''}
                </div>
                """
                await self.email_service.send_email(
                    to=recipient_email,
                    subject=f"[OpenLMS] {title}",
                    html_content=html_body,
                )
            except Exception:
                pass  # Do not block on external email error

        return self._to_dto(saved)

    async def notify_course_students(
        self,
        course_id: UUID,
        notif_type: str,
        title: str,
        message: str,
        link: Optional[str] = None,
    ) -> int:
        if not self.enrollment_repo:
            return 0

        students = await self.enrollment_repo.list_students_by_course(course_id)
        if not students:
            return 0

        now = datetime.now(timezone.utc)
        notifications = [
            Notification(
                id=uuid4(),
                user_id=student.id,
                type=notif_type,
                title=title,
                message=message,
                link=link,
                is_read=False,
                created_at=now,
            )
            for student in students
        ]
        created_count = await self.notif_repo.create_many(notifications)

        # Send emails to students
        if self.email_service:
            emails = [s.email for s in students if s.email]
            if emails:
                html_body = f"""
                <div style="font-family: sans-serif; padding: 20px;">
                    <h2>{title}</h2>
                    <p>{message}</p>
                    {f'<p><a href="{link}">View in OpenLMS</a></p>' if link else ''}
                </div>
                """
                try:
                    await self.email_service.send_bulk_email(
                        to_list=emails,
                        subject=f"[OpenLMS] {title}",
                        html_content=html_body,
                    )
                except Exception:
                    pass

        return created_count

    def _to_dto(self, n: Notification) -> NotificationResponseDTO:
        return NotificationResponseDTO(
            id=n.id,
            user_id=n.user_id,
            type=n.type,
            title=n.title,
            message=n.message,
            is_read=n.is_read,
            link=n.link,
            created_at=n.created_at,
        )
