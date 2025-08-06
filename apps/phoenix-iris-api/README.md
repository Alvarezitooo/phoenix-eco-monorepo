# 🤖 Phoenix Iris API

Assistant IA conversationnel pour les reconversions professionnelles.

## 🚀 Déploiement Railway

### 1. Prérequis
- Compte GitHub
- Compte Railway (gratuit)

### 2. Déploiement automatique
1. Push ce code sur GitHub
2. Connecter Railway à votre repo
3. Railway détecte automatiquement Python + requirements.txt
4. Déploiement en 2 minutes !

### 3. Variables d'environnement
```
PORT=8003  # Automatique sur Railway
ENVIRONMENT=production
```

## 📡 Endpoints

- `GET /` - Statut API
- `POST /api/v1/chat` - Chat avec Iris
- `GET /health` - Health check
- `GET /docs` - Documentation automatique

## 🧪 Test local
```bash
python main.py
# Ouvre http://localhost:8003/docs
```

## 🔗 Intégration Phoenix Letters
Une fois déployé, mettre à jour `IRIS_API_URL` dans Streamlit Cloud :
```
IRIS_API_URL=https://your-iris-api.up.railway.app/api/v1/chat
```