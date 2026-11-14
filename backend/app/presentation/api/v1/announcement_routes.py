from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from app.domain.entities.user import User
from app.application.services.announcement_service import AnnouncementService
from app.application.dtos.announcement_dtos import (
    CreateAnnouncementDTO, UpdateAnnouncementDTO, AttachmentInputDTO
)
from app.presentation.dependencies.auth import get_current_user, require_teacher, ensure_course_access
from app.presentation.dependencies.services import get_announcement_service, get_storage_service, get_course_repo, get_enrollment_repo
from app.infrastructure.external.supabase_storage_service import SupabaseStorageService
from app.infrastructure.repositories.sqlalchemy_course_repo import SQLAlchemyCourseRepository
from app.infrastructure.repositories.sqlalchemy_enrollment_repo import SQLAlchemyEnrollmentRepository
from app.domain.value_objects.file_type import FileType, MAX_FILE_SIZE_BYTES
from app.presentation.schemas.announcement_schemas import (
    AnnouncementResponse, CreateAnnouncementRequest, UpdateAnnouncementRequest
)

router = APIRouter(tags=["Announcements"])


@router.post("/courses/{course_id}/announcements/attachments")
async def upload_announcement_attachment(
    course_id: UUID,
    file: UploadFile = File(...),
    current_user: User = Depends(require_teacher),
    storage_service: SupabaseStorageService = Depends(get_storage_service),
    course_repo: SQLAlchemyCourseRepository = Depends(get_course_repo),
):
    course = await course_repo.get_by_id(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if not current_user.is_admin() and course.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the course teacher can upload announcement attachments")

    file_name = (file.filename or "attachment").replace("\\", "/").rsplit("/", 1)[-1]
    if not file_name:
        raise HTTPException(status_code=400, detail="A file name is required")
    if not FileType(file_name).is_allowed():
        raise HTTPException(status_code=415, detail="File type is not allowed")

    chunks = []
    total_size = 0
    while True:
        chunk = await file.read(min(1024 * 1024, MAX_FILE_SIZE_BYTES + 1 - total_size))
        if not chunk:
            break
        total_size += len(chunk)
        if total_size > MAX_FILE_SIZE_BYTES:
            await file.close()
            raise HTTPException(status_code=413, detail="File exceeds maximum allowed size of 25MB")
        chunks.append(chunk)
    await file.close()

    file_url = await storage_service.upload_file(
        file_bytes=b"".join(chunks),
        filename=file_name,
        content_type=file.content_type or "application/octet-stream",
        bucket="announcements",
    )
    return {"file_url": file_url, "file_name": file_name, "file_size": total_size}


@router.post("/courses/{course_id}/announcements", response_model=AnnouncementResponse)
async def create_announcement(
    course_id: UUID,
    req: CreateAnnouncementRequest,
    current_user: User = Depends(require_teacher),
    announcement_service: AnnouncementService = Depends(get_announcement_service),
):
    attachments = (
        [
            AttachmentInputDTO(file_url=att.file_url, file_name=att.file_name, file_size=att.file_size)
            for att in req.attachments
        ]
        if req.attachments
        else []
    )
    dto = CreateAnnouncementDTO(
        title=req.title,
        content=req.content,
        attachments=attachments,
    )
    return await announcement_service.create_announcement(course_id, dto, current_user)


@router.get("/courses/{course_id}/announcements", response_model=List[AnnouncementResponse])
async def list_course_announcements(
    course_id: UUID,
    current_user: User = Depends(get_current_user),
    announcement_service: AnnouncementService = Depends(get_announcement_service),
    course_repo: SQLAlchemyCourseRepository = Depends(get_course_repo),
    enrollment_repo: SQLAlchemyEnrollmentRepository = Depends(get_enrollment_repo),
):
    await ensure_course_access(course_id, current_user, course_repo, enrollment_repo)
    return await announcement_service.list_announcements(course_id)


@router.get("/announcements/recent", response_model=List[AnnouncementResponse])
async def list_recent_announcements(
    limit: int = Query(5, ge=1, le=20),
    current_user: User = Depends(get_current_user),
    announcement_service: AnnouncementService = Depends(get_announcement_service),
):
    return await announcement_service.list_recent_announcements(current_user.id, limit)


@router.get("/announcements/{id}", response_model=AnnouncementResponse)
async def get_announcement(
    id: UUID,
    current_user: User = Depends(get_current_user),
    announcement_service: AnnouncementService = Depends(get_announcement_service),
    course_repo: SQLAlchemyCourseRepository = Depends(get_course_repo),
    enrollment_repo: SQLAlchemyEnrollmentRepository = Depends(get_enrollment_repo),
):
    ann = await announcement_service.get_announcement_by_id(id)
    if not ann:
        raise HTTPException(status_code=404, detail="Announcement not found")
    await ensure_course_access(ann.course_id, current_user, course_repo, enrollment_repo)
    return ann


@router.put("/announcements/{id}", response_model=AnnouncementResponse)
async def update_announcement(
    id: UUID,
    req: UpdateAnnouncementRequest,
    current_user: User = Depends(require_teacher),
    announcement_service: AnnouncementService = Depends(get_announcement_service),
):
    dto = UpdateAnnouncementDTO(title=req.title, content=req.content)
    ann = await announcement_service.update_announcement(id, dto, current_user)
    if not ann:
        raise HTTPException(status_code=404, detail="Announcement not found")
    return ann


@router.delete("/announcements/{id}")
async def delete_announcement(
    id: UUID,
    current_user: User = Depends(require_teacher),
    announcement_service: AnnouncementService = Depends(get_announcement_service),
):
    deleted = await announcement_service.delete_announcement(id, current_user)
    if not deleted:
        raise HTTPException(status_code=404, detail="Announcement not found")
    return {"message": "Announcement deleted successfully"}
