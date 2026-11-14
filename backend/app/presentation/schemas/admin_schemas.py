from typing import Optional
from pydantic import BaseModel, EmailStr


class SystemSettingsResponse(BaseModel):
    app_name: str
    app_env: str
    support_email: str
    maintenance_mode: bool
    allowed_origins: str
    max_file_size_mb: int


class UpdateSystemSettingsRequest(BaseModel):
    app_name: Optional[str] = None
    support_email: Optional[EmailStr] = None
    maintenance_mode: Optional[bool] = None
