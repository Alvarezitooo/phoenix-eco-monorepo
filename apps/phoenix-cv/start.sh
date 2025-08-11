#!/bin/bash
# 📄 Phoenix CV - Script de démarrage avec connexion agents IA

set -e

echo "📄 Starting Phoenix CV..."
echo "🔗 Agents API URL: ${AGENTS_API_URL:-http://phoenix-agents:8001}"
echo "📊 Streamlit Port: ${STREAMLIT_SERVER_PORT:-8501}"

# Attendre que les agents IA soient disponibles
echo "⏳ Waiting for AI Agents to be ready..."
while ! curl -f ${AGENTS_API_URL:-http://phoenix-agents:8001}/health >/dev/null 2>&1; do
  echo "🔄 AI Agents not ready, waiting 5 seconds..."
  sleep 5
done
echo "✅ AI Agents are ready!"

# Créer le fichier de configuration agents IA pour CV
cat > /app/agents_config.py << EOF
# 🔗 Configuration automatique agents IA - Phoenix CV
AGENTS_API_URL = "${AGENTS_API_URL:-http://phoenix-agents:8001}"
AGENTS_ENABLED = True

import httpx
import asyncio

class CVAgentsClient:
    def __init__(self):
        self.base_url = AGENTS_API_URL
        
    async def validate_cv_security(self, cv_content):
        """Validation sécurité RGPD du CV"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/security/analyze",
                json={"content": cv_content, "content_type": "cv"}
            )
            return response.json() if response.status_code == 200 else {"error": "Failed"}
    
    async def optimize_cv_content(self, cv_data, job_target=None):
        """Optimisation intelligente du contenu CV"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/data/insights",
                json={"cv_data": cv_data, "job_target": job_target, "task": "cv_optimization"}
            )
            return response.json() if response.status_code == 200 else {"error": "Failed"}
            
    async def analyze_cv_competitiveness(self, cv_content, sector="tech"):
        """Analyse compétitivité CV par secteur"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/data/analyze",
                json={"content": cv_content, "analysis_type": "competitiveness", "sector": sector}
            )
            return response.json() if response.status_code == 200 else {"error": "Failed"}

# Instance globale pour Phoenix CV
cv_agents_client = CVAgentsClient()
EOF

echo "🔗 AI Agents connection configured for Phoenix CV!"

# Démarrage Streamlit avec configuration CV optimisée
echo "🚀 Starting Phoenix CV Streamlit server..."
exec streamlit run phoenix_cv/main.py \
  --server.port=${STREAMLIT_SERVER_PORT:-8501} \
  --server.address=0.0.0.0 \
  --server.headless=true \
  --server.enableCORS=false \
  --server.enableXsrfProtection=false