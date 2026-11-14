import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.infrastructure.database.connection import Base, GUID


class FileResourceModel(Base):
    __tablename__ = "file_resources"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    module_id = Column(GUID, ForeignKey("modules.id", ondelete="CASCADE"), nullable=False, index=True)
    uploaded_by = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    file_url = Column(String(1024), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size = Column(Integer, nullable=False)
    uploaded_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    module = relationship("ModuleModel", foreign_keys=[module_id])
    uploader = relationship("UserModel", foreign_keys=[uploaded_by])
