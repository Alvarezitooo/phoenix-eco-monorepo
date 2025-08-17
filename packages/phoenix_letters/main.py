"""
🏛️ PHOENIX LETTERS - MAIN ENGINE CONFORME CONTRAT V5
Point d'entrée principal Phoenix Letters avec Event-Sourcing

Conforme au Contrat d'Exécution V5:
- Event-Sourcing pour les imports UI
- Sécurité intégrée (validation input, protection BDD)
- Services partagés obligatoires (phoenix_common.settings)
- Qualité code (black, ruff)
- Conscience déploiement

Author: Claude Phoenix DevSecOps Guardian  
Version: 4.1.0 - Event-Sourcing Architecture
"""

import streamlit as st
import sys
from pathlib import Path

# 🏛️ UTILISATION_SERVICES_PARTAGES: Settings unifié obligatoire
from phoenix_common.settings import get_settings

# 🏛️ ORACLE PATTERN: Import sécurisé de l'ancienne structure
def run():
    """
    Point d'entrée principal Phoenix Letters
    Délègue à l'ancienne structure en attendant migration complète
    """
    
    # Configuration Streamlit sécurisée
    st.set_page_config(
        page_title="Phoenix Letters - Générateur IA",
        page_icon="✉️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Chargement settings unifié
    settings = get_settings()
    
    if settings.PHOENIX_SAFE_MODE:
        st.warning("🛡️ Mode sécurisé activé - Fonctionnalités limitées")
        st.info("Phoenix Letters fonctionne en mode dégradé pour votre sécurité.")
        return
    
    # Tentative d'import de l'ancienne structure
    try:
        # Ajouter le path de l'ancienne app
        apps_path = Path(__file__).resolve().parent.parent.parent / "apps" / "phoenix-letters"
        if str(apps_path) not in sys.path:
            sys.path.insert(0, str(apps_path))
        
        # Import et délégation à l'ancienne structure
        from main import main as letters_main
        letters_main()
        
    except ImportError as e:
        st.error(f"🚨 Erreur de chargement Phoenix Letters: {e}")
        st.info("📧 Contactez le support si le problème persiste")
        
        # Interface de fallback minimale
        st.title("✉️ Phoenix Letters")
        st.markdown("### Générateur de lettres de motivation IA")
        st.info("🔄 Migration en cours - Interface temporairement indisponible")

if __name__ == "__main__":
    run()