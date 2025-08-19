# ===================================================================
# PHOENIX ECOSYSTEM - DOCKERFILE MONOREPO V1.0
# ===================================================================
# Dockerfile universel pour tous les services Phoenix
# Compatible avec la syntaxe dockerCommand de Render Blueprint

FROM python:3.11-slim

# Metadata
LABEL maintainer="Phoenix Team <contact@phoenix.app>"
LABEL version="2.0.0"
LABEL description="Phoenix Ecosystem - Monorepo Universal Container"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_PORT=80 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Create app user for security
RUN groupadd -r phoenix && useradd -r -g phoenix phoenix

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 🚀 ARCHITECTURE MONOREPO - Copie TOUT le monorepo
COPY . .

# Install requirements for all apps (optimisation layer caching)
RUN find apps/ -name "requirements.txt" -exec pip install --no-cache-dir -r {} \;

# Install pip upgrade
RUN pip install --no-cache-dir --upgrade pip

# Install shared packages si ils existent
RUN if [ -d "packages/phoenix_shared_auth" ]; then pip install -e packages/phoenix_shared_auth; fi && \
    if [ -d "packages/phoenix_shared_ui" ]; then pip install -e packages/phoenix_shared_ui; fi && \
    if [ -d "packages/phoenix_shared_models" ]; then pip install -e packages/phoenix_shared_models; fi

# Set Python path pour inclure la structure monorepo
ENV PYTHONPATH="/app:/app/packages:${PYTHONPATH}"

# Create necessary directories
RUN mkdir -p /app/logs /app/temp && \
    chown -R phoenix:phoenix /app

# Switch to non-root user
USER phoenix

# Expose les ports standards (Render gère automatiquement le mapping)
EXPOSE 80 8000 8501

# Le CMD est défini dans render.yaml via dockerCommand
# Cela permet une flexibilité maximale par service