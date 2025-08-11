## Journal d’exécution – Passage audit → implémentation

Date: 2025-08-11

---

### 1) Webhooks Stripe → Supabase Event Bridge (Happy Path)

Fichier modifié
- `apps/phoenix-website/pages/api/stripe/webhook.ts`

Changements
- Ajout publication d’événements vers Supabase (`SUBSCRIPTION_ACTIVATED|UPDATED|CANCELLED`).
- Gestion anti-replay et rate limiting conservées.
- Extraction `user_id` depuis `metadata.phoenix_user_id` ou `client_reference_id`.
- Payload enrichi (session/subscription/invoice/customer/amount/status/source/app_source/metadata).

Variables d’environnement requises
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`

---

### 2) Hardening Phoenix Aube (CORS/hosts/auth)

Fichier modifié
- `apps/phoenix-aube/phoenix_aube/api/main.py`

Changements
- `CORS`: origines/headers/methods restreints via env `AUBE_ALLOWED_ORIGINS`.
- `TrustedHost`: whitelist via env `AUBE_ALLOWED_HOSTS`.
- Auth exigée (`get_current_user`) sur endpoints sensibles: `/api/v1/metrics`, `/api/v1/transparency/explain-recommendation`, `/api/v1/orchestration/complete-journey`.

Variables d’environnement suggérées
- `AUBE_ALLOWED_ORIGINS="https://phoenix-ecosystem.com,https://*.phoenix-ecosystem.com,http://localhost:8501"`
- `AUBE_ALLOWED_HOSTS="phoenix-ecosystem.com,api.phoenix-ecosystem.com,localhost"`

---

### 3) Standardisation Event Bridge (pause RabbitMQ)

Fichier modifié
- `infrastructure/data-pipeline/phoenix_event_store/main.py`

Changements
- Ajout d’un garde d’environnement `PAUSE_RABBITMQ=true` pour stopper la consommation RabbitMQ et indiquer Supabase comme standard.

---

### 4) Documentation d’exécution créée

Nouveaux fichiers
- `docs/EXECUTION_PLAN_SEMAINE_1.md`
- `docs/CHECKLIST_HARDENING_AUBE.md`
- `docs/PLAYBOOK_STRIPE_WEBHOOKS_EVENT_BRIDGE.md`
- `docs/STANDARDISATION_EVENT_BRIDGE_SUPABASE.md`
- `docs/PLAN_S2_S3_AUTH_OBSERVABILITE.md`

---

### Tests/Lint
- Lint OK sur les fichiers modifiés.
- Prochaines étapes: tests d’intégration Stripe, validation Supabase en environnement avec variables configurées, test CORS/hosts.

---

### 5) Nettoyage site vitrine et déplacement Dojo/Kaizen (Phoenix Rise)

### 6) Paramétrage domaine via variable d’environnement

Changements
- `apps/phoenix-website/app/layout.tsx`: `metadataBase` et `openGraph.url` pilotés par `NEXT_PUBLIC_SITE_URL` (fallback Netlify).
- `apps/phoenix-website/app/manifest.ts`: support de `NEXT_PUBLIC_SITE_URL` pour cohérence (start_url reste '/').

Action requise
- Définir `NEXT_PUBLIC_SITE_URL` dans l’hébergeur (Vercel/Netlify): ex. `https://phoenix-ecosystem.com`.

Changements
- `apps/phoenix-website/app/page.tsx`: remplacement de l’affichage DojoMental par sections marketing (`HeroSection`, `EcosystemSection`, `CTASection`).
- Les composants Dojo/Kaizen/Zazen restent dans le repo mais seront utilisés par Phoenix Rise; la home du site vitrine est désormais purement marketing.



