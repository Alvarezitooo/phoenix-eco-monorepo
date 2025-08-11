## Semaine 1 – Plan d’exécution prioritaire (Happy Path, Sécurité Aube, Event Bridge)

Objectif: sécuriser le parcours revenu (B2C), durcir Aube en prod, et simplifier la data pipeline.

---

### 1) Finaliser le « Happy Path » (Stripe webhooks + propagation premium via Supabase Event Bridge)

Actions
- Implémenter la logique des webhooks Stripe dans `apps/phoenix-website/pages/api/stripe/webhook.ts` (événements: `checkout.session.completed`, `customer.subscription.{created,updated,deleted}`, `invoice.payment_{succeeded,failed}`).
- Sur chaque événement pertinent, publier `SUBSCRIPTION_ACTIVATED`/état associé via `PhoenixEventBridge` (Supabase) avec `user_id`, `plan_id`, `status`, `origin = website`.
- Normaliser les `price_id` et plans entre Website, Letters, Rise. Documenter le mapping prix → plan.
- Mettre à jour la page Pricing Website pour cohérence messaging/prix (doc seulement, pas de code ici).

Données événement (proposition)
- `event_type`: `SUBSCRIPTION_ACTIVATED` | `SUBSCRIPTION_UPDATED` | `SUBSCRIPTION_CANCELLED`
- `user_id`: string (uuid/identifiant Phoenix)
- `payload`: `{ session_id?, subscription_id?, plan_id, status, customer_id, currency, amount, source: "stripe" }`
- `app_source`: `website`
- `metadata`: `{ version: "v1", origin: "webhook" }`

Tests d’acceptation
- Webhook reçoit `checkout.session.completed` et publie un événement avec `status=pending` puis `active` après subscription created/updated.
- Letters/Rise (en lecture) adaptent l’UX selon état premium (flag via Event Store).
- Tests Stripe d’intégration passent: `infrastructure/testing/test_stripe_complete_integration.py`.

Rollback
- Désactiver handlers en renvoyant 200 sans action; journaliser côté Website; laisser l’achat sans upgrade automatique (support manuel).

---

### 2) Sécuriser Phoenix Aube (hardening immédiat)

Actions
- CORS: restreindre `allow_origins` à domaines prod (website/app) et `allow_methods` aux nécessaires.
- TrustedHost: lister explicitement domaines front (sans wildcard `*`).
- Auth: exiger `HTTPBearer` sur endpoints sensibles (transparency/orchestration/metrics admin) selon la politique définie.
- Rate limiting: activer au niveau reverse proxy (Nginx/Cloudflare) pour les routes publiques Aube (ex: 60 req/min/IP).
- Secrets: vérifier variables d’environnement minimales (clé JWT, Sentry, Supabase, etc.).

Tests d’acceptation
- Appels cross-origin refusés hors whitelist.
- Accès sans token refusé là où requis (401/403).
- Latence p95 < 1.5s inchangée; absence d’erreurs 5xx liées au CORS/hosts.

Rollback
- Revenir aux valeurs CORS/hosts précédentes; désactiver règle rate limiting en proxy.

Référence
- Voir `docs/CHECKLIST_HARDENING_AUBE.md`.

---

### 3) Simplifier l’architecture (Supabase Event Bridge = standard)

Actions
- Geler la voie RabbitMQ/Postgres: désactiver les consumers (service non lancé en prod) et marquer la voie « paused » dans la doc et scripts.
- Documenter le schéma événementiel unique Supabase (types, champs, contraintes, idempotence) et pointer les intégrations (Aube, Letters, Rise, Iris, Website).
- Ajouter un « schema registry » minimal (YAML) listant `PhoenixEventType` et structure de `payload`.
- Valider insertion/lecture d’événements depuis chaque app critique.

Tests d’acceptation
- Insertion Supabase OK depuis Website webhook, et lecture depuis Letters/Rise/Aube.
- Aucun composant en prod ne dépend de RabbitMQ.

Rollback
- Réactiver consumer RabbitMQ si nécessaire; privilégier le pont Supabase comme source de vérité.

Référence
- Voir `docs/STANDARDISATION_EVENT_BRIDGE_SUPABASE.md`.

---

### Calendrier indicatif (Semaine 1)

- J1: Webhooks Stripe (handlers + publication événements) – tests locaux.
- J2: Hardening Aube (CORS/hosts/auth/rate limit) – tests de non-régression.
- J3: Standardisation Event Bridge – doc + validations insertion/lecture.
- J4: Tests d’intégration Stripe + E2E funnel basiques.
- J5: Revue, runbooks, préparation déploiement + monitoring minimal.

Definition of Done
- Webhooks opérationnels avec publication d’événements Supabase et tests OK.
- Aube durcie, endpoints critiques sécurisés, CORS/hosts verrouillés, rate limit actif.
- Documentation Event Bridge à jour, voie RabbitMQ officiellement « paused », validations lecture/écriture.


