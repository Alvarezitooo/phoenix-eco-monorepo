# Lettre-Motiv-Auto

> **Générateur de lettres de motivation IA spécialisé dans les reconversions professionnelles**

[![Streamlit App](https://img.shields.io/badge/Streamlit-App-red)](https://your-app.streamlit.app)
[![Python](https://img.shields.io/badge/Python-3.11+-blue)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

![Demo Animation](https://via.placeholder.com/800x400/4285f4/white?text=Demo+Screenshot)

## ✨ **Ce qui rend cette app unique**

### **Spécialisée Reconversion**
- **Prompt magistral IA** qui transforme les parcours atypiques en super-pouvoirs
- **Pont logique** intelligent entre ancien et nouveau métier  
- **Valorisation** des compétences transférables

### **Fonctionnalités Avancées**
- **Mirror Match** : Analyse de culture d'entreprise pour adapter le ton
- **Trajectory Builder** : Plan de reconversion personnalisé
- **Smart Coach** : Feedback IA sur la qualité de la lettre
- **Multi-formats** : Export TXT, DOCX, PDF

### **Sécurité & RGPD**
- **Anonymisation PII** automatique (Presidio)
- **Données chiffrées** pour utilisateurs premium
- **Gestion consentement** conforme RGPD

## **Démo Rapide**

```bash
# Clone et lance
git clone https://github.com/your-github-username/lettre-motiv-auto.git
cd lettre-motiv-auto
pip install -r requirements.txt
streamlit run app.py
```

**Ou teste directement :** [→ App Live](https://your-app.streamlit.app)

## ️ **Stack Technique**

- **Framework** : Streamlit (Python)
- **IA** : Google Gemini 1.5 Flash
- **Sécurité** : Presidio (anonymisation), ClamAV (scan uploads)
- **RGPD** : Chiffrement AES, gestion consentement
- **Architecture** : Modular services, cache intelligent

## **Installation Développement**

### Prérequis
```bash
Python 3.11+
Google API Key (Gemini)
```

### Setup
```bash
# 1. Clone
git clone https://github.com/your-github-username/lettre-motiv-auto.git
cd lettre-motiv-auto

# 2. Environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. Dependencies
pip install -r requirements.txt

# 4. Configuration
cp .env.example .env
# Édite .env avec tes clés API

# 5. Launch
streamlit run app.py
```

## **Cas d'Usage Parfaits**

- **Aide-soignant** → Cybersécurité
- **Professeur** → Product Manager  
- **Comptable** → Data Analyst
- **Commercial** → Développeur
- **Manager** → Coach/Consultant

## ️ **Architecture**

```
lettre-motiv-auto/
├── app.py                 # Interface Streamlit
├── services/
│   ├── letter_service.py  # Logique génération lettres
│   ├── api_client.py      # Clients APIs (Gemini, France Travail)
│   ├── data_anonymizer.py # Anonymisation RGPD
│   └── trajectory_service.py # Plans reconversion
├── models/                # Modèles Pydantic
├── utils/                 # Utilitaires (cache, etc.)
└── requirements.txt
```

## **Roadmap**

### ✅ **V1.0 - Core MVP** 
- [x] Génération lettres reconversion
- [x] Interface intuitive  
- [x] Sécurité RGPD

### **V1.1 - En Cours**
- [ ] Story Arc Builder
- [ ] Optimisation performance
- [ ] Tests automatisés

### **V2.0 - Vision**
- [ ] API publique
- [ ] Intégrations (LinkedIn, Indeed)
- [ ] Mobile app

## **Contribution**

Les contributions sont les bienvenues ! 

1. **Fork** le projet
2. **Crée** ta branche (`git checkout -b feature/amazing-feature`)
3. **Commit** (`git commit -m 'Add amazing feature'`)
4. **Push** (`git push origin feature/amazing-feature`)
5. **Ouvre** une Pull Request

## **License**

Distribué sous licence MIT. Voir [LICENSE](LICENSE) pour plus d'informations.

## ‍ **Auteur**

**Alva Ito** - [@your-github-username](https://github.com/your-github-username)

- Portfolio : [your-portfolio-site.com](https://your-portfolio-site.com)
- Email : your-email@example.com
- LinkedIn : [linkedin.com/in/your-linkedin-profile](https://linkedin.com/in/your-linkedin-profile)

## **Remerciements**

- **Anthropic Claude** - Conception architecturale et prompt engineering
- **Google Gemini** - Génération de contenu IA
- **Streamlit** - Framework web Python fantastique
- **Communauté open source** - Inspiration et outils

---

⭐ **Si ce projet t'aide dans ta reconversion, n'hésite pas à lui mettre une étoile !**