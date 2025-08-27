from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from api.v1 import router as v1_router
from core.db import dispose_db, init_db
from core.logging_settings import LoggingMiddleware, setup_logging
from fastapi import FastAPI
from models.base import BaseResponse

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    setup_logging()
    logger.info("Приложение запускается...")
    await init_db()
    logger.info("Соединение с базой данных открыто")
    yield
    await dispose_db()
    logger.info("Соединение с базой данных закрыто")
    logger.info("Приложение завершает работу...")


app = FastAPI(title="Notification API", version="0.1.0", lifespan=lifespan)
app.include_router(v1_router)

app.add_middleware(LoggingMiddleware)


@app.get(
    "/health", description="Health Check", response_model=BaseResponse, tags=["Common"]
)
async def health_check() -> BaseResponse:
    return BaseResponse(success=True, message="Ok")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
