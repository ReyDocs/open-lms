from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from app.domain.entities.user import User
from app.application.services.announcement_service import AnnouncementService
from app.application.dtos.announcement_dtos import (
    CreateAnnouncementDTO, UpdateAnnouncementDTO, AttachmentInputDTO
)
from app.presentation.dependencies.auth import get_current_user, require_teacher
from app.presentation.dependencies.services import get_announcement_service
from app.presentation.schemas.announcement_schemas import (
    AnnouncementResponse, CreateAnnouncementRequest, UpdateAnnouncementRequest
)

router = APIRouter(tags=["Announcements"])


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
):
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
):
    ann = await announcement_service.get_announcement_by_id(id)
    if not ann:
        raise HTTPException(status_code=404, detail="Announcement not found")
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
