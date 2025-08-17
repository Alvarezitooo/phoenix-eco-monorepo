#!/usr/bin/env python3
"""
Phoenix Doctor – monorepo health checks (hors Rise/Aube, sans toucher au CI).

Objectif: Valider ~80% de la checklist Phase 3 en un run:
- Versions min recommandées (requirements.txt)
- Secrets plausibles hardcodés (regex durcies) + garde-fou service-role dans apps
- Imports relatifs interdits
- Double init Supabase interdite dans apps (doit passer par phoenix_shared_auth)
- Smoke tests pytest (UI imports + settings + supabase si secrets)
- Info-only: bandit/gitleaks si présents (ne bloque pas)
- Options: --only, --report JSON, --format json, --emit-event

Conformité:
- Respecte Directive V3 (monorepo, sécurité, shared services)
- Exclut apps/phoenix-rise et apps/phoenix-aube
- Ne modifie ni fichiers ni CI
"""

from __future__ import annotations
import argparse, os, sys, re, json, subprocess, time, pathlib
from typing import Tuple, List, Dict, Any

# ---------------------------------------------------------------------
# Config monorepo
# ---------------------------------------------------------------------
ROOT = pathlib.Path(__file__).resolve().parents[1]  # tools/.. -> racine repo
APPS = [ROOT/"apps/phoenix-cv", ROOT/"apps/phoenix-letters", ROOT/"apps/phoenix-website"]
EXCLUDES = ("apps/phoenix-rise", "apps/phoenix-aube")
REQUIRED_MARKERS = ("packages", "apps")

# Versions min recommandées (tu peux ajuster ici)
MIN_VERS = {
    "streamlit": (1, 33),
    "pydantic":  (2, 0),
    "httpx":     (0, 27),
}

# Patterns secrets durcis (valeurs plausibles, pas juste noms)
SECRET_VALUE_RE = re.compile(
    r"(?:"
    r"sk_(?:live|test)_[A-Za-z0-9]{20,}"   # Stripe secret
    r"|pk_live_[A-Za-z0-9]{20,}"           # Stripe publishable (pas critique, on alerte quand même)
    r"|whsec_[A-Za-z0-9]{20,}"             # Stripe webhook secret
    r"|eyJhbGci[A-Za-z0-9_\-]{10,}"        # JWT/clé encodée
    r")"
)

# ---------------------------------------------------------------------
# Utils
# ---------------------------------------------------------------------
def which(bin_name: str) -> str | None:
    from shutil import which as _which
    return _which(bin_name)

