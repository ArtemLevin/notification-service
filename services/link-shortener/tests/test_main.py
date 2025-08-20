"""Базовые unit тесты для Link Shortener сервиса"""

import pytest
from fastapi import HTTPException
from ..main import app, shorten_link, redirect_link
from pydantic import ValidationError


class TestLinkShortenerUnit:
    """Unit тесты для Link Shortener сервиса"""

    def test_root_endpoint(self, client):
        """Тест корневого эндпоинта"""
        response = client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()
        assert response.json()["message"] == "Link Shortener Service"

    def test_health_check_endpoint(self, client):
        """Тест эндпоинта здоровья"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "service" in data
        assert data["service"] == "link-shortener"

    def test_shorten_link_valid_url(self, client, sample_url, cleanup_redis):
        """Тест сокращения валидного URL"""
        response = client.post("/shorten", json={"original_url": sample_url})
        assert response.status_code == 200
        data = response.json()
        assert "short_code" in data
        assert "original_url" in data
        assert "short_url" in data
        assert data["original_url"] == sample_url
        assert len(data["short_code"]) > 0

    def test_shorten_link_with_custom_alias(self, client, sample_url, cleanup_redis):
        """Тест сокращения URL с кастомным алиасом"""
        custom_alias = "my-custom-link"
        response = client.post("/shorten", json={
            "original_url": sample_url,
            "custom_alias": custom_alias
        })
        assert response.status_code == 200
        data = response.json()
        assert data["short_code"] == custom_alias
        assert data["original_url"] == sample_url

    def test_shorten_link_duplicate_custom_alias(self, client, sample_url, cleanup_redis):
        """Тест попытки создания дубликата кастомного алиаса"""
        custom_alias = "duplicate-test"
        # Создаем первый URL с алиасом
        client.post("/shorten", json={
            "original_url": sample_url,
            "custom_alias": custom_alias
        })

        # Пытаемся создать второй URL с тем же алиасом
        response = client.post("/shorten", json={
            "original_url": "https://another-example.com",
            "custom_alias": custom_alias
        })
        assert response.status_code == 400

    def test_redirect_nonexistent_link(self, client, cleanup_redis):
        """Тест редиректа несуществующего короткого URL"""
        response = client.get("/nonexistent123")
        assert response.status_code == 404

    def test_get_stats_nonexistent_link(self, client, cleanup_redis):
        """Тест получения статистики несуществующего короткого URL"""
        response = client.get("/stats/nonexistent123")
        assert response.status_code == 404

    def test_shorten_link_invalid_url(self, client, cleanup_redis):
        """Тест сокращения невалидного URL"""
        response = client.post("/shorten", json={"original_url": "invalid-url"})
        # Может быть как 200 (если не валидируем), так и 422 (если валидируем)
        # В данном случае сервис не валидирует URL, поэтому 200
        assert response.status_code == 200


class TestLinkShortenerModels:
    """Тесты моделей данных"""

    def test_link_create_model_valid(self):
        """Тест валидной модели LinkCreate"""
        from ..main import LinkCreate
        data = {"original_url": "https://example.com"}
        model = LinkCreate(**data)
        assert model.original_url == data["original_url"]
        assert model.custom_alias is None

    def test_link_create_model_with_alias(self):
        """Тест модели LinkCreate с кастомным алиасом"""
        from ..main import LinkCreate
        data = {"original_url": "https://example.com", "custom_alias": "test"}
        model = LinkCreate(**data)
        assert model.original_url == data["original_url"]
        assert model.custom_alias == data["custom_alias"]

    def test_link_response_model(self):
        """Тест модели LinkResponse"""
        from ..main import LinkResponse
        from datetime import datetime
        data = {
            "short_code": "abc123",
            "original_url": "https://example.com",
            "short_url": "http://localhost:8001/abc123",
            "created_at": datetime.utcnow()
        }
        model = LinkResponse(**data)
        assert model.short_code == data["short_code"]
        assert model.original_url == data["original_url"]
        assert model.short_url == data["short_url"]