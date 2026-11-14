from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Response
from app.domain.entities.user import User
from app.application.services.grading_service import GradingService
from app.application.dtos.grading_dtos import GradeSubmissionDTO
from app.presentation.dependencies.auth import get_current_user, require_teacher
from app.presentation.dependencies.services import get_grading_service
from app.presentation.schemas.grading_schemas import (
    GradeSubmissionRequest, GradebookResponse, StudentGradeResponse
)
from app.presentation.schemas.submission_schemas import SubmissionResponse

router = APIRouter(tags=["Grading"])


@router.post("/submissions/{id}/grade", response_model=SubmissionResponse)
async def grade_submission(
    id: UUID,
    req: GradeSubmissionRequest,
    current_user: User = Depends(require_teacher),
    grading_service: GradingService = Depends(get_grading_service),
):
    dto = GradeSubmissionDTO(
        submission_id=id,
        grade=req.grade,
        feedback=req.feedback,
    )
    return await grading_service.grade_submission(dto, current_user)


@router.get("/courses/{id}/gradebook", response_model=GradebookResponse)
async def get_gradebook(
    id: UUID,
    current_user: User = Depends(require_teacher),
    grading_service: GradingService = Depends(get_grading_service),
):
    return await grading_service.get_gradebook(id, current_user)


@router.get("/courses/{id}/gradebook/export")
async def export_gradebook_csv(
    id: UUID,
    current_user: User = Depends(require_teacher),
    grading_service: GradingService = Depends(get_grading_service),
):
    csv_data = await grading_service.export_gradebook_csv(id, current_user)
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=course_{id}_gradebook.csv"},
    )


@router.get("/courses/{id}/grades/mine", response_model=List[StudentGradeResponse])
async def get_my_grades(
    id: UUID,
    current_user: User = Depends(get_current_user),
    grading_service: GradingService = Depends(get_grading_service),
):
    return await grading_service.get_my_grades(id, current_user)