def run(cmd: str) -> Tuple[int, str, str]:
    p = subprocess.Popen(cmd, shell=True, cwd=str(ROOT),
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = p.communicate()
    return p.returncode, out, err

def parse_requirements_min(text: str) -> Dict[str, Tuple[str, Tuple[int, ...]]]:
    d: Dict[str, Tuple[str, Tuple[int, ...]]] = {}
    for ln in text.splitlines():
        m = re.match(r"\s*([A-Za-z0-9_.\-]+)\s*([>=]=|==)\s*([0-9.]+)", ln)
        if not m:
            continue
        name = m.group(1).lower()
        op = m.group(2)
        ver = tuple(int(x) for x in m.group(3).split(".") if x.isdigit())
        d[name] = (op, ver)
    return d

def version_ge(v: Tuple[int, ...], minv: Tuple[int, ...]) -> bool:
    L = max(len(v), len(minv))
    v2 = v + (0,)*(L-len(v))
    m2 = minv + (0,)*(L-len(minv))
    return v2 >= m2

def is_excluded(path: pathlib.Path) -> bool:
    rel = str(path.relative_to(ROOT)) if path.is_absolute() else str(path)
    return rel.startswith(EXCLUDES[0]) or rel.startswith(EXCLUDES[1])

# ---------------------------------------------------------------------
# Scans
# ---------------------------------------------------------------------
def scan_rel_imports(bases: List[pathlib.Path]) -> List[str]:
    hits: List[str] = []
    pat = re.compile(r"^from\s+\.(?:\.|[A-Za-z_])", re.M)
    for base in bases:
        if not base.exists(): continue
        for p in base.rglob("*.py"):
            if is_excluded(p): continue
            try:
                txt = p.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            if pat.search(txt):
                hits.append(str(p.relative_to(ROOT)))
    return hits

def scan_supabase_local_init(bases: List[pathlib.Path]) -> List[str]:
    hits: List[str] = []
    pat = re.compile(r"(?:create_client\(|supabase\.create_client\()", re.M)
    for base in bases:
        if not base.exists(): continue
        for p in base.rglob("*.py"):
            if is_excluded(p): continue
            try:
                txt = p.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            if pat.search(txt):
                hits.append(str(p.relative_to(ROOT)))
    return hits

def scan_service_role_in_apps() -> List[str]:
    """Références au SERVICE ROLE interdites côté apps (même variable)."""
    hits: List[str] = []
    for base in [ROOT/"apps/phoenix-cv", ROOT/"apps/phoenix-letters"]:
        if not base.exists(): continue
        for p in base.rglob("*.py"):
            try:
                txt = p.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            if "SUPABASE_SERVICE_ROLE_KEY" in txt:
                hits.append(str(p.relative_to(ROOT)))
    return hits

def scan_secrets(bases: List[pathlib.Path]) -> List[Tuple[str, int, str]]:
    """
    Détecte des valeurs plausibles de secrets (et non de simples noms).
    Ignore: settings.py, docs (md), rise/aube, .env*, __pycache__.
    """
    results: List[Tuple[str,int,str]] = []
    ignore_ext = {".md", ".MD"}
    for base in bases:
        if not base.exists(): continue
        for p in base.rglob("*"):
            if p.is_dir(): continue
            if p.suffix in ignore_ext:  # ignore docs
                continue
            rel = str(p.relative_to(ROOT))
            if rel.startswith("packages/phoenix_common/settings.py"):
                continue
            if rel.startswith(EXCLUDES[0]) or rel.startswith(EXCLUDES[1]):
                continue
            if "/__pycache__/" in rel or rel.startswith(".env"):
                continue
            try:
                for i, ln in enumerate(p.read_text(encoding="utf-8", errors="ignore").splitlines(), start=1):
                    if SECRET_VALUE_RE.search(ln) and "REDACT" not in ln:
                        results.append((rel, i, ln.strip()[:200]))
            except Exception:
                continue
    return results

# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(description="Phoenix Doctor – monorepo health checks")
    parser.add_argument("--format", choices=["text","json"], default="text", help="Sortie lisible ou JSON")
    parser.add_argument("--report", type=str, default="", help="Chemin fichier rapport JSON")
    parser.add_argument("--only", type=str, default="", help="Checks ciblés (ex: imports,secrets,versions,supabase,pytest)")
    parser.add_argument("--emit-event", action="store_true", help="(Optionnel) publier un événement DevDoctorRun via phoenix_event_bridge")
    args = parser.parse_args()

    os.chdir(ROOT)
    # Garde-fou: ressemble bien à ton monorepo
    missing = [m for m in REQUIRED_MARKERS if not (ROOT/m).exists()]
    if missing:
        print(f"Ce script doit être lancé à la racine du monorepo (manque: {', '.join(missing)})", file=sys.stderr)
        sys.exit(2)

    requested = set(s.strip() for s in args.only.split(",") if s.strip())
    def allow(name: str) -> bool:
        return not requested or (name in requested)

    report: Dict[str, Any] = {
        "root": str(ROOT),
        "timestamp": int(time.time()),
        "checks": [],
        "summary": {"ok": True, "problems": []},
    }

    def add_check(name: str, ok: bool, details: Any = None, problems: List[str] | None = None):
        ck = {"name": name, "ok": bool(ok)}
        if details is not None: ck["details"] = details
        if problems: ck["problems"] = problems
        report["checks"].append(ck)
        if not ok:
            report["summary"]["ok"] = False
            report["summary"]["problems"].append(name)

    # 1) Versions min (requirements.txt)
    if allow("versions"):
        req_path = ROOT/"requirements.txt"
        problems: List[str] = []
        details: Dict[str, Any] = {}
        if req_path.exists():
            reqs = parse_requirements_min(req_path.read_text(encoding="utf-8"))
            for name, minv in MIN_VERS.items():
                v = reqs.get(name)
                if not v:
                    details[name] = "non_specifie"
                    continue
                op, ver = v
                details[name] = {"op": op, "ver": ".".join(map(str, ver))}
                if op not in (">=", "=="):
                    problems.append(f"{name}: opérateur {op} non recommandé (>= ou ==)")
                if not version_ge(ver, minv):
                    problems.append(f"{name}: {ver} < {'.'.join(map(str, minv))}")
            add_check("versions_min", len(problems) == 0, details=details, problems=problems if problems else None)
        else:
            add_check("versions_min", True, details={"note": "requirements.txt absent (OK si géré ailleurs)"} )

    # 2) Secrets plausibles hardcodés
    if allow("secrets"):
        hits = scan_secrets([ROOT/"packages", *APPS])
        add_check(
            "secrets_hardcode",
            len(hits) == 0,
            details={"total": len(hits), "hits": hits[:50]},
            problems=[f"{len(hits)} occurrence(s) de valeurs sensibles plausibles (hors settings.py)"] if hits else None
        )

    # 3) Imports relatifs interdits
    if allow("imports"):
        rels = scan_rel_imports([ROOT/"packages", *APPS])
        add_check(
            "imports_relatifs",
            len(rels) == 0,
            details={"files": rels},
            problems=[f"{len(rels)} fichier(s) avec imports relatifs"] if rels else None
        )

    # 4) Double init Supabase interdite dans apps
    if allow("supabase"):
        supa_dupes = scan_supabase_local_init([ROOT/"apps/phoenix-cv", ROOT/"apps/phoenix-letters"])
        add_check(
            "supabase_double_init",
            len(supa_dupes) == 0,
            details={"files": supa_dupes},
            problems=[f"{len(supa_dupes)} fichier(s) init supabase locale"] if supa_dupes else None
        )
        # 4b) Service role key interdite côté apps
        sr_refs = scan_service_role_in_apps()
        add_check(
            "supabase_service_role_in_apps",
            len(sr_refs) == 0,
            details={"files": sr_refs},
            problems=[f"{len(sr_refs)} référence(s) à SUPABASE_SERVICE_ROLE_KEY dans apps (interdit)"] if sr_refs else None
        )

    # 5) Pytest smoke (si pytest disponible)
    if allow("pytest"):
        if which("pytest"):
            rc_ui, out_ui, _ = run("pytest -q tests/test_ui_imports.py")
            rc_set, out_set, _ = run("pytest -q tests/test_settings.py")
            rc_supa, out_supa, _ = run("pytest -q tests/test_supabase_connection.py")
            ok_ui   = (rc_ui   == 0)
            ok_set  = (rc_set  == 0)
            ok_supa = (rc_supa == 0) or ("SKIP" in (out_supa or "").upper())
            add_check("pytest_ui_imports", ok_ui,  details={"rc": rc_ui})
            add_check("pytest_settings",   ok_set, details={"rc": rc_set})
            add_check("pytest_supabase",   ok_supa,details={"rc": rc_supa, "note":"OK ou SKIP"})
        else:
            add_check("pytest_smoke", True, details={"note":"pytest non installé – check sauté"})

    # 6) bandit/gitleaks (info-only)
    if allow("bandit"):
        if which("bandit"):
            rc_b, _, _ = run("bandit -q -r packages apps/phoenix-cv apps/phoenix-letters apps/phoenix-website -x apps/phoenix-rise,apps/phoenix-aube")
            add_check("bandit", rc_b == 0, details={"rc": rc_b, "note": "Voir scripts tools/check_security.sh pour détails"})
        else:
            add_check("bandit", True, details={"note":"bandit non installé – info"})
    if allow("gitleaks"):
        if which("gitleaks"):
            rc_g, _, _ = run("gitleaks detect --no-banner --redact")
            add_check("gitleaks", rc_g == 0, details={"rc": rc_g, "note": "Utilise tools/check_secrets.sh pour un rapport JSON"})
        else:
            add_check("gitleaks", True, details={"note":"gitleaks non installé – info"})

    # Événement optionnel (tracé dev), ne doit pas faire échouer
    if args.emit_event:
        try:
            from phoenix_event_bridge.helpers import publish_event  # type: ignore
            from phoenix_shared_models.events import DevDoctorRun   # type: ignore
            publish_event(DevDoctorRun(summary=report["summary"], checks=report["checks"]))
        except Exception:
            pass

    # Sortie
    if args.report:
        pathlib.Path(args.report).parent.mkdir(parents=True, exist_ok=True)
        pathlib.Path(args.report).write_text(json.dumps(report, indent=2), encoding="utf-8")

    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        print(f"\nPhoenix Doctor @ {report['root']}")
        for ck in report["checks"]:
            mark = "✔" if ck["ok"] else "✖"
            print(f"  {mark} {ck['name']}")
            if not ck["ok"] and "problems" in ck:
                for p in ck["problems"]:
                    print("     -", p)
        if report["summary"]["ok"]:
            print("\n✅ Monorepo OK (obligatoires).")
        else:
            print("\n❌ Problèmes détectés (voir détails ci-dessus).")

    sys.exit(0 if report["summary"]["ok"] else 2)

if __name__ == "__main__":
    main()
