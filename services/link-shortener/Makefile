.PHONY: test test-unit test-integration test-cov clean-test

# Запуск всех тестов
test:
	pytest tests/ -v

# Запуск unit тестов
test-unit:
	pytest tests/test_main.py -v

# Запуск интеграционных тестов
test-integration:
	pytest tests/test_integration.py -v

# Запуск тестов с coverage
test-cov:
	pytest tests/ --cov=. --cov-report=html --cov-report=term

# Очистка тестовых артефактов
clean-test:
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +

# Установка тестовых зависимостей
install-test:
	pip install -r requirements-test.txt