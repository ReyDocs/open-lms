import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.infrastructure.database.connection import Base, GUID


class AssignmentModel(Base):
    __tablename__ = "assignments"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    total_points = Column(Integer, nullable=False)
    status = Column(String(50), default="draft", nullable=False)  # draft | published
    due_date = Column(DateTime(timezone=True), nullable=False)
    module_id = Column(GUID, ForeignKey("modules.id", ondelete="CASCADE"), nullable=False, index=True)
    course_id = Column(GUID, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    module = relationship("ModuleModel", foreign_keys=[module_id])
    course = relationship("CourseModel", foreign_keys=[course_id])
