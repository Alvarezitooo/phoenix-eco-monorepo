## CI Pipeline – Lint + Tests API/Stripe en gating

Objectif: empêcher tout déploiement si l’intégration Stripe/Supabase échoue.

---

Étapes recommandées (CI générique)
- Install Python and Node versions attendues
- Lint (ESLint + Ruff/Flake8 selon repo)
- Tests unitaires
- Tests d’intégration minimalistes:
  - `python infrastructure/testing/ci_integration_checks.py`
    - Stripe read-only (list customers)
    - Supabase REST insert(event)

Variables d’environnement CI
- `STRIPE_TEST_KEY` ou `STRIPE_SECRET_KEY`
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`

Exemple GitHub Actions (extrait)
```
jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: npm ci --prefix apps/phoenix-website
      - run: pip install -r apps/phoenix-letters/requirements.txt || true
      - run: pip install stripe requests
      - name: CI Integration Checks
        env:
          STRIPE_TEST_KEY: ${{ secrets.STRIPE_TEST_KEY }}
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_SERVICE_ROLE_KEY: ${{ secrets.SUPABASE_SERVICE_ROLE_KEY }}
        run: python infrastructure/testing/ci_integration_checks.py
```

Gating
- Échec → pipeline rouge; aucun déploiement.
- Succès → build + déploiement possible.


