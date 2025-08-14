#!/bin/bash

# 🚀 Phoenix Builder - Générateur de requirements.txt optimisés
# Conforme au Contrat d'Exécution V5 - OPTIMISATION_PLATEFORME

set -e  # Exit on any error

echo "🏗️ Phoenix Builder - Génération requirements.txt optimisés"

# =============================================================
# FONCTION: Générer requirements.txt pour Phoenix Letters
# =============================================================
generate_letters_requirements() {
    echo "📝 Génération requirements.txt pour Phoenix Letters..."
    
    poetry export \
        --only=letters \
        --with=main \
        --without=dev \
        --format=requirements.txt \
        --output=apps/phoenix-letters/requirements.txt \
        --without-hashes
    
    # Ajout des packages Phoenix locaux (Contrat V5)
    echo "" >> apps/phoenix-letters/requirements.txt
    echo "# 📦 Phoenix Packages Partagés (Contrat V5)" >> apps/phoenix-letters/requirements.txt
    echo "-e ../../packages/phoenix_shared_auth" >> apps/phoenix-letters/requirements.txt
    echo "-e ../../packages/phoenix_event_bridge" >> apps/phoenix-letters/requirements.txt
    echo "-e ../../packages/phoenix-shared-models" >> apps/phoenix-letters/requirements.txt
    echo "-e ../../packages/phoenix-shared-db" >> apps/phoenix-letters/requirements.txt
    
    echo "✅ requirements.txt générés pour Phoenix Letters"
}

# =============================================================
# FONCTION: Générer requirements.txt pour Phoenix CV
# =============================================================
generate_cv_requirements() {
    echo "📄 Génération requirements.txt pour Phoenix CV..."
    
    poetry export \
        --only=cv \
        --with=main \
        --without=dev \
        --format=requirements.txt \
        --output=apps/phoenix-cv/requirements.txt \
        --without-hashes
    
    # Ajout des packages Phoenix locaux (Contrat V5)
    echo "" >> apps/phoenix-cv/requirements.txt
    echo "# 📦 Phoenix Packages Partagés (Contrat V5)" >> apps/phoenix-cv/requirements.txt
    echo "-e ../../packages/phoenix_shared_auth" >> apps/phoenix-cv/requirements.txt
    echo "-e ../../packages/phoenix_event_bridge" >> apps/phoenix-cv/requirements.txt
    echo "-e ../../packages/phoenix-shared-models" >> apps/phoenix-cv/requirements.txt
    echo "-e ../../packages/phoenix-shared-db" >> apps/phoenix-cv/requirements.txt
    
    echo "✅ requirements.txt générés pour Phoenix CV"
}

# =============================================================
# FONCTION: Vérifier la validité des requirements
# =============================================================
validate_requirements() {
    echo "🔍 Validation des requirements générés..."
    
    # Vérifier la taille des fichiers (Streamlit Cloud optimisation)
    letters_lines=$(wc -l < apps/phoenix-letters/requirements.txt)
    cv_lines=$(wc -l < apps/phoenix-cv/requirements.txt)
    
    echo "📊 Statistiques:"
    echo "   - Phoenix Letters: $letters_lines lignes"
    echo "   - Phoenix CV: $cv_lines lignes"
    
    if [ $letters_lines -gt 50 ]; then
        echo "⚠️ WARNING: Phoenix Letters a $letters_lines dépendances (recommandé < 50 pour Streamlit Cloud)"
    fi
    
    if [ $cv_lines -gt 50 ]; then
        echo "⚠️ WARNING: Phoenix CV a $cv_lines dépendances (recommandé < 50 pour Streamlit Cloud)"
    fi
    
    echo "✅ Validation terminée"
}

# =============================================================
# EXÉCUTION PRINCIPALE
# =============================================================

case "${1:-all}" in
    letters)
        generate_letters_requirements
        ;;
    cv)
        generate_cv_requirements  
        ;;
    all)
        generate_letters_requirements
        generate_cv_requirements
        validate_requirements
        ;;
    *)
        echo "Usage: $0 {letters|cv|all}"
        echo ""
        echo "Exemples:"
        echo "  $0 letters  # Génère seulement pour Phoenix Letters"
        echo "  $0 cv       # Génère seulement pour Phoenix CV" 
        echo "  $0 all      # Génère pour tous (défaut)"
        exit 1
        ;;
esac

echo ""
echo "🎯 INSTRUCTIONS DE DÉPLOIEMENT STREAMLIT CLOUD:"
echo ""
echo "1️⃣ Pour Phoenix Letters:"
echo "   - Repository: phoenix-eco-monorepo"
echo "   - Branch: main"
echo "   - Main file path: apps/phoenix-letters/main.py"
echo "   - Requirements file: apps/phoenix-letters/requirements.txt"
echo ""
echo "2️⃣ Pour Phoenix CV:"
echo "   - Repository: phoenix-eco-monorepo" 
echo "   - Branch: main"
echo "   - Main file path: apps/phoenix-cv/phoenix_cv/main.py"
echo "   - Requirements file: apps/phoenix-cv/requirements.txt"
echo ""
echo "3️⃣ Variables d'environnement requises:"
echo "   - SUPABASE_URL"
echo "   - SUPABASE_ANON_KEY" 
echo "   - GEMINI_API_KEY"
echo "   - STRIPE_PUBLISHABLE_KEY"
echo ""
echo "✅ Phoenix Builder - Génération terminée avec succès!"