# 🔥 Phoenix Backend Unifié

Backend FastAPI centralisé pour l'écosystème Phoenix (Aube, Rise, CV).

## 🚀 Features

- **Authentication centralisée** avec Supabase
- **APIs REST** pour Phoenix Aube (diagnostic carrière)  
- **APIs REST** pour Phoenix Rise (Kaizen + Zazen)
- **JWT Security** avec refresh tokens
- **CORS configuré** pour les frontends Vercel
- **Health checks** et monitoring
- **Error handling** centralisé
- **Docker ready** pour Railway

## 📋 Architecture

```
phoenix-backend-unified/
├── main.py                 # Application FastAPI principale
├── routers/
│   ├── auth.py            # Authentification (/api/v1/auth/*)
│   ├── aube.py            # Phoenix Aube (/api/v1/aube/*)
│   ├── rise.py            # Phoenix Rise (/api/v1/rise/*)
│   └── health.py          # Health checks (/health)
├── services/
│   ├── supabase_client.py # Client Supabase centralisé
│   └── auth_service.py    # Service authentification
├── middleware/
│   └── error_handler.py   # Gestion d'erreurs globales
└── config/
    └── settings.py        # Configuration environnement
```

## 🔧 Installation Locale

```bash
cd apps/phoenix-backend-unified

# Installation dépendances
pip install -r requirements.txt

# Configuration environnement
cp .env.example .env
# Éditer .env avec tes variables Supabase

# Démarrage développement
uvicorn main:app --reload --port 8000
```

## 📱 APIs Disponibles

### Authentication
- `POST /api/v1/auth/login` - Connexion utilisateur
- `GET /api/v1/auth/verify` - Vérification token
- `GET /api/v1/auth/me` - Info utilisateur connecté

### Phoenix Aube
- `POST /api/v1/aube/diagnostic/submit` - Soumission diagnostic
- `GET /api/v1/aube/career/matches/{user_id}` - Matches carrière
- `POST /api/v1/aube/events` - Tracking événements

### Phoenix Rise
- `POST /api/v1/rise/kaizen` - Créer action Kaizen
- `GET /api/v1/rise/kaizen/{user_id}` - Historique Kaizen
- `PUT /api/v1/rise/kaizen/{kaizen_id}` - Mise à jour Kaizen
- `POST /api/v1/rise/zazen-session` - Session Zazen
- `GET /api/v1/rise/zazen-sessions/{user_id}` - Historique Zazen
- `GET /api/v1/rise/stats/{user_id}` - Statistiques utilisateur

### Health & Monitoring
- `GET /health` - Health check basique
- `GET /health/detailed` - Health check détaillé
- `GET /` - Info API
- `GET /docs` - Documentation Swagger

## 🚀 Déploiement Railway

1. **Connecter ce dossier** à Railway
2. **Variables d'environnement** à configurer :
   ```
   SUPABASE_URL=https://ton-project.supabase.co
   SUPABASE_ANON_KEY=ton-anon-key
   JWT_SECRET=ton-secret-jwt
   ALLOWED_ORIGINS=https://phoenix-aube.vercel.app,https://phoenix-rise.vercel.app
   ```
3. **Health check** : `/health`
4. **Port** : 8000

## 🔗 Intégration Frontends

### Vercel.json à mettre à jour :
```json
{
  "rewrites": [
    {
      "source": "/api/v1/:path*",
      "destination": "https://ton-backend.railway.app/api/v1/:path*"
    }
  ]
}
```

## 🛡️ Sécurité

- JWT tokens avec expiration
- CORS strictement configuré
- Rate limiting (à ajouter)
- Validation Pydantic automatique
- Logs sécurisés (PII anonymisée)

## 📊 Monitoring

- Health checks intégrés
- Logs structurés JSON
- Métriques système (CPU, RAM, Disk)
- Suivi erreurs centralisé