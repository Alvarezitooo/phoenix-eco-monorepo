# 🚀 PHOENIX ECOSYSTEM - Guide de Déploiement Render

## ✅ Prérequis Validés

✅ **Architecture monorepo** - Prête pour déploiement  
✅ **Docker configuration** - Dockerfile universel créé  
✅ **Services refactorisés** - Clean Code appliqué  
✅ **Render CLI installé** - Version 2.1.4 opérationnelle  

## 🎯 Méthodes de Déploiement

### Option 1: Script Python Automatique (RECOMMANDÉ)

```bash
# 1. Obtenez votre clé API Render
open https://dashboard.render.com/account/api-keys

# 2. Exportez la clé API
export RENDER_API_KEY=rnd_your_api_key_here

# 3. Déployez l'écosystème
python3 deploy-render.py
```

### Option 2: Blueprint Manual

```bash
# 1. Push le code sur GitHub
git add .
git commit -m "🚀 DEPLOY: Phoenix Ecosystem ready for Render"
git push origin main

# 2. Créez un nouveau service sur Render Dashboard
# https://dashboard.render.com/create/blueprint

# 3. Connectez votre repo GitHub
# Repo: votre-username/phoenix-eco-monorepo
# Branch: main
# Blueprint: render.yaml
```

## 📋 Services à Déployer

| Service | Type | Port | Health Check |
|---------|------|------|-------------|
| **phoenix-letters** | Web (Streamlit) | 8501 | `/_stcore/health` |
| **phoenix-cv** | Web (Streamlit) | 8501 | `/_stcore/health` |
| **phoenix-backend-unified** | Web (FastAPI) | 8000 | `/health` |
| **phoenix-iris-api** | Web (FastAPI) | 8000 | `/health` |
| **phoenix-agents-ai** | Web (FastAPI) | 8000 | `/health` |
| **phoenix-event-bridge** | Worker | - | - |
| **phoenix-user-profile** | Worker | - | - |
| **phoenix-redis** | Database | - | - |

## 🔐 Variables d'Environnement Critiques

**Après déploiement**, configurez ces variables sur le dashboard Render :

### Authentification & Sécurité
```bash
JWT_SECRET_KEY=your_jwt_secret_key
JWT_REFRESH_SECRET=your_refresh_secret
```

### Base de Données (Supabase)
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
```

### Intelligence Artificielle
```bash
GOOGLE_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key
```

### Paiements (Stripe)
```bash
STRIPE_SECRET_KEY=sk_live_or_test_your_key
STRIPE_PUBLISHABLE_KEY=pk_live_or_test_your_key
STRIPE_CV_PRICE_ID=price_your_cv_price_id
```

## 🏗️ Architecture Déployée

```
🌐 Phoenix Ecosystem sur Render
├── 🔸 phoenix-letters.onrender.com
├── 🔸 phoenix-cv.onrender.com  
├── 🔸 phoenix-backend-unified.onrender.com
├── 🔸 phoenix-iris-api.onrender.com
├── 🔸 phoenix-agents-ai.onrender.com
├── ⚙️ phoenix-event-bridge (worker)
├── ⚙️ phoenix-user-profile (worker)  
└── 🗄️ phoenix-redis (database)
```

## ✅ Validation Post-Déploiement

Après déploiement, testez chaque service :

```bash
# Test des services web
curl https://phoenix-letters.onrender.com/_stcore/health
curl https://phoenix-cv.onrender.com/_stcore/health
curl https://phoenix-backend-unified.onrender.com/health
curl https://phoenix-iris-api.onrender.com/health
curl https://phoenix-agents-ai.onrender.com/health
```

## 🛠️ Dépannage

### Erreur de Build Docker
- Vérifiez que le Dockerfile est à la racine du monorepo
- Vérifiez les variables d'environnement APP_NAME

### Erreur 503 Service Unavailable  
- Attendez que le build se termine (premier déploiement = 5-10 min)
- Vérifiez les logs dans le dashboard Render

### Erreur d'authentification
- Vérifiez que toutes les clés API sont configurées
- Testez les connexions Supabase et Stripe séparément

## 🎉 Succès !

Une fois déployé, votre écosystème Phoenix sera accessible 24/7 avec :
- ✅ Auto-scaling automatique
- ✅ SSL/HTTPS natif
- ✅ Monitoring intégré
- ✅ Logs centralisés
- ✅ Zero-downtime deployments

---

**🏛️ Phoenix Architect** - Écosystème déployé avec succès !