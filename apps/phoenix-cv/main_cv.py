"""
🚀 Phoenix CV - Point d'Entrée Dédié
Implémentation avec requirements minimaux et imports optimisés

Author: Claude Phoenix DevSecOps Guardian  
Version: 1.0.0 - Optimized Dependencies
"""

import sys
import os
from pathlib import Path

# Configuration PYTHONPATH pour monorepo
ROOT_DIR = Path(__file__).resolve().parent.parent.parent

# Ajouter packages partagés
PACKAGES_PATH = ROOT_DIR / "packages"
if str(PACKAGES_PATH) not in sys.path:
    sys.path.insert(0, str(PACKAGES_PATH))

# Configuration environnement
os.environ.setdefault("SUPABASE_URL", os.getenv("SUPABASE_URL", ""))
os.environ.setdefault("SUPABASE_ANON_KEY", os.getenv("SUPABASE_ANON_KEY", ""))
os.environ.setdefault("STRIPE_SECRET_KEY", os.getenv("STRIPE_SECRET_KEY", ""))
os.environ.setdefault("STRIPE_PUBLISHABLE_KEY", os.getenv("STRIPE_PUBLISHABLE_KEY", ""))

# Import de l'application principale
try:
    from phoenix_cv.main import main
    
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    import streamlit as st
    st.error(f"❌ Erreur import Phoenix CV: {e}")
    st.info("🔧 Vérifier l'installation des dépendances")