# 🚀 Phoenix Ecosystem - Dockerfile Monorepo Universel
# Ce Dockerfile peut builder n'importe quelle app du monorepo
# Usage: docker build --build-arg APP_NAME=phoenix-letters .

FROM python:3.11-slim

# Build argument pour spécifier quelle app builder
ARG APP_NAME=phoenix-letters

# Metadata
LABEL maintainer="Phoenix Team <contact@phoenix.app>"
LABEL version="2.0.0"
LABEL description="Phoenix Ecosystem - Monorepo Universal Container"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_PORT=8501 \
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

# Copy requirements first (for layer caching)
COPY apps/${APP_NAME}/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 🚀 ARCHITECTURE MONOREPO - Copie TOUT le monorepo
# Cela donne accès à la "boîte à outils commune" (packages/)
COPY . .

# Install shared packages
RUN if [ -d "packages/phoenix_shared_auth" ]; then pip install -e packages/phoenix_shared_auth; fi && \
    if [ -d "packages/phoenix_shared_ui" ]; then pip install -e packages/phoenix_shared_ui; fi && \
    if [ -d "packages/phoenix_shared_models" ]; then pip install -e packages/phoenix_shared_models; fi

# Set Python path to include monorepo structure
ENV PYTHONPATH="/app:/app/packages:${PYTHONPATH}"

# Create necessary directories
RUN mkdir -p /app/logs /app/temp && \
    chown -R phoenix:phoenix /app

# Switch to non-root user
USER phoenix

# Health check (adaptable selon l'app)
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Expose port
EXPOSE 8501

# Set working directory to the specific app
WORKDIR /app/apps/${APP_NAME}

# Start command dynamique selon le type d'app
CMD if [ -f "app.py" ] && grep -q "streamlit" requirements.txt 2>/dev/null; then \
        streamlit run app.py --server.port=8501 --server.address=0.0.0.0; \
    elif [ -f "app.py" ] && grep -q "fastapi\|uvicorn" requirements.txt 2>/dev/null; then \
        python app.py; \
    elif [ -f "main.py" ]; then \
        python main.py; \
    else \
        echo "No valid entry point found" && exit 1; \
    fi