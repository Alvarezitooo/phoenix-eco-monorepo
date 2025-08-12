#!/bin/bash

# Script de démarrage Phoenix Aube Full Stack
echo "🚀 Démarrage de Phoenix Aube (Frontend React + Backend FastAPI)"

# Vérifier si nous sommes dans le bon répertoire
if [ ! -d "frontend" ] || [ ! -d "phoenix_aube" ]; then
    echo "❌ Erreur: Ce script doit être exécuté depuis le dossier apps/phoenix-aube/"
    exit 1
fi

# Fonction pour installer les dépendances Node.js si nécessaire
install_frontend_deps() {
    echo "📦 Vérification des dépendances frontend..."
    cd frontend
    if [ ! -d "node_modules" ]; then
        echo "📥 Installation des dépendances npm..."
        npm install
    fi
    cd ..
}

# Fonction pour démarrer le backend FastAPI
start_backend() {
    echo "🔧 Démarrage du backend FastAPI..."
    # Activer l'environnement virtuel si disponible
    if [ -d "venv" ]; then
        source venv/bin/activate
    elif [ -d "../../../venv" ]; then
        source ../../../venv/bin/activate
    fi
    
    # Démarrer FastAPI en arrière-plan
    cd phoenix_aube
    python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload &
    BACKEND_PID=$!
    echo "✅ Backend FastAPI démarré (PID: $BACKEND_PID) sur http://localhost:8000"
    cd ..
}

# Fonction pour démarrer le frontend React
start_frontend() {
    echo "⚛️  Démarrage du frontend React..."
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    echo "✅ Frontend React démarré (PID: $FRONTEND_PID) sur http://localhost:3000"
    cd ..
}

# Fonction de nettoyage
cleanup() {
    echo ""
    echo "🛑 Arrêt des services..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo "✅ Backend arrêté"
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        echo "✅ Frontend arrêté"
    fi
    echo "👋 Phoenix Aube arrêté proprement"
    exit 0
}

# Capturer les signaux d'arrêt
trap cleanup SIGINT SIGTERM

# Étapes de démarrage
install_frontend_deps
start_backend
sleep 3  # Attendre que le backend démarre
start_frontend

echo ""
echo "🎉 Phoenix Aube est maintenant disponible :"
echo "   Frontend React: http://localhost:3000"
echo "   Backend API:    http://localhost:8000"
echo "   Swagger UI:     http://localhost:8000/docs"
echo ""
echo "Appuyez sur Ctrl+C pour arrêter les services"

# Attendre indéfiniment
wait