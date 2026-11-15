from typing import List, Optional, Tuple
from uuid import UUID, uuid4
from datetime import datetime, timezone

from app.application.interfaces.repositories.i_course_repository import ICourseRepository
from app.application.interfaces.repositories.i_user_repository import IUserRepository
from app.application.dtos.course_dtos import CreateCourseDTO, UpdateCourseDTO, CourseResponseDTO
from app.domain.entities.course import Course
from app.domain.entities.user import User


class CourseService:
    def __init__(self, course_repo: ICourseRepository, user_repo: Optional[IUserRepository] = None):
        self.course_repo = course_repo
        self.user_repo = user_repo

    async def get_course_by_id(self, course_id: UUID) -> Optional[CourseResponseDTO]:
        course = await self.course_repo.get_by_id(course_id)
        if not course:
            return None
        return self._to_dto(course)

    async def get_course_by_code(self, code: str) -> Optional[CourseResponseDTO]:
        course = await self.course_repo.get_by_code(code)
        if not course:
            return None
        return self._to_dto(course)

    async def create_course(self, dto: CreateCourseDTO, teacher: User) -> CourseResponseDTO:
        now = datetime.now(timezone.utc)
        course = Course(
            id=uuid4(),
            title=dto.title.strip(),
            code=dto.code.strip().upper(),
            description=dto.description.strip(),
            semester=dto.semester.strip(),
            teacher_id=teacher.id,
            cover_image_url=dto.cover_image_url,
            created_at=now,
            updated_at=now,
        )
        saved = await self.course_repo.create(course)
        return self._to_dto(saved)

    async def update_course(
        self, course_id: UUID, dto: UpdateCourseDTO, current_user: User
    ) -> Optional[CourseResponseDTO]:
        course = await self.course_repo.get_by_id(course_id)
        if not course:
            return None
        # Must be owner or admin
        if not current_user.is_admin() and course.teacher_id != current_user.id:
            raise PermissionError("Only the course teacher or an admin can update this course")

        if dto.title is not None:
            course.title = dto.title.strip()
        if dto.description is not None:
            course.description = dto.description.strip()
        if dto.semester is not None:
            course.semester = dto.semester.strip()
        if dto.cover_image_url is not None:
            course.cover_image_url = dto.cover_image_url
        course.updated_at = datetime.now(timezone.utc)

        updated = await self.course_repo.update(course)
        return self._to_dto(updated)

    async def delete_course(self, course_id: UUID, current_user: User) -> bool:
        course = await self.course_repo.get_by_id(course_id)
        if not course:
            return False
        if not current_user.is_admin() and course.teacher_id != current_user.id:
            raise PermissionError("Only the course teacher or an admin can delete this course")

        return await self.course_repo.delete(course_id)

    async def list_user_courses(
        self, current_user: User, page: int = 1, per_page: int = 20
    ) -> Tuple[List[CourseResponseDTO], int]:
        if current_user.is_admin():
            return [], 0
        elif current_user.role == "teacher":
            courses, total = await self.course_repo.list_by_teacher(current_user.id, page, per_page)
        else:
            courses, total = await self.course_repo.list_by_student(current_user.id, page, per_page)

        return [self._to_dto(c) for c in courses], total

    async def list_all_courses(self, page: int = 1, per_page: int = 20) -> Tuple[List[CourseResponseDTO], int]:
        courses, total = await self.course_repo.list_all(page, per_page)
        return [self._to_dto(c) for c in courses], total

    async def search_courses(
        self, query: str, current_user: User, page: int = 1, per_page: int = 20
    ) -> Tuple[List[CourseResponseDTO], int]:
        user_id = None if current_user.is_admin() else current_user.id
        courses, total = await self.course_repo.search(query, user_id, page, per_page)
        return [self._to_dto(c) for c in courses], total

    def _to_dto(self, course: Course) -> CourseResponseDTO:
        return CourseResponseDTO(
            id=course.id,
            title=course.title,
            code=course.code,
            description=course.description,
            semester=course.semester,
            teacher_id=course.teacher_id,
            cover_image_url=course.cover_image_url,
            created_at=course.created_at,
            updated_at=course.updated_at,
        )
