import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.infrastructure.database.connection import Base, GUID


class SubmissionModel(Base):
    __tablename__ = "submissions"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    assignment_id = Column(GUID, ForeignKey("assignments.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    file_url = Column(String(1024), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    grade = Column(Integer, nullable=True)
    feedback = Column(Text, nullable=True)
    submitted_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    graded_at = Column(DateTime(timezone=True), nullable=True)

    assignment = relationship("AssignmentModel", foreign_keys=[assignment_id])
    student = relationship("UserModel", foreign_keys=[student_id])
