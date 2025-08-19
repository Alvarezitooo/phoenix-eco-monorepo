# 🔥 Phoenix Letters - Générateur IA de Lettres de Motivation

> Votre copilote bienveillant pour créer des lettres de motivation d'exception

## 🚀 Architecture Refactorisée

Cette version a été complètement refactorisée selon les principes Clean Code et préparée pour le déploiement Docker sur **Render**.

### 📂 Structure Modulaire

```
phoenix-letters/
├── app.py                 # Point d'entrée Streamlit
├── main.py               # Application principale refactorisée  
├── ui_components.py      # Composants UI centralisés
├── services.py           # Services métier
├── auth_manager.py       # Gestion authentification
├── requirements.txt      # Dépendances optimisées
├── Dockerfile           # Container de production
├── docker-compose.yml   # Développement local
├── .env.example        # Template variables d'environnement
└── config/
    └── settings.py     # Configuration centralisée
```

## 🔧 Configuration

### Variables d'Environnement Requises

```bash
# 🤖 AI Configuration
GOOGLE_API_KEY=your_google_gemini_api_key_here

# 🗄️ Supabase Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key_here

# 💳 Stripe Payments
STRIPE_PUBLISHABLE_KEY=pk_test_your_key_here
STRIPE_SECRET_KEY=sk_test_your_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
STRIPE_LETTERS_PRICE_ID=price_your_letters_price_id
STRIPE_CV_PRICE_ID=price_your_cv_price_id
STRIPE_BUNDLE_PRICE_ID=price_your_bundle_price_id

# 🔐 Authentication
AUTH_ENABLED=true
JWT_SECRET_KEY=your_jwt_secret_min_32_chars
JWT_REFRESH_SECRET=your_refresh_secret_min_32_chars
```

### Configuration Initiale

```bash
# 1. Copier le template d'environnement
cp .env.example .env

# 2. Remplir vos vraies valeurs dans .env
nano .env
```

## 🐳 Déploiement Architecture Monorepo

### 🏗️ **Architecture "Boîte à Outils Commune"**

Phoenix Letters utilise l'architecture monorepo avec accès direct aux `packages/` partagés :

```python
# Import direct depuis la "boîte à outils commune"
from packages.phoenix_shared_auth.client import AuthManager
from packages.phoenix_shared_models.user_profile import UserProfile
```

### Développement Local

```bash
# Depuis la RACINE du monorepo
docker build --build-arg APP_NAME=phoenix-letters -t phoenix-letters .
docker run -p 8501:8501 --env-file apps/phoenix-letters/.env phoenix-letters
```

### Production sur Render

1. **Configuration complète dans `render.yaml`**
   - Web Services : phoenix-letters, phoenix-cv, phoenix-website  
   - Background Workers : phoenix-event-bridge, phoenix-user-profile

2. **Déploiement automatique :**
   ```bash
   # Push vers GitHub déclenche automatiquement :
   git push origin main
   # → Render détecte render.yaml
   # → Build de tous les services
   # → Déploiement orchestré
   ```

3. **Architecture scalable :**
   - **Web Services** : Gèrent les utilisateurs (Streamlit, Next.js)
   - **Background Workers** : Traitent les données (Event Bridge, User Profile)  
   - **Packages partagés** : Code commun à tous les services

## 🧩 Fonctionnalités

### Version Gratuite
- ✅ 3 lettres par mois
- ✅ Templates de base
- ✅ Génération IA simple

### Version Premium  
- 💎 Lettres illimitées
- 💎 Mirror Match - Adaptation au recruteur
- 💎 ATS Analyzer - Optimisation filtres
- 💎 Smart Coach - Conseils personnalisés
- 💎 Trajectory Builder - Parcours professionnel

## 🛡️ Sécurité

- 🔒 Données chiffrées RGPD
- 🔒 Authentification sécurisée
- 🔒 Variables d'environnement
- 🔒 Container non-root
- 🔒 Validation des inputs

## 📊 Monitoring & Logs

```bash
# Voir les logs en temps réel
docker-compose logs -f phoenix-letters

# Health check
curl http://localhost:8501/_stcore/health
```

## 🚨 Dépannage

### Erreurs communes

1. **Erreur GOOGLE_API_KEY manquante**
   ```bash
   # Vérifier que la variable est définie
   echo $GOOGLE_API_KEY
   ```

2. **Erreur Supabase connexion**
   ```bash
   # Vérifier les URLs et clés
   curl -H "apikey: $SUPABASE_ANON_KEY" "$SUPABASE_URL/rest/v1/"
   ```

3. **Build Docker échoue**
   ```bash
   # Nettoyer et rebuilder
   docker-compose down
   docker system prune -a
   docker-compose up --build
   ```

## 📈 Métriques

- Performance: ~2s temps de réponse IA
- Sécurité: Audit régulier des dépendances
- Disponibilité: Health checks intégrés

## 🤝 Support

- 📧 Contact: support@phoenix.app  
- 🐛 Issues: [GitHub Issues](https://github.com/your-repo/issues)
- 📚 Documentation: [Docs Phoenix](https://docs.phoenix.app)

---

**Rationale d'Architecte :** Cette refactorisation respecte les principes SOLID, sépare les responsabilités, externalise toutes les configurations et prépare l'application pour un déploiement containerisé scalable sur Render.