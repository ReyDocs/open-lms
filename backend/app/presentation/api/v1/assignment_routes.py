from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from app.domain.entities.user import User
from app.application.services.assignment_service import AssignmentService
from app.application.dtos.assignment_dtos import CreateAssignmentDTO, UpdateAssignmentDTO
from app.presentation.dependencies.auth import get_current_user, require_teacher, ensure_course_access
from app.presentation.dependencies.services import get_assignment_service, get_course_repo, get_enrollment_repo
from app.application.interfaces.repositories.i_course_repository import ICourseRepository
from app.application.interfaces.repositories.i_enrollment_repository import IEnrollmentRepository
from app.presentation.schemas.assignment_schemas import (
    AssignmentResponse, CreateAssignmentRequest, UpdateAssignmentRequest
)

router = APIRouter(tags=["Assignments"])


@router.post("/modules/{module_id}/assignments", response_model=AssignmentResponse)
async def create_assignment(
    module_id: UUID,
    req: CreateAssignmentRequest,
    current_user: User = Depends(require_teacher),
    assignment_service: AssignmentService = Depends(get_assignment_service),
):
    dto = CreateAssignmentDTO(
        title=req.title,
        description=req.description,
        total_points=req.total_points,
        due_date=req.due_date,
        status=req.status,
    )
    return await assignment_service.create_assignment(module_id, dto, current_user)


@router.get("/courses/{course_id}/assignments", response_model=List[AssignmentResponse])
async def list_course_assignments(
    course_id: UUID,
    current_user: User = Depends(get_current_user),
    assignment_service: AssignmentService = Depends(get_assignment_service),
    course_repo: ICourseRepository = Depends(get_course_repo),
    enrollment_repo: IEnrollmentRepository = Depends(get_enrollment_repo),
):
    await ensure_course_access(course_id, current_user, course_repo, enrollment_repo)
    return await assignment_service.list_by_course(course_id, current_user)


@router.get("/assignments/upcoming", response_model=List[AssignmentResponse])
async def list_upcoming_assignments(
    days: int = Query(7, ge=1, le=30),
    current_user: User = Depends(get_current_user),
    assignment_service: AssignmentService = Depends(get_assignment_service),
):
    return await assignment_service.list_upcoming_deadlines(current_user.id, days)


@router.get("/assignments/{id}", response_model=AssignmentResponse)
async def get_assignment(
    id: UUID,
    current_user: User = Depends(get_current_user),
    assignment_service: AssignmentService = Depends(get_assignment_service),
    course_repo: ICourseRepository = Depends(get_course_repo),
    enrollment_repo: IEnrollmentRepository = Depends(get_enrollment_repo),
):
    assignment = await assignment_service.get_assignment_by_id(id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    await ensure_course_access(assignment.course_id, current_user, course_repo, enrollment_repo)
    return assignment


@router.put("/assignments/{id}", response_model=AssignmentResponse)
async def update_assignment(
    id: UUID,
    req: UpdateAssignmentRequest,
    current_user: User = Depends(require_teacher),
    assignment_service: AssignmentService = Depends(get_assignment_service),
):
    dto = UpdateAssignmentDTO(
        title=req.title,
        description=req.description,
        total_points=req.total_points,
        due_date=req.due_date,
        status=req.status,
    )
    assignment = await assignment_service.update_assignment(id, dto, current_user)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return assignment


@router.patch("/assignments/{id}/publish", response_model=AssignmentResponse)
async def publish_assignment(
    id: UUID,
    current_user: User = Depends(require_teacher),
    assignment_service: AssignmentService = Depends(get_assignment_service),
):
    assignment = await assignment_service.publish_assignment(id, current_user)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return assignment


@router.delete("/assignments/{id}")
async def delete_assignment(
    id: UUID,
    current_user: User = Depends(require_teacher),
    assignment_service: AssignmentService = Depends(get_assignment_service),
):
    deleted = await assignment_service.delete_assignment(id, current_user)
    if not deleted:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return {"message": "Assignment deleted successfully"}
