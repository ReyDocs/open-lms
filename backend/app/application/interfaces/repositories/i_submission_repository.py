from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from app.domain.entities.submission import Submission


class ISubmissionRepository(ABC):
    @abstractmethod
    async def get_by_id(self, submission_id: UUID) -> Optional[Submission]:
        pass

    @abstractmethod
    async def create(self, submission: Submission) -> Submission:
        pass

    @abstractmethod
    async def update(self, submission: Submission) -> Submission:
        pass

    @abstractmethod
    async def get_latest_by_student_and_assignment(
        self, student_id: UUID, assignment_id: UUID
    ) -> Optional[Submission]:
        pass

    @abstractmethod
    async def list_by_assignment(self, assignment_id: UUID) -> List[Submission]:
        pass

    @abstractmethod
    async def list_by_student_and_assignment(
        self, student_id: UUID, assignment_id: UUID
    ) -> List[Submission]:
        pass

    @abstractmethod
    async def list_by_student_and_course(
        self, student_id: UUID, course_id: UUID
    ) -> List[Submission]:
        pass

    @abstractmethod
    async def list_latest_by_course(self, course_id: UUID) -> List[Submission]:
        pass
