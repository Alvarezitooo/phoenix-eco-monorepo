#!/bin/bash
# 🌅 Phoenix Aube - Script de démarrage avec connexion agents IA

set -e

echo "🌅 Starting Phoenix Aube..."
echo "🔗 Agents API URL: ${AGENTS_API_URL:-http://phoenix-agents:8001}"
echo "📊 Streamlit Port: ${STREAMLIT_SERVER_PORT:-8501}"

# Attendre que les agents IA soient disponibles
echo "⏳ Waiting for AI Agents to be ready..."
while ! curl -f ${AGENTS_API_URL:-http://phoenix-agents:8001}/health >/dev/null 2>&1; do
  echo "🔄 AI Agents not ready, waiting 5 seconds..."
  sleep 5
done
echo "✅ AI Agents are ready!"

# Créer le fichier de configuration agents IA pour Phoenix Aube
cat > /app/agents_config.py << EOF
# 🔗 Configuration automatique agents IA - Phoenix Aube
AGENTS_API_URL = "${AGENTS_API_URL:-http://phoenix-agents:8001}"
AGENTS_ENABLED = True

import httpx
import asyncio

class AubeAgentsClient:
    def __init__(self):
        self.base_url = AGENTS_API_URL
        
    async def validate_career_exploration(self, exploration_data):
        """Validation IA des résultats d'exploration carrière"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/data/analyze",
                json={"data": exploration_data, "analysis_type": "career_validation"}
            )
            return response.json() if response.status_code == 200 else {"error": "Failed"}
    
    async def generate_career_insights(self, personality_results, market_data=None):
        """Génération insights carrière basés sur personnalité + marché"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/data/insights",
                json={"personality": personality_results, "market_data": market_data, "task": "career_exploration"}
            )
            return response.json() if response.status_code == 200 else {"error": "Failed"}
            
    async def check_european_compliance(self, career_data):
        """Vérification conformité réglementation européenne"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/security/analyze",
                json={"content": career_data, "content_type": "career_exploration", "region": "EU"}
            )
            return response.json() if response.status_code == 200 else {"error": "Failed"}
            
    async def predict_career_success(self, profile_data, target_careers):
        """Prédiction probabilité succès par carrière"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/data/predict",
                json={"profile": profile_data, "careers": target_careers, "model": "career_success"}
            )
            return response.json() if response.status_code == 200 else {"error": "Failed"}
            
    async def analyze_trust_transparency(self, ai_recommendations):
        """Analyse transparence et confiance des recommandations IA"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/data/analyze",
                json={"data": ai_recommendations, "analysis_type": "trust_transparency"}
            )
            return response.json() if response.status_code == 200 else {"error": "Failed"}

# Instance globale pour Phoenix Aube
aube_agents_client = AubeAgentsClient()
EOF

echo "🔗 AI Agents connection configured for Phoenix Aube!"

# Démarrage Streamlit avec configuration Aube optimisée
echo "🚀 Starting Phoenix Aube Streamlit server..."
exec streamlit run main.py \
  --server.port=${STREAMLIT_SERVER_PORT:-8501} \
  --server.address=0.0.0.0 \
  --server.headless=true \
  --server.enableCORS=false \
  --server.enableXsrfProtection=false