# Phoenix CV

Ce projet vise à créer le générateur de CV IA le plus avancé du marché, spécialement optimisé pour les reconversions professionnelles, en parfaite synergie avec Phoenix Letters.

## Structure du Projet

```
phoenix_cv/
├── models/             # Définitions des modèles de données Pydantic (CVRequest, CVResponse, etc.)
├── services/           # Logique métier principale (CVGeneratorService, etc.)
├── utils/              # Fonctions utilitaires (parsing, anonymisation, etc.)
├── templates/          # Fichiers de templates pour la génération de CV
├── requirements.txt    # Dépendances Python du projet
└── README.md           # Ce fichier de documentation
```

## Installation

1. Cloner le dépôt (si applicable).
2. Naviguer vers le répertoire `phoenix_cv`.
3. Installer les dépendances Python :
   ```bash
   pip install -r requirements.txt
   ```
4. Télécharger le modèle spaCy pour le français :
   ```bash
   python -m spacy download fr_core_news_md
   ```

## Utilisation

(À compléter une fois les fonctionnalités implémentées)

## Objectifs Clés

- Parsing intelligent de CV/annonces avec spaCy.
- Génération structurée et fiable de contenu CV avec Instructor.
- Extraction de mots-clés ATS intelligente avec Yake.
- Exécution asynchrone pour une réactivité maximale.
