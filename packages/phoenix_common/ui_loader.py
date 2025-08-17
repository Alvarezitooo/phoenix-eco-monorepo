"""
🏛️ PHOENIX COMMON - UI Safe Loader
Importeur UI sécurisé réutilisable pour tout l'écosystème Phoenix
Conforme au Contrat d'Exécution V5

Author: Claude Phoenix DevSecOps Guardian  
Version: 4.1.0 - UI Safe Loading
"""

import importlib
import importlib.util
import traceback
import streamlit as st
from typing import Dict, List, Optional, Any

# Global state pour diagnostics UI
UI_ERRORS: Dict[str, str] = {}

def import_ui_safe(module_path: str, names: List[str]) -> List[Optional[Any]]:
    """
    Import sécurisé avec Event-Sourcing conforme Contrat V5
    
    Args:
        module_path: Chemin du module à importer
        names: Liste des attributs à extraire
        
    Returns:
        Liste des objets importés (None si échec)
    """
    
    # Vérification de l'existence du module
    spec = importlib.util.find_spec(module_path)
    if spec is None:
        msg = f"Module introuvable (sys.path): {module_path}"
        UI_ERRORS[module_path] = msg
        
        # 🎯 EVENT-SOURCING: Publication événement d'échec
        _publish_ui_import_failed(module_path, "not_found", msg)
        return [None for _ in names]
    
    # Tentative d'import du module
    try:
        mod = importlib.import_module(module_path)
        out = []
        
        # Extraction des attributs demandés
        for name in names:
            try:
                out.append(getattr(mod, name))
            except AttributeError:
                tb = traceback.format_exc()
                key = f"{module_path}.{name}"
                UI_ERRORS[key] = tb
                
                # 🎯 EVENT-SOURCING: Échec d'attribut
                _publish_ui_import_failed(key, "attr_error", tb)
                out.append(None)
        
        return out
        
    except Exception:
        tb = traceback.format_exc()
        UI_ERRORS[module_path] = tb
        
        # 🎯 EVENT-SOURCING: Échec d'import
        _publish_ui_import_failed(module_path, "import_error", tb)
        return [None for _ in names]

def render_ui_diagnostics_safe():
    """
    Interface diagnostics UI conforme sécurité Contrat V5
    """
    if UI_ERRORS:
        with st.expander("🔍 Diagnostics UI (imports)", expanded=False):
            st.warning("⚠️ Certains composants UI ne sont pas disponibles")
            
            for module_path, error_msg in UI_ERRORS.items():
                st.markdown(f"**❌ {module_path}**")
                st.code(error_msg, language="python")
                
                # 🛡️ SÉCURITÉ: Pas de secrets dans les tracebacks
                if _contains_sensitive_info(error_msg):
                    st.error("🛡️ Erreur contenant des informations sensibles masquée")

def create_ui_fallback(component_name: str, fallback_message: str = None):
    """
    Créer une classe de fallback pour composant UI manquant
    
    Args:
        component_name: Nom du composant
        fallback_message: Message personnalisé
        
    Returns:
        Classe de fallback
    """
    
    message = fallback_message or f"Composant {component_name} indisponible"
    
    class UIFallback:
        @staticmethod
        def render(*args, **kwargs):
            st.info(f"🔗 {message}")
            st.caption("Mode dégradé - composant indisponible")
        
        @staticmethod
        def render_main_nav():
            st.info("🔗 Navigation indisponible en mode dégradé")
        
        @staticmethod
        def render_sidebar_nav():
            pass
        
        @staticmethod
        def render_breadcrumb(pages):
            st.markdown(" → ".join(pages))
    
    UIFallback.__name__ = f"{component_name}Fallback"
    return UIFallback

def get_ui_import_status() -> Dict[str, str]:
    """
    Statut des imports UI pour monitoring
    
    Returns:
        Dict avec statut de chaque import
    """
    if not UI_ERRORS:
        return {"status": "✅ Tous les composants UI disponibles"}
    
    status = {"status": f"⚠️ {len(UI_ERRORS)} erreurs d'import UI"}
    for module, error in UI_ERRORS.items():
        status[module] = "❌ Échec"
    
    return status

def clear_ui_errors():
    """Vider les erreurs UI (utile pour tests)"""
    global UI_ERRORS
    UI_ERRORS.clear()

def _publish_ui_import_failed(module_path: str, reason: str, traceback: str = ""):
    """Publication événement d'échec import UI"""
    try:
        from phoenix_shared_models.events import UIComponentImportFailed
        from phoenix_event_bridge.helpers import publish_event
        
        publish_event(UIComponentImportFailed(
            module_path=module_path,
            reason=reason,
            traceback=traceback
        ))
    except ImportError:
        # Fallback si event sourcing indisponible
        print(f"📡 EVENT (fallback): UIComponentImportFailed - {module_path} - {reason}")

def _contains_sensitive_info(text: str) -> bool:
    """Vérifier si le texte contient des informations sensibles"""
    sensitive_keywords = [
        'password', 'token', 'key', 'secret', 'api_key',
        'stripe_sk', 'supabase_key', 'gemini_api_key'
    ]
    
    return any(keyword in text.lower() for keyword in sensitive_keywords)