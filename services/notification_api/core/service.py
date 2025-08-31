from typing import List, Dict, Any
from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from core.db import Notification, NotificationTemplate, get_db_session
from core.repository import NotificationRepository, NotificationTemplateRepository
from core.broker import publish_message
from core.settings import settings
from core.shortener import shorten
from models.delivery import QueueName, NotificationType
from models.notification import (
    NotificationCreate,
    NotificationTemplateBase,
    NotificationEvent,
)


class NotificationService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.notification_repo = NotificationRepository(session)
        self.template_repo = NotificationTemplateRepository(session)

    # === helpers ===
    async def _all_recipient_ids(self) -> List[str]:
        # admin_panel создаёт таблицу "recipients" (UUID PK). Читаем напрямую.
        result = await self.session.execute(text("SELECT id::text FROM recipients"))
        return [row[0] for row in result.all()]

    async def _prepare_body(self, body: str, data: Dict[str, Any]) -> str:
        # упрощённая подстановка коротких ссылок: data["links"] = ["http://...", ...]
        links = data.get("links") or []
        if isinstance(links, list) and links:
            short_links = []
            for url in links:
                short_links.append(await shorten(str(url)))
            # простой протокол замены {{linkN}}
            for i, s in enumerate(short_links, start=1):
                body = body.replace(f"{{{{link{i}}}}}", s)
        return body

    def _queue_for_type(self, ntype: NotificationType) -> QueueName:
        return {
            NotificationType.EMAIL: QueueName.EMAIL,
            NotificationType.SMS: QueueName.SMS,
            NotificationType.PUSH: QueueName.PUSH,
            NotificationType.INSTANT: QueueName.INSTANT,
        }[ntype]

    # === основной поток ===
    async def send_notification(self, data: NotificationCreate) -> List[Notification]:
        notifications: List[Notification] = []
        template = await self.template_repo.get_by_id(data.template_id)
        if not template:
            raise ValueError("Шаблон не найден")

        recipients = data.recipients
        if len(recipients) == 1 and recipients[0].upper() == "ALL":
            recipients = await self._all_recipient_ids()

        for user_id in recipients:
            body = await self._prepare_body(template.body, data.data)
            notification = Notification(
                user_id=user_id,
                template_id=data.template_id,
                subject=template.subject,
                body=body,
                notification_type=data.notification_type,
                status="pending",
                data=data.data,
                scheduled_time=data.scheduled_time,
                is_recurring=data.is_recurring,
                recurrence_pattern=data.recurrence_pattern,
            )
            created = await self.notification_repo.create(notification)
            notifications.append(created)

            # публикуем сразу, если не отложено/не повторяющееся
            if not data.scheduled_time and not data.is_recurring:
                await publish_message(
                    self._queue_for_type(data.notification_type),
                    {
                        "notification_id": str(created.id),
                        "user_id": user_id,
                        "template_id": str(data.template_id),
                        "subject": template.subject,
                        "body": body,
                        "notification_type": data.notification_type.value,
                        "data": data.data,
                    },
                )

        return notifications

    # событие от внешних сервисов (свободный формат)
    async def process_event(self, event: NotificationEvent) -> Dict[str, Any]:
        # Простой роутинг:
        payload = event.data.copy()
        template_id = payload.get("template_id")
        ntype = payload.get("notification_type")
        recipients = payload.get("recipients") or ([event.user_id] if event.user_id else [])

        if not template_id or not ntype or not recipients:
            # простой маппинг для примеров:
            # user_registered -> welcome шаблон / email
            # new_movie -> recommendation шаблон / push всем
            if event.event_type == "user_registered" and event.user_id:
                payload["notification_type"] = NotificationType.EMAIL.value
                payload["recipients"] = [event.user_id]
                # template_id должен прийти извне; тут можно захардкодить/найти по имени
            elif event.event_type == "new_movie":
                payload["notification_type"] = NotificationType.PUSH.value
                payload["recipients"] = ["ALL"]

        create = NotificationCreate(
            template_id=UUID(payload["template_id"]),
            recipients=list(map(str, payload["recipients"])),
            notification_type=NotificationType(payload["notification_type"]),
            scheduled_time=payload.get("scheduled_time"),
            is_recurring=payload.get("is_recurring", False),
            recurrence_pattern=payload.get("recurrence_pattern"),
            data=payload.get("data", {}),
        )
        created = await self.send_notification(create)
        return {"created": [str(n.id) for n in created]}

    # === выдача пользователю уведомлений ===
    async def get_user_notifications(self, user_id: str) -> List[Notification]:
        return await self.notification_repo.get_by_user(user_id)

    # === CRUD уведомлений ===
    async def get_notification(self, notification_id: UUID) -> Notification:
        notification = await self.notification_repo.get_by_id(notification_id)
        if not notification:
            raise ValueError("Уведомление не найдено")
        return notification

    async def list_notifications(self) -> List[Notification]:
        return await self.notification_repo.list()

    async def update_notification(self, notification_id: UUID, update_data: dict) -> Notification:
        notification = await self.notification_repo.update(notification_id, update_data)
        if not notification:
            raise ValueError("Уведомление не найдено для обновления")
        return notification

    async def delete_notification(self, notification_id: UUID) -> None:
        deleted = await self.notification_repo.delete_notification(notification_id)
        if not deleted:
            raise ValueError("Уведомление не найдено для удаления")

    # === CRUD шаблонов ===
    async def get_templates(self) -> List[NotificationTemplate]:
        return await self.template_repo.list()

    async def get_template(self, template_id: UUID) -> NotificationTemplate:
        template = await self.template_repo.get_by_id(template_id)
        if not template:
            raise ValueError("Шаблон не найден")
        return template

    async def create_template(self, template_data: NotificationTemplateBase) -> NotificationTemplate:
        templates = await self.template_repo.list()
        if any(t.name == template_data.name for t in templates):
            raise ValueError("Шаблон с таким именем уже существует")
        template = NotificationTemplate(**template_data.model_dump())
        return await self.template_repo.create(template)

    async def update_template(self, template_id: UUID, update_data: dict) -> NotificationTemplate:
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
