import json
from typing import Any, Dict

import aio_pika

from core.settings import settings
from models.delivery import QueueName


def _amqp_url() -> str:
    return (
        f"amqp://{settings.rabbitmq_user}:{settings.rabbitmq_password}"
        f"@{settings.rabbitmq_host}:{settings.rabbitmq_port}/{settings.rabbitmq_vhost.lstrip('/')}"
    )


async def publish_message(queue_name: QueueName, message: Dict[str, Any]) -> None:
    connection = await aio_pika.connect_robust(_amqp_url())
    try:
        channel = await connection.channel()
        # гарантируем durable очередь
        queue = await channel.declare_queue(queue_name.value, durable=True)
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
