from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from app.domain.entities.notification import Notification


class INotificationRepository(ABC):
    @abstractmethod
    async def get_by_id(self, notification_id: UUID) -> Optional[Notification]:
        pass

    @abstractmethod
    async def create(self, notification: Notification) -> Notification:
        pass

    @abstractmethod
    async def create_many(self, notifications: List[Notification]) -> int:
        pass

    @abstractmethod
    async def list_by_user(self, user_id: UUID, page: int = 1, per_page: int = 20) -> List[Notification]:
        pass

    @abstractmethod
    async def mark_as_read(self, notification_id: UUID, user_id: UUID) -> bool:
        pass

    @abstractmethod
    async def mark_all_as_read(self, user_id: UUID) -> int:
        pass

    @abstractmethod
    async def get_unread_count(self, user_id: UUID) -> int:
        pass
