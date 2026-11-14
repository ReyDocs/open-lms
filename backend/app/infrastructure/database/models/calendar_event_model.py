import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.infrastructure.database.connection import Base, GUID


class CalendarEventModel(Base):
    __tablename__ = "calendar_events"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    course_id = Column(GUID, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    created_by = Column(GUID, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    event_datetime = Column(DateTime(timezone=True), nullable=False)
    source = Column(String(50), default="manual", nullable=False)  # auto | manual
    assignment_id = Column(GUID, ForeignKey("assignments.id", ondelete="CASCADE"), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    course = relationship("CourseModel", foreign_keys=[course_id])
    assignment = relationship("AssignmentModel", foreign_keys=[assignment_id])
