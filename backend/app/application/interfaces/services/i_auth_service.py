from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from uuid import UUID


class IAuthService(ABC):
    @abstractmethod
    def create_access_token(self, user_id: UUID, email: str, role: str) -> str:
        pass

    @abstractmethod
    def create_refresh_token(self) -> str:
        pass

    @abstractmethod
    def hash_token(self, token: str) -> str:
        pass

    @abstractmethod
    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        pass
