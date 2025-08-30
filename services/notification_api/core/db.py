from datetime import datetime
from typing import Any, AsyncGenerator, Dict, List, Optional
from uuid import UUID, uuid4

from core.settings import settings
from models.delivery import DeliveryStatus, NotificationType
from models.notification import NotificationBase, NotificationTemplateBase
from sqlalchemy import ARRAY, Column, DateTime, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.ext.mutable import MutableDict, MutableList
from sqlmodel import Field, Relationship, SQLModel


class NotificationTemplate(
    NotificationTemplateBase, table=True
):  # type: ignore[call-arg]
    __tablename__ = "notification_templates"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True, nullable=False)
    subject: str = Field(nullable=False)
    body: str = Field(nullable=False)
    notification_type: NotificationType = Field(nullable=False)
    variables: List[str] = Field(
        default_factory=list, sa_type=MutableList.as_mutable(ARRAY(String))
    )

    notifications: List["Notification"] = Relationship(back_populates="template")


class Notification(NotificationBase, table=True):  # type: ignore[call-arg]
    __tablename__ = "notifications"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    subject: str = Field(nullable=False)
    body: str = Field(nullable=False)
    notification_type: NotificationType = Field(nullable=False)
    status: DeliveryStatus = Field(default=DeliveryStatus.PENDING)
    sent_at: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=True))
    )
    delivered_at: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=True))
    )
    template_id: UUID = Field(foreign_key="notification_templates.id", nullable=False)

    template: NotificationTemplate = Relationship(back_populates="notifications")
    data: Dict[str, Any] = Field(
        default_factory=dict,
        sa_type=MutableDict.as_mutable(JSONB),
    )


# Создаем асинхронный движок
engine: AsyncEngine = create_async_engine(
    settings.database_url,
    pool_pre_ping=True,
    echo=settings.database_echo,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
)

# Создаем асинхронную фабрику сессий
AsyncDBSession = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def init_db() -> None:
    """Асинхронное создание таблиц"""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def dispose_db() -> None:
    """Асинхронное закрытие соединения с БД"""
    await engine.dispose()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncDBSession() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
