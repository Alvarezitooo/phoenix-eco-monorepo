## Checklist – Mise à jour CORS/Hosts (Aube & Iris)

Objectif: autoriser le site vitrine et sécuriser les APIs publiques.

### 1) Phoenix Aube (FastAPI)
- AUBE_ALLOWED_ORIGINS
  - Ajouter: https://phoenix-eco-monorepo.vercel.app
  - Ajouter: http://localhost:3000 (dev)
  - Optionnel migration: https://phoenixcreator.netlify.app
  - Domaine final (quand dispo): https://phoenix-ecosystem.com
- AUBE_ALLOWED_HOSTS
  - Ajouter: phoenix-eco-monorepo.vercel.app
  - Ajouter: localhost
  - Domaine final (quand dispo): phoenix-ecosystem.com, www.phoenix-ecosystem.com
  - Sous-domaine API (si utilisé): api.phoenix-ecosystem.com
- Redeploy Aube

### 2) Iris API (FastAPI)
- IRIS_ALLOWED_ORIGINS
  - Ajouter: https://phoenix-eco-monorepo.vercel.app
  - Ajouter: http://localhost:3000 (dev)
- Redeploy Iris

### 3) Supabase (si le site appelle Supabase côté client)
- Auth/CORS: ajouter https://phoenix-eco-monorepo.vercel.app

### 4) Vérification rapide
- Lancer le script:
  ```bash
  python infrastructure/testing/check_cors_hosts.py \
    --site https://phoenix-eco-monorepo.vercel.app \
    --aube https://<AUBE_API_BASE> \
    --iris https://<IRIS_API_BASE>
  ```
- Attendu: CORS OK, health 200, hosts OK

Notes
- Ne pas autoriser des wildcards (`*`) en production.
- Les URLs Preview Vercel changent; tester en local ou ajouter l’origine spécifiquement si besoin ponctuel.
