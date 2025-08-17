#!/bin/bash
# tools/check_secrets.sh
# 🛡️ PHASE 3: Audit sécurité des secrets

echo "🛡️ AUDIT SÉCURITÉ - Détection secrets hardcodés"
echo "============================================"

# Dossiers à scanner (scope Phase 3)
SCAN_DIRS="apps/phoenix-cv apps/phoenix-letters apps/phoenix-website packages/"

# Patterns de secrets dangereux
SECRET_PATTERNS=(
    "sk_[a-zA-Z0-9_]{20,}"           # Stripe secret keys
    "pk_test_[a-zA-Z0-9_]{20,}"      # Stripe public test keys
    "pk_live_[a-zA-Z0-9_]{20,}"      # Stripe public live keys
    "AIza[a-zA-Z0-9_]{35}"           # Google API keys
    "ya29\.[a-zA-Z0-9_-]{100,}"      # Google OAuth tokens
    "[a-zA-Z0-9_-]{32,}\.[a-zA-Z0-9_-]{6,}\.[a-zA-Z0-9_-]{27,}" # JWT tokens
    "postgres://[^[:space:]]+:[^[:space:]]+@[^[:space:]]+"       # DB URLs avec creds
    "mongodb://[^[:space:]]+:[^[:space:]]+@[^[:space:]]+"        # MongoDB URLs
    "https://[a-z0-9-]+\.supabase\.co"                          # Supabase URLs hardcodées
)

# Exclusions (fichiers légitimes)
EXCLUDE_PATTERNS=(
    "\.env\.example"
    "\.md$"
    "test_"
    "\.example\."
    "README"
    "GUIDE_"
)

echo "📋 Scanning directories: $SCAN_DIRS"
echo ""

total_violations=0

for pattern in "${SECRET_PATTERNS[@]}"; do
    echo "🔍 Searching pattern: $pattern"
    
    # Construire la commande rg avec exclusions
    exclude_args=""
    for exclude in "${EXCLUDE_PATTERNS[@]}"; do
        exclude_args="$exclude_args --glob !*$exclude*"
    done
    
    # Scanner avec ripgrep
    results=$(eval "rg --type py --type js --type ts --type json '$pattern' $SCAN_DIRS $exclude_args --line-number --no-heading 2>/dev/null")
    
    if [ -n "$results" ]; then
        echo "🚨 SECRETS HARDCODÉS DÉTECTÉS:"
        echo "$results"
        violation_count=$(echo "$results" | wc -l)
        total_violations=$((total_violations + violation_count))
        echo ""
    else
        echo "✅ Aucun secret hardcodé trouvé pour ce pattern"
    fi
    echo ""
done

echo "📊 RÉSUMÉ AUDIT SÉCURITÉ"
echo "========================"
if [ $total_violations -eq 0 ]; then
    echo "✅ AUDIT RÉUSSI: Aucun secret hardcodé détecté"
    echo "✅ Utilisation correcte de phoenix_common.settings"
else
    echo "🚨 AUDIT ÉCHOUÉ: $total_violations secrets hardcodés détectés"
    echo "❌ ACTIONS REQUISES:"
    echo "   1. Migrer vers phoenix_common.settings.get_settings()"
    echo "   2. Utiliser variables d'environnement"
    echo "   3. Retirer secrets du code source"
fi

echo ""
echo "🔧 VÉRIFICATION UTILISATION phoenix_common.settings"
echo "================================================="

# Vérifier utilisation correcte du service centralisé
correct_usage=$(rg --type py "from phoenix_common\.settings import get_settings" $SCAN_DIRS --count 2>/dev/null | awk -F: '{sum += $2} END {print sum+0}')
old_usage=$(rg --type py "os\.environ\.get|st\.secrets" $SCAN_DIRS --count 2>/dev/null | awk -F: '{sum += $2} END {print sum+0}')

echo "✅ Utilisation phoenix_common.settings: $correct_usage occurrences"
echo "⚠️  Accès directs os.environ/st.secrets: $old_usage occurrences"

if [ $old_usage -gt 0 ]; then
    echo ""
    echo "📋 DÉTAIL ACCÈS DIRECTS À MIGRER:"
    rg --type py "os\.environ\.get|st\.secrets" $SCAN_DIRS --line-number --no-heading | head -10
fi

echo ""
echo "🎯 RECOMMANDATIONS"
echo "=================="
echo "1. Utiliser UNIQUEMENT phoenix_common.settings.get_settings()"
echo "2. Tester avec PYTHONPATH=./packages dans tous les environments"
echo "3. Vérifier .env.example mais jamais de .env committé"
echo "4. Activer secrets_migration.py warnings en dev"

exit $total_violations