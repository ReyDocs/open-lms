from dataclasses import dataclass
from typing import Optional, List
from uuid import UUID
from datetime import datetime


@dataclass
class CreateModuleDTO:
    title: str
    description: Optional[str] = None
    sort_order: int = 0


@dataclass
class UpdateModuleDTO:
    title: Optional[str] = None
    description: Optional[str] = None
    sort_order: Optional[int] = None


@dataclass
class FileResourceDTO:
    id: UUID
    module_id: UUID
    uploaded_by: UUID
    file_url: str
    file_name: str
    file_type: str
    file_size: int
    uploaded_at: datetime


@dataclass
class ModuleResponseDTO:
    id: UUID
    title: str
    course_id: UUID
    description: Optional[str] = None
    sort_order: int = 0
    created_at: Optional[datetime] = None
    resources: Optional[List[FileResourceDTO]] = None
