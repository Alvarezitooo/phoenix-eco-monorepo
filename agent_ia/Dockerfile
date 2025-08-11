# 🧠 Phoenix Agents IA - Dockerfile optimisé DevSecOps
FROM python:3.11-slim

# Métadonnées sécurité
LABEL maintainer="Phoenix DevSecOps Team"
LABEL version="1.0"
LABEL description="Phoenix AI Agents with Ollama integration"

# Variables d'environnement sécurisées
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Utilisateur non-root pour sécurité
RUN groupadd -r phoenix && useradd -r -g phoenix phoenix

# Installation dépendances système
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Répertoire de travail
WORKDIR /app

# Copie et installation requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code source
COPY . .

# Changement de propriétaire
RUN chown -R phoenix:phoenix /app

# Répertoire pour logs
RUN mkdir -p /app/logs && chown phoenix:phoenix /app/logs

# Port d'exposition
EXPOSE 8001

# Utilisateur non-root
USER phoenix

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:8001/health || exit 1

# Script de démarrage
COPY --chown=phoenix:phoenix start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Commande de démarrage
CMD ["./start.sh"]