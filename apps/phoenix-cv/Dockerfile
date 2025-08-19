# 📄 Phoenix CV - Dockerfile DevSecOps
FROM python:3.11-slim

# Métadonnées sécurité
LABEL maintainer="Phoenix DevSecOps Team"
LABEL version="1.0"
LABEL description="Phoenix CV - Générateur CV professionnel IA"

# Variables d'environnement sécurisées
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PYTHONPATH="/app:/app/packages"
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Utilisateur non-root pour sécurité
RUN groupadd -r phoenix && useradd -r -g phoenix phoenix

# Installation dépendances système (pour PDF processing)
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    libreoffice \
    wkhtmltopdf \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Répertoire de travail
WORKDIR /app

# Copie et installation requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Installation streamlit et dépendances CV
RUN pip install streamlit>=1.28.0 pypdf2 python-docx reportlab

# 🚀 ARCHITECTURE MONOREPO - Copie depuis la racine du repo
COPY ../../. .

# Install shared packages
RUN if [ -d "packages/phoenix_shared_auth" ]; then pip install -e packages/phoenix_shared_auth; fi && \
    if [ -d "packages/phoenix_shared_ui" ]; then pip install -e packages/phoenix_shared_ui; fi && \
    if [ -d "packages/phoenix_shared_models" ]; then pip install -e packages/phoenix_shared_models; fi

# Changement de propriétaire
RUN chown -R phoenix:phoenix /app

# Répertoires pour données temporaires
RUN mkdir -p /app/data /app/logs /app/temp_cv && chown -R phoenix:phoenix /app/data /app/logs /app/temp_cv

# Port d'exposition (Railway utilise $PORT)
EXPOSE $PORT

# Utilisateur non-root
USER phoenix

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:$PORT/_stcore/health || exit 1

# Set working directory to app
WORKDIR /app/apps/phoenix-cv

# Commande de démarrage Railway
CMD streamlit run main.py --server.port=$PORT --server.address=0.0.0.0