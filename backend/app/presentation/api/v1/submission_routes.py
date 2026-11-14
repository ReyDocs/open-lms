from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from app.domain.entities.user import User
from app.application.services.submission_service import SubmissionService
from app.presentation.dependencies.auth import get_current_user, require_teacher
from app.presentation.dependencies.services import get_submission_service
from app.presentation.schemas.submission_schemas import SubmissionResponse

router = APIRouter(tags=["Submissions"])


@router.post("/assignments/{id}/submissions", response_model=SubmissionResponse)
async def submit_assignment_file(
    id: UUID,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    submission_service: SubmissionService = Depends(get_submission_service),
):
    content = await file.read()
    content_type = file.content_type or "application/octet-stream"
    return await submission_service.submit_assignment(
        assignment_id=id,
        file_bytes=content,
        file_name=file.filename or "submission",
        content_type=content_type,
        student=current_user,
    )


@router.get("/assignments/{id}/submissions", response_model=List[SubmissionResponse])
async def list_assignment_submissions(
    id: UUID,
    current_user: User = Depends(require_teacher),
    submission_service: SubmissionService = Depends(get_submission_service),
):
    return await submission_service.list_assignment_submissions(id, current_user)


@router.get("/assignments/{id}/submissions/mine", response_model=SubmissionResponse)
async def get_my_submission(
    id: UUID,
    current_user: User = Depends(get_current_user),
    submission_service: SubmissionService = Depends(get_submission_service),
):
    sub = await submission_service.get_my_submission(id, current_user)
    if not sub:
        raise HTTPException(status_code=404, detail="No submission found")
    return sub


@router.get("/submissions/{id}", response_model=SubmissionResponse)
async def get_submission(
    id: UUID,
    current_user: User = Depends(get_current_user),
    submission_service: SubmissionService = Depends(get_submission_service),
):
    sub = await submission_service.get_submission_by_id(id, current_user)
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")
    return sub
