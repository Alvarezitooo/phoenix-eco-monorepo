## Phoenix Monorepo – Exemple de variables d’environnement

Copiez ces clés dans vos environnements (Vercel/hosts API) et vos `.env.local` (local). Ne jamais committer de secrets.

### Website (Next.js)
- NEXT_PUBLIC_SITE_URL=https://phoenix-eco-monorepo.vercel.app
- STRIPE_SECRET_KEY=sk_live_… (Prod) / sk_test_… (Preview/Dev)
- STRIPE_WEBHOOK_SECRET=whsec_live_… (Prod) / whsec_test_… (Preview)
- SUPABASE_URL=https://<project>.supabase.co
- SUPABASE_SERVICE_ROLE_KEY=<service-role>

### Phoenix Aube (FastAPI)
- AUBE_ALLOWED_ORIGINS=https://phoenix-eco-monorepo.vercel.app,http://localhost:8501
- AUBE_ALLOWED_HOSTS=phoenix-eco-monorepo.vercel.app,localhost

### Iris API (FastAPI)
- IRIS_ALLOWED_ORIGINS=https://phoenix-eco-monorepo.vercel.app,http://localhost:8501

### Data Pipeline
- PAUSE_RABBITMQ=true  # Supabase Event Bridge prioritaire

### Monitoring (optionnel)
- SENTRY_DSN=…

Notes
- STRIPE_* et SUPABASE_SERVICE_ROLE_KEY ne doivent jamais être exposées côté client (pas de `NEXT_PUBLIC_`).
- Redéployez après toute modification d’environnement.
