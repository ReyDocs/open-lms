from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class Module:
    id: UUID
    title: str
    course_id: UUID
    sort_order: int = 0
    description: Optional[str] = None
    created_at: Optional[datetime] = None
