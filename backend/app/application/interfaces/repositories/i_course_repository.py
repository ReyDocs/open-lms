from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from uuid import UUID
from app.domain.entities.course import Course


class ICourseRepository(ABC):
    @abstractmethod
    async def get_by_id(self, course_id: UUID) -> Optional[Course]:
        pass

    @abstractmethod
    async def get_by_code(self, code: str) -> Optional[Course]:
        pass

    @abstractmethod
    async def create(self, course: Course) -> Course:
        pass

    @abstractmethod
    async def update(self, course: Course) -> Course:
        pass

    @abstractmethod
    async def delete(self, course_id: UUID) -> bool:
        pass

    @abstractmethod
    async def list_all(self, page: int = 1, per_page: int = 20) -> Tuple[List[Course], int]:
        pass

    @abstractmethod
    async def list_by_teacher(self, teacher_id: UUID, page: int = 1, per_page: int = 20) -> Tuple[List[Course], int]:
        pass

    @abstractmethod
    async def list_by_student(self, student_id: UUID, page: int = 1, per_page: int = 20) -> Tuple[List[Course], int]:
        pass

    @abstractmethod
    async def search(self, query: str, user_id: Optional[UUID] = None, page: int = 1, per_page: int = 20) -> Tuple[List[Course], int]:
        pass
