from typing import List
from uuid import UUID

from core.db import Notification, NotificationTemplate, get_db_session
from core.repository import NotificationRepository, NotificationTemplateRepository
from fastapi import Depends
from models.notification import NotificationCreate, NotificationTemplateBase
from sqlalchemy.ext.asyncio import AsyncSession


class NotificationService:
    def __init__(self, session: AsyncSession):
        self.notification_repo = NotificationRepository(session)
        self.template_repo = NotificationTemplateRepository(session)

    # Notification CRUD
    async def send_notification(self, data: NotificationCreate) -> List[Notification]:
        notifications = []
        template = await self.template_repo.get_by_id(data.template_id)
        if not template:
            raise ValueError("Шаблон не найден")
        for user_id in data.recipients:
            notification = Notification(
                user_id=user_id,
                template_id=data.template_id,
                subject=template.subject,
                body=template.body,
                notification_type=data.notification_type,
                status="pending",
                data=data.data,
            )
            notifications.append(await self.notification_repo.create(notification))
        return notifications

    async def get_user_notifications(self, user_id: str) -> List[Notification]:
        return await self.notification_repo.get_by_user(  # type: ignore[no-any-return]
            user_id
        )

    async def get_notification(self, notification_id: UUID) -> Notification:
        notification = await self.notification_repo.get_by_id(notification_id)
        if not notification:
            raise ValueError("Уведомление не найдено")
        return notification

    async def list_notifications(self) -> List[Notification]:
        return await self.notification_repo.list()  # type: ignore[no-any-return]

    async def update_notification(
        self, notification_id: UUID, update_data: dict
    ) -> Notification:
        notification = await self.notification_repo.update(notification_id, update_data)
        if not notification:
            raise ValueError("Уведомление не найдено для обновления")
        return notification

    async def delete_notification(self, notification_id: UUID) -> None:
        deleted = await self.notification_repo.delete_notification(notification_id)
        if not deleted:
            raise ValueError("Уведомление не найдено для удаления")

    # Template CRUD
    async def get_templates(self) -> List[NotificationTemplate]:
        return await self.template_repo.list()  # type: ignore[no-any-return]

    async def get_template(self, template_id: UUID) -> NotificationTemplate:
        template = await self.template_repo.get_by_id(template_id)
        if not template:
            raise ValueError("Шаблон не найден")
        return template

    async def create_template(
        self, template_data: NotificationTemplateBase
    ) -> NotificationTemplate:
        # Проверка на дублирование по имени шаблона
        templates = await self.template_repo.list()
        if any(template.name == template_data.name for template in templates):
            raise ValueError("Шаблон с таким именем уже существует")
        template = NotificationTemplate(**template_data.model_dump())
        return await self.template_repo.create(template)

    async def update_template(
        self, template_id: UUID, update_data: dict
    ) -> NotificationTemplate:
        template = await self.template_repo.update(template_id, update_data)
        if not template:
            raise ValueError("Шаблон не найден для обновления")
        return template

    async def delete_template(self, template_id: UUID) -> None:
        deleted = await self.template_repo.delete_template(template_id)
        if not deleted:
            raise ValueError("Шаблон не найден для удаления")


async def get_notification_service(
    session: AsyncSession = Depends(get_db_session),
) -> NotificationService:
    return NotificationService(session)
