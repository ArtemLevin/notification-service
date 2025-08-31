import asyncio
import json
import hmac
import hashlib
from typing import Dict, Set

import aio_pika
import structlog
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException

from .settings import settings

logger = structlog.get_logger(__name__)
app = FastAPI(title="WebSocket Server")


def amqp_url() -> str:
    return (
        f"amqp://{settings.rabbitmq_user}:{settings.rabbitmq_password}"
        f"@{settings.rabbitmq_host}:{settings.rabbitmq_port}/{settings.rabbitmq_vhost.lstrip('/')}"
    )


# Пул подключений по user_id
connections: Dict[str, Set[WebSocket]] = {}


def authorized(user_id: str, token: str) -> bool:
    expected = hmac.new(
        settings.websocket_secret.encode(), user_id.encode(), hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, token)


@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket, user_id: str, token: str) -> None:
    if not authorized(user_id, token):
        await ws.close(code=4401)
        return

    await ws.accept()
    connections.setdefault(user_id, set()).add(ws)
    logger.info("WS_CONNECTED", user_id=user_id)

    try:
        while True:
            # клиент сообщения не шлёт — просто держим соединение
            await asyncio.sleep(60)
    except WebSocketDisconnect:
        pass
    finally:
        connections[user_id].discard(ws)
        if not connections[user_id]:
            del connections[user_id]
        logger.info("WS_DISCONNECTED", user_id=user_id)


async def consumer_loop() -> None:
    """Читает instant_notifications и пушит по ws."""
    connection = await aio_pika.connect_robust(amqp_url())
    try:
        channel = await connection.channel()
        queue = await channel.declare_queue("instant_notifications", durable=True)
        async with queue.iterator() as qit:
            async for message in qit:
                async with message.process():
                    try:
                        payload = json.loads(message.body.decode("utf-8"))
                        uid = payload["user_id"]
                        text = json.dumps(
                            {
                                "subject": payload["subject"],
                                "body": payload["body"],
                                "data": payload.get("data", {}),
                            },
                            ensure_ascii=False,
                        )
                        for ws in connections.get(uid, set()).copy():
                            await ws.send_text(text)
                    except Exception as e:
                        logger.exception("WS_CONSUMER_ERROR", error=str(e))
    finally:
        await connection.close()


@app.on_event("startup")
async def on_startup() -> None:
    asyncio.create_task(consumer_loop())
