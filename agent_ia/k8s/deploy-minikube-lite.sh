#!/bin/bash
# 🚀 PHOENIX LETTERS - Déploiement Minikube LITE (3GB RAM)
set -e

echo "☸️ PHOENIX LETTERS - Kubernetes Minikube LITE"
echo "============================================="

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

# Vérifications
log_info "Vérification des prérequis..."

if ! command -v minikube &> /dev/null; then
    log_error "Minikube n'est pas installé : brew install minikube"
    exit 1
fi

if ! command -v kubectl &> /dev/null; then
    log_error "kubectl n'est pas installé : brew install kubectl"
    exit 1
fi

log_success "Prérequis OK"

# Démarrage Minikube LITE
log_info "Démarrage Minikube LITE (compatible Docker Desktop 4GB)..."

minikube start \
    --memory=3000 \
    --cpus=2 \
    --disk-size=10g \
    --driver=docker \
    --kubernetes-version=v1.28.0

if [ $? -ne 0 ]; then
    log_error "Échec démarrage Minikube"
    log_info "Solutions possibles :"
    echo "1. Augmenter RAM Docker Desktop (Settings → Resources → Memory → 6GB)"
    echo "2. Arrêter autres applications consommatrices RAM"
    echo "3. Redémarrer Docker Desktop"
    exit 1
fi

log_success "Minikube LITE démarré avec succès"

# Activation addons essentiels
log_info "Activation addons essentiels..."
minikube addons enable dashboard
minikube addons enable metrics-server

# Configuration Docker environnement
log_info "Configuration environnement Docker Minikube..."
eval $(minikube docker-env)

# Build UNIQUEMENT Smart Router (plus léger)
log_info "Build Smart Router uniquement (version LITE)..."
cd "$(dirname "$0")/.."

docker build -f docker/Dockerfile.smart-router \
    -t phoenix-letters/smart-router:latest .

log_success "Smart Router buildé dans Minikube"

# Déploiement Kubernetes LITE
log_info "Déploiement Kubernetes LITE..."

# Namespace
kubectl apply -f k8s/namespace.yaml

# UNIQUEMENT Smart Router pour commencer
log_info "Déploiement Smart Router..."
kubectl apply -f k8s/smart-router.yaml

# Vérification déploiement
log_info "Vérification du déploiement..."
kubectl get pods -n phoenix-letters

# Attente que le pod soit prêt
log_info "Attente initialisation Smart Router..."
kubectl wait --for=condition=ready pod \
    -l component=smart-router \
    -n phoenix-letters --timeout=120s

# URLs d'accès
SMART_ROUTER_URL=$(minikube service smart-router-service -n phoenix-letters --url 2>/dev/null)

echo ""
echo "🎉 DÉPLOIEMENT LITE TERMINÉ !"
echo "============================"
echo ""
echo "📊 URLs d'accès :"
echo "- Smart Router: $SMART_ROUTER_URL"
echo "- Dashboard K8s: minikube dashboard"
echo ""
echo "🧪 Tests :"
echo "curl $SMART_ROUTER_URL/health"
echo ""
echo "📊 Monitoring :"
echo "kubectl get pods -n phoenix-letters"
echo "kubectl logs -f deployment/smart-router -n phoenix-letters"
echo ""
echo "🚀 Prochaines étapes :"
echo "1. Tester Smart Router"
echo "2. Si OK, déployer Security Guardian : kubectl apply -f k8s/security-guardian.yaml"
echo "3. Dashboard : minikube dashboard"
echo ""
echo "🛑 Arrêt :"
echo "kubectl delete namespace phoenix-letters"
echo "minikube stop"

log_success "Phoenix Letters Smart Router déployé sur Kubernetes ! 🚀"