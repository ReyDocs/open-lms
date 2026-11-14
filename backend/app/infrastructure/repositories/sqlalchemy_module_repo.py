from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.application.interfaces.repositories.i_module_repository import IModuleRepository
from app.domain.entities.module import Module
from app.domain.entities.file_resource import FileResource
from app.infrastructure.database.models.module_model import ModuleModel
from app.infrastructure.database.models.file_resource_model import FileResourceModel


class SQLAlchemyModuleRepository(IModuleRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, module_id: UUID) -> Optional[Module]:
        stmt = select(ModuleModel).where(ModuleModel.id == module_id)
        res = await self.session.execute(stmt)
        model = res.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def create(self, module: Module) -> Module:
        model = ModuleModel(
            id=module.id,
            title=module.title,
            description=module.description,
            sort_order=module.sort_order,
            course_id=module.course_id,
            created_at=module.created_at,
        )
        self.session.add(model)
        await self.session.flush()
        return self._to_entity(model)

    async def update(self, module: Module) -> Module:
        stmt = select(ModuleModel).where(ModuleModel.id == module.id)
        res = await self.session.execute(stmt)
        model = res.scalar_one_or_none()
        if not model:
            raise ValueError(f"Module {module.id} not found")

        model.title = module.title
        model.description = module.description
        model.sort_order = module.sort_order
        await self.session.flush()
        return self._to_entity(model)

    async def delete(self, module_id: UUID) -> bool:
        stmt = delete(ModuleModel).where(ModuleModel.id == module_id)
        res = await self.session.execute(stmt)
        await self.session.flush()
        return res.rowcount > 0

    async def list_by_course(self, course_id: UUID) -> List[Module]:
        stmt = (
            select(ModuleModel)
            .where(ModuleModel.course_id == course_id)
            .order_by(ModuleModel.sort_order.asc(), ModuleModel.created_at.asc())
        )
        models = (await self.session.execute(stmt)).scalars().all()
        return [self._to_entity(m) for m in models]

    async def update_sort_order(self, module_id: UUID, sort_order: int) -> bool:
        stmt = select(ModuleModel).where(ModuleModel.id == module_id)
        res = await self.session.execute(stmt)
        model = res.scalar_one_or_none()
        if not model:
            return False
        model.sort_order = sort_order
        await self.session.flush()
        return True

    async def add_file_resource(self, resource: FileResource) -> FileResource:
        model = FileResourceModel(
            id=resource.id,
            module_id=resource.module_id,
            uploaded_by=resource.uploaded_by,
            file_url=resource.file_url,
            file_name=resource.file_name,
            file_type=resource.file_type,
            file_size=resource.file_size,
            uploaded_at=resource.uploaded_at,
        )
        self.session.add(model)
        await self.session.flush()
        return FileResource(
            id=model.id,
            module_id=model.module_id,
            uploaded_by=model.uploaded_by,
            file_url=model.file_url,
            file_name=model.file_name,
            file_type=model.file_type,
            file_size=model.file_size,
            uploaded_at=model.uploaded_at,
        )

    async def get_file_resources(self, module_id: UUID) -> List[FileResource]:
        stmt = (
            select(FileResourceModel)
            .where(FileResourceModel.module_id == module_id)
            .order_by(FileResourceModel.uploaded_at.asc())
        )
        models = (await self.session.execute(stmt)).scalars().all()
        return [
            FileResource(
                id=m.id,
                module_id=m.module_id,
                uploaded_by=m.uploaded_by,
                file_url=m.file_url,
                file_name=m.file_name,
                file_type=m.file_type,
                file_size=m.file_size,
                uploaded_at=m.uploaded_at,
            )
            for m in models
        ]

    def _to_entity(self, m: ModuleModel) -> Module:
        return Module(
            id=m.id,
            title=m.title,
            course_id=m.course_id,
            description=m.description,
            sort_order=m.sort_order,
            created_at=m.created_at,
        )
