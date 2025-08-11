#!/bin/bash
# 🌐 Phoenix Agents IA - Setup Tunnel Cloudflare PERMANENT
# URL fixe gratuite à vie pour tes agents IA locaux

set -e

echo "🌐 Phoenix Agents IA - Setup Tunnel Cloudflare Permanent"
echo "=========================================================="
echo ""

# Vérification cloudflared
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
echo ""

# Étape 1: Login Cloudflare
echo "🔐 ÉTAPE 1/4: Authentification Cloudflare"
echo "==========================================="
echo "💡 Une page va s'ouvrir dans votre navigateur"
echo "   → Connectez-vous avec votre compte Cloudflare (gratuit)"
echo "   → Autorisez cloudflared à accéder à votre compte"
echo ""
read -p "Appuyez sur Entrée pour continuer..."

cloudflared tunnel login

if [ $? -ne 0 ]; then
    echo "❌ Erreur lors de l'authentification Cloudflare"
    echo "💡 Créez un compte gratuit sur https://dash.cloudflare.com/"
    exit 1
fi

echo "✅ Authentification réussie!"
echo ""

# Étape 2: Création du tunnel nommé
echo "🚇 ÉTAPE 2/4: Création tunnel permanent"
echo "======================================"
TUNNEL_NAME="phoenix-agents-$(date +%s)"
echo "📝 Nom du tunnel: $TUNNEL_NAME"
echo ""

cloudflared tunnel create $TUNNEL_NAME

if [ $? -ne 0 ]; then
    echo "❌ Erreur lors de la création du tunnel"
    echo "💡 Vérifiez votre connexion et réessayez"
    exit 1
fi

echo "✅ Tunnel créé avec succès!"
echo ""

# Obtenir l'UUID du tunnel
TUNNEL_UUID=$(cloudflared tunnel list | grep $TUNNEL_NAME | awk '{print $1}')
echo "🆔 UUID du tunnel: $TUNNEL_UUID"
echo ""

# Étape 3: Configuration du tunnel
echo "⚙️ ÉTAPE 3/4: Configuration tunnel"
echo "=================================="

# Créer le répertoire de config
mkdir -p ~/.cloudflared

# Créer le fichier de configuration
cat > ~/.cloudflared/config.yml << EOF
tunnel: $TUNNEL_UUID
credentials-file: ~/.cloudflared/$TUNNEL_UUID.json

ingress:
  - hostname: $TUNNEL_NAME.cfargotunnel.com
    service: http://localhost:8001
  - service: http_status:404
EOF

echo "📝 Configuration sauvée dans ~/.cloudflared/config.yml"
echo ""

# Étape 4: Test et informations finales
echo "🧪 ÉTAPE 4/4: Test et finalisation"
echo "================================="

# URL fixe du tunnel
TUNNEL_URL="https://$TUNNEL_NAME.cfargotunnel.com"

echo "🎉 TUNNEL PERMANENT CONFIGURÉ AVEC SUCCÈS!"
echo ""
echo "🔗 URL FIXE DE VOS AGENTS IA:"
echo "   $TUNNEL_URL"
echo ""
echo "📋 CONFIGURATION POUR VOS APPS DÉPLOYÉES:"
echo "   Variable d'environnement à ajouter dans Railway/Streamlit:"
echo "   AGENTS_API_URL=$TUNNEL_URL"
echo ""
echo "🚀 ENDPOINTS DISPONIBLES:"
echo "   • Health Check: $TUNNEL_URL/health"
echo "   • Security Analysis: $TUNNEL_URL/security/analyze"
echo "   • Data Insights: $TUNNEL_URL/data/insights"
echo "   • System Status: $TUNNEL_URL/system/status"
echo ""

# Sauvegarder la config dans un fichier
cat > tunnel_permanent_config.env << EOF
# 🌐 Phoenix Agents IA - Configuration Tunnel PERMANENT
# URL fixe Cloudflare - valable à vie!
# Généré le $(date)

TUNNEL_NAME=$TUNNEL_NAME
TUNNEL_UUID=$TUNNEL_UUID
AGENTS_API_URL=$TUNNEL_URL

# Variables pour vos apps déployées
AGENTS_API_ENABLED=true
AGENTS_API_TIMEOUT=30
AGENTS_FALLBACK_ENABLED=true

# Endpoints
AGENTS_HEALTH_ENDPOINT=$TUNNEL_URL/health
AGENTS_SECURITY_ENDPOINT=$TUNNEL_URL/security/analyze
AGENTS_DATA_ENDPOINT=$TUNNEL_URL/data/insights
AGENTS_STATUS_ENDPOINT=$TUNNEL_URL/system/status
EOF

echo "💾 Configuration sauvée dans: tunnel_permanent_config.env"
echo ""
echo "🔄 COMMENT DÉMARRER LE TUNNEL:"
echo "   1. Démarrez vos agents IA: python3 consciousness_service.py"
echo "   2. Démarrez le tunnel permanent: ./start_permanent_tunnel.sh"
echo ""
echo "⚡ Le tunnel aura la même URL à chaque démarrage!"
echo "   Plus besoin de changer la config de vos apps déployées!"
echo ""
echo "✅ Setup terminé! Tunnel permanent prêt à l'usage."