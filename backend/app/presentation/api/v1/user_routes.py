from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from app.domain.entities.user import User
from app.application.services.user_service import UserService
from app.application.dtos.user_dtos import CreateUserDTO, UpdateUserDTO
from app.presentation.dependencies.auth import require_admin
from app.presentation.dependencies.services import get_user_service
from app.presentation.schemas.user_schemas import (
    UserResponse, CreateUserRequest, UpdateUserRequest, BulkImportResponse
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=dict)
async def list_users(
    role: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    user_service: UserService = Depends(get_user_service),
    admin: User = Depends(require_admin),
):
    users, total = await user_service.list_users(role, search, page, per_page)
    total_pages = (total + per_page - 1) // per_page if total > 0 else 1
    return {
        "data": [u.__dict__ for u in users],
        "meta": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": total_pages,
        },
    }


@router.post("", response_model=UserResponse)
async def create_user(
    req: CreateUserRequest,
    user_service: UserService = Depends(get_user_service),
    admin: User = Depends(require_admin),
):
    dto = CreateUserDTO(
        email=req.email,
        full_name=req.full_name,
        role=req.role,
        student_id=req.student_id,
        avatar_url=req.avatar_url,
    )
    user = await user_service.create_user(dto)
    return user


@router.get("/{id}", response_model=UserResponse)
async def get_user(
    id: UUID,
    user_service: UserService = Depends(get_user_service),
    admin: User = Depends(require_admin),
):
    user = await user_service.get_user_by_id(id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{id}", response_model=UserResponse)
async def update_user(
    id: UUID,
    req: UpdateUserRequest,
    user_service: UserService = Depends(get_user_service),
    admin: User = Depends(require_admin),
):
    dto = UpdateUserDTO(
        full_name=req.full_name,
        role=req.role,
        student_id=req.student_id,
        avatar_url=req.avatar_url,
    )
    user = await user_service.update_user(id, dto)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/{id}")
async def delete_user(
    id: UUID,
    user_service: UserService = Depends(get_user_service),
    admin: User = Depends(require_admin),
):
    success = await user_service.delete_user(id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}


@router.post("/bulk-import", response_model=BulkImportResponse)
async def bulk_import_users(
    file: UploadFile = File(...),
    user_service: UserService = Depends(get_user_service),
    admin: User = Depends(require_admin),
):
    content = await file.read()
    try:
        csv_str = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Invalid CSV encoding, expected UTF-8")

    result = await user_service.bulk_import_csv(csv_str)
    return BulkImportResponse(
        imported_count=result.imported_count,
        errors=result.errors,
    )
