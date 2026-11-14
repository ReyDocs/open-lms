import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey
from app.infrastructure.database.connection import Base, GUID


class AssignmentReminderModel(Base):
    __tablename__ = "assignment_reminders"

    assignment_id = Column(
        GUID,
        ForeignKey("assignments.id", ondelete="CASCADE"),
        primary_key=True,
        default=uuid.uuid4,
    )
    sent_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
