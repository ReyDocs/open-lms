from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID


@dataclass
class Assignment:
    id: UUID
    title: str
    description: str
    total_points: int
    status: str  # draft | published
    due_date: datetime
    module_id: UUID
    course_id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def is_published(self) -> bool:
        return self.status == "published"

    def is_past_due(self) -> bool:
        now = datetime.now(timezone.utc)
        due = self.due_date if self.due_date.tzinfo else self.due_date.replace(tzinfo=timezone.utc)
        return now > due
