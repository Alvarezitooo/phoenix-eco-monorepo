# 🚀 Phoenix Shared Auth - Module d'Authentification Unifié

Module d'authentification centralisé pour l'écosystème Phoenix (Letters, CV, Rise, Site).

## 🎯 **Fonctionnalités**

✅ **Authentification unifiée** - Un seul système pour toutes les apps Phoenix  
✅ **Support multi-applications** - Permissions granulaires par app  
✅ **Streamlit intégré** - Middleware prêt à l'emploi  
✅ **Supabase natif** - Connexion optimisée avec RLS  
✅ **Session management** - Gestion robuste des sessions  
✅ **Mode invité** - Accès limité sans inscription  

## 🛠️ **Installation**

```bash
# Depuis le dossier de ton app Phoenix
pip install -e ../phoenix_shared_auth
```

## 🚀 **Usage Rapide**

### **1. Configuration Environnement**
```bash
# Variables requises dans .env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
JWT_SECRET_KEY=your-secret-key
SUPABASE_SCHEMA=api
```

### **2. Intégration dans App Streamlit**
```python
import streamlit as st
from phoenix_shared_auth import (
    get_phoenix_settings,
    get_phoenix_db_connection, 
    PhoenixAuthService,
    PhoenixStreamlitAuth,
    PhoenixApp
)
from phoenix_shared_auth.services.jwt_manager import JWTManager

# Configuration
settings = get_phoenix_settings(".env")
db_connection = get_phoenix_db_connection()
jwt_manager = JWTManager(settings.jwt.secret_key)

# Services
auth_service = PhoenixAuthService(db_connection, jwt_manager)
streamlit_auth = PhoenixStreamlitAuth(auth_service, PhoenixApp.CV)  # ou LETTERS, RISE

# Page protégée
@streamlit_auth.require_auth
def main_app():
    user = streamlit_auth.get_current_user()
    st.write(f"Bienvenue {user.display_name} !")
    
    if st.button("Déconnexion"):
        streamlit_auth.logout_user()

# Point d'entrée
if __name__ == "__main__":
    if streamlit_auth.is_authenticated():
        main_app()
    else:
        streamlit_auth.render_auth_page()
```

## 📋 **Structure du Module**

```
phoenix_shared_auth/
├── entities/
│   └── phoenix_user.py          # Entités utilisateur unifiées
├── services/
│   ├── phoenix_auth_service.py  # Service d'authentification principal
│   └── jwt_manager.py          # Gestion JWT (à créer)
├── database/
│   └── phoenix_db_connection.py # Connexion Supabase centralisée
├── middleware/
│   └── phoenix_streamlit_auth.py # Middleware Streamlit
├── config/
│   └── phoenix_settings.py     # Configuration unifiée
└── utils/                      # Utilitaires partagés (à créer)
```

## 🗄️ **Schéma Base de Données Supabase**

```sql
-- Schéma API Phoenix
CREATE SCHEMA IF NOT EXISTS api;

-- Table utilisateurs principale
CREATE TABLE api.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    username VARCHAR(100),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    status VARCHAR(20) DEFAULT 'active',
    email_verified BOOLEAN DEFAULT false,
    newsletter_opt_in BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_login TIMESTAMPTZ
);

-- Table abonnements utilisateur
CREATE TABLE api.user_subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES api.users(id) ON DELETE CASCADE,
    current_tier VARCHAR(20) DEFAULT 'free',
    enabled_apps TEXT[] DEFAULT ARRAY['letters', 'cv'],
    subscription_start TIMESTAMPTZ,
    subscription_end TIMESTAMPTZ,
    auto_renewal BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table statistiques d'usage par app
CREATE TABLE api.app_usage_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES api.users(id) ON DELETE CASCADE,
    app VARCHAR(20) NOT NULL,
    letters_generated INTEGER DEFAULT 0,
    cvs_created INTEGER DEFAULT 0,
    coaching_sessions INTEGER DEFAULT 0,
    premium_features_used INTEGER DEFAULT 0,
    last_activity TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- RLS Policies
ALTER TABLE api.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE api.user_subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE api.app_usage_stats ENABLE ROW LEVEL SECURITY;

-- Policies pour les utilisateurs
CREATE POLICY "Users can view their own data" ON api.users FOR SELECT USING (auth.uid()::text = id::text);
CREATE POLICY "Users can insert their own data" ON api.users FOR INSERT WITH CHECK (true);
```

## 🎯 **Exemples d'Intégration**

### **Phoenix Letters**
```python
# Dans app.py de Phoenix Letters
from phoenix_shared_auth import PhoenixStreamlitAuth, PhoenixApp

auth = PhoenixStreamlitAuth(auth_service, PhoenixApp.LETTERS)

@auth.require_auth  
def generate_letter_page():
    user = auth.get_current_user()
    # Logique génération lettre...
```

### **Phoenix CV**
```python
# Dans app.py de Phoenix CV  
from phoenix_shared_auth import PhoenixStreamlitAuth, PhoenixApp

auth = PhoenixStreamlitAuth(auth_service, PhoenixApp.CV)

@auth.require_auth
def create_cv_page():
    user = auth.get_current_user()
    # Logique création CV...
```

## 🔒 **Sécurité**

- **RLS Supabase** - Row Level Security activé
- **JWT Tokens** - Access + Refresh tokens
- **Hashing BCrypt** - Mots de passe sécurisés  
- **Session management** - Expiration automatique
- **RGPD Compliant** - Données minimales stockées

## 🚀 **Prochaines Étapes**

1. **Créer JWT Manager** - Gestion des tokens
2. **Ajouter utils** - Helpers communs
3. **Tests unitaires** - Coverage complète
4. **Documentation API** - Référence complète
5. **Migration tools** - Outils de migration DB

## 🤝 **Support**

Pour toute question ou problème, consulter la documentation ou créer une issue.

---

**🔥 PHOENIX ECOSYSTEM - Une authentification, toutes les possibilités ! 🚀**