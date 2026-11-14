from typing import List
from fastapi import APIRouter, Depends, Query
from app.config import settings
from app.domain.entities.user import User
from app.application.services.course_service import CourseService
from app.presentation.dependencies.auth import require_admin
from app.presentation.dependencies.services import get_course_service
from app.presentation.schemas.admin_schemas import SystemSettingsResponse, UpdateSystemSettingsRequest
from app.presentation.schemas.course_schemas import CourseResponse

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/settings", response_model=SystemSettingsResponse)
async def get_system_settings(admin: User = Depends(require_admin)):
    return SystemSettingsResponse(
        app_name=settings.app_name,
        app_env=settings.app_env,
        support_email=settings.support_email,
        maintenance_mode=settings.maintenance_mode,
        allowed_origins=settings.allowed_origins,
        max_file_size_mb=settings.max_file_size_mb,
    )


@router.put("/settings", response_model=SystemSettingsResponse)
async def update_system_settings(
    req: UpdateSystemSettingsRequest,
    admin: User = Depends(require_admin),
):
    if req.app_name is not None:
        settings.app_name = req.app_name
    if req.support_email is not None:
        settings.support_email = req.support_email
    if req.maintenance_mode is not None:
        settings.maintenance_mode = req.maintenance_mode

    return SystemSettingsResponse(
        app_name=settings.app_name,
        app_env=settings.app_env,
        support_email=settings.support_email,
        maintenance_mode=settings.maintenance_mode,
        allowed_origins=settings.allowed_origins,
        max_file_size_mb=settings.max_file_size_mb,
    )


@router.get("/courses", response_model=dict)
async def get_all_courses(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    admin: User = Depends(require_admin),
    course_service: CourseService = Depends(get_course_service),
):
    courses, total = await course_service.list_all_courses(page, per_page)
    total_pages = (total + per_page - 1) // per_page if total > 0 else 1
    return {
        "data": [c.__dict__ for c in courses],
        "meta": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": total_pages,
        },
    }
