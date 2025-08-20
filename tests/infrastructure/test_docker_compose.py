import pytest
import subprocess
import time
import requests
import os


class TestDockerComposeInfrastructure:
    """Тесты для проверки инфраструктурных сервисов"""

    def test_postgres_connection(self):
        """Тест подключения к PostgreSQL"""
        # Проверяем, что контейнер запущен
        result = subprocess.run([
            "docker", "inspect", "notification-postgres", "--format", "{{.State.Running}}"
        ], capture_output=True, text=True)

        assert result.returncode == 0
        assert result.stdout.strip() == "true"

    def test_redis_connection(self):
        """Тест подключения к Redis"""
        result = subprocess.run([
            "docker", "inspect", "notification-redis", "--format", "{{.State.Running}}"
        ], capture_output=True, text=True)

        assert result.returncode == 0
        assert result.stdout.strip() == "true"

    def test_rabbitmq_connection(self):
        """Тест подключения к RabbitMQ"""
        result = subprocess.run([
            "docker", "inspect", "notification-rabbitmq", "--format", "{{.State.Running}}"
        ], capture_output=True, text=True)

        assert result.returncode == 0
        assert result.stdout.strip() == "true"

    def test_link_shortener_health(self):
        """Тест health check Link Shortener"""
        # Ждем запуск сервиса
        time.sleep(10)

        port = os.getenv('LINK_SHORTENER_PORT', '8001')

        try:
            response = requests.get(f"http://localhost:{port}/health", timeout=5)
            assert response.status_code == 200
            assert response.json()["status"] == "ok"
        except requests.exceptions.RequestException:
            pytest.fail("Link Shortener service is not responding")

    def test_elasticsearch_connection(self):
        """Тест подключения к Elasticsearch"""
        try:
            response = requests.get("http://localhost:9200", timeout=5)
            assert response.status_code == 200
        except requests.exceptions.RequestException:
            pytest.fail("Elasticsearch is not responding")

    def test_kibana_connection(self):
        """Тест подключения к Kibana"""
        try:
            response = requests.get("http://localhost:5601", timeout=5)
            assert response.status_code == 200
        except requests.exceptions.RequestException:
            pytest.fail("Kibana is not responding")