import logging
import time
from typing import Callable

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from .settings import settings


def setup_logging() -> None:
    root_logger = logging.getLogger()
    for root_handler in root_logger.handlers[:]:
        root_logger.removeHandler(root_handler)

    handler = logging.StreamHandler()
    root_logger.addHandler(handler)
    root_logger.setLevel(settings.log_level)

    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", key="timestamp"),
        structlog.processors.format_exc_info,
    ]

    if settings.log_json_format:
        processors = shared_processors + [
            structlog.processors.JSONRenderer(
                ensure_ascii=False,
                indent=None,
                sort_keys=False,
            ),
        ]
    else:
        processors = shared_processors + [structlog.dev.ConsoleRenderer()]

    structlog.configure(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    logging.getLogger("uvicorn").handlers = []
    logging.getLogger("uvicorn.access").handlers = []
    logging.getLogger("uvicorn").propagate = True

    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("aioredis").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        logger = structlog.get_logger("http")

        try:
            response = await call_next(request)
            process_time = time.time() - start_time

            logger.info(
                "Successful request",
                method=request.method,
                path=request.url.path,
                query=str(request.url.query),
                client_ip=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
                status_code=response.status_code,
                process_time=round(process_time, 3),
            )

            return response

        except Exception as error:
            process_time = time.time() - start_time

            logger.error(
                "Request failed",
                method=request.method,
                path=request.url.path,
                query=str(request.url.query),
                client_ip=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
                error=str(error),
                process_time=round(process_time, 3),
            )
            raise
