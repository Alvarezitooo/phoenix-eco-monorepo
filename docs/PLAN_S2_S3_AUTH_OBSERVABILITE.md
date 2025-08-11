## Semaines 2–3 – Auth unifiée et Observabilité (System Health)

Objectif: migration vers `phoenix-shared-auth` et mise en place d’une première page « System Health ».

---

### 1) Authentification unifiée (Letters + Rise)

Actions
- Intégrer `packages/phoenix-shared-auth` (JWTManager, PhoenixAuthService, PhoenixStreamlitAuth) dans Letters et Rise.
- Cookies: HttpOnly + SameSite=Lax/Strict; refresh flow commun; claims standard (`sub`, `tier`, `consent`).
- Remplacer les fallbacks locaux; centraliser la configuration (secrets, durations) via env.
- Harmoniser le gating par `user_tier` (FREE/PREMIUM/PREMIUM+) côté UI et services.

Tests d’acceptation
- Login/logout/refresh tokens fonctionnels, UX inchangée.
- Accès features premium conditionné par le `tier` (alimenté via Event Store).

Rollback
- Revenir temporairement aux implémentations locales (feature flag), en conservant la lib partagée installée.

---

### 2) Observabilité – Page « System Health » v1

Portée
- Agréger l’état des services critiques: Aube API, Iris API, Agents IA (8000/8001/8002), Website (self-check), Event Bridge (insert/read test).

Spécification minimale
- Backend: endpoint `/system/health` qui appelle séquentiellement:
  - `http://smart-router:8000/health`
  - `http://security-guardian:8001/health`
  - `http://data-flywheel:8002/health`
  - `AubeAPI/health` (ou `/docs` si pas de route dédiée)
  - `IrisAPI/health`
  - Test Supabase: insert/lecture no-op (table dédiée `health_checks` ou event marqué `health_check=true`).
- Front: page simple (cards vert/orange/rouge), temps de réponse et dernier succès.

Métriques de base
- Disponibilité (OK/KO), latence, timestamp dernier succès.

Tests d’acceptation
- Page affiche l’état de tous les services; latence < 2s; erreur agrégée claire.

Rollback
- Désactiver la page en cas d’incident; conserver scripts CLI de santé (curl) en secours.


