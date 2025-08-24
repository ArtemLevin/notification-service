import os

import pytest
import redis
from fastapi.testclient import TestClient

from ..main import app


@pytest.fixture  # type: ignore[misc]
def client() -> TestClient:
    """Фикстура для тестового клиента FastAPI"""
    return TestClient(app)


@pytest.fixture  # type: ignore[misc]
def sample_url() -> str:
    """Фикстура с тестовым URL"""
    return "https://example.com/test-page"


@pytest.fixture  # type: ignore[misc]
def redis_client() -> pytest.Fixture[None]:
    """Фикстура для Redis клиента"""
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", 6379))
    client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
    yield client
    # Очистка после тестов
    client.flushdb()


@pytest.fixture  # type: ignore[misc]
def cleanup_redis(redis_client: redis.Redis) -> pytest.Fixture[None]:
    """Фикстура для очистки Redis перед и после тестов"""
    redis_client.flushdb()
    yield
    redis_client.flushdb()
