from sqlalchemy import Column, String, Text, DateTime
from datetime import datetime, timezone
from app.infrastructure.database.connection import Base


class SystemSettingModel(Base):
    __tablename__ = "system_settings"

    key = Column(String(100), primary_key=True)
    value = Column(Text, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
