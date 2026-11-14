from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from app.domain.entities.user import User
from app.application.services.notification_service import NotificationService
from app.presentation.dependencies.auth import get_current_user
from app.presentation.dependencies.services import get_notification_service
from app.presentation.schemas.notification_schemas import (
    NotificationResponse, UnreadCountResponse
)

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=List[NotificationResponse])
async def list_notifications(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service),
):
    return await notification_service.list_user_notifications(current_user.id, page, per_page)


@router.get("/unread-count", response_model=UnreadCountResponse)
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service),
):
    count = await notification_service.get_unread_count(current_user.id)
    return UnreadCountResponse(unread_count=count)


@router.patch("/{id}/read")
async def mark_notification_read(
    id: UUID,
    current_user: User = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service),
):
    success = await notification_service.mark_as_read(id, current_user.id)
    return {"success": success}


@router.patch("/read-all")
async def mark_all_notifications_read(
    current_user: User = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service),
):
    count = await notification_service.mark_all_as_read(current_user.id)
    return {"marked_read_count": count}
