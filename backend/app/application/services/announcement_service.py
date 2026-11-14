from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime, timezone

from app.application.interfaces.repositories.i_announcement_repository import IAnnouncementRepository
from app.application.interfaces.repositories.i_course_repository import ICourseRepository
from app.application.interfaces.repositories.i_user_repository import IUserRepository
from app.application.services.notification_service import NotificationService
from app.application.dtos.announcement_dtos import (
    CreateAnnouncementDTO, UpdateAnnouncementDTO, AnnouncementResponseDTO, AttachmentResponseDTO
)
from app.domain.entities.announcement import Announcement, AnnouncementAttachment
from app.domain.entities.user import User
from app.application.services.rich_text import sanitize_rich_text


class AnnouncementService:
    def __init__(
        self,
        announcement_repo: IAnnouncementRepository,
        course_repo: ICourseRepository,
        user_repo: IUserRepository,
        notification_service: Optional[NotificationService] = None,
    ):
        self.announcement_repo = announcement_repo
        self.course_repo = course_repo
        self.user_repo = user_repo
        self.notification_service = notification_service

    async def create_announcement(
        self, course_id: UUID, dto: CreateAnnouncementDTO, author: User
    ) -> AnnouncementResponseDTO:
        course = await self.course_repo.get_by_id(course_id)
        if not course:
            raise ValueError("Course not found")
        if not author.is_admin() and course.teacher_id != author.id:
            raise PermissionError("Only the course teacher can create announcements")

        # Sanitize HTML with bleach
        clean_content = sanitize_rich_text(dto.content)

        now = datetime.now(timezone.utc)
        announcement_id = uuid4()

        attachments: List[AnnouncementAttachment] = []
        if dto.attachments:
            for att in dto.attachments:
                attachments.append(
                    AnnouncementAttachment(
                        id=uuid4(),
                        announcement_id=announcement_id,
                        file_url=att.file_url,
                        file_name=att.file_name,
                        file_size=att.file_size,
                    )
                )

        announcement = Announcement(
            id=announcement_id,
            course_id=course_id,
            author_id=author.id,
            title=dto.title.strip(),
            content=clean_content,
            created_at=now,
            attachments=attachments,
        )
        saved = await self.announcement_repo.create(announcement)

        # Notify enrolled students
        if self.notification_service:
            await self.notification_service.notify_course_students(
                course_id=course_id,
                notif_type="announcement",
                title=f"New Announcement: {saved.title}",
                message=f"{author.full_name} posted an announcement in {course.title}.",
                link=f"/courses/{course_id}/announcements/{saved.id}",
            )

        return self._to_dto(saved, author.full_name)

    async def list_announcements(self, course_id: UUID) -> List[AnnouncementResponseDTO]:
        items = await self.announcement_repo.list_by_course(course_id)
        dtos: List[AnnouncementResponseDTO] = []
        for ann in items:
            author = await self.user_repo.get_by_id(ann.author_id)
            name = author.full_name if author else None
            dtos.append(self._to_dto(ann, name))
        return dtos

    async def get_announcement_by_id(self, announcement_id: UUID) -> Optional[AnnouncementResponseDTO]:
        ann = await self.announcement_repo.get_by_id(announcement_id)
        if not ann:
            return None
        author = await self.user_repo.get_by_id(ann.author_id)
        name = author.full_name if author else None
        return self._to_dto(ann, name)

    async def update_announcement(
        self, announcement_id: UUID, dto: UpdateAnnouncementDTO, user: User
    ) -> Optional[AnnouncementResponseDTO]:
        ann = await self.announcement_repo.get_by_id(announcement_id)
        if not ann:
            return None
        if not user.is_admin() and ann.author_id != user.id:
            raise PermissionError("Access denied")

        if dto.title is not None:
            ann.title = dto.title.strip()
        if dto.content is not None:
            ann.content = sanitize_rich_text(dto.content)

        updated = await self.announcement_repo.update(ann)
        author = await self.user_repo.get_by_id(updated.author_id)
        name = author.full_name if author else None
        return self._to_dto(updated, name)

    async def delete_announcement(self, announcement_id: UUID, user: User) -> bool:
        ann = await self.announcement_repo.get_by_id(announcement_id)
        if not ann:
            return False
        if not user.is_admin() and ann.author_id != user.id:
            raise PermissionError("Access denied")

        return await self.announcement_repo.delete(announcement_id)

    async def list_recent_announcements(self, user_id: UUID, limit: int = 5) -> List[AnnouncementResponseDTO]:
        items = await self.announcement_repo.list_recent_for_user(user_id, limit)
        dtos: List[AnnouncementResponseDTO] = []
        for ann in items:
            author = await self.user_repo.get_by_id(ann.author_id)
            name = author.full_name if author else None
            dtos.append(self._to_dto(ann, name))
        return dtos

    def _to_dto(self, a: Announcement, author_name: Optional[str] = None) -> AnnouncementResponseDTO:
        att_dtos = [
            AttachmentResponseDTO(
                id=att.id,
                announcement_id=att.announcement_id,
                file_url=att.file_url,
                file_name=att.file_name,
                file_size=att.file_size,
            )
            for att in a.attachments
        ]
        return AnnouncementResponseDTO(
            id=a.id,
            course_id=a.course_id,
            author_id=a.author_id,
            title=a.title,
            content=a.content,
            created_at=a.created_at,
            author_name=author_name,
            attachments=att_dtos,
        )
