#!/bin/bash
# 📊 Phoenix Letters - Script de démarrage avec connexion agents IA

set -e

echo "📊 Starting Phoenix Letters..."
echo "🔗 Agents API URL: ${AGENTS_API_URL:-http://phoenix-agents:8001}"
echo "📊 Streamlit Port: ${STREAMLIT_SERVER_PORT:-8501}"

# Attendre que les agents IA soient disponibles
echo "⏳ Waiting for AI Agents to be ready..."
while ! curl -f ${AGENTS_API_URL:-http://phoenix-agents:8001}/health >/dev/null 2>&1; do
  echo "🔄 AI Agents not ready, waiting 5 seconds..."
  sleep 5
done
echo "✅ AI Agents are ready!"

# Créer le fichier de configuration agents IA
cat > /app/agents_config.py << EOF
# 🔗 Configuration automatique agents IA
AGENTS_API_URL = "${AGENTS_API_URL:-http://phoenix-agents:8001}"
AGENTS_ENABLED = True

# Import des classes agents
import httpx
import asyncio

class AgentsClient:
    def __init__(self):
        self.base_url = AGENTS_API_URL
        
    async def analyze_security(self, content, content_type="cv"):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/security/analyze",
                json={"content": content, "content_type": content_type}
            )
            return response.json() if response.status_code == 200 else {"error": "Failed"}
    
    async def generate_insights(self, data):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/data/insights",
                json={"data": data}
            )
            return response.json() if response.status_code == 200 else {"error": "Failed"}

# Instance globale
agents_client = AgentsClient()
EOF

echo "🔗 AI Agents connection configured!"

# Démarrage Streamlit avec configuration optimisée
echo "🚀 Starting Streamlit server..."
exec streamlit run main.py \
  --server.port=${STREAMLIT_SERVER_PORT:-8501} \
  --server.address=0.0.0.0 \
  --server.headless=true \
  --server.enableCORS=false \
  --server.enableXsrfProtection=false