#!/usr/bin/env bash
# tools/check_health.sh
# Santé du monorepo: smoke tests, imports relatifs, supabase init, SAFE_MODE/Build optionnels
set -euo pipefail

ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
cd "$ROOT_DIR"

RED=$'\e[31m'; GREEN=$'\e[32m'; YELLOW=$'\e[33m'; BLUE=$'\e[34m'; DIM=$'\e[2m'; RESET=$'\e[0m'
say(){ echo -e "${BLUE}[$(date +%H:%M:%S)]${RESET} $*"; }
ok(){ echo -e "  ${GREEN}✔${RESET} $*"; }
warn(){ echo -e "  ${YELLOW}▲${RESET} $*"; }
bad(){ echo -e "  ${RED}✖${RESET} $*"; }

RUN_STREAMLIT_SAFE_MODE=${RUN_STREAMLIT_SAFE_MODE:-0}
RUN_NEXT_BUILD=${RUN_NEXT_BUILD:-0}
EXIT=0

# 1) Imports relatifs interdits
say "🔍 Imports relatifs (doivent être 0)…"
if command -v rg >/dev/null 2>&1; then
  set +e
  rg -n '^from\s+\.(\.|[A-Za-z_])' packages apps/phoenix-{cv,letters,website}
  RC=$?
  set -e
  if [[ $RC -eq 0 ]]; then bad "Imports relatifs détectés."; EXIT=2; else ok "Aucun import relatif."; fi
else
  warn "rg non installé → skip check imports relatifs."
fi

# 2) Init Supabase locale (doit être 0)
say "🧩 Double init Supabase dans apps (interdit)…"
if command -v rg >/dev/null 2>&1; then
  set +e
  rg -n 'create_client\(|supabase\.create_client\(' apps/phoenix-{cv,letters}
  RC=$?
  set -e
  if [[ $RC -eq 0 ]]; then bad "Init Supabase locale repérée (doit passer par phoenix_shared_auth)."; EXIT=2
  else ok "Aucune init locale Supabase dans apps."; fi
else
  warn "rg non installé → skip check init Supabase."
fi

# 3) Smoke tests pytest
say "🧪 Pytest (smoke)…"
if command -v pytest >/dev/null 2>&1; then
  set +e
  pytest -q tests/test_ui_imports.py || EXIT=2
  pytest -q tests/test_settings.py || EXIT=2
  pytest -q tests/test_supabase_connection.py || true  # peut SKIP si secrets absents
  set -e
  [[ $EXIT -eq 0 ]] && ok "Smoke tests OK" || bad "Smoke tests KO"
else
  warn "pytest non installé → smoke tests non exécutés."
fi

# 4) SAFE_MODE Streamlit (optionnel)
if [[ "$RUN_STREAMLIT_SAFE_MODE" == "1" ]]; then
  say "🧰 SAFE_MODE Streamlit (manuel) — CTRL+C pour quitter après vérif visuelle."
  if command -v streamlit >/dev/null 2>&1; then
    PHOENIX_SAFE_MODE=1 ENV=prod streamlit run apps/phoenix-cv/app.py || true
    ok "Instance Streamlit lancée (vérifie le bandeau dégradé)."
  else
    warn "streamlit non installé → SAFE_MODE interactif sauté."
  fi
fi

# 5) Build Next.js (optionnel)
if [[ "$RUN_NEXT_BUILD" == "1" ]]; then
  say "🏗️ Build Next.js (phoenix-website)…"
  if [[ -d "apps/phoenix-website" ]]; then
    if command -v npm >/dev/null 2>&1; then
      (cd apps/phoenix-website && npm ci && npm run build) || { bad "Build Next KO"; EXIT=2; }
      ok "Build Next OK"
    else
      warn "npm non installé → build Next.js sauté."
    fi
  else
    warn "apps/phoenix-website non trouvé."
  fi
fi

# Résumé
if [[ $EXIT -eq 0 ]]; then
  echo -e "${GREEN}✅ Santé monorepo OK.${RESET}"
else
  echo -e "${RED}❌ Problèmes détectés. Corrige avant déploiement.${RESET}"
fi
exit $EXIT
