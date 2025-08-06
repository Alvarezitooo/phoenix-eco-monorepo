#!/bin/bash
#
# SCRIPT D'AUDIT DE SÉCURITÉ LOCAL POUR PHOENIX-WEBSITE
# Auteur: Phoenix Senior Dev
# Objectif: Fournir un bilan de santé de sécurité rapide et à jour.
#

# Couleurs pour la sortie
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}--- Lancement de l'audit de sécurité pour phoenix-website ---${NC}"

# --- 1. Audit des dépendances NPM ---
echo -e "\n${YELLOW}[1/3] Audit des dépendances avec NPM...${NC}"
npm audit

if [ $? -eq 0 ]; then
    echo -e "${GREEN}  => Résultat : Aucune vulnérabilité connue dans les dépendances.${NC}"
else
    echo -e "${RED}  => ALERTE : Des vulnérabilités ont été trouvées. Veuillez analyser le rapport ci-dessus.${NC}"
fi

# --- 2. Recherche de code HTML dangereux (XSS) ---
echo -e "\n${YELLOW}[2/3] Recherche de l'utilisation de 'dangerouslySetInnerHTML'...${NC}"
DANGEROUS_HTML=$(grep -r "dangerouslySetInnerHTML" app/ components/ lib/ pages/ --exclude-dir=node_modules)

if [ -z "$DANGEROUS_HTML" ]; then
    echo -e "${GREEN}  => Résultat : Aucune utilisation de dangerouslySetInnerHTML détectée.${NC}"
else
    echo -e "${RED}  => ALERTE : Utilisation de dangerouslySetInnerHTML détectée. Vérification manuelle requise :${NC}"
    echo "$DANGEROUS_HTML"
fi

# --- 3. Recherche de secrets codés en dur ---
echo -e "\n${YELLOW}[3/3] Recherche de secrets potentiels (API_KEY, SECRET, PASSWORD)...${NC}"
# Exclut les fichiers de lock et les node_modules pour réduire les faux positifs
HARDCODED_SECRETS=$(grep -r -E "API_KEY|SECRET|PASSWORD" . --exclude-dir=node_modules --exclude=package-lock.json --exclude=next.config.js)

if [ -z "$HARDCODED_SECRETS" ]; then
    echo -e "${GREEN}  => Résultat : Aucun secret évident codé en dur n'a été trouvé.${NC}"
else
    echo -e "${RED}  => ALERTE : Des secrets potentiels ont été trouvés. Vérification manuelle requise :${NC}"
    echo "$HARDCODED_SECRETS"
fi

echo -e "\n${GREEN}--- Audit de sécurité terminé ---${NC}"
