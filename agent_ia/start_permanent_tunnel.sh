#!/bin/bash
# 🚀 Phoenix Agents IA - Démarrage Tunnel Permanent
# Utilise la configuration Cloudflare permanente

set -e

echo "🚀 Phoenix Agents IA - Démarrage Tunnel Permanent"
echo "================================================="
echo ""

# Vérification des prérequis
if [ ! -f ~/.cloudflared/config.yml ]; then
    echo "❌ Configuration tunnel non trouvée!"
    echo "💡 Lancez d'abord: ./setup_permanent_tunnel.sh"
    exit 1
fi

# Vérification agents IA
AGENTS_PORT=8001
echo "🔍 Vérification agents IA sur port $AGENTS_PORT..."

if ! curl -f http://localhost:$AGENTS_PORT/health >/dev/null 2>&1; then
    echo "❌ Agents IA non démarrés sur port $AGENTS_PORT"
    echo "💡 Démarrez d'abord: python3 consciousness_service.py"
    exit 1
fi

echo "✅ Agents IA opérationnels"

# Lecture configuration tunnel
if [ -f tunnel_permanent_config.env ]; then
    source tunnel_permanent_config.env
    echo "📋 Configuration chargée:"
    echo "   • Nom tunnel: $TUNNEL_NAME"
    echo "   • URL fixe: $AGENTS_API_URL"
else
    echo "⚠️ Fichier de config non trouvé, utilisation config par défaut"
fi

echo ""
echo "🌐 Démarrage tunnel permanent Cloudflare..."
echo "⚠️  Le tunnel restera actif avec URL FIXE"
echo "   Appuyez sur Ctrl+C pour arrêter"
echo ""

# Fonction de nettoyage
cleanup() {
    echo ""
    echo "🛑 Arrêt du tunnel permanent..."
    echo "✅ Tunnel arrêté proprement"
    exit 0
}

# Capture des signaux d'arrêt
trap cleanup SIGINT SIGTERM

# Démarrage tunnel permanent
echo "🚀 Tunnel permanent démarré!"
if [ ! -z "$AGENTS_API_URL" ]; then
    echo "🔗 URL fixe active: $AGENTS_API_URL"
    echo ""
    echo "📋 Variables pour vos apps déployées:"
    echo "   AGENTS_API_URL=$AGENTS_API_URL"
    echo ""
    echo "✅ Vos apps déployées peuvent maintenant utiliser les agents IA!"
fi
echo "========================================================="

# Démarrer cloudflared avec config permanente
cloudflared tunnel run

# Cette ligne ne sera jamais atteinte en fonctionnement normal
echo "⚠️ Tunnel arrêté de manière inattendue"