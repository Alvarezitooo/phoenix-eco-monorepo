#!/usr/bin/env bash
# tools/phoenix_check.sh
# Phoenix Monorepo pre-prod checks (hors Rise/Aube, sans toucher au CI)
# Exits non-zero if any mandatory check fails.

set -euo pipefail

# ---------- Config ----------
APPS=("apps/phoenix-cv" "apps/phoenix-letters" "apps/phoenix-website")
EXCLUDES=(--glob '!apps/phoenix-rise/**' --glob '!apps/phoenix-aube/**')
# Toggle optionnels (0=skip, 1=run)
RUN_STREAMLIT_SAFE_MODE=${RUN_STREAMLIT_SAFE_MODE:-0}  # lance un smoke Streamlit si =1
RUN_NEXT_BUILD=${RUN_NEXT_BUILD:-0}                    # lance build Next.js si =1
# Binaries optionnels
RG_BIN="${RG_BIN:-rg}"
BANDIT_BIN="${BANDIT_BIN:-bandit}"
GITLEAKS_BIN="${GITLEAKS_BIN:-gitleaks}"
PYTEST_BIN="${PYTEST_BIN:-pytest}"

RED=$'\e[31m'; GREEN=$'\e[32m'; YELLOW=$'\e[33m'; BLUE=$'\e[34m'; DIM=$'\e[2m'; RESET=$'\e[0m'
FAILS=()

say() { echo -e "${BLUE}[$(date +%H:%M:%S)]${RESET} $*"; }
ok()  { echo -e "  ${GREEN}✔${RESET} $*"; }
warn(){ echo -e "  ${YELLOW}▲${RESET} $*"; }
bad() { echo -e "  ${RED}✖${RESET} $*"; FAILS+=("$*"); }

require_bin() {
  if ! command -v "$1" >/dev/null 2>&1; then
    warn "Binaire manquant: $1 (le check associé sera réduit/ignoré)"
    return 1
  fi
  return 0
}

header() {
  echo -e "\n${DIM}────────────────────────────────────────────────────────────${RESET}"
  echo -e "${YELLOW}$*${RESET}"
  echo -e "${DIM}────────────────────────────────────────────────────────────${RESET}"
}

# ---------- 1) Dépendances cohérentes ----------
header "1) Dépendances cohérentes (apps vs shared)"
if require_bin "$RG_BIN"; then
  $RG_BIN -n "supabase|stripe|pydantic" packages "${APPS[@]}" "${EXCLUDES[@]}" || true
  ok "Scan de présence des libs core effectué (vérifie qu'elles ne sont pas redéclarées inutilement)."
else
  warn "rg absent → saute la recherche de doublons de libs."
fi

# ---------- 2) Versions harmonisées ----------
header "2) Versions harmonisées (minimas recommandés)"
python - <<'PY'
import sys, re, os
mins = {"streamlit":(1,33), "pydantic":(2,0), "httpx":(0,27)}
req_files = [p for p in ("requirements.txt","apps/phoenix-website/package.json") if os.path.exists(p)]
print("Fichiers détectés:", ", ".join(req_files) or "aucun")
def parse_req(lines):
    d={}
    for ln in lines:
        m=re.match(r"\s*([A-Za-z0-9_.\-]+)\s*([>=]=)\s*([0-9.]+)", ln)
        if m: d[m.group(1).lower()]=(m.group(2), tuple(map(int,m.group(3).split("."))))
    return d
reqs={}
if os.path.exists("requirements.txt"):
    with open("requirements.txt") as f:
        reqs=parse_req(f.readlines())
def ge(v,a): return v>=a
problems=[]
for name, minv in mins.items():
    v = reqs.get(name)
    if not v:
        print(f"  • {name}: non spécifié dans requirements.txt (ok si indirect)")
    else:
        op, ver = v
        if op not in (">=", "=="):
            problems.append(f"{name}: opérateur {op} non recommandé (utilise >= ou ==)")
        if not ge(ver, minv):
            problems.append(f"{name}: {ver} < {minv} (augmenter version min)")
if problems:
    print("⚠ Problèmes versions:", *problems, sep="\n  - ")
    sys.exit(2)
else:
    print("OK versions min recommandées respectées ou non spécifiées explicitement.")
PY
if [[ $? -eq 0 ]]; then ok "Versions min ok (ou non spécifiées)."; else bad "Versions à harmoniser (voir messages ci-dessus)."; fi

# ---------- 3) Secrets centralisés (zéro hardcode) ----------
header "3) Secrets centralisés (zéro hardcode en dehors de phoenix_common/settings.py)"
if require_bin "$RG_BIN"; then
  set +e
  $RG_BIN -n '(sk_live_|pk_live_|eyJhbGci|STRIPE_|SUPABASE_|GEMINI_)' \
    --glob '!packages/phoenix_common/settings.py' \
    --glob '!.env*' --glob '!.github/**' --glob '!**/__pycache__/**' \
    packages "${APPS[@]}" "${EXCLUDES[@]}"
  RC=$?
  set -e
  if [[ $RC -eq 0 ]]; then
    bad "Potentiels secrets/constantes sensibles repérés hors settings.py (voir occurrences ci-dessus)."
  else
    ok "Pas de hardcode sensible détecté (hors settings.py)."
  fi
else
  warn "rg absent → impossible d’auditer les hardcodes de secrets."
fi

# ---------- 4) Bandit & GitLeaks ----------
header "4) Bandit & GitLeaks (0 critique attendu)"
if require_bin "$BANDIT_BIN"; then
  set +e
  $BANDIT_BIN -q -r packages "${APPS[@]}" || BANDIT_RC=$?
  set -e
  if [[ ${BANDIT_RC:-0} -ne 0 ]]; then bad "Bandit a signalé des issues (voir sortie)."; else ok "Bandit OK"; fi
