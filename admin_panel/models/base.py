from enum import Enum
from datetime import datetime
from uuid import UUID as PyUUID, uuid4

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs


class Status(Enum):
    """Статусы отправки"""
    
    pending: str = "pending"
    sent: str = "sent"
    failed: str = "failed"


class RepeatInterval(str, Enum):
    """Статусы интервальной отправки"""

    none = "none"       
    daily = "daily"     
    weekly = "weekly"   
    monthly = "monthly" 


class Base(AsyncAttrs, DeclarativeBase):
    id: Mapped[PyUUID] = mapped_column(primary_key=True, default=uuid4)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
