# Makefile Phoenix Monorepo
# Automatisation rapide pour dev

.PHONY: fmt lint test smoke

fmt:
	poetry run black packages apps tests

lint:
	poetry run ruff check packages apps tests
	poetry run mypy packages apps

test:
	poetry run pytest

smoke:
	poetry run pytest -q tests/test_ui_imports.py