## Playbook – Webhooks Stripe → Supabase Event Bridge

Objectif: activer le « Happy Path » en promouvant automatiquement l’utilisateur en premium via événements Supabase.

---

### Endpoints concernés
- Website: `apps/phoenix-website/pages/api/stripe/webhook.ts` (handlers existants, TODO à compléter)
- Event Bridge: `infrastructure/data-pipeline/phoenix_event_bridge.py` (types `PhoenixEventType`, `PhoenixEventData`)

---

### Événements Stripe à gérer
- `checkout.session.completed`: session OK, l’utilisateur revient avec `session_id`.
- `customer.subscription.created|updated|deleted`: source de vérité état abonnement.
- `invoice.payment_succeeded|failed`: statut paiement récurrent.

---

### Mapping → Phoenix Event Bridge (Supabase)

Type principal
- `SUBSCRIPTION_ACTIVATED` (et variations `UPDATED`, `CANCELLED`)

Champs (proposition)
- `user_id`: identifiant Phoenix (dérivé de metadata Stripe: `phoenix_user_id` si présent, sinon mapping par email sécurisé)
- `plan_id`: `premium` | `premium_plus` (mapping à documenter)
- `status`: `active` | `trialing` | `past_due` | `canceled` | `incomplete` | `incomplete_expired`
- `payload`: `{ session_id?, subscription_id?, customer_id, currency, amount? }`
- `app_source`: `website`
- `metadata`: `{ origin: 'webhook', bridge_version: 'v1' }`

Idempotence
- Utiliser `subscription_id` comme clé naturelle; ignorer si événement déjà publié (contrôle côté Supabase/bridge selon besoins).

---

### Sécurité
- Vérifier la signature webhook Stripe (`STRIPE_WEBHOOK_SECRET`).
- Valider types d’événements autorisés; rejeter le reste (400).
- Log structuré (sans PII) pour audit.

---

### Tests
- Tests unitaires handler (mocks Stripe events) – s’assurer publication Event Bridge.
- Tests d’intégration: `infrastructure/testing/test_stripe_complete_integration.py`.
- E2E manuel: checkout test → webhook → événement Supabase visible → app consommatrice ajuste l’UX premium.

---

### Rollback
- Renvoyer 200 aux webhooks sans publication d’événements (graceful noop), tout en loggant et en assurant support manuel.


