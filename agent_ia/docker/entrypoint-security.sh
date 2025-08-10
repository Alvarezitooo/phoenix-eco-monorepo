#!/bin/bash
# 🛡️ Security Guardian - Point d'entrée optimisé

set -e

echo "🚀 Starting Phoenix Security Guardian Agent..."

# Fonction de nettoyage
cleanup() {
    echo "🔄 Shutting down Security Guardian..."
    pkill -f ollama || true
    exit 0
}

# Gestionnaire de signaux
trap cleanup SIGTERM SIGINT

# Démarrage Ollama en arrière-plan
echo "🤖 Starting Ollama server..."
ollama serve &
OLLAMA_PID=$!

# Attente de la disponibilité d'Ollama
echo "⏳ Waiting for Ollama to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:11434/api/version > /dev/null; then
        echo "✅ Ollama is ready!"
        break
    fi
    echo "⏳ Attempt $i/30..."
    sleep 2
done

# Vérification du modèle
echo "🔍 Checking model availability..."
if ! ollama list | grep -q "phi3.5"; then
    echo "📥 Downloading Phi-3.5 model (this may take a few minutes)..."
    timeout 300 ollama pull phi3.5:latest || {
        echo "⚠️ Model download timeout, will try on first request"
    }
fi

# Test rapide du modèle
echo "🧪 Testing model..."
echo "Test de fonctionnement" | ollama run phi3.5:latest > /dev/null 2>&1 || {
    echo "❌ Model test failed, retrying..."
    ollama pull phi3.5:latest
}

echo "✅ Security Guardian ready for requests!"

# Démarrage de l'API Python
echo "🚀 Starting Security API..."
exec "$@" &
API_PID=$!

# Attente des processus
wait $API_PID $OLLAMA_PID