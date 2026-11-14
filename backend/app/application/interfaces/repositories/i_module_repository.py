from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from app.domain.entities.module import Module
from app.domain.entities.file_resource import FileResource


class IModuleRepository(ABC):
    @abstractmethod
    async def get_by_id(self, module_id: UUID) -> Optional[Module]:
        pass

    @abstractmethod
    async def create(self, module: Module) -> Module:
        pass

    @abstractmethod
    async def update(self, module: Module) -> Module:
        pass

    @abstractmethod
    async def delete(self, module_id: UUID) -> bool:
        pass

    @abstractmethod
    async def list_by_course(self, course_id: UUID) -> List[Module]:
        pass

    @abstractmethod
    async def update_sort_order(self, module_id: UUID, sort_order: int) -> bool:
        pass

    @abstractmethod
    async def add_file_resource(self, resource: FileResource) -> FileResource:
        pass

    @abstractmethod
    async def get_file_resources(self, module_id: UUID) -> List[FileResource]:
        pass
