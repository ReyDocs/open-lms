from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


class FileResourceResponse(BaseModel):
    id: UUID
    module_id: UUID
    uploaded_by: UUID
    file_url: str
    file_name: str
    file_type: str
    file_size: int
    uploaded_at: datetime


class ModuleResponse(BaseModel):
    id: UUID
    title: str
    course_id: UUID
    description: Optional[str] = None
    sort_order: int = 0
    created_at: Optional[datetime] = None
    resources: Optional[List[FileResourceResponse]] = []


class CreateModuleRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    sort_order: int = 0


class UpdateModuleRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    sort_order: Optional[int] = None


class ReorderModuleRequest(BaseModel):
    sort_order: int
