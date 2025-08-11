# 🌅 Phoenix Rise - Dockerfile DevSecOps
FROM python:3.11-slim

# Métadonnées sécurité
LABEL maintainer="Phoenix DevSecOps Team"
LABEL version="1.0"
LABEL description="Phoenix Rise - Coaching mental et développement personnel IA"

# Variables d'environnement sécurisées
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Utilisateur non-root pour sécurité
RUN groupadd -r phoenix && useradd -r -g phoenix phoenix

# Installation dépendances système
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Répertoire de travail
WORKDIR /app

# Copie et installation requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Installation streamlit et dépendances coaching
RUN pip install streamlit>=1.28.0 plotly pandas

# Copie du code source
COPY . .

# Changement de propriétaire
RUN chown -R phoenix:phoenix /app

# Répertoires pour données temporaires
RUN mkdir -p /app/data /app/logs /app/sessions && chown -R phoenix:phoenix /app/data /app/logs /app/sessions

# Port d'exposition
EXPOSE 8501

# Utilisateur non-root
USER phoenix

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Script de démarrage
COPY --chown=phoenix:phoenix start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Commande de démarrage
CMD ["./start.sh"]