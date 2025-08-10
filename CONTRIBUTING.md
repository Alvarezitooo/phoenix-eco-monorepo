# Contribuer au monorepo Phoenix Ecosystem

Ce guide décrit comment développer, tester et livrer des changements dans ce monorepo.

## Prérequis
- Python 3.11 recommandé
- Poetry 2.x
- Node 20 (pour `apps/phoenix-website`)

## Bootstrap

```bash
poetry install --with dev
pre-commit install
```

## Commandes utiles
- Lint: `make lint`
- Typage: `make typecheck`
- Tests: `make test`

## Structure
- `apps/`: applications déployables (CV, Letters, Rise, Aube, Website)
- `packages/`: librairies internes partagées (auth, ai, db, ui, event_bridge, etc.)
- `infrastructure/`: tests end-to-end, scripts utilitaires, schémas

## Conventions
- Imports stables via deps locales Poetry (pas de `sys.path.append`)
- Typage explicite dans `packages/*`
- Respect du linter (ruff) et mypy

## Pull Requests
- Créer une branche feature/fix
- Ouvrir une PR avec description claire (voir template)
- CI doit être verte (lint, type, tests)

## Sécurité & RGPD
- Ne pas committer de secrets
- Utiliser `python-dotenv` localement uniquement
- Pseudonymiser/Mocker les données dans les tests

