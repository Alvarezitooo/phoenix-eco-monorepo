# ===================================================================  
# PHOENIX ECOSYSTEM - DOCKERFILE RAILWAY V2.0
# ===================================================================
# Dockerfile universel optimisé pour Railway
# Support: Streamlit + FastAPI + Workers

FROM python:3.11-slim

# Metadata
LABEL maintainer="Phoenix Team <contact@phoenix.app>"
LABEL version="2.1.0"  
LABEL description="Phoenix Ecosystem - Railway Monorepo Container"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app:/app/packages" \
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

# CMD par défaut pour Railway (peut être surchargé par Start Command)
CMD ["echo", "Railway service ready - Use Start Command to specify which app to run"]