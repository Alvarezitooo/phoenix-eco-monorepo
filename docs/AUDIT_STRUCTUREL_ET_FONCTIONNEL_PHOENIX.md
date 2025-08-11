## Audit structurel et fonctionnel – Phoenix Aube Ecosystem

Date: 2025-08-11

---

## Vue d’ensemble de l’architecture

- **Website (Next.js)**: `apps/phoenix-website` – SEO, pages marketing, PWA, headers sécurité (CSP, X-Frame-Options, etc.).
- **Phoenix Aube (Streamlit + FastAPI)**: `apps/phoenix-aube` – Exploration métier + validation IA future-proof, Transparency Engine (XAI). Points d’entrée via `run_app.py` (streamlit/api/both).
- **Phoenix Letters (Streamlit)**: `apps/phoenix-letters` – Génération lettre, ATS, Mirror Match, Coach, Stripe, widget Iris.
- **Phoenix Rise (Streamlit)**: `apps/phoenix-rise` – Coach IA (version de test déploiement OK), script `start.sh` attend les Agents IA.
- **Phoenix Iris API (FastAPI)**: `apps/phoenix-iris-api` – Assistant conversationnel (chat, health, topics) avec CORS stricts.
- **Agents IA conteneurisés (FastAPI)**: `agent_ia/` – Smart Router (8000), Security Guardian (8001), Data Flywheel (8002), K8s-ready.
- **Data pipeline / Event Store**:
  - Supabase Event Bridge: `infrastructure/data-pipeline/phoenix_event_bridge.py` (typé, multi-apps)
  - RabbitMQ → Postgres Event Store: `infrastructure/data-pipeline/phoenix_event_store/main.py`

---

## Points d’entrée clés

- **Website**: Next 14, scripts `dev/build/start`. Sécurité renforcée dans `next.config.js` (headers, CSP). PWA: `app/manifest.ts`.
- **Aube API/UI**: `apps/phoenix-aube/run_app.py` (streamlit/api/both), API principale `phoenix_aube/api/main.py` (endpoints analyse, data, transparency, orchestration, metrics).
- **Letters UI**: `apps/phoenix-letters/phoenix_letters/main.py` (UI + services). Auth Streamlit, Stripe, widget Iris.
- **Rise UI**: `apps/phoenix-rise/phoenix_rise/main.py` (version minimale). `start.sh` configure la connexion aux Agents IA.
- **Iris API**: `apps/phoenix-iris-api/main.py` (chat, health, docs). Dojo API(s) dédiées dans `dojo_api*.py`.
- **Agents IA**: `agent_ia/smart_router_api.py`, `agent_ia/security_api.py`, `agent_ia/flywheel_api.py` (uvicorn entrypoints intégrés, endpoints health, throttle, circuit-breaker, metrics).
- **Event Store**:
  - Supabase Event Bridge partagé (types `PhoenixEventType`, `PhoenixEventData`).
  - RabbitMQ/Postgres (consumer avec ack/nack, table `events`).

---

## Forces (à capitaliser)

- **Différenciation EU XAI**: Transparency Engine documenté (`apps/phoenix-aube/docs/TRANSPARENCY_ENGINE.md`), endpoints de transparence et d’orchestration.
- **Website solide**: SEO, PWA, headers sécurité, metadata propre – prêt pour acquisition et crédibilité.
- **Agents IA découplés**: Security, Smart Router, Data Flywheel; scripts Docker/K8s et health endpoints.
- **Data pipeline**: Event Bridge structuré, typé, multi-apps; analytics activables.
- **Paiements**: Services Stripe (Letters, Rise), endpoints webhooks en place côté website (TODO notés).
- **Compliance**: Outils RGPD (audit manager, anonymisation), Green AI metrics, sécurité intégrée.
- **Tests**: Suite d’intégration/validation (API/Stripe/charge) orchestrée pour pré-prod.

---

## Gaps et risques observés

