## Checklist Hardening – Phoenix Aube (FastAPI)

But: sécuriser immédiatement l’API Aube pour déploiement public sans modifier les fonctionnalités.

---

### Portée
- Service: `apps/phoenix-aube/phoenix_aube/api/main.py`
- Middleware: `CORS`, `TrustedHost`, `HTTPBearer` où pertinent.

---

### 1) CORS restrictif
- Définir `allow_origins` avec les domaines officiels (prod et préprod):
  - `https://phoenix-ecosystem.com`
  - `https://*.phoenix-ecosystem.com`
  - `https://phoenix-letters.streamlit.app` (si nécessaire)
  - `http://localhost:8501` (dev)
- `allow_methods`: `GET,POST,OPTIONS` (réduire si possible)
- `allow_headers`: `Authorization, Content-Type`

Validation
- Requêtes cross-origin hors whitelist → 403/CORS blocked.

---

### 2) TrustedHost strict
- `allowed_hosts`: lister explicitement:
  - `phoenix-ecosystem.com`
  - `api.phoenix-ecosystem.com`
  - `localhost`

Validation
- Requêtes Host non listé → 400/host interdit.

---

### 3) Authentification endpoints sensibles
- Exiger `HTTPBearer` (ou dépendance auth partagée) pour:
  - `/api/v1/transparency/*`
  - `/api/v1/orchestration/*`
  - `/api/v1/metrics` (admin)
- S’assurer que les endpoints purement publics restent accessibles.

Validation
- Appels sans token → 401/403 sur routes sensibles.

---

### 4) Rate limiting (proxy)
- Mettre en place au niveau Nginx/Cloudflare (exemple indicatif):

Nginx (extrait indicatif)
```
limit_req_zone $binary_remote_addr zone=aube_limit:10m rate=60r/m;
server {
  location / {
    limit_req zone=aube_limit burst=30 nodelay;
    proxy_pass http://aube_upstream;
  }
}
```

Validation
- Générer > 60 req/min/IP → réponses 429.

---

### 5) Secrets et variables d’environnement (minima)
- `JWT_SECRET_KEY` (forte entropie)
- `ALLOWED_ORIGINS` (liste séparée par virgules)
- `ALLOWED_HOSTS` (liste séparée par virgules)
- `SENTRY_DSN` (optionnel monitoring)
- `SUPABASE_URL`, `SUPABASE_KEY` (si lecture/écriture Event Store)

---

### 6) Tests de non-régression
- p95 latence < 1.5s; pas d’augmentation d’erreurs 4xx/5xx inattendues.
- Health/Docs accessibles pour environnements autorisés.

---

### Rollback
- Revenir aux paramètres précédents CORS/hosts.
- Désactiver règles rate limiting proxy.
- Maintenir logs pour post-mortem.