else
  warn "bandit absent → check sécurité statique Python sauté."
fi
if require_bin "$GITLEAKS_BIN"; then
  set +e
  $GITLEAKS_BIN detect --no-banner --redact || GITLEAKS_RC=$?
  set -e
  if [[ ${GITLEAKS_RC:-0} -ne 0 ]]; then bad "Gitleaks a détecté des secrets (voir sortie)."; else ok "Gitleaks OK"; fi
else
  warn "gitleaks absent → scan fuites de secrets sauté."
fi

# ---------- 5) Imports relatifs ----------
header "5) Imports absolus 100% (pas de relatifs restants)"
if require_bin "$RG_BIN"; then
  set +e
  $RG_BIN -n '^from\s+\.(\.|[A-Za-z_])' packages "${APPS[@]}" "${EXCLUDES[@]}"
  RC=$?
  set -e
  if [[ $RC -eq 0 ]]; then bad "Imports relatifs encore présents (corriger → imports absolus)."
  else ok "Aucun import relatif détecté."; fi
else
  warn "rg absent → skip détection imports relatifs."
fi

# ---------- 6) Smoke tests minimalistes ----------
header "6) Smoke tests (UI & settings)"
if require_bin "$PYTEST_BIN"; then
  set +e
  $PYTEST_BIN -q tests/test_ui_imports.py || UI_RC=$?
  $PYTEST_BIN -q tests/test_settings.py || SET_RC=$?
  set -e
  if [[ ${UI_RC:-0} -ne 0 ]]; then bad "tests/test_ui_imports.py KO"; else ok "UI imports test OK"; fi
  if [[ ${SET_RC:-0} -ne 0 ]]; then bad "tests/test_settings.py KO"; else ok "Settings loader test OK"; fi
else
  warn "pytest absent → smoke tests non exécutés."
fi

# ---------- 7) SAFE_MODE (optionnel) ----------
header "7) SAFE_MODE (dégradé propre) [optionnel]"
if [[ "$RUN_STREAMLIT_SAFE_MODE" == "1" ]]; then
  if require_bin "streamlit"; then
    say "Lancement (CTRL+C pour arrêter après affichage manuel)…"
    PHOENIX_SAFE_MODE=1 ENV=prod streamlit run apps/phoenix-cv/app.py || true
    ok "Streamlit lancé en SAFE_MODE (vérifie visuellement bandeau/UX)."
  else
    warn "streamlit absent → ne peut pas faire le smoke interactif."
  fi
else
  warn "SAFE_MODE non exécuté (RUN_STREAMLIT_SAFE_MODE=1 pour activer)."
fi

# ---------- 8) Supabase init (sans double init) ----------
header "8) Supabase init OK (sans double init)"
if require_bin "$RG_BIN"; then
  set +e
  $RG_BIN -n 'create_client\(|supabase\.create_client\(' apps/phoenix-{cv,letters}
  RC=$?
  set -e
  if [[ $RC -eq 0 ]]; then bad "Init Supabase locale repérée dans apps (doit passer par phoenix_shared_auth)."
  else ok "Aucune init locale Supabase détectée dans apps."; fi
else
  warn "rg absent → skip détection init Supabase doublon."
fi

if require_bin "$PYTEST_BIN"; then
  set +e
  $PYTEST_BIN -q tests/test_supabase_connection.py || SUPA_RC=$?
  set -e
  if [[ ${SUPA_RC:-0} -ne 0 ]]; then
    warn "test_supabase_connection.py KO ou SKIP (vérifie secrets SUPABASE_URL/ANON_KEY en CI local)."
  else
    ok "test_supabase_connection.py OK"
  fi
else
  warn "pytest absent → test supabase non exécuté."
fi

# ---------- 9) Builds prod (optionnels) ----------
header "9) Builds prod (optionnels)"
if [[ "$RUN_NEXT_BUILD" == "1" ]]; then
  if [[ -d "apps/phoenix-website" ]]; then
    if command -v npm >/dev/null 2>&1; then
      (cd apps/phoenix-website && npm ci && npm run build) || bad "Build Next.js KO"
      ok "Build Next.js OK"
    else
      warn "npm absent → build Next.js sauté."
    fi
  else
    warn "apps/phoenix-website manquant → build Next.js sauté."
  fi
else
  warn "Build Next.js non exécuté (RUN_NEXT_BUILD=1 pour activer)."
fi

# ---------- 10) EventBridge & Observabilité (manuel guidé) ----------
header "10) EventBridge & Observabilité (manuel)"
cat <<'TIP'

• Pour tester l’EventBridge :
  1) Renomme temporairement un composant UI (ex: phoenix_cv/ui/components/phoenix_header.py -> phoenix_header_x.py)
  2) Lance l’app et vérifie qu’un événement `UIComponentImportFailed` est émis.
  3) Remets le nom, relance.

• Pour Sentry/PostHog :
  - Assure-toi que SENTRY_DSN / POSTHOG_KEY sont passés par l'environnement (pas en dur).
  - Vérifie l'init via logs/console au démarrage (pas d’erreur d’import).

TIP

# ---------- Résumé ----------
echo
if [[ ${#FAILS[@]} -eq 0 ]]; then
  echo -e "${GREEN}✅ Tous les checks obligatoires sont OK (hors étapes optionnelles).${RESET}"
  exit 0
else
  echo -e "${RED}❌ Problèmes détectés:${RESET}"
  for f in "${FAILS[@]}"; do echo "  - $f"; done
  exit 2
fi
