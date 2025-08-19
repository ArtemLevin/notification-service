"""Unit tests for shared models"""

from shared.models.notification import NotificationTemplate, NotificationType


def test_notification_template_creation(sample_template_data):
    """Тест создания шаблона уведомления"""
    template = NotificationTemplate(**sample_template_data)

    assert template.id == sample_template_data["id"]
    assert template.name == sample_template_data["name"]
    assert template.notification_type == NotificationType.EMAIL