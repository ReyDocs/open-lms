from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from app.domain.entities.assignment import Assignment


class IAssignmentRepository(ABC):
    @abstractmethod
    async def get_by_id(self, assignment_id: UUID) -> Optional[Assignment]:
        pass

    @abstractmethod
    async def create(self, assignment: Assignment) -> Assignment:
        pass

    @abstractmethod
    async def update(self, assignment: Assignment) -> Assignment:
        pass

    @abstractmethod
    async def delete(self, assignment_id: UUID) -> bool:
        pass

    @abstractmethod
    async def list_by_course(self, course_id: UUID, published_only: bool = False) -> List[Assignment]:
        pass

    @abstractmethod
    async def list_by_module(self, module_id: UUID, published_only: bool = False) -> List[Assignment]:
        pass

    @abstractmethod
    async def list_upcoming(self, user_id: UUID, days: int = 7) -> List[Assignment]:
        pass
