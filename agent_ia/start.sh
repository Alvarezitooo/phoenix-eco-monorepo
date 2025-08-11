#!/bin/bash
# 🚀 Phoenix Agents IA - Script de démarrage DevSecOps

set -e

echo "🧠 Starting Phoenix AI Agents Service..."
echo "📊 Environment: ${ENVIRONMENT:-development}"
echo "🔧 Ollama Host: ${OLLAMA_HOST:-localhost:11434}"

# Attendre que Ollama soit disponible
echo "⏳ Waiting for Ollama to be ready..."
while ! curl -f ${OLLAMA_HOST:-localhost:11434}/api/version >/dev/null 2>&1; do
  echo "🔄 Ollama not ready, waiting 5 seconds..."
  sleep 5
done
echo "✅ Ollama is ready!"

# Installation automatique des modèles optimisés si nécessaire
echo "🤖 Checking AI models..."
if ! curl -s ${OLLAMA_HOST:-localhost:11434}/api/tags | grep -q "qwen2.5:1.5b"; then
  echo "📥 Installing qwen2.5:1.5b..."
  curl -X POST ${OLLAMA_HOST:-localhost:11434}/api/pull -d '{"name":"qwen2.5:1.5b"}'
fi

if ! curl -s ${OLLAMA_HOST:-localhost:11434}/api/tags | grep -q "gemma2:2b"; then
  echo "📥 Installing gemma2:2b..."
  curl -X POST ${OLLAMA_HOST:-localhost:11434}/api/pull -d '{"name":"gemma2:2b"}'
fi

echo "✅ AI models ready!"

# Démarrage du service avec monitoring
echo "🚀 Starting Phoenix AI Agents API..."
exec python3 consciousness_service.py