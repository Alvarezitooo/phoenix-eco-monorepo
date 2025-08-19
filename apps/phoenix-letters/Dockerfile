# ✅ Phoenix Letters - Dockerfile Monorepo Optimisé pour Railway (avec Root Directory = apps/phoenix-letters)
FROM python:3.11-slim

# 1. Configuration de base
ENV PYTHONDONTWRITEBYTECODE=1     PYTHONUNBUFFERED=1     PIP_NO_CACHE_DIR=1     PYTHONPATH="/app:/app/packages"     STREAMLIT_SERVER_HEADLESS=true     STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

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
EXPOSE ${PORT:-8501}

# Le Health Check utilise aussi le port dynamique
HEALTHCHECK CMD curl -f http://localhost:${PORT:-8501}/_stcore/health || exit 1

# Le CMD utilise le port dynamique fourni par Railway
CMD ["streamlit", "run", "main.py", "--server.port=${PORT:-8501}", "--server.address=0.0.0.0"]