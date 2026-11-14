from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from app.domain.entities.user import User
from app.application.services.module_service import ModuleService
from app.application.dtos.module_dtos import CreateModuleDTO, UpdateModuleDTO
from app.presentation.dependencies.auth import get_current_user, require_teacher
from app.presentation.dependencies.services import get_module_service
from app.presentation.schemas.module_schemas import (
    ModuleResponse, CreateModuleRequest, UpdateModuleRequest,
    ReorderModuleRequest, FileResourceResponse
)

router = APIRouter(tags=["Modules"])


@router.post("/courses/{course_id}/modules", response_model=ModuleResponse)
async def create_module(
    course_id: UUID,
    req: CreateModuleRequest,
    current_user: User = Depends(require_teacher),
    module_service: ModuleService = Depends(get_module_service),
):
    dto = CreateModuleDTO(
        title=req.title,
        description=req.description,
        sort_order=req.sort_order,
    )
    return await module_service.create_module(course_id, dto, current_user)


@router.get("/courses/{course_id}/modules", response_model=List[ModuleResponse])
async def list_course_modules(
    course_id: UUID,
    current_user: User = Depends(get_current_user),
    module_service: ModuleService = Depends(get_module_service),
):
    return await module_service.list_modules(course_id)


@router.put("/modules/{id}", response_model=ModuleResponse)
async def update_module(
    id: UUID,
    req: UpdateModuleRequest,
    current_user: User = Depends(require_teacher),
    module_service: ModuleService = Depends(get_module_service),
):
    dto = UpdateModuleDTO(
        title=req.title,
        description=req.description,
        sort_order=req.sort_order,
    )
    module = await module_service.update_module(id, dto, current_user)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    return module


@router.delete("/modules/{id}")
async def delete_module(
    id: UUID,
    current_user: User = Depends(require_teacher),
    module_service: ModuleService = Depends(get_module_service),
):
    deleted = await module_service.delete_module(id, current_user)
    if not deleted:
        raise HTTPException(status_code=404, detail="Module not found")
    return {"message": "Module deleted successfully"}


@router.patch("/modules/{id}/reorder")
async def reorder_module(
    id: UUID,
    req: ReorderModuleRequest,
    current_user: User = Depends(require_teacher),
    module_service: ModuleService = Depends(get_module_service),
):
    success = await module_service.reorder_module(id, req.sort_order, current_user)
    if not success:
        raise HTTPException(status_code=404, detail="Module not found")
    return {"message": "Module sort order updated"}


@router.post("/modules/{id}/files", response_model=FileResourceResponse)
async def upload_module_file(
    id: UUID,
    file: UploadFile = File(...),
    current_user: User = Depends(require_teacher),
    module_service: ModuleService = Depends(get_module_service),
):
    content = await file.read()
    content_type = file.content_type or "application/octet-stream"
    return await module_service.add_file_resource(
        module_id=id,
        file_bytes=content,
        file_name=file.filename or "file",
        content_type=content_type,
        user=current_user,
    )
