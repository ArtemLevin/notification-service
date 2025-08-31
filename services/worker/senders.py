import structlog

logger = structlog.get_logger(__name__)


class EmailSender:
    async def send(self, to: str, subject: str, body: str) -> None:
        logger.info("EMAIL_SENT", to=to, subject=subject)


class SmsSender:
    async def send(self, to: str, subject: str, body: str) -> None:
        logger.info("SMS_SENT", to=to)


class PushSender:
    async def send(self, to: str, subject: str, body: str) -> None:
        logger.info("PUSH_SENT", to=to, title=subject)
