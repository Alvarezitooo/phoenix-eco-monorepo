# ✅ Phoenix Iris API - Dockerfile Monorepo Optimisé pour Railway
FROM python:3.11-slim

# 1. Configuration de base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=1.7.1 \
    POETRY_VIRTUALENVS_CREATE=false \
    PYTHONPATH="/app:/app/packages"

WORKDIR /app

# 2. Installation de Poetry
RUN pip install "poetry==$POETRY_VERSION"

# 3. Installation des dépendances
COPY apps/phoenix-iris-api/pyproject.toml apps/phoenix-iris-api/poetry.lock* ./
COPY packages/ /app/packages/
RUN poetry install --no-interaction --no-ansi --only main

# 4. Copie du code de l'application
COPY apps/phoenix-iris-api/ /app/

# 5. Configuration de production
RUN useradd --create-home --shell /bin/bash iris && \
    chown -R iris:iris /app
USER iris

# Le port est exposé dynamiquement
EXPOSE ${PORT:-8000}

# Le Health Check utilise aussi le port dynamique
HEALTHCHECK CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Le CMD utilise le port dynamique fourni par Railway
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "${PORT:-8000}"]
