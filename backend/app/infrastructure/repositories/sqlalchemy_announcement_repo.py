from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from app.application.interfaces.repositories.i_announcement_repository import IAnnouncementRepository
from app.domain.entities.announcement import Announcement, AnnouncementAttachment
from app.infrastructure.database.models.announcement_model import AnnouncementModel, AnnouncementAttachmentModel
from app.infrastructure.database.models.enrollment_model import EnrollmentModel


class SQLAlchemyAnnouncementRepository(IAnnouncementRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, announcement_id: UUID) -> Optional[Announcement]:
        stmt = (
            select(AnnouncementModel)
            .options(selectinload(AnnouncementModel.attachments))
            .where(AnnouncementModel.id == announcement_id)
        )
        res = await self.session.execute(stmt)
        model = res.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def create(self, announcement: Announcement) -> Announcement:
        model = AnnouncementModel(
            id=announcement.id,
            course_id=announcement.course_id,
            author_id=announcement.author_id,
            title=announcement.title,
            content=announcement.content,
            created_at=announcement.created_at,
        )
        for att in announcement.attachments:
            att_model = AnnouncementAttachmentModel(
                id=att.id,
                announcement_id=announcement.id,
                file_url=att.file_url,
                file_name=att.file_name,
                file_size=att.file_size,
            )
            model.attachments.append(att_model)

        self.session.add(model)
        await self.session.flush()
        return self._to_entity(model)

    async def update(self, announcement: Announcement) -> Announcement:
        stmt = select(AnnouncementModel).where(AnnouncementModel.id == announcement.id)
        res = await self.session.execute(stmt)
        model = res.scalar_one_or_none()
        if not model:
            raise ValueError(f"Announcement {announcement.id} not found")

        model.title = announcement.title
        model.content = announcement.content
        await self.session.flush()
        return await self.get_by_id(announcement.id)

    async def delete(self, announcement_id: UUID) -> bool:
        stmt = delete(AnnouncementModel).where(AnnouncementModel.id == announcement_id)
        res = await self.session.execute(stmt)
        await self.session.flush()
        return res.rowcount > 0

    async def list_by_course(self, course_id: UUID) -> List[Announcement]:
        stmt = (
            select(AnnouncementModel)
            .options(selectinload(AnnouncementModel.attachments))
            .where(AnnouncementModel.course_id == course_id)
            .order_by(AnnouncementModel.created_at.desc())
        )
        models = (await self.session.execute(stmt)).scalars().all()
        return [self._to_entity(m) for m in models]

    async def list_recent_for_user(self, user_id: UUID, limit: int = 5) -> List[Announcement]:
        enrolled_courses = select(EnrollmentModel.course_id).where(EnrollmentModel.user_id == user_id)
        stmt = (
            select(AnnouncementModel)
            .options(selectinload(AnnouncementModel.attachments))
            .where(AnnouncementModel.course_id.in_(enrolled_courses))
            .order_by(AnnouncementModel.created_at.desc())
            .limit(limit)
        )
        models = (await self.session.execute(stmt)).scalars().all()
        return [self._to_entity(m) for m in models]

    async def add_attachment(self, attachment: AnnouncementAttachment) -> AnnouncementAttachment:
        model = AnnouncementAttachmentModel(
            id=attachment.id,
            announcement_id=attachment.announcement_id,
            file_url=attachment.file_url,
            file_name=attachment.file_name,
            file_size=attachment.file_size,
        )
        self.session.add(model)
        await self.session.flush()
        return attachment

    def _to_entity(self, m: AnnouncementModel) -> Announcement:
        attachments = [
            AnnouncementAttachment(
                id=att.id,
                announcement_id=att.announcement_id,
                file_url=att.file_url,
                file_name=att.file_name,
                file_size=att.file_size,
            )
            for att in (m.attachments or [])
        ]
        return Announcement(
            id=m.id,
            course_id=m.course_id,
            author_id=m.author_id,
            title=m.title,
            content=m.content,
            created_at=m.created_at,
            attachments=attachments,
        )
