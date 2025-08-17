#!/usr/bin/env bash
# tools/check_secrets.sh
# Détection de secrets (gitleaks + rg patterns sensibles)
set -euo pipefail

ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
cd "$ROOT_DIR"

RED=$'\e[31m'; GREEN=$'\e[32m'; YELLOW=$'\e[33m'; BLUE=$'\e[34m'; DIM=$'\e[2m'; RESET=$'\e[0m'
say(){ echo -e "${BLUE}[$(date +%H:%M:%S)]${RESET} $*"; }
ok(){ echo -e "  ${GREEN}✔${RESET} $*"; }
warn(){ echo -e "  ${YELLOW}▲${RESET} $*"; }
bad(){ echo -e "  ${RED}✖${RESET} $*"; }

mkdir -p reports
TS="$(date +%Y%m%d_%H%M%S)"
EXIT=0

say "🕵️ Scan gitleaks…"
if command -v gitleaks >/dev/null 2>&1; then
  if gitleaks detect --no-banner --redact --report-path "reports/gitleaks_${TS}.json"; then
    ok "Gitleaks OK (aucun secret trouvé)."
  else
    bad "Gitleaks a détecté des secrets (voir reports/gitleaks_${TS}.json)."
    EXIT=2
  fi
else
  warn "gitleaks non installé. \`brew install gitleaks\` recommandé."
fi

say "🔎 Scan ripgrep (patterns sensibles) hors settings.py/Rise/Aube…"
if command -v rg >/dev/null 2>&1; then
  set +e
  rg -n '(sk_live_|pk_live_|eyJhbGci|STRIPE_|SUPABASE_|GEMINI_)' \
     packages apps/phoenix-{cv,letters,website} \
     --glob '!packages/phoenix_common/settings.py' \
     --glob '!apps/phoenix-rise/**' --glob '!apps/phoenix-aube/**' \
     --glob '!.env*' --glob '!**/__pycache__/**'
  RC=$?
  set -e
  if [[ $RC -eq 0 ]]; then
    bad "Patterns sensibles repérés hors loader central. Corrige immédiatement."
    EXIT=2
  else
    ok "Aucun hardcode sensible détecté hors settings.py."
  fi
else
  warn "ripgrep (rg) non installé. \`brew install ripgrep\`."
fi

exit $EXIT
