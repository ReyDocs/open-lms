from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class FileResource:
    id: UUID
    module_id: UUID
    uploaded_by: UUID
    file_url: str
    file_name: str
    file_type: str
    file_size: int
    uploaded_at: datetime
