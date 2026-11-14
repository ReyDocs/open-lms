from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime, timezone

from app.application.interfaces.repositories.i_module_repository import IModuleRepository
from app.application.interfaces.repositories.i_course_repository import ICourseRepository
from app.application.interfaces.services.i_storage_service import IStorageService
from app.application.dtos.module_dtos import (
    CreateModuleDTO, UpdateModuleDTO, ModuleResponseDTO, FileResourceDTO
)
from app.domain.entities.module import Module
from app.domain.entities.file_resource import FileResource
from app.domain.entities.user import User


class ModuleService:
    def __init__(
        self,
        module_repo: IModuleRepository,
        course_repo: ICourseRepository,
        storage_service: Optional[IStorageService] = None,
    ):
        self.module_repo = module_repo
        self.course_repo = course_repo
        self.storage_service = storage_service

    async def get_module_by_id(self, module_id: UUID) -> Optional[ModuleResponseDTO]:
        module = await self.module_repo.get_by_id(module_id)
        if not module:
            return None
        resources = await self.module_repo.get_file_resources(module.id)
        return self._to_dto(module, resources)

    async def create_module(
        self, course_id: UUID, dto: CreateModuleDTO, user: User
    ) -> ModuleResponseDTO:
        course = await self.course_repo.get_by_id(course_id)
        if not course:
            raise ValueError("Course not found")
        if not user.is_admin() and course.teacher_id != user.id:
            raise PermissionError("Only the course teacher can create modules")

        now = datetime.now(timezone.utc)
        module = Module(
            id=uuid4(),
            title=dto.title.strip(),
            course_id=course_id,
            description=dto.description.strip() if dto.description else None,
            sort_order=dto.sort_order,
            created_at=now,
        )
        saved = await self.module_repo.create(module)
        return self._to_dto(saved, [])

    async def update_module(
        self, module_id: UUID, dto: UpdateModuleDTO, user: User
    ) -> Optional[ModuleResponseDTO]:
        module = await self.module_repo.get_by_id(module_id)
        if not module:
            return None
        course = await self.course_repo.get_by_id(module.course_id)
        if not course or (not user.is_admin() and course.teacher_id != user.id):
            raise PermissionError("Access denied")

        if dto.title is not None:
            module.title = dto.title.strip()
        if dto.description is not None:
            module.description = dto.description.strip()
        if dto.sort_order is not None:
            module.sort_order = dto.sort_order

        updated = await self.module_repo.update(module)
        resources = await self.module_repo.get_file_resources(updated.id)
        return self._to_dto(updated, resources)

    async def delete_module(self, module_id: UUID, user: User) -> bool:
        module = await self.module_repo.get_by_id(module_id)
        if not module:
            return False
        course = await self.course_repo.get_by_id(module.course_id)
        if not course or (not user.is_admin() and course.teacher_id != user.id):
            raise PermissionError("Access denied")

        return await self.module_repo.delete(module_id)

    async def reorder_module(self, module_id: UUID, new_sort_order: int, user: User) -> bool:
        module = await self.module_repo.get_by_id(module_id)
        if not module:
            return False
        course = await self.course_repo.get_by_id(module.course_id)
        if not course or (not user.is_admin() and course.teacher_id != user.id):
            raise PermissionError("Access denied")

        return await self.module_repo.update_sort_order(module_id, new_sort_order)

    async def list_modules(self, course_id: UUID) -> List[ModuleResponseDTO]:
        modules = await self.module_repo.list_by_course(course_id)
        dtos: List[ModuleResponseDTO] = []
        for m in modules:
            res = await self.module_repo.get_file_resources(m.id)
            dtos.append(self._to_dto(m, res))
        return dtos

    async def add_file_resource(
        self,
        module_id: UUID,
        file_bytes: bytes,
        file_name: str,
        content_type: str,
        user: User,
    ) -> FileResourceDTO:
        module = await self.module_repo.get_by_id(module_id)
        if not module:
            raise ValueError("Module not found")
        course = await self.course_repo.get_by_id(module.course_id)
        if not course or (not user.is_admin() and course.teacher_id != user.id):
            raise PermissionError("Access denied")

        if not self.storage_service:
            raise RuntimeError("Storage service is unavailable")

        file_url = await self.storage_service.upload_file(
            file_bytes=file_bytes,
            filename=file_name,
            content_type=content_type,
            bucket="resources",
        )

        now = datetime.now(timezone.utc)
        ext = file_name.split(".")[-1].lower() if "." in file_name else "bin"
        resource = FileResource(
            id=uuid4(),
            module_id=module_id,
            uploaded_by=user.id,
            file_url=file_url,
            file_name=file_name,
            file_type=ext,
            file_size=len(file_bytes),
            uploaded_at=now,
        )
        saved = await self.module_repo.add_file_resource(resource)
        return FileResourceDTO(
            id=saved.id,
            module_id=saved.module_id,
            uploaded_by=saved.uploaded_by,
            file_url=saved.file_url,
            file_name=saved.file_name,
            file_type=saved.file_type,
            file_size=saved.file_size,
            uploaded_at=saved.uploaded_at,
        )

    def _to_dto(self, module: Module, resources: List[FileResource]) -> ModuleResponseDTO:
        res_dtos = [
            FileResourceDTO(
                id=r.id,
                module_id=r.module_id,
                uploaded_by=r.uploaded_by,
                file_url=r.file_url,
                file_name=r.file_name,
                file_type=r.file_type,
                file_size=r.file_size,
                uploaded_at=r.uploaded_at,
            )
            for r in resources
        ]
        return ModuleResponseDTO(
            id=module.id,
            title=module.title,
            course_id=module.course_id,
            description=module.description,
            sort_order=module.sort_order,
            created_at=module.created_at,
            resources=res_dtos,
        )
