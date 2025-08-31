from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import Column, DateTime
from sqlmodel import SQLModel, Field

from .settings import settings


class Recipient(SQLModel, table=True):
    __tablename__ = "recipients"
    id: UUID = Field(primary_key=True)
    name: str
    email: str


class Notification(SQLModel, table=True):
    __tablename__ = "notifications"
    id: UUID = Field(primary_key=True)
    user_id: str
    template_id: UUID
    subject: str
    body: str
    notification_type: str
    status: str
    sent_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    delivered_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    error_message: Optional[str] = None
    # scheduling
    scheduled_time: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    is_recurring: bool = False
    recurrence_pattern: Optional[str] = None


engine = create_async_engine(settings.database_url, pool_pre_ping=True, echo=False)
AsyncDBSession = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
