import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.infrastructure.database.connection import Base, GUID


class EnrollmentModel(Base):
    __tablename__ = "enrollments"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    course_id = Column(GUID, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    method = Column(String(50), default="pool", nullable=False)  # pool | invite
    enrolled_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "course_id", name="uq_user_course_enrollment"),
    )

    user = relationship("UserModel", foreign_keys=[user_id])
    course = relationship("CourseModel", foreign_keys=[course_id])
