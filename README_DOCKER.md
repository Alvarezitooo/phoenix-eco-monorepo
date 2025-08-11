# 🐳 Phoenix Ecosystem - Docker DevSecOps

## 🚀 **Lancement ULTRA-Simple (tout automatisé !)**

```bash
# 1. Setup tunnel Cloudflare (une seule fois)
./setup_docker_tunnel.sh

# 2. Démarrer toute la stack Phoenix (agents IA + tunnel + monitoring)
docker compose up -d

# 3. C'est tout ! 🎉
# → Agents IA avec URL fixe automatique
# → Plus besoin de gérer plusieurs terminaux
```

**URL fixe générée automatiquement :** `https://phoenix-docker-123.cfargotunnel.com`

## 🏗️ **Architecture Docker**

```
🐳 Phoenix Ecosystem Docker Stack
├── 🧠 phoenix-agents:8001    → Agents IA (FastAPI)
├── 🌐 phoenix-tunnel         → Tunnel Cloudflare permanent
├── 🤖 phoenix-ollama:11434   → Modèles locaux (Ollama)
├── 📊 phoenix-letters:8501   → App principale 
├── 📄 phoenix-cv:8502        → Générateur CV
├── 🌅 phoenix-rise:8503      → Coaching mental
├── 🌅 phoenix-aube:8504      → Exploration carrière EU
├── 📈 prometheus:9090        → Métriques
├── 🗃️ loki:3100             → Logs centralisés  
├── 🎨 grafana:3000          → Dashboard monitoring
└── 🔒 nginx:80/443          → Reverse proxy SSL
```

## 📊 **Monitoring & Logs**

### **Dashboard Grafana** → `http://localhost:3000`
- **User**: `admin` 
- **Password**: `phoenix123`
- **Dashboards**: Phoenix Apps, AI Agents, System Health

### **Logs en temps réel**
```bash
# Logs de tous les services
docker compose logs -f

# Logs des agents IA seulement  
docker compose logs -f phoenix-agents

# Logs de l'app Letters
docker compose logs -f phoenix-letters
```

## 🛡️ **Sécurité DevSecOps**

### **✅ Bonnes pratiques implémentées**
- **Utilisateurs non-root** dans tous les conteneurs
- **Health checks** pour tous les services  
- **Réseau isolé** Phoenix (172.20.0.0/16)
- **Volumes persistants** pour les données
- **SSL/TLS ready** avec Nginx
- **Monitoring complet** Prometheus + Grafana
- **Logs centralisés** avec Loki

### **🔐 Variables sensibles**
Toutes les clés API sont dans `.env` (jamais commitées)

## 🚀 **Commandes Utiles**

```bash
# Démarrer la stack complète
docker compose up -d

# Arrêter proprement
docker compose down

# Rebuild après modifications
docker compose up -d --build

# Voir les logs en temps réel
docker compose logs -f

# Status des services
docker compose ps

# Accéder au shell d'un service
docker compose exec phoenix-agents /bin/bash

# Nettoyer complètement (⚠️ supprime données)
docker compose down -v
docker system prune -a
```

## 🎯 **URLs d'accès rapide**

| Service | URL | Description |
|---------|-----|-------------|
| **Phoenix Letters** | http://localhost:8501 | App principale |
| **Phoenix CV** | http://localhost:8502 | Générateur CV |  
| **Phoenix Rise** | http://localhost:8503 | Coaching mental |
| **Phoenix Aube** | http://localhost:8504 | Exploration carrière EU |
| **AI Agents API** | http://localhost:8001 | API agents IA |
| **Grafana** | http://localhost:3000 | Monitoring |
| **Prometheus** | http://localhost:9090 | Métriques |
| **Ollama** | http://localhost:11434 | Modèles IA |

## 🔧 **Développement**

### **Hot reload activé**
Les volumes Docker permettent le hot reload - modifiez votre code et voyez les changements instantanément !

### **Debug d'un service**
```bash
# Logs détaillés
docker compose logs -f phoenix-agents

# Shell dans le conteneur  
docker compose exec phoenix-agents /bin/bash

# Redémarrer un service
docker compose restart phoenix-agents
```

---

## ✨ **Ready to go !**

**Une seule commande pour tout démarrer** :
```bash
docker compose up -d
```

Puis ouvrez **http://localhost** et profitez de votre écosystème Phoenix sécurisé ! 🚀