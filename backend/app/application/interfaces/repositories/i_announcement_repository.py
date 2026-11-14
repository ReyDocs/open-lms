from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from app.domain.entities.announcement import Announcement, AnnouncementAttachment


class IAnnouncementRepository(ABC):
    @abstractmethod
    async def get_by_id(self, announcement_id: UUID) -> Optional[Announcement]:
        pass

    @abstractmethod
    async def create(self, announcement: Announcement) -> Announcement:
        pass

    @abstractmethod
    async def update(self, announcement: Announcement) -> Announcement:
        pass

    @abstractmethod
    async def delete(self, announcement_id: UUID) -> bool:
        pass

    @abstractmethod
    async def list_by_course(self, course_id: UUID) -> List[Announcement]:
        pass

    @abstractmethod
    async def list_recent_for_user(self, user_id: UUID, limit: int = 5) -> List[Announcement]:
        pass

    @abstractmethod
    async def add_attachment(self, attachment: AnnouncementAttachment) -> AnnouncementAttachment:
        pass
