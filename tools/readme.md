# 🛠️ Phoenix Tools

Ensemble d’outils internes pour surveiller, diagnostiquer et stabiliser le monorepo **Phoenix**.  
Ces scripts ne modifient rien : ils analysent, rapportent, et aident à garder la qualité du code avant déploiement.

---

## 📂 Contenu

- **phoenix_doctor.py**  
  Outil principal de diagnostic.  
  Vérifie versions minimales, secrets plausibles, imports relatifs, initialisations Supabase, tests smoke, etc.

- **check_security.sh**  
  Lance les audits Bandit (sécu code) et GitLeaks (fuites de secrets).

- **check_imports.sh**  
  Vérifie qu’il ne reste **aucun import relatif** dans `packages/` et `apps/`.

- **check_secrets.sh**  
  Scan rapide des clés API/Stripe/Supabase pour s’assurer qu’elles ne sont pas hardcodées.

- **run_all.sh**  
  Orchestrateur → exécute tous les checks en chaîne et produit un rapport global.

---

## 🚀 Usage rapide

Depuis la racine du repo :

```bash
# Check complet en mode lisible
python tools/phoenix_doctor.py

# Check complet en mode JSON (utile pour IA)
python tools/phoenix_doctor.py --format json --report reports/doctor.json

# Exécuter tous les scripts shell
tools/run_all.sh
🎯 Vérifications principales
Versions minimales

streamlit ≥ 1.33

pydantic ≥ 2.0

httpx ≥ 0.27

Secrets

Détection des valeurs plausibles (sk_live_..., whsec_..., JWT, etc.).

Les settings doivent être centralisés dans packages/phoenix_common/settings.py.

Imports

Zéro from . ou from ...

Tout doit être absolu.

Supabase

Une seule init via phoenix_shared_auth.

🚫 Pas de SUPABASE_SERVICE_ROLE_KEY dans apps/.

Tests smoke

pytest tests/test_ui_imports.py

pytest tests/test_settings.py

pytest tests/test_supabase_connection.py (skip si pas de secrets dispo)

Sécurité

Bandit : vulnérabilités Python.

GitLeaks : secrets oubliés dans le code.

🧠 Bonnes pratiques
Toujours lancer phoenix_doctor.py avant un push important.

Surveillez particulièrement les erreurs sur :

secrets_hardcode

supabase_service_role_in_apps

imports_relatifs

run_all.sh est idéal en pré-prod.

Pour Gemini/Claude, utilisez le mode JSON + rapport (--report) → plus facile à parser.

📌 Exemple (Gemini/Claude en code-run)
bash
Copier
Modifier
python tools/phoenix_doctor.py --format json --report reports/doctor.json
👉 L’IA peut ensuite analyser reports/doctor.json et proposer des correctifs ciblés.

⚠️ Limitations
Ce dossier exclut automatiquement phoenix-rise et phoenix-aube.

Ne remplace pas les audits complets CI/CD (déjà gérés dans GitHub Actions).

Les résultats sont indicatifs : toujours valider avant de merger.

