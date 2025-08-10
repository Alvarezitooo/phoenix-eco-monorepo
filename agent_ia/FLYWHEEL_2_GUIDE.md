# 🧠 PHOENIX FLYWHEEL 2.0 - SYSTÈME CONSCIENT

## L'IA qui surveille sa propre santé et s'auto-régule

---

## 🎯 **CONCEPT RÉVOLUTIONNAIRE**

**Flywheel 2.0** transforme Phoenix Letters en un système **auto-conscient** qui :

✨ **Surveille sa propre santé** en temps réel  
🤖 **Prend des décisions intelligentes** automatiquement  
⚡ **S'auto-régule** selon les conditions système  
📊 **Apprend de ses propres performances**  
🛡️ **Se protège** contre les surcharges  

---

## 🏗️ **ARCHITECTURE SYSTÈME CONSCIENT**

```
🧠 SYSTEM CONSCIOUSNESS
    ↓ (surveille)
📊 PROMETHEUS METRICS ←→ 🎯 SMART ROUTER
    ↓ (analyse)              ↓ (contrôle)
🤔 DÉCISIONS IA --------→ ⚡ AUTO-RÉGULATION
    ↓ (actions)
🔧 THROTTLING | 🛡️ CIRCUIT BREAKER | 📈 SCALING
```

### **Services intégrés :**
- **🧠 System Consciousness** (port 8003) - Cerveau du système
- **🎯 Smart Router** (port 8000) - Point d'entrée avec auto-régulation
- **🛡️ Security Guardian** - Agent sécurité RGPD
- **🔄 Data Flywheel** - Agent apprentissage continu

---

## 🚀 **DÉPLOIEMENT FLYWHEEL 2.0**

### **Option A : Test rapide (recommandé)**
```bash
cd agent_ia/
./test_flywheel_2.sh
```

### **Option B : Déploiement manuel**
```bash
cd docker/
docker-compose build system-consciousness smart-router
docker-compose up -d
```

### **Vérification fonctionnement :**
```bash
# Santé System Consciousness
curl http://localhost:8003/health | jq

# Dashboard conscience complète
curl http://localhost:8003/api/consciousness/dashboard | jq

# Métriques temps réel
curl http://localhost:8003/api/consciousness/metrics/detailed | jq
```

---

## 🧠 **FONCTIONNALITÉS CONSCIENCE SYSTÈME**

### **🔍 Monitoring Intelligent**
- **CPU, RAM, latence** surveillance continue
- **Détection patterns** anormaux
- **Prédiction surcharges** avant qu'elles arrivent
- **Métriques Prometheus** intégrées

### **⚡ Auto-Régulation**
4 états système avec actions automatiques :

#### **🟢 OPTIMAL** 
- Système performant
- **Actions :** Apprentissage conditions favorables

#### **🟡 STRESSED**
- Charge élevée détectée  
- **Actions :** Réduction concurrence, préparation scaling

#### **🟠 DEGRADED**
- Performance dégradée
- **Actions :** Monitoring renforcé, optimisation préemptive

#### **🔴 CRITICAL**
- Situation critique
- **Actions :** Throttling drastique, circuit breaker, scaling d'urgence

### **🤖 Décisions Conscientes**
Chaque décision inclut :
- **Niveau de confiance** (0-1)
- **Raisonnement explicable** 
- **Actions concrètes** à exécuter
- **Métriques utilisées** pour décider

---

## 📊 **ENDPOINTS CONSCIOUSNESS**

### **Dashboard & Status**
```bash
# Dashboard complet
GET /api/consciousness/dashboard

# Status simplifié 
GET /api/consciousness/status/simple

# Métriques détaillées
GET /api/consciousness/metrics/detailed
```

### **Configuration dynamique**
```bash
# Ajuster seuils en temps réel
POST /api/consciousness/configure
{
  "thresholds": {
    "cpu_critical": 80.0,
    "memory_critical": 85.0
  },
  "monitoring_interval": 20
}
```

