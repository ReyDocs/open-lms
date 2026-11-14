from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from app.domain.entities.enrollment import Enrollment
from app.domain.entities.user import User


class IEnrollmentRepository(ABC):
    @abstractmethod
    async def get(self, user_id: UUID, course_id: UUID) -> Optional[Enrollment]:
        pass

    @abstractmethod
    async def enroll(self, enrollment: Enrollment) -> Enrollment:
        pass

    @abstractmethod
    async def unenroll(self, user_id: UUID, course_id: UUID) -> bool:
        pass

    @abstractmethod
    async def list_students_by_course(self, course_id: UUID) -> List[User]:
        pass

    @abstractmethod
    async def list_course_ids_by_user(self, user_id: UUID) -> List[UUID]:
        pass

    @abstractmethod
    async def is_enrolled(self, user_id: UUID, course_id: UUID) -> bool:
        pass
