from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID
from datetime import datetime


class IRefreshTokenRepository(ABC):
    @abstractmethod
    async def create(self, user_id: UUID, token_hash: str, expires_at: datetime) -> UUID:
        pass

    @abstractmethod
    async def get_valid(self, token_hash: str) -> Optional[dict]:
        pass

    @abstractmethod
    async def revoke(self, token_hash: str) -> bool:
        pass

    @abstractmethod
    async def revoke_all_for_user(self, user_id: UUID) -> int:
        pass
