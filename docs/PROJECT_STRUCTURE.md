# Structure du projet

```
phoenix-eco-monorepo/
├── apps/
│   ├── phoenix-aube/
│   ├── phoenix-cv/
│   ├── phoenix-iris-api/
│   ├── phoenix-letters/
│   ├── phoenix-rise/
│   └── phoenix-website/
├── packages/
│   ├── phoenix-shared-auth/
│   ├── phoenix-shared-ai/
│   ├── phoenix-shared-db/
│   ├── phoenix-shared-models/
│   ├── phoenix_event_bridge/
│   ├── phoenix_shared_ui/
│   ├── iris-agent/
│   ├── iris-client/
│   └── pdf-security-patch/
├── infrastructure/
│   ├── data-pipeline/
│   ├── database/
│   ├── deploy/
│   ├── research/
│   └── testing/
├── docs/
│   └── PROJECT_STRUCTURE.md (ce fichier)
└── outillage racine
    ├── pyproject.toml, poetry.lock
    ├── ruff.toml, mypy.ini, pytest.ini
    ├── .pre-commit-config.yaml, .editorconfig, .gitignore
    └── .github/workflows/*
```

Principes:
- Apps consomment les packages via deps locales Poetry
- CI unifiée (lint/type/tests)
- Pas de `sys.path.append` (imports stables)

