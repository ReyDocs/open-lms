from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
from app.application.interfaces.repositories.i_notification_repository import INotificationRepository
from app.domain.entities.notification import Notification
from app.infrastructure.database.models.notification_model import NotificationModel


class SQLAlchemyNotificationRepository(INotificationRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, notification_id: UUID) -> Optional[Notification]:
        stmt = select(NotificationModel).where(NotificationModel.id == notification_id)
        res = await self.session.execute(stmt)
        model = res.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def create(self, notification: Notification) -> Notification:
        model = NotificationModel(
            id=notification.id,
            user_id=notification.user_id,
            type=notification.type,
            title=notification.title,
            message=notification.message,
            link=notification.link,
            is_read=notification.is_read,
            created_at=notification.created_at,
        )
        self.session.add(model)
        await self.session.flush()
        return self._to_entity(model)

    async def create_many(self, notifications: List[Notification]) -> int:
        count = 0
        for n in notifications:
            model = NotificationModel(
                id=n.id,
                user_id=n.user_id,
                type=n.type,
                title=n.title,
                message=n.message,
                link=n.link,
                is_read=n.is_read,
                created_at=n.created_at,
            )
            self.session.add(model)
            count += 1
        await self.session.flush()
        return count

    async def list_by_user(self, user_id: UUID, page: int = 1, per_page: int = 20) -> List[Notification]:
        stmt = (
            select(NotificationModel)
            .where(NotificationModel.user_id == user_id)
            .order_by(NotificationModel.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        models = (await self.session.execute(stmt)).scalars().all()
        return [self._to_entity(m) for m in models]

    async def mark_as_read(self, notification_id: UUID, user_id: UUID) -> bool:
        stmt = (
            update(NotificationModel)
            .where(NotificationModel.id == notification_id, NotificationModel.user_id == user_id)
            .values(is_read=True)
        )
        res = await self.session.execute(stmt)
        await self.session.flush()
        return res.rowcount > 0

    async def mark_all_as_read(self, user_id: UUID) -> int:
        stmt = (
            update(NotificationModel)
            .where(NotificationModel.user_id == user_id, NotificationModel.is_read == False)
            .values(is_read=True)
        )
        res = await self.session.execute(stmt)
        await self.session.flush()
        return res.rowcount

    async def get_unread_count(self, user_id: UUID) -> int:
        stmt = (
            select(func.count(NotificationModel.id))
            .where(NotificationModel.user_id == user_id, NotificationModel.is_read == False)
        )
        return (await self.session.execute(stmt)).scalar() or 0

    def _to_entity(self, m: NotificationModel) -> Notification:
        return Notification(
            id=m.id,
            user_id=m.user_id,
            type=m.type,
            title=m.title,
            message=m.message,
            link=m.link,
            is_read=m.is_read,
            created_at=m.created_at,
        )
