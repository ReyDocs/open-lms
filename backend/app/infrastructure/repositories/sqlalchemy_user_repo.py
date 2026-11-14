from typing import List, Optional, Tuple
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, delete
from app.application.interfaces.repositories.i_user_repository import IUserRepository
from app.domain.entities.user import User
from app.infrastructure.database.models.user_model import UserModel


class SQLAlchemyUserRepository(IUserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(UserModel).where(func.lower(UserModel.email) == email.lower().strip())
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_google_id(self, google_id: str) -> Optional[User]:
        stmt = select(UserModel).where(UserModel.google_id == google_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def create(self, user: User) -> User:
        model = UserModel(
            id=user.id,
            email=user.email.lower().strip(),
            full_name=user.full_name,
            avatar_url=user.avatar_url,
            role=user.role,
            student_id=user.student_id,
            google_id=user.google_id,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
        self.session.add(model)
        await self.session.flush()
        return self._to_entity(model)

    async def update(self, user: User) -> User:
        stmt = select(UserModel).where(UserModel.id == user.id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            raise ValueError(f"User {user.id} not found")

        model.full_name = user.full_name
        model.avatar_url = user.avatar_url
        model.role = user.role
        model.student_id = user.student_id
        model.google_id = user.google_id
        model.updated_at = user.updated_at
        await self.session.flush()
        return self._to_entity(model)

    async def delete(self, user_id: UUID) -> bool:
        stmt = delete(UserModel).where(UserModel.id == user_id)
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount > 0

    async def list_users(
        self, role: Optional[str] = None, search: Optional[str] = None, page: int = 1, per_page: int = 20
    ) -> Tuple[List[User], int]:
        stmt = select(UserModel)
        count_stmt = select(func.count(UserModel.id))

        if role:
            stmt = stmt.where(UserModel.role == role)
            count_stmt = count_stmt.where(UserModel.role == role)

        if search:
            search_filter = or_(
                UserModel.full_name.ilike(f"%{search}%"),
                UserModel.email.ilike(f"%{search}%"),
                UserModel.student_id.ilike(f"%{search}%"),
            )
            stmt = stmt.where(search_filter)
            count_stmt = count_stmt.where(search_filter)

        total_res = await self.session.execute(count_stmt)
        total = total_res.scalar() or 0

        stmt = stmt.order_by(UserModel.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models], total

    async def bulk_create_or_update(self, users: List[User]) -> int:
        count = 0
        for u in users:
            existing = await self.get_by_email(u.email)
            if existing:
                # Update student_id or name if provided
                if u.student_id:
                    existing.student_id = u.student_id
                if u.full_name:
                    existing.full_name = u.full_name
                await self.update(existing)
            else:
                await self.create(u)
            count += 1
        return count

    def _to_entity(self, m: UserModel) -> User:
        return User(
            id=m.id,
            email=m.email,
            full_name=m.full_name,
            avatar_url=m.avatar_url,
            role=m.role,
            student_id=m.student_id,
            google_id=m.google_id,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )
