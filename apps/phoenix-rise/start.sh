#!/bin/bash
# 🌅 Phoenix Rise - Script de démarrage avec connexion agents IA

set -e

echo "🌅 Starting Phoenix Rise..."
echo "🔗 Agents API URL: ${AGENTS_API_URL:-http://phoenix-agents:8001}"
echo "📊 Streamlit Port: ${STREAMLIT_SERVER_PORT:-8501}"

# Attendre que les agents IA soient disponibles
echo "⏳ Waiting for AI Agents to be ready..."
while ! curl -f ${AGENTS_API_URL:-http://phoenix-agents:8001}/health >/dev/null 2>&1; do
  echo "🔄 AI Agents not ready, waiting 5 seconds..."
  sleep 5
done
echo "✅ AI Agents are ready!"

# Créer le fichier de configuration agents IA pour Phoenix Rise
cat > /app/agents_config.py << EOF
# 🔗 Configuration automatique agents IA - Phoenix Rise
AGENTS_API_URL = "${AGENTS_API_URL:-http://phoenix-agents:8001}"
AGENTS_ENABLED = True

import httpx
import asyncio

class RiseAgentsClient:
    def __init__(self):
        self.base_url = AGENTS_API_URL
        
    async def analyze_emotional_state(self, journal_data):
        """Analyse état émotionnel basé sur journal"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/data/analyze",
                json={"data": journal_data, "analysis_type": "emotional_state"}
            )
            return response.json() if response.status_code == 200 else {"error": "Failed"}
    
    async def generate_coaching_insights(self, user_data, objectives=None):
        """Génération insights coaching personnalisés"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/data/insights",
                json={"user_data": user_data, "objectives": objectives, "task": "coaching"}
            )
            return response.json() if response.status_code == 200 else {"error": "Failed"}
            
    async def validate_privacy_compliance(self, sensitive_data):
        """Validation conformité données sensibles coaching"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/security/analyze",
                json={"content": sensitive_data, "content_type": "coaching_session"}
            )
            return response.json() if response.status_code == 200 else {"error": "Failed"}
            
    async def predict_coaching_trajectory(self, historical_data, goals):
        """Prédiction trajectoire coaching basée sur historique"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/data/predict",
                json={"history": historical_data, "goals": goals, "model": "coaching_trajectory"}
            )
            return response.json() if response.status_code == 200 else {"error": "Failed"}

# Instance globale pour Phoenix Rise
rise_agents_client = RiseAgentsClient()
EOF

echo "🔗 AI Agents connection configured for Phoenix Rise!"

# Démarrage Streamlit avec configuration Rise optimisée
echo "🚀 Starting Phoenix Rise Streamlit server..."
exec streamlit run phoenix_rise/main.py \
  --server.port=${STREAMLIT_SERVER_PORT:-8501} \
  --server.address=0.0.0.0 \
  --server.headless=true \
  --server.enableCORS=false \
  --server.enableXsrfProtection=false