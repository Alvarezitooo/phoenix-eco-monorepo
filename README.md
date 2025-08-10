# 🔥 Phoenix Ecosystem - Monorepo

> **La première plateforme IA française spécialisée reconversion professionnelle**

[![License](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](LICENSE)
[![Security Audit](https://img.shields.io/badge/Security%20Audit-PASSED-brightgreen.svg)](PHOENIX_SECURITY_AUDIT_2025.md)
[![OWASP](https://img.shields.io/badge/OWASP%20Top%2010-Compliant-blue.svg)](SECURITY.md)
[![Zero Vulns](https://img.shields.io/badge/Critical%20Vulns-0-brightgreen.svg)](PHOENIX_SECURITY_AUDIT_2025.md)
[![RGPD](https://img.shields.io/badge/RGPD-Compliant-green.svg)](SECURITY.md)

## 🎯 **Vue d'ensemble**

Phoenix Ecosystem est une suite d'applications IA révolutionnant l'accompagnement des reconversions professionnelles en France.

### **🚀 Applications**
- **📝 Phoenix Letters** - Générateur IA de lettres de motivation ultra-personnalisées
- **📄 Phoenix CV** - Optimiseur IA de CV avec analyse ATS avancée  
- **🌐 Phoenix Website** - Site principal de l'écosystème

### **💰 Modèle économique**
- Freemium avec fonctionnalités premium Stripe
- Plans : Letters (9,99€), CV (7,99€), Bundle (15,99€)

## 🏗️ **Architecture Monorepo**

```
phoenix-ecosystem/
├── apps/                          # Applications principales
│   ├── phoenix-letters/           # App Streamlit Letters
│   ├── phoenix-cv/               # App Streamlit CV
│   └── phoenix-website/          # Site Next.js
├── packages/                      # Modules partagés
│   ├── phoenix-shared-auth/      # Authentification unifiée
│   └── phoenix-shared-models/    # Modèles de données
├── infrastructure/               # Infrastructure technique
│   ├── data-pipeline/           # Pipeline données & IA
│   ├── database/               # Schémas DB
│   └── testing/               # Tests ecosystem
├── docs/                        # Documentation
└── pricing.html               # Page pricing standalone
```

## 🚀 **Démarrage rapide**

### **Monorepo (recommandé)**
```bash
poetry install --with dev
pre-commit install
make lint && make typecheck && make test
```

### **Phoenix Website**
```bash
cd apps/phoenix-website
npm ci
npm run dev
```

## 🔧 **Configuration**

### **Variables d'environnement**
Chaque app nécessite :
```env
# Stripe (obligatoire)
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# IA (obligatoire)  
GOOGLE_API_KEY=your_gemini_key

# Auth (optionnel)
SUPABASE_URL=https://...
SUPABASE_KEY=...
```

## 🛡️ **Sécurité**

- **Audit complet** : Voir [Security Audit](docs/SECURITY_AUDIT_ECOSYSTEM_PHOENIX.md)
- **RGPD Compliant** : Protection données personnelles by design
- **Scan continu** : Bandit, Snyk, vulnérabilités
- **Chiffrement** : AES-256 pour données premium

## 📊 **Monitoring & Analytics**

- **Métriques temps réel** : Performance, utilisation, conversion
- **Data Pipeline** : Event sourcing + Supabase
- **IA Analytics** : Optimisation continue prompts Gemini

## 🚀 **Déploiement**

### **Production**
- **Phoenix Letters** : https://phoenix-letters.streamlit.app
- **Phoenix CV** : https://phoenix-cv.streamlit.app  
- **Website** : À déployer sur Netlify

### **Technologies**
- **Backend** : Python 3.11+, Streamlit
- **Frontend** : Next.js 14, React, TypeScript
- **IA** : Google Gemini 1.5 Flash
- **Base de données** : Supabase PostgreSQL
- **Paiements** : Stripe
- **Auth** : JWT + Supabase Auth

## 🎯 **Roadmap 2025**

### **Phase 1 - MVP (Q1)**
- [x] Phoenix Letters production
- [x] Phoenix CV production  
- [x] Intégration Stripe complète
- [ ] Website déployé

### **Phase 2 - Scale (Q2)**
- [ ] Data pipeline complet
- [ ] Analytics avancées
- [ ] API publique
- [ ] Mobile apps

### **Phase 3 - Expansion (Q3-Q4)**
- [ ] Marketplace templates
- [ ] Partenariats RH
- [ ] IA coaching avancé

## 🤝 **Contribution**

1. Fork le projet
2. Créer une branche feature
3. Tests + sécurité validés
4. Pull request avec description

## 📄 **License**

GNU General Public License v3.0 - Voir [LICENSE](LICENSE)

**Protection Copyleft :** Toute modification doit rester open source sous GPL v3  
**Dual Licensing :** Licence commerciale disponible pour usage propriétaire  
**Contact :** contact.phoenixletters@gmail.com

## 📞 **Contact**

- **Email** : contact.phoenixletters@gmail.com
- **GitHub** : https://github.com/Alvarezitooo/Phoenix-eco
- **Support** : Via les apps Streamlit

---

**🔥 Révolutionnons ensemble les reconversions professionnelles ! 🚀**