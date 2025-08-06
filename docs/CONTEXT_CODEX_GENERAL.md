# 🧠 CONTEXT_CODEX_GENERAL.md

## 🔥 PHOENIX ECOSYSTEM - CONTEXTE GLOBAL POUR AGENTS CODEX

> Ce fichier définit la **vision stratégique, l'architecture technique, les règles de sécurité et les priorités d’audit** de l’écosystème Phoenix. Il est destiné à tout agent Codex ou IA technique interagissant avec ce codebase.

---

## 🎯 MISSION PHOENIX

> **Révolutionner l’accompagnement à la reconversion professionnelle** via un écosystème modulaire basé sur l’IA, avec une architecture sécurisée, éthique et performante.

**Positionnement :** Plateforme IA française 100% reconversion  
**Apps principales :**
- `phoenix-letters` : Générateur de lettres motivation IA
- `phoenix-cv` : Créateur de CV optimisés ATS
- `phoenix-rise` : Coach motivationnel & levée des blocages psychologiques
- `phoenix-website` : Site vitrine marketing (Next.js)

**Stack globale :** Python 3.11+, Streamlit, Next.js, Supabase, Redis, Event Sourcing, IA Gemini

---

## 🏗️ ARCHITECTURE TECHNIQUE

### 🔧 Monorepo Structure
```
phoenix-ecosystem/
├── apps/
│   ├── phoenix-letters/
│   ├── phoenix-cv/
│   ├── phoenix-rise/
│   └── phoenix-website/
├── packages/
│   ├── phoenix-shared-auth/
│   └── phoenix-shared-models/
├── infrastructure/
│   ├── data-pipeline/ (Event Sourcing + Supabase)
│   ├── testing/
│   └── docker/
└── docs/ (Audit, RGPD, etc)
```

### 📡 Data Pipeline Unifié
- **Event Store PostgreSQL** : source of truth
- **Bus d’événements (RabbitMQ)** : synchro cross-apps
- **Read Models spécialisés** pour chaque app

### 🤖 Flywheel 2.0 (Système Conscient)
- Monitoring Prometheus
- Smart Router, Throttling, Scaling, Alerting IA
- Agents : Data Flywheel, Security Guardian, System Consciousness

---

## 🔐 SÉCURITÉ & CONFORMITÉ

- **RGPD-first** : Anonymisation PII, logs sécurisés, session limitées
- **OWASP Top 10** : 100% compliant (cf `PHOENIX_SECURITY_AUDIT_2025.md`)
- **Chiffrement** : AES-256, PBKDF2
- **Audit OK** : 0 vulnérabilité critique (août 2025)

---

## 🧪 AUDIT – PROTOCOLE STANDARD POUR CODEX

Merci d’appliquer cette méthodologie lors de l’audit d’un composant Phoenix :

### Étapes :
1. Identifier le module cible (ex: `phoenix-rise`)
2. Évaluer :
   - Sécurité & RGPD
   - Cohérence structurelle
   - Performance IA / API
   - UX métier
   - Opportunités refactoring
3. Si autorisé : créer branche `codex/audit-[module]`
4. Générer PR avec résumé clair par commit

### Règles :
- 🔒 Ne jamais push sur `main`
- 🔁 Préférer `develop` comme base
- 📄 Inclure `CONTEXT_CODEX_GENERAL.md` dans chaque PR pour transparence

---

## 🧭 OBJECTIFS STRATÉGIQUES DE CHAQUE MODULE

| Module          | Rôle Clé                                     | IA / UX Spécifique                  |
|----------------|-----------------------------------------------|------------------------------------|
| phoenix-letters| Générer des lettres persos alignées avec offre| Prompt engineering + ATS Matching |
| phoenix-cv     | Créer des CVs optimisés pour recrutement      | Parsing + scoring ATS              |
| phoenix-rise   | Lever blocages émotionnels + coaching IA      | Recommandation motivationnelle     |
| phoenix-website| Acquisition SEO + storytelling fondateur      | Marketing, conversion               |

---

## 📦 DOCUMENTS COMPLÉMENTAIRES RECOMMANDÉS
- `PHOENIX_SECURITY_AUDIT_2025.md`
- `FLYWHEEL_2_GUIDE.md`
- `GUIDE_EVENT_SOURCING_VULGARISE.md`
- `architecture_data_pipeline.md`

Ces fichiers offrent à Codex une compréhension approfondie du système.

---

Merci Codex. Respecte la **vision écosystème**, la **sécurité des utilisateurs**, et la **lisibilité du code** comme tes 3 lois fondatrices.
