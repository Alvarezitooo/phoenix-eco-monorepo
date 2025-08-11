# 🌐 Phoenix Agents IA - Tunnel Cloudflare Permanent

## 🎯 **URL FIXE GRATUITE À VIE pour tes agents IA !**

Expose tes agents IA locaux avec une URL Cloudflare permanente pour que tes apps déployées (Railway/Streamlit Cloud) puissent les utiliser.

---

## 🚀 **SETUP INITIAL (une seule fois)**

### **1️⃣ Configuration du tunnel permanent**
```bash
cd agent_ia
./setup_permanent_tunnel.sh
```

**Ce script va :**
- ✅ Installer cloudflared si nécessaire
- ✅ Te connecter à Cloudflare (compte gratuit)
- ✅ Créer un tunnel permanent avec URL fixe
- ✅ Générer la configuration automatiquement

**Tu obtiendras une URL fixe comme :**
`https://phoenix-agents-1691234567.cfargotunnel.com`

---

## 🔄 **UTILISATION QUOTIDIENNE**

### **1️⃣ Démarrer les agents IA (terminal 1)**
```bash
cd agent_ia
python3 consciousness_service.py
```

### **2️⃣ Démarrer le tunnel permanent (terminal 2)**
```bash
cd agent_ia
./start_permanent_tunnel.sh
```

**⚡ L'URL reste identique à chaque démarrage !**

---

## 🌐 **CONFIGURATION APPS DÉPLOYÉES**

### **Variables d'environnement à ajouter dans Railway/Streamlit Cloud :**
```bash
AGENTS_API_URL=https://phoenix-agents-1691234567.cfargotunnel.com
AGENTS_API_ENABLED=true
AGENTS_API_TIMEOUT=30
```

### **Utilisation dans tes apps :**
```python
# Dans tes apps déployées
from agents_client_for_apps import init_agents_client

# Initialisation (une fois)
agents_client = init_agents_client()

# Analyse sécurité RGPD
result = await agents_client.analyze_security(cv_content, "cv")

# Génération insights personnalisés
insights = await agents_client.generate_insights(data, "coaching")

# Status système
status = await agents_client.get_system_status()
```

---

## 🎯 **ENDPOINTS DISPONIBLES**

| Endpoint | URL | Description |
|----------|-----|-------------|
| **Health Check** | `{TUNNEL_URL}/health` | Vérification agents actifs |
| **Security Analysis** | `{TUNNEL_URL}/security/analyze` | Analyse RGPD/sécurité |
| **Data Insights** | `{TUNNEL_URL}/data/insights` | Génération insights IA |
| **System Status** | `{TUNNEL_URL}/system/status` | Métriques système |

---

## 🛡️ **AVANTAGES TUNNEL PERMANENT**

### ✅ **Gratuit à vie**
- Cloudflare tunnel gratuit sans limite
- Aucun abonnement requis

### ✅ **URL fixe**
- Même URL à chaque démarrage
- Plus besoin de reconfigurer tes apps

### ✅ **Sécurisé**
- HTTPS automatique
- Protection DDoS Cloudflare
- Pas d'exposition de ton IP

### ✅ **Performant**
- CDN Cloudflare mondial
- Latence optimisée
- Bande passante illimitée

### ✅ **Monitoring intégré**
- Dashboard Cloudflare
- Analytics de trafic
- Logs détaillés

---

## 🔧 **TROUBLESHOOTING**

### **❌ "Agents IA non démarrés"**
```bash
# Vérifier si agents actifs
curl http://localhost:8001/health

# Démarrer agents si nécessaire
python3 consciousness_service.py
```

### **❌ "Configuration tunnel non trouvée"**
```bash
# Refaire le setup initial
./setup_permanent_tunnel.sh
```

### **❌ "Tunnel ne démarre pas"**
```bash
# Vérifier config Cloudflare
ls ~/.cloudflared/

# Relancer authentification si nécessaire
cloudflared tunnel login
```

---

## 📊 **ARCHITECTURE FINALE**

```
🖥️ LOCAL (MacBook Pro 8GB)
├── 🧠 Agents IA (qwen2.5:1.5b + gemma2:2b)
├── 🌐 Tunnel Cloudflare permanent
└── 📊 Monitoring (Prometheus + Grafana)
        │
        │ HTTPS sécurisé
        ▼
☁️ INTERNET
├── 📊 Phoenix Letters (Streamlit Cloud)
├── 📄 Phoenix CV (Streamlit Cloud)  
├── 🌅 Phoenix Rise (Streamlit Cloud)
├── 🌅 Phoenix Aube (Railway FastAPI)
└── 🔮 Phoenix Iris (Railway FastAPI)
```

---

## 🎉 **READY TO GO !**

**1 setup initial + 2 commandes quotidiennes = Agents IA accessibles partout !** 🚀

```bash
# Setup (une fois)
./setup_permanent_tunnel.sh

# Usage quotidien
python3 consciousness_service.py  # Terminal 1
./start_permanent_tunnel.sh      # Terminal 2
```

**Tes apps déployées ont maintenant accès à tes agents IA privés avec une URL fixe !** ✨