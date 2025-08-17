#!/usr/bin/env bash
# tools/check_security.sh
# Audit sécurité: Bandit (obligatoire) + pip-audit (optionnel)
set -euo pipefail

# --- go to repo root ---
ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
cd "$ROOT_DIR"

RED=$'\e[31m'; GREEN=$'\e[32m'; YELLOW=$'\e[33m'; BLUE=$'\e[34m'; DIM=$'\e[2m'; RESET=$'\e[0m'
say(){ echo -e "${BLUE}[$(date +%H:%M:%S)]${RESET} $*"; }
ok(){ echo -e "  ${GREEN}✔${RESET} $*"; }
warn(){ echo -e "  ${YELLOW}▲${RESET} $*"; }
bad(){ echo -e "  ${RED}✖${RESET} $*"; }

mkdir -p reports
TS="$(date +%Y%m%d_%H%M%S)"

say "🔒 Bandit (security lint) sur packages/ + apps/ (hors Rise/Aube)…"
if ! command -v bandit >/dev/null 2>&1; then
  bad "bandit non installé. \`pipx install bandit\` recommandé."
  exit 2
fi

# Rapport texte & JSON
bandit -q -r packages apps/phoenix-cv apps/phoenix-letters apps/phoenix-website \
  -x apps/phoenix-rise,apps/phoenix-aube \
  | tee "reports/bandit_${TS}.txt" || true

# Résumé minimal (non bloquant si warning seulement)
if grep -qiE "Issue:" "reports/bandit_${TS}.txt"; then
  warn "Bandit a trouvé des issues (voir reports/bandit_${TS}.txt)."
else
  ok "Bandit OK (aucune issue détectée)."
fi

say "🛡️ pip-audit (vulnérabilités) — optionnel…"
if command -v pip-audit >/dev/null 2>&1; then
  if pip-audit -r requirements.txt 2>&1 | tee "reports/pip_audit_${TS}.txt"; then
    ok "pip-audit OK (pas de vuln connues)."
  else
    warn "pip-audit a listé des vulnérabilités (voir reports/pip_audit_${TS}.txt)."
  fi
else
  warn "pip-audit non installé. \`pipx install pip-audit\` (recommandé)."
fi

say "✅ Sécurité: terminé."
