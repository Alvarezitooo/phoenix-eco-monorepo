# 🦋 Phoenix Rise - Coach IA Reconversion

Application Streamlit de coaching IA pour accompagner les reconversions professionnelles.

## 🚀 Démarrage Rapide

### 1. Installation
```bash
git clone [votre-repo]
cd Phoenix-rise
pip install -r requirements.txt
```

### 2. Configuration
```bash
# Copier le template d'environnement
cp .env.example .env

# Éditer .env avec vos vraies clés API
nano .env
```

### 3. Lancement
```bash
streamlit run rise_app.py
```

## 🏗️ Stack Technique

- **Frontend:** Streamlit + CSS personnalisé
- **Backend:** Supabase (PostgreSQL + Auth)  
- **IA:** Google Gemini 1.5 Flash
- **Sécurité:** Validation inputs, protection XSS, logs anonymisés
- **Déploiement:** Streamlit Cloud

## 📁 Architecture

```
Phoenix-rise/
├── models/           # Structures de données Pydantic
├── services/         # Logique métier (auth, db, ai)
├── ui/              # Composants interface utilisateur  
├── utils/           # Utilitaires et sécurité
├── rise_app.py      # 🎯 Point d'entrée principal
└── requirements.txt # Dépendances Python
```

## 🛡️ Sécurité & RGPD

- ✅ Validation et sanitisation inputs utilisateur
- ✅ Protection XSS intégrée  
- ✅ Logs anonymisés (pas d'exposition PII)
- ✅ UUID validation pour user_id
- ✅ Limitation longueur textes (protection DoS)

## 🔧 Configuration Requise

1. **Supabase Project** avec tables :
   - `mood_entries` (user_id, mood_score, confidence_level, notes, created_at)

2. **Google AI Studio** :
   - Clé API Gemini 1.5 Flash

3. **Variables d'environnement** (voir `.env.example`)
