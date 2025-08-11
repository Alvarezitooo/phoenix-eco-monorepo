## Standardisation – Supabase Event Bridge (mise en pause RabbitMQ)

Objectif: unifier tous les flux d’événements sur Supabase Event Bridge pour simplifier opérations et analytics.

---

### Décisions
- Supabase Event Bridge devient la source de vérité pour les événements applicatifs (user, abonnement, usage).
- La voie RabbitMQ/Postgres est « paused » (non supprimée) jusqu’à nouvel ordre.

---

### Actions
- Ne pas déployer/activer les services consommateurs RabbitMQ en prod.
- Documenter le schéma d’événements Supabase (types/champs/contraintes/idempotence) et pointer les intégrations (Website, Aube, Letters, Rise, Iris, Agents IA si lecture nécessaire).
- Introduire un « schema registry » minimal (YAML) pour `PhoenixEventType` et structure de `payload` (emplacement: `docs/event_schema_registry.yaml`).
- Vérifier l’insertion (Website webhooks) et lecture (Letters/Rise/Aube) fin-à-fin.

---

### Schéma événementiel (proposition)
- `event_id`: uuid (généré par Supabase)
- `stream_id`: `user_id` ou identifiant de flux
- `event_type`: enum `PhoenixEventType`
- `payload`: JSONB (schema par type dans registry)
- `app_source`: `website|letters|rise|aube|iris|agents`
- `timestamp`: ISO datetime
- `metadata`: JSONB `{ version, origin, published_at }`

---

### Tests d’acceptation
- Publication d’un `SUBSCRIPTION_ACTIVATED` via Website → lecture confirmée par Letters et Rise.
- Publication d’un event Aube (ex: `transparence_demandée`) → trace visible dans Supabase.

---

### Rollback
- Réactiver la consommation RabbitMQ si besoin (scripts + services), tout en conservant Supabase comme cible prioritaire.


