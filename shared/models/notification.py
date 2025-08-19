from enum import Enum
from pydantic import BaseModel, Field
from typing import  List, Dict, Any
from uuid import UUID
from datetime import datetime

class NotificationType(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    INSTANT = "instant"

class DeliveryStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    DELIVERED = "delivered"

class NotificationTemplate(BaseModel):
    id: UUID
    name: str
    subject: str
    body: str
    notification_type: NotificationType
    variables: List[str] = Field(default_factory=list)

class NotificationCreate(BaseModel):
    template_id: UUID
    recipients: List[str]
    notification_type: NotificationType
    scheduled_time: datetime | None = None
    is_recurring: bool = False
    recurrence_pattern: str | None = None
    data: Dict[str, Any] = Field(default_factory=dict)

class NotificationEvent(BaseModel):
    event_type: str
    user_id: str | None = None
    data: Dict[str, Any] = Field(default_factory=dict)

class NotificationMessage(BaseModel):
    user_id: str
    template_id: UUID
    subject: str
    body: str
    notification_type: NotificationType
    data: Dict[str, Any] = Field(default_factory=dict)

class Notification(BaseModel):
    id: UUID
    user_id: str
    template_id: UUID
    subject: str
    body: str
    notification_type: NotificationType
    status: DeliveryStatus
    sent_at: datetime | None = None
    delivered_at: datetime | None = None
    error_message: str | None = None
    data: Dict[str, Any] = Field(default_factory=dict)