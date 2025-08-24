"""Интеграционные тесты для Link Shortener сервиса"""

import time

import pytest


class TestLinkShortenerIntegration:
    """Интеграционные тесты для Link Shortener сервиса"""

    def test_full_shorten_redirect_flow(
        self,
        client: pytest.Fixture,
        sample_url: pytest.Fixture,
        cleanup_redis: pytest.Fixture,
    ) -> None:
        """Тест полного цикла: сокращение -> редирект"""
        # 1. Сокращаем URL
        response = client.post("/shorten", json={"original_url": sample_url})
        assert response.status_code == 200
        data = response.json()
        short_code = data["short_code"]

        # 2. Проверяем редирект
        response = client.get(f"/{short_code}", follow_redirects=False)
        assert response.status_code == 200
        assert response.json()["redirect"] == sample_url

    def test_shorten_get_stats_flow(
        self,
        client: pytest.Fixture,
        sample_url: pytest.Fixture,
        cleanup_redis: pytest.Fixture,
    ) -> None:
        """Тест цикла: сокращение -> статистика"""
        # 1. Сокращаем URL
        response = client.post("/shorten", json={"original_url": sample_url})
        assert response.status_code == 200
        data = response.json()
        short_code = data["short_code"]

        # 2. Получаем статистику
        response = client.get(f"/stats/{short_code}")
        assert response.status_code == 200
        stats = response.json()
        assert stats["short_code"] == short_code
        assert stats["original_url"] == sample_url
        assert stats["click_count"] == 0

    def test_click_counting(
        self,
        client: pytest.Fixture,
        sample_url: pytest.Fixture,
        cleanup_redis: pytest.Fixture,
    ) -> None:
        """Тест подсчета кликов"""
        # 1. Сокращаем URL
        response = client.post("/shorten", json={"original_url": sample_url})
        assert response.status_code == 200
        data = response.json()
        short_code = data["short_code"]

        # 2. Делаем несколько кликов
        for _ in range(3):
            client.get(f"/{short_code}")
            time.sleep(0.1)  # Небольшая задержка

        # 3. Проверяем счетчик кликов
        response = client.get(f"/stats/{short_code}")
        assert response.status_code == 200
        stats = response.json()
        assert stats["click_count"] == 3

    def test_multiple_urls_shortening(
        self, client: pytest.Fixture, cleanup_redis: pytest.Fixture
    ) -> None:
        """Тест сокращения нескольких URL"""
        urls = [
            "https://example1.com",
            "https://example2.com/page",
            "https://example3.com/test?param=value",
        ]

        short_codes = []
        for url in urls:
            response = client.post("/shorten", json={"original_url": url})
            assert response.status_code == 200
            data = response.json()
            short_codes.append(data["short_code"])
            assert data["original_url"] == url

        # Проверяем, что все коды уникальны
        assert len(set(short_codes)) == len(short_codes)

    def test_custom_alias_uniqueness(
        self, client: pytest.Fixture, cleanup_redis: pytest.Fixture
    ) -> None:
        """Тест уникальности кастомных алиасов"""
        custom_alias = "unique-test"

        # Создаем первый URL
        response1 = client.post(
            "/shorten",
            json={"original_url": "https://example1.com", "custom_alias": custom_alias},
        )
        assert response1.status_code == 200

        # Пытаемся создать второй URL с тем же алиасом
        response2 = client.post(
            "/shorten",
            json={"original_url": "https://example2.com", "custom_alias": custom_alias},
        )
        assert response2.status_code == 400

    def test_health_check_with_redis(self, client: pytest.Fixture) -> None:
        """Тест health check с проверкой Redis"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "link-shortener"
        # Может быть "connected" или "disconnected" в зависимости от окружения
        assert "redis" in data