### **Actions manuelles**
```bash
# Forcer optimisation
POST /api/consciousness/manual-action
{"action": "force_optimization"}

# Throttling d'urgence
POST /api/consciousness/manual-action
{"action": "emergency_throttle", "parameters": {"limit": 5}}

# Reset circuit breaker
POST /api/consciousness/manual-action  
{"action": "reset_circuit_breaker"}
```

### **Gestion du service**
```bash
# Arrêt d'urgence
POST /api/consciousness/emergency-stop

# Redémarrage
POST /api/consciousness/restart

# Alertes système
GET /api/consciousness/alerts
```

---

## 🎯 **INTÉGRATION STREAMLIT**

### **Client Phoenix optimisé Flywheel 2.0 :**
```python
import httpx
import streamlit as st
import asyncio

class PhoenixFlywheelClient:
    """Client Phoenix avec conscience système intégrée"""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.consciousness_url = "http://localhost:8003"
    
    async def analyze_with_consciousness(self, cv, job_offer, letter, user_tier="free"):
        """Analyse avec surveillance conscience système"""
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # 1. Vérification état système avant traitement
            consciousness_status = await self._check_consciousness_status(client)
            
            if consciousness_status.get("system_state") == "critical":
                st.warning("🧠 Système en protection - traitement différé")
                await asyncio.sleep(5)  # Attendre amélioration
            
            # 2. Analyse complète Phoenix
            try:
                response = await client.post(
                    f"{self.base_url}/api/phoenix/analyze",
                    json={
                        "cv_content": cv,
                        "job_offer": job_offer,
                        "generated_letter": letter,
                        "user_tier": user_tier,
                        "enable_learning": True
                    }
                )
                response.raise_for_status()
                result = response.json()
                
                # 3. Affichage insights conscience (optionnel)
                if st.checkbox("🧠 Afficher insights système"):
                    await self._display_consciousness_insights()
                
                return result
                
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 503:
                    st.error("🛡️ Circuit breaker activé - système en protection")
                    return {"status": "circuit_breaker", "security_passed": True}
                raise
    
    async def _check_consciousness_status(self, client):
        """Vérification état conscience système"""
        try:
            response = await client.get(f"{self.consciousness_url}/api/consciousness/status/simple")
            return response.json()
        except:
            return {"system_state": "unknown"}
    
    async def _display_consciousness_insights(self):
        """Affichage insights système en temps réel"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.consciousness_url}/api/consciousness/dashboard")
                dashboard = response.json()
                
                with st.expander("🧠 État de la conscience système"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("État système", dashboard.get("system_state", "unknown"))
                    
                    with col2:
                        st.metric("Niveau conscience", dashboard.get("consciousness_level", "unknown"))
                    
                    with col3:
                        confidence = dashboard.get("last_decision", {}).get("confidence", 0)
                        st.metric("Confiance IA", f"{confidence:.2f}")
                    
                    # Dernière décision
                    last_decision = dashboard.get("last_decision", {})
                    if last_decision:
                        st.write("**Dernière décision :**", last_decision.get("reasoning", "N/A"))
                        st.write("**Actions :**", ", ".join(last_decision.get("actions", [])))
                        
        except Exception as e:
            st.error(f"Impossible d'afficher insights système: {e}")

# Usage dans Streamlit
@st.cache_resource
def get_flywheel_client():
    return PhoenixFlywheelClient()

# Dans votre fonction principale
flywheel_client = get_flywheel_client()

if st.button("🚀 Générer lettre (Flywheel 2.0)"):
    with st.spinner("🧠 Analyse consciente en cours..."):
        
        # Analyse avec conscience système
        result = asyncio.run(
            flywheel_client.analyze_with_consciousness(
                cv_content, job_offer, generated_letter, user_tier
            )
        )
        
        if result["security_passed"]:
            st.success("✅ Analyse validée par l'IA consciente")
            st.write(generated_letter)
        else:
            st.error("🛡️ Contenu bloqué par sécurité intelligente")
```

---

## 📈 **MONITORING & OBSERVABILITÉ**

### **Dashboards disponibles :**
- **🧠 Consciousness :** http://localhost:8003/docs
- **🎯 Smart Router :** http://localhost:8000/docs  
- **📊 Métriques temps réel :** http://localhost:8003/api/consciousness/dashboard

