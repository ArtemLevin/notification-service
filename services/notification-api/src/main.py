from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI

from api.v1 import router as v1_router
from core.logging_settings import setup_logging, LoggingMiddleware

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("Приложение запускается...")
    yield
    logger.info("Приложение завершает работу...")


app = FastAPI(title="Notification API", version="0.1.0", lifespan=lifespan)
app.include_router(v1_router)

app.add_middleware(LoggingMiddleware)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
