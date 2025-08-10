PYTHON ?= 3.11

.PHONY: bootstrap lint typecheck test clean pre-commit

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

clean:
	rm -rf **/__pycache__ **/.pytest_cache **/.mypy_cache **/.ruff_cache || true

pre-commit:
	pre-commit run --all-files

