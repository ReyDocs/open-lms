import logging
from html import escape
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.infrastructure.database.connection import AsyncSessionLocal
from app.infrastructure.database.models.assignment_model import AssignmentModel
from app.infrastructure.database.models.assignment_reminder_model import AssignmentReminderModel
from app.infrastructure.database.models.course_model import CourseModel
from app.infrastructure.database.models.enrollment_model import EnrollmentModel
from app.infrastructure.database.models.notification_model import NotificationModel
from app.infrastructure.database.models.user_model import UserModel
from app.infrastructure.external.resend_email_service import ResendEmailService

logger = logging.getLogger(__name__)


async def send_due_date_reminders() -> None:
    """Send the one-day reminder once per published assignment."""
    now = datetime.now(timezone.utc)
    # The job runs every five minutes; this ten-minute window catches each due
    # time once while keeping the reminder close to 24 hours in advance.
    start = now + timedelta(hours=23, minutes=55)
    end = now + timedelta(hours=24, minutes=5)
    email_batches: list[tuple[str, str, str, list[str]]] = []

    async with AsyncSessionLocal() as session:
        sent_assignment_ids = select(AssignmentReminderModel.assignment_id)
        assignments = (
            await session.execute(
                select(AssignmentModel)
                .where(
                    AssignmentModel.status == "published",
                    AssignmentModel.due_date >= start,
                    AssignmentModel.due_date < end,
                    ~AssignmentModel.id.in_(sent_assignment_ids),
                )
            )
        ).scalars().all()

        for assignment in assignments:
            course = await session.get(CourseModel, assignment.course_id)
            recipients = (
                await session.execute(
                    select(UserModel).join(
                        EnrollmentModel, EnrollmentModel.user_id == UserModel.id
                    ).where(EnrollmentModel.course_id == assignment.course_id)
                )
            ).scalars().all()
            title = f"Assignment due tomorrow: {assignment.title}"
            message = f"{assignment.title} in {course.title if course else 'your course'} is due in about 24 hours."
            link = f"/courses/{assignment.course_id}/assignments/{assignment.id}"

            session.add(AssignmentReminderModel(assignment_id=assignment.id, sent_at=now))
            session.add_all(
                [
                    NotificationModel(
                        user_id=user.id,
                        type="reminder",
                        title=title,
                        message=message,
                        link=link,
                        is_read=False,
                        created_at=now,
                    )
                    for user in recipients
                ]
            )
            email_batches.append((title, message, link, [user.email for user in recipients if user.email]))

        await session.commit()

    email_service = ResendEmailService()
    for title, message, link, emails in email_batches:
        if not emails:
            continue
        html = (
            "<div style='font-family:sans-serif;padding:20px'>"
            f"<h2>{escape(title)}</h2><p>{escape(message)}</p>"
            f"<p><a href='{link}'>View assignment</a></p></div>"
        )
        try:
            await email_service.send_bulk_email(emails, f"[OpenLMS] {title}", html)
        except Exception:
            logger.exception("Failed to send assignment due date reminder email")
