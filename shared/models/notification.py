from datetime import datetime
from typing import Any, Dict, List, Union
from uuid import UUID

from pydantic import BaseModel, Field

from shared.enums.delivery import DeliveryStatus, NotificationType


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
    scheduled_time: Union[datetime, None] = None
    is_recurring: bool = False
    recurrence_pattern: Union[str, None] = None
    data: Dict[str, Any] = Field(default_factory=dict)


class NotificationEvent(BaseModel):
    event_type: str
    user_id: Union[str, None] = None
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
    sent_at: Union[datetime, None] = None
    delivered_at: Union[datetime, None] = None
    error_message: Union[str, None] = None
    data: Dict[str, Any] = Field(default_factory=dict)
