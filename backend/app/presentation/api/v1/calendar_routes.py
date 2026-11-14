from typing import List, Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from app.domain.entities.user import User
from app.application.services.calendar_service import CalendarService
from app.application.dtos.calendar_dtos import CreateCalendarEventDTO, UpdateCalendarEventDTO
from app.presentation.dependencies.auth import get_current_user, require_teacher, ensure_course_access
from app.presentation.dependencies.services import get_calendar_service, get_course_repo, get_enrollment_repo
from app.application.interfaces.repositories.i_course_repository import ICourseRepository
from app.application.interfaces.repositories.i_enrollment_repository import IEnrollmentRepository
from app.presentation.schemas.calendar_schemas import (
    CalendarEventResponse, CreateCalendarEventRequest, UpdateCalendarEventRequest
)

router = APIRouter(tags=["Calendar"])


@router.get("/courses/{id}/calendar", response_model=List[CalendarEventResponse])
async def get_course_calendar(
    id: UUID,
    current_user: User = Depends(get_current_user),
    calendar_service: CalendarService = Depends(get_calendar_service),
    course_repo: ICourseRepository = Depends(get_course_repo),
    enrollment_repo: IEnrollmentRepository = Depends(get_enrollment_repo),
):
    await ensure_course_access(id, current_user, course_repo, enrollment_repo)
    return await calendar_service.get_course_calendar(id)


@router.post("/courses/{id}/calendar", response_model=CalendarEventResponse)
async def create_course_event(
    id: UUID,
    req: CreateCalendarEventRequest,
    current_user: User = Depends(require_teacher),
    calendar_service: CalendarService = Depends(get_calendar_service),
):
    dto = CreateCalendarEventDTO(
        course_id=id,
        title=req.title,
        event_datetime=req.event_datetime,
        description=req.description,
    )
    return await calendar_service.create_manual_event(dto, current_user)


@router.get("/calendar", response_model=List[CalendarEventResponse])
async def get_aggregated_calendar(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user),
    calendar_service: CalendarService = Depends(get_calendar_service),
):
    return await calendar_service.get_aggregated_calendar(current_user.id, start_date, end_date)


@router.put("/calendar/{id}", response_model=CalendarEventResponse)
async def update_calendar_event(
    id: UUID,
    req: UpdateCalendarEventRequest,
    current_user: User = Depends(require_teacher),
    calendar_service: CalendarService = Depends(get_calendar_service),
):
    dto = UpdateCalendarEventDTO(
        title=req.title,
        event_datetime=req.event_datetime,
        description=req.description,
    )
    event = await calendar_service.update_event(id, dto, current_user)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.delete("/calendar/{id}")
async def delete_calendar_event(
    id: UUID,
    current_user: User = Depends(require_teacher),
    calendar_service: CalendarService = Depends(get_calendar_service),
):
    deleted = await calendar_service.delete_event(id, current_user)
    if not deleted:
        raise HTTPException(status_code=404, detail="Event not found")
    return {"message": "Event deleted successfully"}
