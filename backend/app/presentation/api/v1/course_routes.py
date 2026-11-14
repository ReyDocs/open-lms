from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from app.domain.entities.user import User
from app.application.services.course_service import CourseService
from app.application.services.enrollment_service import EnrollmentService
from app.application.dtos.course_dtos import CreateCourseDTO, UpdateCourseDTO
from app.presentation.dependencies.auth import get_current_user, require_teacher, ensure_course_access
from app.presentation.dependencies.services import get_course_service, get_enrollment_service, get_course_repo, get_enrollment_repo
from app.application.interfaces.repositories.i_course_repository import ICourseRepository
from app.application.interfaces.repositories.i_enrollment_repository import IEnrollmentRepository
from app.presentation.schemas.course_schemas import (
    CourseResponse, CreateCourseRequest, UpdateCourseRequest,
    EnrollStudentRequest, InviteStudentRequest
)
from app.presentation.schemas.user_schemas import UserResponse

router = APIRouter(prefix="/courses", tags=["Courses"])


@router.post("", response_model=CourseResponse)
async def create_course(
    req: CreateCourseRequest,
    current_user: User = Depends(require_teacher),
    course_service: CourseService = Depends(get_course_service),
):
    dto = CreateCourseDTO(
        title=req.title,
        code=req.code,
        description=req.description,
        semester=req.semester,
        cover_image_url=req.cover_image_url,
    )
    return await course_service.create_course(dto, current_user)


@router.get("/search", response_model=dict)
async def search_courses(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    course_service: CourseService = Depends(get_course_service),
):
    courses, total = await course_service.search_courses(q, current_user, page, per_page)
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


@router.get("", response_model=dict)
async def list_courses(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    course_service: CourseService = Depends(get_course_service),
):
    courses, total = await course_service.list_user_courses(current_user, page, per_page)
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


@router.get("/{id}", response_model=CourseResponse)
async def get_course(
    id: UUID,
    current_user: User = Depends(get_current_user),
    course_service: CourseService = Depends(get_course_service),
    course_repo: ICourseRepository = Depends(get_course_repo),
    enrollment_repo: IEnrollmentRepository = Depends(get_enrollment_repo),
):
    await ensure_course_access(id, current_user, course_repo, enrollment_repo)
    course = await course_service.get_course_by_id(id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.put("/{id}", response_model=CourseResponse)
async def update_course(
    id: UUID,
    req: UpdateCourseRequest,
    current_user: User = Depends(require_teacher),
    course_service: CourseService = Depends(get_course_service),
):
    dto = UpdateCourseDTO(
        title=req.title,
        description=req.description,
        semester=req.semester,
        cover_image_url=req.cover_image_url,
    )
    course = await course_service.update_course(id, dto, current_user)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.delete("/{id}")
async def delete_course(
    id: UUID,
    current_user: User = Depends(require_teacher),
    course_service: CourseService = Depends(get_course_service),
):
    deleted = await course_service.delete_course(id, current_user)
    if not deleted:
        raise HTTPException(status_code=404, detail="Course not found")
    return {"message": "Course deleted successfully"}


# Enrollment endpoints
@router.post("/{id}/enroll", response_model=List[UserResponse])
async def enroll_students(
    id: UUID,
    req: EnrollStudentRequest,
    current_user: User = Depends(require_teacher),
    enrollment_service: EnrollmentService = Depends(get_enrollment_service),
):
    return await enrollment_service.enroll_students_from_pool(id, req.student_ids, current_user)


@router.post("/{id}/invite", response_model=UserResponse)
async def invite_student(
    id: UUID,
    req: InviteStudentRequest,
    current_user: User = Depends(require_teacher),
    enrollment_service: EnrollmentService = Depends(get_enrollment_service),
):
    return await enrollment_service.invite_student_by_email(id, req.email, current_user)


@router.get("/{id}/students", response_model=List[UserResponse])
async def list_enrolled_students(
    id: UUID,
    current_user: User = Depends(get_current_user),
    enrollment_service: EnrollmentService = Depends(get_enrollment_service),
):
    return await enrollment_service.list_enrolled_students(id, current_user)


@router.delete("/{id}/students/{student_id}")
async def remove_student(
    id: UUID,
    student_id: UUID,
    current_user: User = Depends(require_teacher),
    enrollment_service: EnrollmentService = Depends(get_enrollment_service),
):
    removed = await enrollment_service.remove_student(id, student_id, current_user)
    if not removed:
        raise HTTPException(status_code=404, detail="Student enrollment not found")
    return {"message": "Student unenrolled successfully"}
