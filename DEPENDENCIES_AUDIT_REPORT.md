# 📋 AUDIT DÉPENDANCES - Rapport de Doublons

**Date**: 2025-01-17  
**Scope**: apps/phoenix-cv, apps/phoenix-letters, packages/*

## 🚨 DOUBLONS CRITIQUES DÉTECTÉS

### 1. Dépendances Core Dupliquées

| Package | CV requirements.txt | Letters requirements.txt | phoenix-shared-auth |
|---------|-------------------|-------------------------|---------------------|
| **streamlit** | >=1.30.0 | >=1.30.0 | >=1.28.0 |
| **supabase** | >=2.0.0 | >=2.0.0 | >=2.1.0 |
| **pydantic** | >=2.5.0 | >=2.5.0 | >=2.5.0 |
| **PyJWT** | - | >=2.8.0 | >=2.8.0 |
| **bcrypt** | >=4.0.0 | >=4.0.0 | >=4.0.1 |
| **cryptography** | >=41.0.0 | >=41.0.0 | - |
| **requests** | >=2.31.0 | >=2.31.0 | - |
| **python-dateutil** | >=2.8.2 | >=2.8.2 | >=2.8.2 |

### 2. Conflits de Versions Potentiels

- **supabase**: CV (>=2.0.0) vs phoenix-shared-auth (>=2.1.0)
- **streamlit**: Letters/CV (>=1.30.0) vs phoenix-shared-auth (>=1.28.0)
- **bcrypt**: CV/Letters (>=4.0.0) vs phoenix-shared-auth (>=4.0.1)

### 3. Dépendances qui Devraient être dans Packages

Les apps déclarent directement:
- `supabase` → devrait être dans `phoenix_common`
- `stripe` → devrait être dans `phoenix_common`  
- `PyJWT` → devrait être dans `phoenix-shared-auth`
- `bcrypt` → devrait être dans `phoenix-shared-auth`

## 🎯 PLAN DE CONSOLIDATION

### Étape 1: Centraliser Core Dependencies

**phoenix_common/pyproject.toml** (à créer):
```toml
[project]
dependencies = [
    "supabase>=2.1.0",
    "stripe>=8.0.0", 
    "pydantic>=2.5.0",
    "requests>=2.31.0",
    "python-dotenv>=1.0.0",
    "structlog>=23.2.0",
    "cachetools>=5.3.0"
]
```

**phoenix-shared-auth/pyproject.toml** (mettre à jour):
```toml
[project]
dependencies = [
    "streamlit>=1.30.0",
    "bcrypt>=4.0.1",
    "PyJWT>=2.8.0",
    "cryptography>=41.0.0",
    "passlib[bcrypt]>=1.7.4"
]
```

### Étape 2: Simplifier Apps Requirements

**apps/phoenix-cv/requirements.txt** (épuré):
```
# UI & Core
streamlit>=1.30.0

# AI Spécifique CV
google-generativeai>=0.3.2
pytesseract>=0.3.10
PyPDF2>=3.0.0
PyMuPDF>=1.24.1
python-docx>=1.1.0
Pillow>=10.3.0

# Phoenix Packages (qui apportent leurs deps)
-e ../../packages/phoenix_common
-e ../../packages/phoenix-shared-auth
-e ../../packages/phoenix_event_bridge
-e ../../packages/phoenix-shared-models
```

**apps/phoenix-letters/requirements.txt** (épuré):
```
# UI & Core  
streamlit>=1.30.0

# AI Spécifique Letters
google-generativeai>=0.3.2

# Analytics Spécifique Letters
tenacity>=8.2.0
plotly>=5.0.0
pandas>=1.5.0

# Phoenix Packages (qui apportent leurs deps)
-e ../../packages/phoenix_common
-e ../../packages/phoenix-shared-auth
-e ../../packages/phoenix_event_bridge
-e ../../packages/phoenix-shared-models
```

## ✅ BÉNÉFICES ATTENDUS

- **Maintenance simplifiée**: 1 lieu par dépendance
- **Cohérence versions**: Plus de conflits
- **Sécurité renforcée**: Updates centralisées
- **Build plus rapide**: Moins de téléchargements dupliqués