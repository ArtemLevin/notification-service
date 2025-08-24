.PHONY: help install test lint type-check ci-setup

help:
	@echo "Notification System Makefile"
	@echo "Usage:"
	@echo "  make install     - Install dependencies"
	@echo "  make test        - Run tests"
	@echo "  make lint        - Run linter"
	@echo "  make type-check  - Run mypy type checking"
	@echo "  make ci-setup    - Setup CI environment"

install:
	pip install -r requirements.txt

test:
	pytest tests/

lint:
	flake8 . --format=html --htmldir=lint-report

type-check:
	mypy .

ci-setup:
	pip install wemake-python-styleguide mypy pytest flake8-html
