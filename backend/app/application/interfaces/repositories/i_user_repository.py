from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from uuid import UUID
from app.domain.entities.user import User


class IUserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    async def get_by_google_id(self, google_id: str) -> Optional[User]:
        pass

    @abstractmethod
    async def create(self, user: User) -> User:
        pass

    @abstractmethod
    async def update(self, user: User) -> User:
        pass

    @abstractmethod
    async def delete(self, user_id: UUID) -> bool:
        pass

    @abstractmethod
    async def list_users(
        self, role: Optional[str] = None, search: Optional[str] = None, page: int = 1, per_page: int = 20
    ) -> Tuple[List[User], int]:
        pass

    @abstractmethod
    async def bulk_create_or_update(self, users: List[User]) -> int:
        pass
