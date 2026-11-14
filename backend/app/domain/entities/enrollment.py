from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class Enrollment:
    id: UUID
    user_id: UUID
    course_id: UUID
    method: str  # pool | invite
    enrolled_at: datetime
