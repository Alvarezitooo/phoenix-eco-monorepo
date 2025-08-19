# Phoenix Iris API - Production Dockerfile
FROM python:3.11-slim

# Métadonnées
LABEL maintainer="Phoenix DevSecOps Team"
LABEL description="Iris AI Assistant API for Phoenix Ecosystem"
LABEL version="2.0.0"

# Variables d'environnement
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Répertoire de travail
WORKDIR /app

# Installation des dépendances système
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Installation de Poetry
RUN pip install poetry==1.7.1

# Configuration Poetry
RUN poetry config virtualenvs.create false

# Copier les fichiers de configuration
COPY pyproject.toml poetry.lock* ./

# Installation des dépendances Python
RUN poetry install --only main --no-interaction --no-ansi

# Copier le code source
COPY . .

# Créer un utilisateur non-root pour la sécurité
RUN useradd --create-home --shell /bin/bash iris && \
    chown -R iris:iris /app
USER iris

# Vérification de santé
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:$PORT/health || exit 1

# Port d'exposition (Railway utilise la variable PORT)
EXPOSE 8000

# Commande de démarrage
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]