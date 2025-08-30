from typing import List, Optional
from uuid import UUID

from core.db import Notification, NotificationTemplate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


class NotificationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, notification: Notification) -> Notification:
        self.session.add(notification)
        await self.session.commit()
        await self.session.refresh(notification)
        return notification

    async def get_by_id(self, notification_id: UUID) -> Optional[Notification]:
        result = await self.session.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user(self, user_id: str) -> List[Notification]:
        result = await self.session.execute(
            select(Notification).where(Notification.user_id == user_id)
        )
        return result.scalars().all()  # type: ignore[no-any-return]

    async def list(self) -> List[Notification]:
        result = await self.session.execute(select(Notification))
        return result.scalars().all()  # type: ignore[no-any-return]

    async def delete(self, notification_id: UUID) -> None:
        notification = await self.get_by_id(notification_id)
        if notification:
            await self.session.delete(notification)
            await self.session.commit()

    async def update(
        self, notification_id: UUID, update_data: dict
    ) -> Optional[Notification]:
        notification = await self.get_by_id(notification_id)
        if not notification:
            return None
        for key, value in update_data.items():
            setattr(notification, key, value)
        await self.session.commit()
        await self.session.refresh(notification)
        return notification

    async def delete_notification(self, notification_id: UUID) -> bool:
        notification = await self.get_by_id(notification_id)
        if notification:
            await self.session.delete(notification)
            await self.session.commit()
            return True
        return False


class NotificationTemplateRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, template: NotificationTemplate) -> NotificationTemplate:
        self.session.add(template)
        await self.session.commit()
        await self.session.refresh(template)
        return template

    async def get_by_id(self, template_id: UUID) -> Optional[NotificationTemplate]:
        result = await self.session.execute(
            select(NotificationTemplate).where(NotificationTemplate.id == template_id)
        )
        return result.scalar_one_or_none()

    async def list(self) -> List[NotificationTemplate]:
        result = await self.session.execute(select(NotificationTemplate))
        return result.scalars().all()  # type: ignore[no-any-return]

    async def delete(self, template_id: UUID) -> None:
        template = await self.get_by_id(template_id)
        if template:
            await self.session.delete(template)
            await self.session.commit()

    async def update(
        self, template_id: UUID, update_data: dict
    ) -> Optional[NotificationTemplate]:
        template = await self.get_by_id(template_id)
        if not template:
            return None
        for key, value in update_data.items():
            setattr(template, key, value)
        await self.session.commit()
        await self.session.refresh(template)
        return template

    async def delete_template(self, template_id: UUID) -> bool:
        template = await self.get_by_id(template_id)
        if template:
            await self.session.delete(template)
            await self.session.commit()
            return True
        return False
