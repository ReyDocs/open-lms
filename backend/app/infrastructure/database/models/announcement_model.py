import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.infrastructure.database.connection import Base, GUID


class AnnouncementModel(Base):
    __tablename__ = "announcements"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    course_id = Column(GUID, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    author_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)  # rich text HTML sanitized
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    course = relationship("CourseModel", foreign_keys=[course_id])
    author = relationship("UserModel", foreign_keys=[author_id])
    attachments = relationship("AnnouncementAttachmentModel", back_populates="announcement", cascade="all, delete-orphan")


class AnnouncementAttachmentModel(Base):
    __tablename__ = "announcement_attachments"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    announcement_id = Column(GUID, ForeignKey("announcements.id", ondelete="CASCADE"), nullable=False, index=True)
    file_url = Column(String(1024), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)

    announcement = relationship("AnnouncementModel", back_populates="attachments")
