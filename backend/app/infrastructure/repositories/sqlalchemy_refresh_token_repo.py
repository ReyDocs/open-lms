from typing import Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_
from app.application.interfaces.repositories.i_refresh_token_repository import IRefreshTokenRepository
from app.infrastructure.database.models.refresh_token_model import RefreshTokenModel


class SQLAlchemyRefreshTokenRepository(IRefreshTokenRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_id: UUID, token_hash: str, expires_at: datetime) -> UUID:
        token_id = uuid4()
        model = RefreshTokenModel(
            id=token_id,
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
            is_revoked=False,
            created_at=datetime.now(timezone.utc),
        )
        self.session.add(model)
        await self.session.flush()
        return token_id

    async def get_valid(self, token_hash: str) -> Optional[Dict[str, Any]]:
        now = datetime.now(timezone.utc)
        stmt = select(RefreshTokenModel).where(
            and_(
                RefreshTokenModel.token_hash == token_hash,
                RefreshTokenModel.is_revoked == False,
                RefreshTokenModel.expires_at > now,
            )
        )
        res = await self.session.execute(stmt)
        model = res.scalar_one_or_none()
        if not model:
            return None
        return {
            "id": model.id,
            "user_id": model.user_id,
            "token_hash": model.token_hash,
            "expires_at": model.expires_at,
            "is_revoked": model.is_revoked,
        }

    async def revoke(self, token_hash: str) -> bool:
        stmt = (
            update(RefreshTokenModel)
            .where(RefreshTokenModel.token_hash == token_hash)
            .values(is_revoked=True)
        )
        res = await self.session.execute(stmt)
        await self.session.flush()
        return res.rowcount > 0

    async def revoke_all_for_user(self, user_id: UUID) -> int:
        stmt = (
            update(RefreshTokenModel)
            .where(RefreshTokenModel.user_id == user_id)
            .values(is_revoked=True)
        )
        res = await self.session.execute(stmt)
        await self.session.flush()
        return res.rowcount
