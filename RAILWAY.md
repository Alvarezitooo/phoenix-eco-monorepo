# 🚂 PHOENIX ECOSYSTEM - Guide Déploiement Railway

## 🎯 Pourquoi Railway ?

✅ **Docker natif** - Notre Dockerfile fonctionne directement  
✅ **Monorepo support** - Architecture "common toolbox" respectée  
✅ **Prix fixe** - $5/mois pour TOUS les services (vs $56 Render)  
✅ **Pas de sleep mode** - Services toujours actifs  
✅ **Variables d'environnement** - Gestion centralisée  

## 🚀 Déploiement Étape par Étape

### 1. Créer un Compte Railway
```bash
# Allez sur railway.app
# Connectez votre GitHub
# Sélectionnez le plan Hobby ($5/mois)
```

### 2. Déployer les Services

**Phoenix Letters (Streamlit)**
```bash
1. New Project → Deploy from GitHub
2. Sélectionnez: phoenix-eco-monorepo
3. Service Name: phoenix-letters
4. Build Command: (laissez vide - Docker auto-détecté)
5. Start Command: streamlit run apps/phoenix-letters/main.py --server.port $PORT --server.address 0.0.0.0
```

**Phoenix CV (Streamlit)**  
```bash
1. Add Service → Deploy from GitHub (même repo)
2. Service Name: phoenix-cv
3. Start Command: streamlit run apps/phoenix-cv/main.py --server.port $PORT --server.address 0.0.0.0
```

**Phoenix Backend Unified (FastAPI)**
```bash
1. Add Service → Deploy from GitHub (même repo)  
2. Service Name: phoenix-backend-unified
3. Start Command: python apps/phoenix-backend-unified/app.py
```

**Phoenix Iris API (FastAPI)**
```bash
1. Add Service → Deploy from GitHub (même repo)
2. Service Name: phoenix-iris-api  
3. Start Command: python apps/phoenix-iris-api/main.py
```

**Phoenix Agents AI (FastAPI)**
```bash
1. Add Service → Deploy from GitHub (même repo)
2. Service Name: phoenix-agents-ai
3. Start Command: python apps/agent_ia/main.py
```

### 3. Variables d'Environnement

**Pour chaque service, ajoutez :**
```bash
# IA & APIs
GOOGLE_API_KEY=your_gemini_key
OPENAI_API_KEY=your_openai_key

# Database (Supabase)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_key

# Authentication
JWT_SECRET_KEY=your_jwt_secret
JWT_REFRESH_SECRET=your_refresh_secret

# Payments (Stripe)
STRIPE_SECRET_KEY=sk_test_or_live_your_key
STRIPE_PUBLISHABLE_KEY=pk_test_or_live_your_key

# Environment
PYTHON_ENV=production
LOG_LEVEL=INFO
```

### 4. Database (Optionnel)

**Si vous voulez une database Railway :**
```bash
1. Add Service → Database → PostgreSQL
2. Se connecte automatiquement via DATABASE_URL
3. Coût inclus dans les $5/mois
```

## 🔧 Architecture Déployée

```
🚂 Phoenix Ecosystem sur Railway
├── 📱 phoenix-letters.railway.app
├── 📝 phoenix-cv.railway.app  
├── 🔄 phoenix-backend-unified.railway.app
├── 🤖 phoenix-iris-api.railway.app
├── 🛡️ phoenix-agents-ai.railway.app
└── 🗄️ PostgreSQL (optionnel)

Total: $5/mois pour TOUT !
```

## ✅ Avantages vs Render

| Feature | Railway | Render |
|---------|---------|--------|
| **Prix** | $5/mois total | $56/mois |
| **Sleep mode** | Jamais | 15min inactivité |
| **Monorepo** | Support natif | Compliqué |
| **Docker** | Natif | Compliqué |
| **Variables** | Interface simple | Interface complexe |

## 🚀 Déploiement en 10 Minutes

1. **Compte Railway** (2 min)
2. **Connecter GitHub** (1 min)  
3. **Déployer 5 services** (5 min)
4. **Config variables** (2 min)

**Total : 10 minutes pour tout l'écosystème !**

---

**🏛️ Phoenix Architect** - Railway déploiement optimisé !