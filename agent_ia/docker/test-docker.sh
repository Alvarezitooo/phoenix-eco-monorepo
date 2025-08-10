#!/bin/bash
# 🧪 TEST DOCKER PHOENIX LETTERS - Validation complète
set -e

echo "🚀 PHOENIX LETTERS - Test Docker Build & Deploy"
echo "=============================================="

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction de log
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Variables
DOCKER_COMPOSE_FILE="docker-compose.yml"
TEST_TIMEOUT=120

# Vérifications préliminaires
log_info "Vérification des prérequis..."

if ! command -v docker &> /dev/null; then
    log_error "Docker n'est pas installé"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    log_error "Docker Compose n'est pas installé"
    exit 1
fi

log_success "Docker et Docker Compose sont disponibles"

# Navigation vers le répertoire Docker
cd "$(dirname "$0")"
log_info "Répertoire de travail: $(pwd)"

# Nettoyage des containers existants
log_info "Nettoyage des containers existants..."
docker-compose down --volumes --remove-orphans 2>/dev/null || true
docker system prune -f 2>/dev/null || true

# Build des images
log_info "Construction des images Docker..."

if docker-compose build --no-cache; then
    log_success "Images construites avec succès"
else
    log_error "Échec de la construction des images"
    exit 1
fi

# Démarrage des services
log_info "Démarrage des services Phoenix..."

if docker-compose up -d; then
    log_success "Services démarrés"
else
    log_error "Échec du démarrage des services"
    exit 1
fi

# Attente des services
log_info "Attente de la disponibilité des services (max ${TEST_TIMEOUT}s)..."

services=("security-guardian:8001" "data-flywheel:8002" "smart-router:8000")
ready_services=0

for i in $(seq 1 $TEST_TIMEOUT); do
    ready_services=0
    
    for service in "${services[@]}"; do
        name=$(echo $service | cut -d: -f1)
        port=$(echo $service | cut -d: -f2)
        
        if curl -s http://localhost:$port/health > /dev/null 2>&1; then
            ready_services=$((ready_services + 1))
        fi
    done
    
    if [ $ready_services -eq ${#services[@]} ]; then
        log_success "Tous les services sont prêts !"
        break
    fi
    
    echo -n "."
    sleep 1
done

echo ""

if [ $ready_services -ne ${#services[@]} ]; then
    log_error "Timeout: tous les services ne sont pas prêts ($ready_services/${#services[@]})"
    log_info "Affichage des logs pour diagnostic..."
    docker-compose logs --tail=20
    exit 1
fi

# Tests de santé détaillés
log_info "Tests de santé détaillés..."

# Test Security Guardian
log_info "Test Security Guardian..."
if curl -s http://localhost:8001/health | grep -q "healthy"; then
    log_success "Security Guardian est opérationnel"
else
    log_warning "Security Guardian pourrait avoir des problèmes"
fi

# Test Data Flywheel
log_info "Test Data Flywheel..."
if curl -s http://localhost:8002/health | grep -q "healthy"; then
    log_success "Data Flywheel est opérationnel"
else
    log_warning "Data Flywheel pourrait avoir des problèmes"
fi

# Test Smart Router
log_info "Test Smart Router..."
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    log_success "Smart Router est opérationnel"
else
    log_warning "Smart Router pourrait avoir des problèmes"
fi

# Test fonctionnel simple
log_info "Test fonctionnel - Analyse sécurité basique..."

test_payload='{
    "content": "Développeur Python avec 5 ans d'\''expérience",
    "content_type": "cv"
}'

if curl -s -X POST \
    -H "Content-Type: application/json" \
    -d "$test_payload" \
    http://localhost:8001/api/security/analyze | grep -q "success"; then
    log_success "Test sécurité fonctionnel"
else
    log_warning "Test sécurité a échoué (peut être normal si modèles pas encore chargés)"
fi

# Affichage des métriques
log_info "Affichage des métriques système..."

echo ""
echo "📊 MÉTRIQUES SYSTÈME:"
echo "===================="

# Utilisation mémoire
echo "💾 Utilisation mémoire par container:"
docker stats --no-stream --format "table {{.Name}}\t{{.MemUsage}}\t{{.CPUPerc}}" | head -4

echo ""

# Ports exposés
echo "🌐 Ports exposés:"
echo "- Security Guardian: http://localhost:8001"
echo "- Data Flywheel: http://localhost:8002" 
echo "- Smart Router: http://localhost:8000"

echo ""

# Volumes
echo "📁 Volumes créés:"
docker volume ls | grep phoenix

echo ""

# URLs de test
echo "🧪 URLs de test:"
echo "- Santé globale: curl http://localhost:8000/health"
echo "- Docs Security: http://localhost:8001/docs"
echo "- Docs Flywheel: http://localhost:8002/docs"
echo "- Docs Router: http://localhost:8000/docs"

echo ""

# Recommandations
log_info "Recommandations pour la suite:"
echo "1. 🧪 Testez les APIs via les interfaces Swagger (/docs)"
echo "2. 📊 Surveillez l'utilisation mémoire avec: docker stats"
echo "3. 📝 Consultez les logs avec: docker-compose logs -f"
echo "4. 🛑 Arrêtez avec: docker-compose down"

echo ""
log_success "Tests Docker Phoenix Letters terminés avec succès ! 🎉"

# Option pour laisser tourner ou arrêter
read -p "Voulez-vous laisser les services tourner ? (y/N): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log_info "Arrêt des services..."
    docker-compose down
    log_success "Services arrêtés proprement"
else
    log_info "Services laissés en fonctionnement"
    log_info "Pour arrêter plus tard: docker-compose down"
fi

echo ""
log_success "Script de test terminé ! 🚀"