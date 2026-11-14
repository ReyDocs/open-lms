from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from app.domain.entities.user import User
from app.application.services.submission_service import SubmissionService
from app.presentation.dependencies.auth import get_current_user, require_teacher
from app.presentation.dependencies.services import get_submission_service
from app.presentation.schemas.submission_schemas import SubmissionResponse
from app.domain.value_objects.file_type import MAX_FILE_SIZE_BYTES
from app.application.services.assignment_service import AssignmentService
from app.presentation.dependencies.auth import ensure_course_access
from app.presentation.dependencies.services import get_assignment_service, get_course_repo, get_enrollment_repo
from app.application.interfaces.repositories.i_course_repository import ICourseRepository
from app.application.interfaces.repositories.i_enrollment_repository import IEnrollmentRepository

router = APIRouter(tags=["Submissions"])


@router.post("/assignments/{id}/submissions", response_model=SubmissionResponse)
async def submit_assignment_file(
    id: UUID,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    submission_service: SubmissionService = Depends(get_submission_service),
):
    # UploadFile.read() without a size reads the whole file into memory before
    # SubmissionService can enforce its limit. Read in bounded chunks and stop
    # as soon as the request exceeds the configured MVP cap.
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
    content = b"".join(chunks)
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
    assignment_service: AssignmentService = Depends(get_assignment_service),
    course_repo: ICourseRepository = Depends(get_course_repo),
    enrollment_repo: IEnrollmentRepository = Depends(get_enrollment_repo),
):
    assignment = await assignment_service.get_assignment_by_id(id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    await ensure_course_access(assignment.course_id, current_user, course_repo, enrollment_repo)
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
    assignment_service: AssignmentService = Depends(get_assignment_service),
    course_repo: ICourseRepository = Depends(get_course_repo),
    enrollment_repo: IEnrollmentRepository = Depends(get_enrollment_repo),
):
    sub = await submission_service.get_submission_by_id(id, current_user)
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")
    assignment = await assignment_service.get_assignment_by_id(sub.assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    if current_user.is_teacher():
        await ensure_course_access(assignment.course_id, current_user, course_repo, enrollment_repo)
    return sub
