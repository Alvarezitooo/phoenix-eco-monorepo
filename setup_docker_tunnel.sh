#!/bin/bash
# 🐳 Phoenix Docker - Setup Tunnel Cloudflare intégré
# Configuration tunnel permanent dans Docker

set -e

echo "🐳 Phoenix Docker - Setup Tunnel Cloudflare"
echo "============================================"
echo ""

# Vérification cloudflared local pour setup
if ! command -v cloudflared &> /dev/null; then
    echo "📥 Installation cloudflared pour setup..."
    if command -v brew &> /dev/null; then
        brew install cloudflared
    else
        echo "❌ Homebrew requis pour installer cloudflared"
        exit 1
    fi
fi

echo "✅ cloudflared disponible"
echo ""

# Étape 1: Login Cloudflare
echo "🔐 ÉTAPE 1/3: Authentification Cloudflare"
echo "=========================================="
echo "💡 Une page va s'ouvrir dans votre navigateur"
echo "   → Connectez-vous avec votre compte Cloudflare (gratuit)"
echo "   → Autorisez cloudflared à accéder à votre compte"
echo ""
read -p "Appuyez sur Entrée pour continuer..."

cloudflared tunnel login

if [ $? -ne 0 ]; then
    echo "❌ Erreur lors de l'authentification Cloudflare"
    exit 1
fi

echo "✅ Authentification réussie!"
echo ""

# Étape 2: Création du tunnel
echo "🚇 ÉTAPE 2/3: Création tunnel Docker"
echo "===================================="
TUNNEL_NAME="phoenix-docker-$(date +%s)"
echo "📝 Nom du tunnel: $TUNNEL_NAME"

cloudflared tunnel create $TUNNEL_NAME

if [ $? -ne 0 ]; then
    echo "❌ Erreur lors de la création du tunnel"
    exit 1
fi

# Obtenir l'UUID du tunnel
TUNNEL_UUID=$(cloudflared tunnel list | grep $TUNNEL_NAME | awk '{print $1}')
echo "🆔 UUID du tunnel: $TUNNEL_UUID"
echo ""

# Étape 3: Configuration Docker
echo "⚙️ ÉTAPE 3/3: Configuration Docker"
echo "=================================="

# Créer le répertoire de config pour Docker
mkdir -p tunnel/config

# Copier les credentials
cp ~/.cloudflared/$TUNNEL_UUID.json tunnel/config/

# Créer le fichier de config pour Docker
cat > tunnel/config/config.yml << EOF
tunnel: $TUNNEL_UUID
credentials-file: /etc/cloudflared/$TUNNEL_UUID.json

ingress:
  - hostname: $TUNNEL_NAME.cfargotunnel.com
    service: http://phoenix-agents:8001
  - service: http_status:404
EOF

# URL du tunnel
TUNNEL_URL="https://$TUNNEL_NAME.cfargotunnel.com"

# Générer le token pour Docker
TUNNEL_TOKEN=$(cloudflared tunnel token $TUNNEL_NAME)

# Mettre à jour le .env
if [ ! -f .env ]; then
    cp .env.example .env
fi

# Ajouter/Mettre à jour la configuration tunnel dans .env
echo "" >> .env
echo "# 🌐 Tunnel Cloudflare Configuration" >> .env
echo "CLOUDFLARE_TUNNEL_TOKEN=$TUNNEL_TOKEN" >> .env
echo "TUNNEL_NAME=$TUNNEL_NAME" >> .env
echo "TUNNEL_UUID=$TUNNEL_UUID" >> .env
echo "AGENTS_API_URL=$TUNNEL_URL" >> .env

echo "📝 Configuration Docker sauvée!"
echo ""
echo "🎉 SETUP TUNNEL DOCKER TERMINÉ!"
echo ""
echo "🔗 URL FIXE DE VOS AGENTS IA:"
echo "   $TUNNEL_URL"
echo ""
echo "📋 CONFIGURATION POUR VOS APPS DÉPLOYÉES:"
echo "   AGENTS_API_URL=$TUNNEL_URL"
echo ""
echo "🚀 PROCHAINES ÉTAPES:"
echo "   1. Lancez tout avec: docker compose up -d"
echo "   2. Vérifiez: curl $TUNNEL_URL/health"
echo "   3. Configurez vos apps Railway/Streamlit avec l'URL ci-dessus"
echo ""
echo "✅ Plus besoin de gérer des terminaux multiples !"
echo "   Docker s'occupe de tout : agents IA + tunnel + monitoring"