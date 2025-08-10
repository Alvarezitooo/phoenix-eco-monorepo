#!/bin/bash
# 🧠 TEST FLYWHEEL 2.0 - Architecture Conscience Système Phoenix
set -e

echo "🧠 PHOENIX FLYWHEEL 2.0 - TEST CONSCIENCE SYSTÈME"
echo "================================================="

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

# Variables
BASE_DIR="$(dirname "$0")"
DOCKER_DIR="$BASE_DIR/docker"

# ========================================
# 🚀 DÉMARRAGE SERVICES
# ========================================

log_info "Démarrage architecture Flywheel 2.0..."

cd "$DOCKER_DIR"

# Build services
log_info "Build des services Phoenix avec System Consciousness..."
docker-compose build system-consciousness smart-router

if [ $? -ne 0 ]; then
    log_error "Échec du build"
    exit 1
fi

# Démarrage séquentiel pour éviter surcharge RAM
log_info "Démarrage System Consciousness..."
docker-compose up -d system-consciousness

log_info "Attente initialisation Consciousness (30s)..."
sleep 30

# Vérification Consciousness
log_info "Test santé System Consciousness..."
CONSCIOUSNESS_HEALTH=$(curl -s -f http://localhost:8003/health 2>/dev/null || echo "failed")

if [[ "$CONSCIOUSNESS_HEALTH" == "failed" ]]; then
    log_error "System Consciousness non disponible"
    docker-compose logs system-consciousness
    exit 1
fi

log_success "System Consciousness opérationnel"

# Démarrage Smart Router
log_info "Démarrage Smart Router avec intégration Consciousness..."
docker-compose up -d smart-router

log_info "Attente initialisation Smart Router (20s)..."
sleep 20

# ========================================
# 🧪 TESTS FONCTIONNELS
# ========================================

log_info "Début des tests Flywheel 2.0..."

# Test 1: Dashboard Consciousness
log_info "Test 1: Dashboard System Consciousness"
DASHBOARD_RESPONSE=$(curl -s -f http://localhost:8003/api/consciousness/dashboard 2>/dev/null)

if [[ $? -eq 0 ]]; then
    log_success "✅ Dashboard Consciousness accessible"
    
    # Extraction état système
    SYSTEM_STATE=$(echo "$DASHBOARD_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('system_state', 'unknown'))" 2>/dev/null || echo "unknown")
    log_info "   État système: $SYSTEM_STATE"
    
    CONSCIOUSNESS_LEVEL=$(echo "$DASHBOARD_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('consciousness_level', 'unknown'))" 2>/dev/null || echo "unknown")
    log_info "   Niveau conscience: $CONSCIOUSNESS_LEVEL"
else
    log_error "❌ Dashboard Consciousness inaccessible"
fi

# Test 2: Métriques détaillées
log_info "Test 2: Métriques détaillées"
METRICS_RESPONSE=$(curl -s -f http://localhost:8003/api/consciousness/metrics/detailed 2>/dev/null)

if [[ $? -eq 0 ]]; then
    log_success "✅ Métriques détaillées accessibles"
    
    DECISIONS_COUNT=$(echo "$METRICS_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('total_decisions', 0))" 2>/dev/null || echo "0")
    log_info "   Décisions prises: $DECISIONS_COUNT"
else
    log_error "❌ Métriques détaillées inaccessibles"
fi

# Test 3: Intégration Smart Router
log_info "Test 3: Intégration Smart Router"
ROUTER_HEALTH=$(curl -s -f http://localhost:8000/health 2>/dev/null)

if [[ $? -eq 0 ]]; then
    log_success "✅ Smart Router accessible"
    
    # Test endpoints consciousness via router
    CONSCIOUSNESS_STATUS=$(curl -s -f http://localhost:8000/api/consciousness/status 2>/dev/null)
    
    if [[ $? -eq 0 ]]; then
        log_success "✅ Endpoints Consciousness via Smart Router OK"
    else
        log_warning "⚠️ Endpoints Consciousness via Smart Router non disponibles"
    fi
else
    log_error "❌ Smart Router inaccessible"
fi

# Test 4: Simulation charge système
log_info "Test 4: Simulation charge pour décisions conscience"

log_info "Envoi de requêtes multiples pour tester auto-régulation..."
for i in {1..5}; do
    curl -s http://localhost:8000/health > /dev/null 2>&1 &
    curl -s http://localhost:8003/api/consciousness/dashboard > /dev/null 2>&1 &
done

log_info "Attente réaction System Consciousness (60s)..."
sleep 60

# Vérification réactions
RECENT_DECISIONS=$(curl -s -f http://localhost:8003/api/consciousness/metrics/detailed 2>/dev/null | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    decisions = data.get('recent_decisions', [])
    print(f'{len(decisions)} décisions récentes')
    for decision in decisions[-3:]:
        print(f'  - État: {decision.get(\"state\", \"unknown\")}, Actions: {decision.get(\"actions_count\", 0)}')
except:
    print('Erreur parsing décisions')
" 2>/dev/null)

log_info "Décisions récentes:"
echo "$RECENT_DECISIONS"

# Test 5: Alertes système
log_info "Test 5: Système d'alertes"
ALERTS_RESPONSE=$(curl -s -f http://localhost:8003/api/consciousness/alerts 2>/dev/null)

if [[ $? -eq 0 ]]; then
    ALERT_COUNT=$(echo "$ALERTS_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('alert_count', 0))" 2>/dev/null || echo "0")
    log_success "✅ Système d'alertes: $ALERT_COUNT alertes actives"
else
    log_error "❌ Système d'alertes inaccessible"
fi

# ========================================
# 📊 RAPPORT FINAL
# ========================================

echo ""
log_info "========================================="
log_info "RAPPORT FINAL - FLYWHEEL 2.0"
log_info "========================================="

# Status services
SERVICES_STATUS=""

# Consciousness
if curl -s -f http://localhost:8003/health > /dev/null 2>&1; then
    SERVICES_STATUS="$SERVICES_STATUS\n✅ System Consciousness: OPERATIONAL"
else
    SERVICES_STATUS="$SERVICES_STATUS\n❌ System Consciousness: DOWN"
fi

# Smart Router
if curl -s -f http://localhost:8000/health > /dev/null 2>&1; then
    SERVICES_STATUS="$SERVICES_STATUS\n✅ Smart Router: OPERATIONAL"
else
    SERVICES_STATUS="$SERVICES_STATUS\n❌ Smart Router: DOWN"
fi

echo -e "$SERVICES_STATUS"

# Métriques finales
FINAL_DASHBOARD=$(curl -s -f http://localhost:8003/api/consciousness/dashboard 2>/dev/null)
if [[ $? -eq 0 ]]; then
    echo ""
    log_info "📊 MÉTRIQUES FINALES:"
    
    FINAL_STATE=$(echo "$FINAL_DASHBOARD" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('system_state', 'unknown'))" 2>/dev/null || echo "unknown")
    FINAL_DECISIONS=$(echo "$FINAL_DASHBOARD" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('decisions_count', 0))" 2>/dev/null || echo "0")
    FINAL_LEVEL=$(echo "$FINAL_DASHBOARD" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('consciousness_level', 'unknown'))" 2>/dev/null || echo "unknown")
    
    echo "   - État système final: $FINAL_STATE"
    echo "   - Total décisions: $FINAL_DECISIONS"
    echo "   - Niveau conscience: $FINAL_LEVEL"
fi

# URLs d'accès
echo ""
log_info "🔗 URLS D'ACCÈS:"
echo "   - System Consciousness: http://localhost:8003/docs"
echo "   - Smart Router: http://localhost:8000/docs"
echo "   - Dashboard Consciousness: http://localhost:8003/api/consciousness/dashboard"
echo "   - Métriques temps réel: http://localhost:8003/api/consciousness/metrics/detailed"

# Commandes utiles
echo ""
log_info "🛠️ COMMANDES UTILES:"
echo "   - Logs Consciousness: docker-compose logs -f system-consciousness"
echo "   - Logs Smart Router: docker-compose logs -f smart-router"
echo "   - Status conscience: curl http://localhost:8003/api/consciousness/status/simple | jq"
echo "   - Arrêt urgence: curl -X POST http://localhost:8003/api/consciousness/emergency-stop"

echo ""
if curl -s -f http://localhost:8003/health > /dev/null 2>&1 && curl -s -f http://localhost:8000/health > /dev/null 2>&1; then
    log_success "🎉 FLYWHEEL 2.0 OPÉRATIONNEL - Système conscient et auto-régulé !"
    log_info "🧠 Phoenix Letters dispose maintenant d'une IA qui surveille sa propre santé"
    echo ""
    echo "🚀 Prochaines étapes :"
    echo "   1. Intégrer avec Streamlit: PhoenixAIClient(base_url='http://localhost:8000')"
    echo "   2. Monitorer via dashboard: http://localhost:8003/api/consciousness/dashboard"
    echo "   3. Déployer en production avec Kubernetes"
else
    log_error "🚨 FLYWHEEL 2.0 PARTIELLEMENT FONCTIONNEL"
    echo "Vérifiez les logs pour diagnostiquer les problèmes"
fi

echo ""
log_info "Test terminé. Services maintenus en fonctionnement pour inspection."
log_info "Arrêt: docker-compose down"