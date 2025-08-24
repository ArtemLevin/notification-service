from uuid import uuid4

import pytest


@pytest.fixture
def sample_user_id():
    return str(uuid4())


@pytest.fixture
def sample_template_data():
    return {
        "id": str(uuid4()),
        "name": "Test Template",
        "subject": "Welcome {{ user.name }}!",
        "body": "Hello {{ user.name }}, welcome!",
        "notification_type": "email",
        "variables": ["user.name"],
    }
