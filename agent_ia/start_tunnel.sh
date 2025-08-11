#!/bin/bash
# 🌐 Phoenix Agents IA - Script de démarrage tunnel automatique
# Expose les agents locaux pour apps déployées (Railway/Streamlit Cloud)

set -e

echo "🌐 Phoenix Agents IA - Démarrage Tunnel Cloud"
echo "=" * 50

# Vérification port agents IA
AGENTS_PORT=8001
echo "🔍 Vérification agents IA sur port $AGENTS_PORT..."

if ! curl -f http://localhost:$AGENTS_PORT/health >/dev/null 2>&1; then
    echo "❌ Agents IA non démarrés sur port $AGENTS_PORT"
    echo "💡 Démarrez d'abord les agents: python3 consciousness_service.py"
    exit 1
fi

echo "✅ Agents IA détectés et opérationnels"

# Installation cloudflared si nécessaire
if ! command -v cloudflared &> /dev/null; then
    echo "📥 Installation cloudflared..."
    if command -v brew &> /dev/null; then
        brew install cloudflared
    else
        echo "❌ Homebrew requis pour installer cloudflared"
        echo "💡 Installez manuellement: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/"
        exit 1
    fi
fi

echo "✅ cloudflared disponible"

# Création du fichier de configuration pour apps
echo "📝 Génération configuration tunnel..."

# Démarrage tunnel avec monitoring
echo "🚀 Démarrage tunnel cloudflared..."
echo "⚠️  Le tunnel restera actif. Appuyez sur Ctrl+C pour arrêter."

# Fonction de nettoyage
cleanup() {
    echo ""
    echo "🛑 Arrêt du tunnel..."
    if [ ! -z "$TUNNEL_PID" ]; then
        kill $TUNNEL_PID 2>/dev/null || true
    fi
    echo "✅ Tunnel arrêté proprement"
    exit 0
}

# Capture des signaux d'arrêt
trap cleanup SIGINT SIGTERM

# Démarrage tunnel en arrière-plan et capture de l'URL
cloudflared tunnel --url http://localhost:$AGENTS_PORT --no-autoupdate 2>&1 | while IFS= read -r line; do
    echo "$line"
    
    # Détecter l'URL du tunnel
    if [[ $line == *"https://"*".trycloudflare.com"* ]]; then
        # Extraire l'URL
        TUNNEL_URL=$(echo "$line" | grep -oE 'https://[^[:space:]]+\.trycloudflare\.com')
        
        if [ ! -z "$TUNNEL_URL" ]; then
            echo ""
            echo "🎉 TUNNEL ACTIF: $TUNNEL_URL"
            echo "=" * 60
            
            # Génération config pour apps
            cat > tunnel_config.env << EOF
# 🌐 Phoenix Agents IA - Configuration Tunnel Active
# Variables pour vos apps déployées (Railway/Streamlit Cloud)
# Généré automatiquement le $(date)

AGENTS_API_URL=$TUNNEL_URL
AGENTS_API_ENABLED=true
AGENTS_API_TIMEOUT=30
AGENTS_FALLBACK_ENABLED=true

# Endpoints spécifiques agents IA
AGENTS_SECURITY_ENDPOINT=$TUNNEL_URL/security/analyze
AGENTS_DATA_ENDPOINT=$TUNNEL_URL/data/insights  
AGENTS_HEALTH_ENDPOINT=$TUNNEL_URL/health
AGENTS_STATUS_ENDPOINT=$TUNNEL_URL/system/status
EOF

            echo "📋 Configuration sauvée dans: tunnel_config.env"
            echo ""
            echo "🔗 URLs pour vos apps déployées:"
            echo "  • Health Check: $TUNNEL_URL/health"
            echo "  • Security Analysis: $TUNNEL_URL/security/analyze"
            echo "  • Data Insights: $TUNNEL_URL/data/insights"
            echo "  • System Status: $TUNNEL_URL/system/status"
            echo ""
            echo "📋 Copiez ces variables dans vos apps Railway/Streamlit:"
            echo "  → AGENTS_API_URL=$TUNNEL_URL"
            echo "  → AGENTS_API_ENABLED=true"
            echo ""
            echo "✅ Tunnel opérationnel - Vos apps peuvent maintenant utiliser les agents IA locaux !"
            echo "=" * 60
        fi
    fi
done &

TUNNEL_PID=$!

# Attendre que le tunnel soit arrêté
wait $TUNNEL_PID