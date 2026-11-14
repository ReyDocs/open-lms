import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime
from app.infrastructure.database.connection import Base, GUID


class UserModel(Base):
    __tablename__ = "users"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    avatar_url = Column(String(1024), nullable=True)
    role = Column(String(50), nullable=False, default="student")  # admin, teacher, student
    student_id = Column(String(100), nullable=True, index=True)
    google_id = Column(String(255), unique=True, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