- **Aube API**: Providers mock activés par défaut; CORS/TrustedHost ouverts (`*`).
- **Auth unifiée**: Coexistence de JWT spécifiques et `packages/phoenix-shared-auth` + fallbacks locaux → risque d’incohérences.
- **Event Store double voie**: Supabase Event Bridge et RabbitMQ/Postgres en parallèle → complexité ops et dette d’archi.
- **Stripe**: Webhooks Next.js encore TODO; risque de non-propagation état d’abonnement vers apps.
- **Observabilité**: Logs/métriques présents mais non unifiés (manque traces bout-en-bout/OTel).
- **Sécurité API publiques**: Absence de rate limiting systématique; tokens parfois optionnels.
- **Cohérence produit**: Rise en version de test; Aube solide mais quelques mocks; Iris non branché Event Bridge pour learning global.

---

## Recommandations sans changement de code

### 1) Verrouiller le « happy path » B2C (CPF)

- **Funnel simple**: Website → Aube (exploration + score IA) → Letters (lettre + paiement Stripe) → Iris (support). 
- **Aube = entry point**: CTA unique depuis Website (UTM pour attribution). 
- **Confiance**: Générer un « Trust by Design Report » exportable (PDF/JSON) via endpoints transparence existants.

### 2) Sécurité/Compliance production

- **Aube API**: Restreindre `allow_origins`/`allowed_hosts` aux domaines officiels; auth obligatoire où pertinent; ajouter rate limiting au niveau reverse proxy.
- **Iris API**: Conserver CORS stricts, ajouter quotas anti-abus; logs anonymisés OK.
- **Website CSP**: Remplacer `style-src 'unsafe-inline'` par nonces/hashes.
- **Secrets**: Standardiser variables d’environnement et docs « minimum viable secrets » par app.

### 3) Auth unifiée Phoenix

- **Standardiser** `packages/phoenix-shared-auth` (JWT, middleware Streamlit) dans Letters/Rise; retirer progressivement les fallbacks locaux.
- **Sécurité tokens**: Cookies HttpOnly/SameSite; refresh flow commun; claims standard (user_id, tier, consent flags).
- **Gates tier**: FREE/PREMIUM/PREMIUM+ alignés entre apps (limites déjà amorcées côté Iris/Letters).

### 4) Event Store: choisir une voie prioritaire

- **Court terme**: Standardiser Supabase Event Bridge comme source unique pour réduire la complexité.
- **Moyen terme**: Si RabbitMQ/Postgres requis, documenter précisément (routing keys, DLQ, idempotence, replays) et fournir un « query model » consolidé. Éviter double écriture.
- **Conventions**: Maintenir `PhoenixEventType` cross-apps + « schema registry » minimal (YAML).

### 5) Observabilité bout-en-bout

- **Traces**: OpenTelemetry du Website → Aube/Letters/Rise → Agents IA → Event Bridge (trace/span IDs). 
- **Dashboard santé**: Page interne « System Health » consolidée (Agents 8000/8001/8002, Aube, Iris, Event Store insert/read). 
- **SLO**: p95 < 1.5s Aube/Iris; erreurs < 1%; 99.5% disponibilité mensuelle endpoints publics.

### 6) Stripe production-grade

- **Webhooks Website**: Finaliser handlers et propager état premium via Event Bridge (`SUBSCRIPTION_ACTIVATED`).
- **Cohérence pricing**: Unifier `price_id`/montants entre apps/site.
- **Tests**: Intégrer tests Stripe (déjà présents) dans pipeline CI, gating avant déploiement.

### 7) CI/CD et déploiement

- **Pipeline**: lint + tests unitaires + tests intégration (API/Stripe), scans deps (pip-audit/Safety), scans images.
- **Previews**: Website (Netlify/Vercel) + URL tunnel Cloudflare auto pour Streamlit; liens dans PRs.
- **K8s**: Documenter requests/limits et HPA; secrets via sealed-secrets; health checks déjà en place.

### 8) DX monorepo et gouvernance

- **Task runners**: Makefile/Justfile par app (run/test/lint/build/seed).
- **Runbooks**: Stripe incident, panne Event Store, saturation Agents (checklists support).
- **Packages partagés**: Clarifier frontières (`phoenix-shared-auth`, `phoenix-shared-ai`, `phoenix_shared_ui`, `phoenix_event_bridge`) et interfaces stables.

### 9) Growth/ROI (mission Phoenix Aube)

