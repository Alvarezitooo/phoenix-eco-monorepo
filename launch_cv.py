"""
🚀 Phoenix CV - Point d'Entrée Monorepo
Implémentation de la vision stratégique avec AuthManager unifié
et imports propres selon l'architecture définie

Author: Claude Phoenix DevSecOps Guardian
Version: 1.0.0 - Strategic Vision Implementation
"""

import sys
import os
from pathlib import Path

# Configuration PYTHONPATH pour monorepo Poetry
ROOT_DIR = Path(__file__).resolve().parent

# Ajouter racine monorepo pour imports packages partagés
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Ajouter dossier app phoenix-cv
APP_ROOT = ROOT_DIR / "apps" / "phoenix-cv"
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

# Configuration environnement pour Supabase et Stripe
os.environ.setdefault("SUPABASE_URL", os.getenv("SUPABASE_URL", ""))
os.environ.setdefault("SUPABASE_ANON_KEY", os.getenv("SUPABASE_ANON_KEY", ""))
os.environ.setdefault("STRIPE_SECRET_KEY", os.getenv("STRIPE_SECRET_KEY", ""))
os.environ.setdefault("STRIPE_PUBLISHABLE_KEY", os.getenv("STRIPE_PUBLISHABLE_KEY", ""))

print("✅ Phoenix CV - Environnement monorepo configuré")
print(f"📂 Racine: {ROOT_DIR}")
print(f"📱 App: {APP_ROOT}")

try:
    # Import du service d'authentification unifié selon vision stratégique
    from packages.phoenix_shared_auth.client import get_auth_manager
    auth_manager = get_auth_manager()
    print("✅ AuthManager unifié initialisé")
    
    # Import de la fonction main de Phoenix CV
    from phoenix_cv.main import main
    print("✅ Module Phoenix CV importé")
    
    if __name__ == "__main__":
        print("🚀 Lancement de Phoenix CV avec authentification unifiée...")
        main()

except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
    print("🔄 Fallback vers mode standalone...")
    
    # Fallback: essayer sans packages partagés
    try:
        import streamlit as st
        from phoenix_cv.main import main
        
        st.warning("⚠️ Mode standalone - Services partagés non disponibles")
        print("🔄 Phoenix CV en mode standalone")
        
        if __name__ == "__main__":
            main()
            
    except Exception as fallback_error:
        import streamlit as st
        st.error("❌ Erreur critique lors du chargement de Phoenix CV")
        st.code(f"Erreur: {str(fallback_error)}")
        st.info("💡 Vérifiez la configuration des secrets Streamlit")
        print(f"❌ Erreur fallback: {fallback_error}")

except Exception as e:
    print(f"❌ Erreur inattendue: {e}")
    
    try:
        import streamlit as st
        st.error("❌ Une erreur est survenue lors du chargement de Phoenix CV")
        st.exception(e)
        
        with st.expander("🔍 Informations de débogage"):
            st.code(f"""
            Racine monorepo: {ROOT_DIR}
            App Phoenix CV: {APP_ROOT}
            Erreur: {str(e)}
            PYTHONPATH: {sys.path[:5]}
            """)
    except:
        print("❌ Impossible d'afficher l'interface Streamlit")
        raise e