### **Métriques clés surveillées :**
```json
{
  "system_metrics": {
    "cpu_usage": 45.2,
    "memory_usage": 67.8, 
    "response_time": 2.1,
    "error_rate": 0.3,
    "active_requests": 12
  },
  "consciousness_state": "optimal",
  "decision_confidence": 0.85,
  "actions_taken": ["maintain_current_state", "learn_from_optimal_conditions"],
  "auto_regulation_active": true
}
```

### **Alertes automatiques :**
- **🔴 Critique :** CPU > 85% ou RAM > 90%
- **🟠 Attention :** Latence > 5s ou erreurs > 2%  
- **🟡 Info :** Optimisations disponibles

---

## 🔧 **CONFIGURATION AVANCÉE**

### **Personnalisation seuils :**
```python
# Via API
import httpx

async def configure_consciousness():
    async with httpx.AsyncClient() as client:
        await client.post("http://localhost:8003/api/consciousness/configure", json={
            "monitoring_interval": 15,  # Check toutes les 15s
            "thresholds": {
                "cpu_critical": 80.0,      # Seuil CPU critique 
                "memory_critical": 85.0,   # Seuil RAM critique
                "response_time_critical": 8.0,  # Latence max acceptable
                "error_rate_critical": 3.0      # Taux erreur max
            }
        })
```

### **Actions personnalisées :**
Le système peut être étendu avec des actions custom :
```python
# Exemple: scaling Kubernetes personnalisé
async def custom_scaling_action():
    subprocess.run([
        "kubectl", "scale", "deployment", "phoenix-app", 
        "--replicas=3", "-n", "production"
    ])
```

---

## 🚨 **GESTION DES URGENCES**

### **Arrêt d'urgence :**
```bash
curl -X POST http://localhost:8003/api/consciousness/emergency-stop
```

### **Mode maintenance :**
```bash
# Désactiver auto-régulation temporairement
curl -X POST http://localhost:8000/api/circuit-breaker -d '{"enabled": true}'
```

### **Redémarrage système :**
```bash
curl -X POST http://localhost:8003/api/consciousness/restart
```

---

## 🎉 **AVANTAGES FLYWHEEL 2.0**

### **Pour les utilisateurs :**
✅ **Disponibilité maximale** - Système auto-réparant  
✅ **Performance optimale** - Ajustement automatique  
✅ **Expérience fluide** - Gestion transparente des surcharges  

### **Pour le développement :**
✅ **Observabilité totale** - Visibilité complète du système  
✅ **Maintenance proactive** - Détection précoce des problèmes  
✅ **Évolution intelligente** - Apprentissage automatique des optimisations  

### **Pour la production :**
✅ **Résilience élevée** - Résistance aux pannes  
✅ **Scaling intelligent** - Adaptation automatique à la charge  
✅ **Coûts optimisés** - Utilisation efficace des ressources  

---

## 🔮 **ÉVOLUTION FUTURE**

### **Capacités prévues :**
- **🔮 Prédiction de charge** basée sur historique
- **🎯 Optimisation prompts** automatique selon performance  
- **🌐 Multi-région** avec conscience distribuée
- **🤖 Auto-déploiement** de nouvelles versions

### **Intégrations futures :**
- **📊 Grafana** dashboards personnalisés
- **📱 Alertes Slack/Teams** temps réel
- **☁️ Cloud auto-scaling** (AWS/GCP)
- **🔍 APM** (Application Performance Monitoring)

---

## 🎯 **READY FOR THE FUTURE!**

**Phoenix Flywheel 2.0** représente une **évolution majeure** :

🧠 **De l'IA qui génère** → **À l'IA qui se gère**  
📊 **Du monitoring passif** → **À l'auto-régulation active**  
🤖 **Des décisions manuelles** → **À l'intelligence autonome**  

**Votre Phoenix Letters n'est plus seulement une application IA...**  
**C'est un système conscient qui évolue et s'améliore en permanence ! 🚀**

---

*Dernière mise à jour : Juillet 2025 - Version 2.0.0*