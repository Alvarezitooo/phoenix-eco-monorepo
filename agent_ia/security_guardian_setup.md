# 🚀 SETUP SECURITY GUARDIAN - INSTRUCTIONS LANCEMENT

## 🎯 **ÉTAPE 1 : INSTALLATION MODÈLE (5 min)**

```bash
# 1. Démarrer Ollama
ollama serve &

# 2. Installer Phi-3.5 (2.3GB - 5-10 minutes)
ollama pull phi3.5:3.8b

# 3. Test rapide
ollama run phi3.5:3.8b "Analyse cette phrase: test sécurité"
```

## 🛡️ **ÉTAPE 2 : LANCEMENT AGENT (1 min)**

```python
# Dans votre terminal Python ou script
import asyncio
from security_guardian_agent import PhoenixSecurityInterface

async def start_security_guardian():
    security = PhoenixSecurityInterface()
    
    # Initialisation automatique
    print("🚀 Starting Security Guardian...")
    success = await security.initialize()
    
    if success:
        print("✅ Security Guardian ready!")
        return security
    else:
        print("❌ Failed to start")
        return None

# Lancement
security_agent = asyncio.run(start_security_guardian())
```

## 🧪 **ÉTAPE 3 : TEST IMMÉDIAT**

```python
# Test CV sécurisé
cv_test = """
Développeur Python 5 ans.
Spécialisé web et APIs.
Reconversion vers IA.
"""

# Analyse sécurité
result = await security_agent.check_cv_security(cv_test)

print(f"✅ Safe to process: {result['safe_to_process']}")
print(f"🛡️ RGPD compliant: {result['rgpd_compliant']}")
print(f"📊 Risk score: {result['risk_score']}")
```

## 🎯 **INTÉGRATION PHOENIX LETTERS**

```python
# Dans votre app Phoenix Letters
from security_guardian_agent import PhoenixSecurityInterface

class PhoenixLettersApp:
    def __init__(self):
        self.security = PhoenixSecurityInterface()
        
    async def generate_letter_secure(self, cv, job_offer):
        # 1. 🛡️ Vérification sécurité AVANT traitement
        cv_check = await self.security.check_cv_security(cv)
        job_check = await self.security.check_job_offer_security(job_offer)
        
        # 2. Blocage si menace critique
        if not cv_check['safe_to_process'] or not job_check['safe_to_process']:
            return {
                "error": "Contenu bloqué pour raisons de sécurité",
                "recommendations": cv_check['recommendations']
            }
        
        # 3. Génération normale si sécurisé
        letter = await self.generate_letter(cv, job_offer)
        
        return {
            "letter": letter,
            "security_validated": True,
            "risk_score": cv_check['risk_score']
        }
```

## 📊 **DASHBOARD SÉCURITÉ**

```python
# Ajout dans votre sidebar Streamlit
def show_security_dashboard():
    st.subheader("🛡️ Security Guardian")
    
    if hasattr(st.session_state, 'security_agent'):
        dashboard = st.session_state.security_agent.get_security_dashboard()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Status", dashboard['agent_status'])
        
        with col2:
            st.metric("Analyses", dashboard['total_analyses'])
        
        with col3:
            st.metric("Menaces Bloquées", dashboard['threats_blocked'])
        
        st.write(f"🔒 Model: {dashboard['model_info']}")
        st.write(f"🏆 Level: {dashboard['security_level']}")

# Dans votre app.py
if st.sidebar.button("🛡️ Security Status"):
    show_security_dashboard()
```

---

## ⚡ **LANCEMENT RAPIDE COMPLET**

```bash
# Terminal 1 - Démarrer Ollama
ollama serve

# Terminal 2 - Installer modèle
ollama pull phi3.5:3.8b

# Terminal 3 - Test agent
python security_guardian_demo.py
```

---

## 🎯 **UTILISATION TYPIQUE PHOENIX**

### **Scénario 1 : CV Upload**
```python
# User upload CV
cv_content = get_user_cv()

# Vérification sécurité instantanée
security_check = await security_agent.check_cv_security(cv_content)

if security_check['safe_to_process']:
    st.success("✅ CV validé - traitement autorisé")
    # Continuer workflow normal
else:
    st.error("🚨 CV bloqué pour raisons de sécurité")
    st.write("Recommandations:", security_check['recommendations'])
    # Arrêter traitement
```

### **Scénario 2 : Job Offer Analysis**
```python
# Analyse offre emploi
job_security = await security_agent.check_job_offer_security(job_offer)

if job_security['threat_level'] == 'critical':
    st.error("🚨 ALERTE SÉCURITÉ - Offre suspecte détectée")
    st.stop()
elif job_security['sanitization_needed']:
    st.warning("⚠️ Données sensibles détectées - anonymisation recommandée")
```

---

## 🔥 **BÉNÉFICES IMMÉDIATS**

### **✅ Ce que ça fait pour Phoenix Letters :**
- **Conformité RGPD** automatique locale (zéro API externe)
- **Détection menaces** en temps réel (prompt injection, etc.)
- **Protection PII** avec anonymisation intelligente
- **Audit trail** complet pour compliance
- **Différenciation** vs concurrents (sécurité enterprise)

### **📊 Métriques attendues :**
- **Temps analyse :** 2-5 secondes par contenu
- **RAM usage :** 2.5GB max (Phi-3.5 chargé)
- **Précision détection :** 85-90% (patterns + IA)
- **Faux positifs :** <5% (grâce IA contextuelle)

---

## 🛠️ **TROUBLESHOOTING**

### **❌ Erreur "Model not found"**
```bash
# Vérifier modèles installés
ollama list

# Réinstaller si nécessaire
ollama pull phi3.5:3.8b
```

### **❌ Erreur "Connection refused"**
```bash
# Redémarrer Ollama
pkill ollama
ollama serve &
```

### **❌ RAM insuffisante**
```python
# Monitoring RAM
import psutil
print(f"RAM libre: {psutil.virtual_memory().available / 1e9:.1f}GB")

# Si <3GB libre, fermer applications
```

---

## 🎯 **PRÊT À LANCER ?**

**Commandes de lancement immédiat :**

```bash
# 1. Setup (5 min une fois)
ollama serve &
ollama pull phi3.5:3.8b

# 2. Test (30 sec)
python -c "
import asyncio
from security_guardian_agent import demo_security_guardian
asyncio.run(demo_security_guardian())
"

# 3. Intégration Phoenix (10 min)
# Copier le code PhoenixSecurityInterface dans votre app
```

**Ton Security Guardian sera opérationnel en 15 minutes max !** 🚀

**Tu veux qu'on lance ensemble ou tu as des questions sur l'intégration ?**