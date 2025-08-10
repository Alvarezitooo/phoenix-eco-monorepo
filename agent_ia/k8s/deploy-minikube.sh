#!/bin/bash
# 🚀 PHOENIX LETTERS - Déploiement Minikube
set -e

echo "☸️ PHOENIX LETTERS - Déploiement Kubernetes Minikube"
echo "===================================================="

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
    log_error "Minikube n'est pas installé"
    echo "Installation : brew install minikube"
    exit 1
fi

if ! command -v kubectl &> /dev/null; then
    log_error "kubectl n'est pas installé"  
    echo "Installation : brew install kubectl"
    exit 1
fi

log_success "Prérequis OK"

# Démarrage Minikube
log_info "Démarrage Minikube (optimisé MacBook 8GB)..."

# Configuration adaptée aux limites Docker Desktop
minikube start \
    --memory=3500 \
    --cpus=2 \
    --disk-size=15g \
    --driver=docker \
    --kubernetes-version=v1.28.0

if [ $? -eq 0 ]; then
    log_success "Minikube démarré avec succès"
else
    log_error "Échec démarrage Minikube"
    exit 1
fi

# Activation des addons utiles
log_info "Activation des addons Kubernetes..."
minikube addons enable dashboard
minikube addons enable metrics-server
minikube addons enable ingress

# Build des images dans Minikube
log_info "Configuration environnement Docker Minikube..."
eval $(minikube docker-env)

# Build des images Phoenix dans Minikube
log_info "Build des images Phoenix dans Minikube..."
cd "$(dirname "$0")/.."

# Build Security Guardian
log_info "Building Security Guardian..."
docker build -f docker/Dockerfile.security-guardian \
    -t phoenix-letters/security-guardian:latest .

# Build Data Flywheel  
log_info "Building Data Flywheel..."
docker build -f docker/Dockerfile.data-flywheel \
    -t phoenix-letters/data-flywheel:latest .

# Build Smart Router
log_info "Building Smart Router..."
docker build -f docker/Dockerfile.smart-router \
    -t phoenix-letters/smart-router:latest .

log_success "Images buildées dans Minikube"

# Déploiement Kubernetes
log_info "Déploiement des manifests Kubernetes..."

# Namespace
kubectl apply -f k8s/namespace.yaml

# Services (en séquence pour éviter surcharge RAM)
log_info "Déploiement Security Guardian..."
kubectl apply -f k8s/security-guardian.yaml

log_info "Attente initialisation Security Guardian..."
kubectl wait --for=condition=ready pod \
    -l component=security-guardian \
    -n phoenix-letters --timeout=300s

log_info "Déploiement Smart Router..."
kubectl apply -f k8s/smart-router.yaml

# Vérification déploiement
log_info "Vérification du déploiement..."
kubectl get pods -n phoenix-letters

# URLs d'accès
log_info "Récupération URLs d'accès..."

SMART_ROUTER_URL=$(minikube service smart-router-service -n phoenix-letters --url 2>/dev/null)
SECURITY_URL=$(minikube service security-guardian-service -n phoenix-letters --url 2>/dev/null)

echo ""
echo "🎉 DÉPLOIEMENT TERMINÉ !"
echo "======================"
echo ""
echo "📊 URLs d'accès :"
echo "- Smart Router: $SMART_ROUTER_URL"
echo "- Security Guardian: $SECURITY_URL"
echo "- Dashboard K8s: minikube dashboard"
echo ""
echo "🧪 Tests :"
echo "curl $SMART_ROUTER_URL/health"
echo "curl $SECURITY_URL/health"
echo ""
echo "📊 Monitoring :"
echo "kubectl get pods -n phoenix-letters"
echo "kubectl logs -f deployment/smart-router -n phoenix-letters"
echo ""
echo "🛑 Arrêt :"
echo "kubectl delete namespace phoenix-letters"
echo "minikube stop"

log_success "Phoenix Letters déployé sur Kubernetes ! 🚀"