- **USP**: Mettre en avant « score résistance automatisation » + « plan montée compétences IA » sur la landing pour lever l’anxiété.
- **Trust by Design**: Rapport d’explicabilité partageable (Niveau 1/2/3) – différenciation européenne XAI/AI Act.
- **SEO**: schema.org (JobPosting/HowTo/FAQ), cas clients, intégrations France Travail, preuves chiffrées (NPS, taux d’emploi).
- **Funnel tracking**: Events Supabase → dashboard conversion (site→Aube→Letters→Stripe) avec cohortes 30/60/90j.

---

## Check rapide par app (vue utilisateur)

- **Phoenix Aube**: API claire (analyse, transparence, orchestration), UI Streamlit; durcir sécurité prod, connecter providers non-mock.
- **Phoenix Letters**: Parcours complet (génération, ATS, Mirror Match, Coach), auth Streamlit, Stripe; prêt pour monétisation B2C.
- **Phoenix Rise**: Version test déploiement OK; à compléter pour parcours coaching post-achat.
- **Phoenix Iris API**: Robuste, CORS strict, contrôles longueur, logs anonymisés; raccorder Event Bridge pour learning.
- **Agents IA**: Orchestration/sécurité/apprentissage clairs; endpoints health; K8s-ready.
- **Website**: SEO/sécurité solides; finaliser webhooks Stripe + pages pricing alignées.

---

## Priorités court terme (impact/effort)

### Haute priorité (semaine 1)

- Hardening Aube (CORS/hosts, auth, rate limiting). 
- Finaliser webhooks Stripe + propagation premium via Event Bridge.
- Standardiser Event Bridge Supabase comme voie unique court terme.
- Activer CI: lint + tests API/Stripe en gating.

### Priorité moyenne (semaines 2–3)

- Auth unifiée `phoenix-shared-auth` (Letters/Rise); cookies HttpOnly/refresh flow.
- Observabilité OTel minimal + page « System Health ».
- CSP nonces/hashes côté Website.

### Priorité suivante (mois 2)

- Query model analytique multi-apps et dashboard conversion.
- Rapport « Trust by Design » exportable/public.
- HPA et budgets CPU/RAM Kubernetes documentés/testés.

---

## SLO (proposition)

- **Aube/Iris API**: p95 < 1.5s; taux d’erreur < 1%; uptime mensuel ≥ 99.5%.
- **Agents IA**: health OK ≥ 99%; latence inter-services p95 < 800 ms.
- **Events**: délais d’ingestion < 2s (Supabase Bridge), réussite > 99.9%.

---

## Livrables/CTA

- **Checklists**: Security hardening par app; secrets; readiness prod.
- **Playbook B2C CPF**: Website → Aube → Letters → Stripe → Rise.
- **Plan Event Store**: Standardisation Supabase + conventions d’événements + registry minimal.
- **CI template**: Lint, tests API/Stripe, scans sécurité (deps/images), gating avant déploiement.
- **Runbooks**: Stripe incident, Event Store, Agents IA (circuit breaker/throttle).

---

## Fichiers/repères utiles

- Website: `apps/phoenix-website/next.config.js`, `app/layout.tsx`, `pages/api/stripe/*`.
- Aube: `apps/phoenix-aube/run_app.py`, `phoenix_aube/api/main.py`, `docs/TRANSPARENCY_ENGINE.md`.
- Letters: `apps/phoenix-letters/phoenix_letters/main.py`, `infrastructure/payment/stripe_service.py`, `compliance/rgpd_audit_manager.py`.
- Rise: `apps/phoenix-rise/phoenix_rise/main.py`, `start.sh`.
- Iris: `apps/phoenix-iris-api/main.py`, `dojo_api*.py`.
- Agents IA: `agent_ia/smart_router_api.py`, `security_api.py`, `flywheel_api.py`, `k8s/*`.
- Event pipeline: `infrastructure/data-pipeline/phoenix_event_bridge.py`, `phoenix_event_store/main.py`.

---

## Mission produit et positionnement

- **Mission**: Transformer la peur de l’IA en superpouvoir pour les 35–50 ans en reconversion.
- **Différenciateurs**: IA explicable (XAI) + transparence radicale, human-in-the-loop, conformité AI Act native, partenariat scientifique 3IA.
- **Go-to-market**: SEO, LinkedIn Ads, partenariats coachs, webinars, contenus (blog, livre blanc, témoignages), crédibilité (3IA, cas clients, média).
- **KPIs**: CAC < 500€, LTV 1800€, NPS > 50, MRR 50k€ fin 2025.


