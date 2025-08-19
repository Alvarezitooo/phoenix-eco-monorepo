# ✅ Phoenix Backend Unifié - Dockerfile Monorepo Optimisé pour Railway (avec Root Directory = apps/phoenix-backend-unified)
FROM python:3.11-slim

# 1. Configuration de base
ENV PYTHONDONTWRITEBYTECODE=1     PYTHONUNBUFFERED=1     PIP_NO_CACHE_DIR=1     PYTHONPATH="/app:/app/packages"

WORKDIR /app

# 2. Installation des dépendances
COPY requirements.txt .
RUN pip install -r requirements.txt

# 3. Copie des packages partagés
COPY packages/ /app/packages/

# 4. Copie du code de l'application
COPY . /app/

# 5. Configuration de production
RUN useradd --create-home --shell /bin/bash phoenix &&     chown -R phoenix:phoenix /app
USER phoenix

# Le port est exposé dynamiquement
EXPOSE ${PORT:-8000}

# Le Health Check utilise aussi le port dynamique
HEALTHCHECK CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Le CMD utilise le port dynamique fourni par Railway
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "${PORT:-8000}"]
