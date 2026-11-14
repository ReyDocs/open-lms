import csv
import io
from typing import List, Optional, Tuple
from uuid import UUID, uuid4
from datetime import datetime, timezone

from app.application.interfaces.repositories.i_user_repository import IUserRepository
from app.application.dtos.user_dtos import (
    UserResponseDTO, CreateUserDTO, UpdateUserDTO, BulkImportResultDTO
)
from app.domain.entities.user import User


class UserService:
    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo

    async def get_user_by_id(self, user_id: UUID) -> Optional[UserResponseDTO]:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            return None
        return self._to_dto(user)

    async def get_user_by_email(self, email: str) -> Optional[UserResponseDTO]:
        user = await self.user_repo.get_by_email(email)
        if not user:
            return None
        return self._to_dto(user)

    async def list_users(
        self, role: Optional[str] = None, search: Optional[str] = None, page: int = 1, per_page: int = 20
    ) -> Tuple[List[UserResponseDTO], int]:
        users, total = await self.user_repo.list_users(role, search, page, per_page)
        return [self._to_dto(u) for u in users], total

    async def create_user(self, dto: CreateUserDTO) -> UserResponseDTO:
        now = datetime.now(timezone.utc)
        user = User(
            id=uuid4(),
            email=dto.email.lower().strip(),
            full_name=dto.full_name.strip(),
            role=dto.role,
            student_id=dto.student_id,
            avatar_url=dto.avatar_url,
            google_id=dto.google_id,
            created_at=now,
            updated_at=now,
        )
        saved = await self.user_repo.create(user)
        return self._to_dto(saved)

    async def update_user(self, user_id: UUID, dto: UpdateUserDTO) -> Optional[UserResponseDTO]:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            return None
        if dto.full_name is not None:
            user.full_name = dto.full_name.strip()
        if dto.role is not None:
            user.role = dto.role
        if dto.student_id is not None:
            user.student_id = dto.student_id
        if dto.avatar_url is not None:
            user.avatar_url = dto.avatar_url
        user.updated_at = datetime.now(timezone.utc)

        updated = await self.user_repo.update(user)
        return self._to_dto(updated)

    async def delete_user(self, user_id: UUID) -> bool:
        return await self.user_repo.delete(user_id)

    async def bulk_import_csv(self, csv_content: str) -> BulkImportResultDTO:
        """
        Parses CSV with header: name, email, student_id (optional).
        Creates student pool records.
        """
        imported = 0
        errors: List[str] = []
        reader = csv.DictReader(io.StringIO(csv_content))
        now = datetime.now(timezone.utc)

        users_to_import: List[User] = []
        row_num = 1

        for row in reader:
            row_num += 1
            # Handle possible keys case-insensitively
            normalized = {k.strip().lower(): v.strip() for k, v in row.items() if k}
            email = normalized.get("email")
            name = normalized.get("name") or normalized.get("full_name")
            student_id = normalized.get("student_id") or normalized.get("id")

            if not email or not name:
                errors.append(f"Row {row_num}: Missing email or name")
                continue

            users_to_import.append(
                User(
                    id=uuid4(),
                    email=email.lower().strip(),
                    full_name=name.strip(),
                    role="student",
                    student_id=student_id,
                    created_at=now,
                    updated_at=now,
                )
            )

        if users_to_import:
            imported = await self.user_repo.bulk_create_or_update(users_to_import)

        return BulkImportResultDTO(imported_count=imported, errors=errors)

    def _to_dto(self, user: User) -> UserResponseDTO:
        return UserResponseDTO(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            avatar_url=user.avatar_url,
            student_id=user.student_id,
            created_at=user.created_at,
        )
