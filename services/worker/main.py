import asyncio
import json
from datetime import datetime, timezone
from typing import Any, Dict

import aio_pika
import structlog
from sqlalchemy import select, update
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession

from .settings import settings
from .db import AsyncDBSession, Notification, Recipient
from .senders import EmailSender, SmsSender, PushSender
from .utils import render_template

logger = structlog.get_logger(__name__)


def amqp_url() -> str:
    return (
        f"amqp://{settings.rabbitmq_user}:{settings.rabbitmq_password}"
        f"@{settings.rabbitmq_host}:{settings.rabbitmq_port}/{settings.rabbitmq_vhost.lstrip('/')}"
    )


async def _ensure_db() -> None:
    async with AsyncDBSession() as s:
        async with s.begin():
            await s.run_sync(SQLModel.metadata.create_all)


async def handle_delivery(
    session: AsyncSession, payload: Dict[str, Any], channel: aio_pika.Channel
) -> None:
    """Сбор персонализации и 'отправка'."""
    user_id = payload["user_id"]
    q = await session.execute(select(Recipient).where(Recipient.id == user_id))
    recipient = q.scalar_one_or_none()

    to_email = getattr(recipient, "email", None)
    name = getattr(recipient, "name", "")

    context = {"user": {"id": user_id, "name": name, "email": to_email}, "data": payload.get("data", {})}
    body = await render_template(payload["body"], context)
    subject = payload["subject"]

    ntype = payload["notification_type"]
    if ntype == "email":
        await EmailSender().send(to_email or "", subject, body)
    elif ntype == "sms":
        await SmsSender().send(user_id, subject, body)
    elif ntype == "push":
        await PushSender().send(user_id, subject, body)

    # помечаем как отправленное
    await session.execute(
        update(Notification)
        .where(Notification.id == payload["notification_id"])
        .values(status="sent", sent_at=datetime.now(timezone.utc))
    )
    await session.commit()


async def consume_named(queue_name: str) -> None:
    connection = await aio_pika.connect_robust(amqp_url())
    try:
        channel = await connection.channel()
        queue = await channel.declare_queue(queue_name, durable=True)

        async with AsyncDBSession() as session:
            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    async with message.process():
                        try:
                            payload = json.loads(message.body.decode("utf-8"))
                            await handle_delivery(session, payload, channel)
                        except Exception as e:
                            logger.exception("WORKER_HANDLE_ERROR", error=str(e))
    finally:
        await connection.close()


async def scheduler_loop() -> None:
    """Планировщик: берёт отложенные/повторяющиеся уведомления и публикует в их очереди."""
    await asyncio.sleep(1)
    while True:
        try:
            async with AsyncDBSession() as session:
                now = datetime.now(timezone.utc)
                # отложенные: наступило время и статус pending
                result = await session.execute(
                    select(Notification).where(
                        Notification.scheduled_time.is_not(None),
                        Notification.scheduled_time <= now,
                        Notification.status == "pending",
                    )
                )
                due = list(result.scalars().all())

                for n in due:
                    msg = {
                        "notification_id": str(n.id),
                        "user_id": n.user_id,
                        "template_id": str(n.template_id),
                        "subject": n.subject,
                        "body": n.body,
                        "notification_type": n.notification_type,
                        "data": {},
                    }
                    # публикуем
                    await _publish(n.notification_type, msg)
                    # если повторяющееся — переносим на следующий раз
                    if n.is_recurring and n.recurrence_pattern:
                        nxt = _next_run(now, n.recurrence_pattern)
                        await session.execute(
                            update(Notification)
                            .where(Notification.id == n.id)
                            .values(scheduled_time=nxt)
                        )
                    else:
                        # иначе просто оставим — воркер выставит status=sent
                        pass
                await session.commit()
        except Exception as e:
            logger.exception("SCHEDULER_ERROR", error=str(e))
        await asyncio.sleep(settings.scheduler_poll_seconds)


def _next_run(now: datetime, pattern: str) -> datetime:
    # поддержка простых паттернов: "weekly:FRI", "yearly:MM-DD"
    if pattern.startswith("weekly:"):
        # на следующую указанную неделю
        day = pattern.split(":", 1)[1].upper()
        # map: MON=0..SUN=6
        m = {"MON":0,"TUE":1,"WED":2,"THU":3,"FRI":4,"SAT":5,"SUN":6}
        target = m.get(day, 4)
        delta = (target - now.weekday()) % 7
        delta = 7 if delta == 0 else delta
        return now.replace(hour=9, minute=0, second=0, microsecond=0) + asyncio.timedelta(days=delta)  # type: ignore[attr-defined]
    if pattern.startswith("yearly:"):
        mmdd = pattern.split(":", 1)[1]
        mm, dd = map(int, mmdd.split("-", 1))
        y = now.year if (now.month, now.day) < (mm, dd) else now.year + 1
        return datetime(y, mm, dd, 9, 0, tzinfo=now.tzinfo)
    # по умолчанию через неделю
    return now + asyncio.timedelta(days=7)  # type: ignore[attr-defined]


async def _publish(ntype: str, message: Dict[str, Any]) -> None:
    mapping = {"email": "email_notifications", "sms": "sms_notifications", "push": "push_notifications"}
    qname = mapping.get(ntype, "email_notifications")
    connection = await aio_pika.connect_robust(amqp_url())
    try:
        channel = await connection.channel()
        queue = await channel.declare_queue(qname, durable=True)
        await channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps(message, ensure_ascii=False).encode("utf-8"),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                content_type="application/json",
            ),
            routing_key=queue.name,
        )
    finally:
        await connection.close()


async def main() -> None:
    await _ensure_db()
    tasks = [
        asyncio.create_task(consume_named("email_notifications")),
        asyncio.create_task(consume_named("sms_notifications")),
        asyncio.create_task(consume_named("push_notifications")),
        asyncio.create_task(scheduler_loop()),
    ]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
