from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from app.config import settings
from app.domain.entities.user import User
from app.application.services.course_service import CourseService
from app.presentation.dependencies.auth import require_admin
from app.presentation.dependencies.services import get_course_service
from app.presentation.schemas.admin_schemas import (
    SystemSettingsResponse, UpdateSystemSettingsRequest, PublicAppSettingsResponse,
)
from app.presentation.schemas.course_schemas import CourseResponse
from app.infrastructure.database.connection import get_db
from app.infrastructure.database.models.system_setting_model import SystemSettingModel

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/settings", response_model=SystemSettingsResponse)
async def get_system_settings(
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    values = await _read_settings(db)
    return SystemSettingsResponse(
        app_name=values.get("app_name", settings.app_name),
        app_logo_url=values.get("app_logo_url") or None,
        app_env=settings.app_env,
        support_email=values.get("support_email", settings.support_email),
        maintenance_mode=values.get("maintenance_mode", str(settings.maintenance_mode)).lower() == "true",
        allowed_origins=settings.allowed_origins,
        max_file_size_mb=settings.max_file_size_mb,
        staff_access_code=values.get("staff_access_code", settings.staff_access_code),
    )


@router.get("/settings/public", response_model=PublicAppSettingsResponse)
async def get_public_app_settings(db: AsyncSession = Depends(get_db)):
    values = await _read_settings(db)
    return PublicAppSettingsResponse(
        app_name=values.get("app_name", settings.app_name),
        app_logo_url=values.get("app_logo_url") or None,
    )


@router.put("/settings", response_model=SystemSettingsResponse)
async def update_system_settings(
    req: UpdateSystemSettingsRequest,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    updates = {
        "app_name": req.app_name,
        "app_logo_url": req.app_logo_url,
        "support_email": str(req.support_email) if req.support_email is not None else None,
        "maintenance_mode": str(req.maintenance_mode).lower() if req.maintenance_mode is not None else None,
        "staff_access_code": req.staff_access_code if req.staff_access_code is not None else None,
    }
    for key, value in updates.items():
        if value is None:
            continue
        record = await db.get(SystemSettingModel, key)
        if record:
            record.value = value
            record.updated_at = datetime.now(timezone.utc)
        else:
            db.add(SystemSettingModel(key=key, value=value))

    if req.app_name is not None:
        settings.app_name = req.app_name
    if req.app_logo_url is not None:
        settings.app_logo_url = req.app_logo_url or None
    if req.support_email is not None:
        settings.support_email = str(req.support_email)
    if req.maintenance_mode is not None:
        settings.maintenance_mode = req.maintenance_mode
    if req.staff_access_code is not None:
        settings.staff_access_code = req.staff_access_code

    return SystemSettingsResponse(
        app_name=settings.app_name,
        app_logo_url=settings.app_logo_url,
        app_env=settings.app_env,
        support_email=settings.support_email,
        maintenance_mode=settings.maintenance_mode,
        allowed_origins=settings.allowed_origins,
        max_file_size_mb=settings.max_file_size_mb,
        staff_access_code=settings.staff_access_code,
    )


async def _read_settings(db: AsyncSession) -> dict[str, str]:
    rows = (await db.execute(select(SystemSettingModel))).scalars().all()
    return {row.key: row.value for row in rows}


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
