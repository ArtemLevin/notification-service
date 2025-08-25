from enum import Enum


class NotificationType(str, Enum):
    """Типы уведомлений"""

    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    INSTANT = "instant"


class DeliveryStatus(str, Enum):
    """Статусы доставки уведомлений"""

    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    DELIVERED = "delivered"


class PriorityLevel(str, Enum):
    """Уровни приоритета уведомлений"""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class QueueName(str, Enum):
    """Названия очередей сообщений"""

    EMAIL = "email_notifications"
    SMS = "sms_notifications"
    PUSH = "push_notifications"
    INSTANT = "instant_notifications"
    DEAD_LETTER = "dead_letter_queue"
