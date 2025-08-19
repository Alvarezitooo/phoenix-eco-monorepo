# 🚀 Phoenix Letters - Production Dockerfile for Render
# Optimized for fast deployment and security

FROM python:3.11-slim

# Metadata
LABEL maintainer="Phoenix Team <contact@phoenix.app>"
LABEL version="1.0.0"
LABEL description="Phoenix Letters - AI-Powered Cover Letter Generator"

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

# Copy requirements first (for layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 🚀 ARCHITECTURE MONOREPO - Copie depuis la racine du repo
# Remonte au niveau supérieur puis copie tout
COPY ../../. .

# Install shared packages
RUN if [ -d "packages/phoenix_shared_auth" ]; then pip install -e packages/phoenix_shared_auth; fi && \
    if [ -d "packages/phoenix_shared_ui" ]; then pip install -e packages/phoenix_shared_ui; fi && \
    if [ -d "packages/phoenix_shared_models" ]; then pip install -e packages/phoenix_shared_models; fi

# Create necessary directories
RUN mkdir -p /app/logs /app/temp && \
    chown -R phoenix:phoenix /app

# Switch to non-root user
USER phoenix

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Expose port (Railway utilise $PORT)
EXPOSE $PORT

# Debug : vérifier la structure puis lancer streamlit
CMD ls -la && ls -la apps/ && ls -la apps/phoenix-letters/ && streamlit run apps/phoenix-letters/main.py --server.port=$PORT --server.address=0.0.0.0