import pytest
from fastapi.testclient import TestClient
from ..main import app
import redis
import os

@pytest.fixture
def client():
    """Фикстура для тестового клиента FastAPI"""
    return TestClient(app)

@pytest.fixture
def sample_url():
    """Фикстура с тестовым URL"""
    return "https://example.com/test-page"

@pytest.fixture
def redis_client():
    """Фикстура для Redis клиента"""
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", 6379))
    client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
    yield client
    # Очистка после тестов
    client.flushdb()

@pytest.fixture
def cleanup_redis(redis_client):
    """Фикстура для очистки Redis перед и после тестов"""
    redis_client.flushdb()
    yield
    redis_client.flushdb()