#!/bin/bash
# 🧠 Data Flywheel - Point d'entrée optimisé

set -e

echo "🚀 Starting Phoenix Data Flywheel Agent..."

# Fonction de nettoyage
cleanup() {
    echo "🔄 Shutting down Data Flywheel..."
    pkill -f ollama || true
    exit 0
}

trap cleanup SIGTERM SIGINT

# Initialisation base de données
echo "📊 Initializing database..."
mkdir -p /app/data
touch /app/data/flywheel.db

# Démarrage Ollama
echo "🤖 Starting Ollama server..."
ollama serve &
OLLAMA_PID=$!

# Attente Ollama
echo "⏳ Waiting for Ollama to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:11434/api/version > /dev/null; then
        echo "✅ Ollama is ready!"
        break
    fi
    echo "⏳ Attempt $i/30..."
    sleep 2
done

# Vérification modèle
echo "🔍 Checking Qwen2.5 model..."
if ! ollama list | grep -q "qwen2.5:3b"; then
    echo "📥 Downloading Qwen2.5 model (this may take a while)..."
    timeout 600 ollama pull qwen2.5:3b || {
        echo "⚠️ Model download timeout, will try on first request"
    }
fi

# Test modèle
echo "🧪 Testing Qwen2.5 model..."
echo "Analyse de test" | ollama run qwen2.5:3b > /dev/null 2>&1 || {
    echo "❌ Model test failed, retrying..."
    ollama pull qwen2.5:3b
}

echo "✅ Data Flywheel ready for analytics!"

# Démarrage API
echo "🚀 Starting Flywheel API..."
exec "$@" &
API_PID=$!

# Attente des processus
wait $API_PID $OLLAMA_PID