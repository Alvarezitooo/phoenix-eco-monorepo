
#  गाइड déploiement de l'écosystème Phoenix

## 1. Introduction

Ce guide centralise toutes les instructions pour configurer et déployer les différentes applications et services de l'écosystème Phoenix. Il est conçu pour être la source de vérité unique pour la gestion des secrets et des variables d'environnement.

**Principe fondamental :** Le code est le même partout. Seules les variables d'environnement changent en fonction de l'environnement (développement, production) et de la plateforme (Streamlit Cloud, Vercel, Railway).

## 2. Liste Maîtresse des Secrets

Voici la liste complète des variables d'environnement nécessaires au fonctionnement de l'écosystème. Vous devrez les configurer sur chaque plateforme de déploiement.

```env
# Supabase (Base de données et Auth)
SUPABASE_URL="votre_url_supabase"
SUPABASE_KEY="votre_clé_api_supabase_anon"

# JWT (Authentification)
# Doit être une chaîne de caractères longue et sécurisée
JWT_SECRET_KEY="votre_secret_jwt_de_plus_de_32_caracteres"

# Stripe (Paiement)
STRIPE_SECRET_KEY="sk_live_votre_clé_secrète_stripe"
STRIPE_WEBHOOK_SECRET="whsec_votre_secret_de_webhook_stripe"
STRIPE_PUBLISHABLE_KEY="pk_live_votre_clé_publique_stripe"
STRIPE_PRICE_ID_PREMIUM="price_votre_id_de_prix_premium"

# IA (Google Gemini)
GEMINI_API_KEY="votre_clé_api_google_gemini"

# France Travail (Optionnel pour Phoenix Aube)
FRANCETRAVAIL_CLIENT_ID="votre_client_id_france_travail"
FRANCETRAVAIL_CLIENT_SECRET="votre_client_secret_france_travail"

# Mode de l'application
# Mettre à "true" pour le développement local si nécessaire
DEV_MODE="false"
```

## 3. Instructions par Plateforme

### A. Obtenir les Clés des Services Tiers

- **Supabase (`SUPABASE_URL`, `SUPABASE_KEY`)**
  1. Allez sur votre projet Supabase.
  2. Cliquez sur l'icône "Settings" (roue crantée) dans le menu de gauche.
  3. Sélectionnez "API".
  4. Vous y trouverez votre **URL** et votre clé API "Project API Keys" de type `anon` `public`. C'est cette clé qu'il faut utiliser pour `SUPABASE_KEY`.

- **Stripe (`STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`, etc.)**
  1. Allez sur votre dashboard Stripe.
  2. Assurez-vous de ne pas être en mode "Test".
  3. Allez dans la section "Developers" > "API keys".
  4. Vous y trouverez votre **Clé publique** (`pk_live_...`) et vous pourrez révéler votre **Clé secrète** (`sk_live_...`).
  5. Pour le `STRIPE_WEBHOOK_SECRET`, vous devez créer un "endpoint" de webhook dans la section "Developers" > "Webhooks". Stripe vous fournira le secret (`whsec_...`) à ce moment-là.
  6. L'ID de votre prix (`price_...`) se trouve dans la section "Products".

### B. Configurer les Plateformes de Déploiement

#### Streamlit Cloud (Phoenix Letters, CV, Rise, Aube)

Pour **chaque** application Streamlit que vous déployez :

1.  Allez sur votre dashboard [Streamlit Cloud](https://share.streamlit.io/).
2.  Cliquez sur les trois points `...` à côté de votre application et choisissez "Settings".
3.  Allez dans la section "Secrets".
4.  Copiez-collez **l'intégralité** du contenu de votre fichier de secrets (la "Liste Maîtresse" ci-dessus) dans le champ de texte.
5.  Cliquez sur "Save". Streamlit injectera automatiquement ces variables dans votre application au démarrage.

#### Vercel (Pour le site web Phoenix)

1.  Allez sur votre dashboard Vercel et sélectionnez votre projet.
2.  Allez dans l'onglet "Settings" > "Environment Variables".
3.  Pour chaque variable de la "Liste Maîtresse", cliquez sur "Add New".
4.  Entrez le nom de la variable (ex: `SUPABASE_URL`) et sa valeur.
5.  Assurez-vous de les ajouter pour les environnements "Production", "Preview", et "Development".
6.  Sauvegardez chaque variable. Vercel redéploiera automatiquement votre site avec les nouvelles variables.

#### Railway (Pour les API FastAPI)

1.  Allez sur votre dashboard Railway et sélectionnez votre service FastAPI.
2.  Allez dans l'onglet "Variables".
3.  Cliquez sur "New Variable".
4.  Vous pouvez soit ajouter les variables une par une, soit cliquer sur "Bulk Add" pour copier-coller plusieurs lignes au format `KEY=VALUE`.
5.  Ajoutez toutes les variables de la "Liste Maîtresse" nécessaires à votre API.
6.  Railway redéploiera automatiquement votre service avec les nouvelles variables.

## 4. Développement Local

Pour le développement sur votre machine locale :

1.  Créez un fichier nommé `.env` à la racine de ce projet (au même niveau que `README.md`).
2.  Copiez-collez le contenu de la "Liste Maîtresse" dans ce fichier `.env`.
3.  Remplacez les valeurs par vos clés de développement (vous pouvez utiliser les clés de "Test" de Stripe par exemple).

Le fichier `packages/phoenix-shared-config/settings.py` est configuré pour lire automatiquement ce fichier `.env` s'il existe. **N'ajoutez jamais le fichier `.env` à Git.** Il est déjà listé dans le `.gitignore` pour votre sécurité.
