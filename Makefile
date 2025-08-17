PYTHON ?= 3.11

.PHONY: bootstrap lint typecheck test smoke clean pre-commit ci

bootstrap:
	python -m pip install --upgrade pip poetry
	poetry install --with dev || true
	pre-commit install || true

lint:
	ruff check .

typecheck:
	mypy .

test:
	pytest -q

smoke:
	python3 scripts/smoke_test.py

clean:
	rm -rf **/__pycache__ **/.pytest_cache **/.mypy_cache **/.ruff_cache || true

pre-commit:
	pre-commit run --all-files

ci: lint typecheck test smoke

