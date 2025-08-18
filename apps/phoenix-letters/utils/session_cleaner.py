"""
🧹 Phoenix Letters Session Cleaner - Nettoyage automatique session_state
Prévient le memory bloat et améliore les performances
Version adaptée pour Phoenix Letters
"""

import streamlit as st
from typing import List, Set, Dict, Any
import time
from datetime import datetime, timedelta


class PhoenixLettersSessionCleaner:
    """Nettoyeur de session Phoenix Letters optimisé"""
    
    # Variables critiques à ne JAMAIS nettoyer (spécifiques Letters)
    PROTECTED_KEYS: Set[str] = {
        "user_id",
        "user_email", 
        "is_authenticated",
        "user_tier",
        "current_page",
        "auth_flow",
        "generated_letter",  # Lettre générée
        "optimization_results"  # Résultats d'optimisation
    }
    
    # Variables temporaires à nettoyer après usage (spécifiques Letters)
    TEMPORARY_KEYS: Set[str] = {
        "form_data",
        "generation_progress",
        "upload_state",
        "analysis_results",
        "temp_file_content",
        "processing_status",
        "error_message",
        "success_message",
        "modal_state",
        "loading_state"
    }
    
    # Préfixes de clés temporaires
    TEMP_PREFIXES: List[str] = [
        "temp_",
        "cache_", 
        "loading_",
        "error_",
        "success_",
        "form_",
        "upload_",
        "analysis_",
        "generation_"
    ]
    
    @staticmethod
    def clean_temporary_keys():
        """Nettoie les clés temporaires identifiées"""
        cleaned_count = 0
        
        # Nettoyer les clés temporaires connues
        for key in PhoenixLettersSessionCleaner.TEMPORARY_KEYS:
            if key in st.session_state:
                del st.session_state[key]
                cleaned_count += 1
        
        # Nettoyer les clés avec préfixes temporaires
        keys_to_clean = []
        for key in st.session_state.keys():
            for prefix in PhoenixLettersSessionCleaner.TEMP_PREFIXES:
                if key.startswith(prefix):
                    keys_to_clean.append(key)
                    break
        
        for key in keys_to_clean:
            if key not in PhoenixLettersSessionCleaner.PROTECTED_KEYS:
                del st.session_state[key]
                cleaned_count += 1
        
        return cleaned_count
    
    @staticmethod
    def clean_old_cache_entries(max_age_minutes: int = 30):
        """Nettoie les entrées de cache anciennes"""
        current_time = datetime.now()
        cleaned_count = 0
        
        keys_to_clean = []
        for key, value in st.session_state.items():
            # Chercher les objets avec timestamp
            if isinstance(value, dict) and 'timestamp' in value:
                try:
                    entry_time = datetime.fromisoformat(value['timestamp'])
                    if current_time - entry_time > timedelta(minutes=max_age_minutes):
                        keys_to_clean.append(key)
                except (ValueError, TypeError):
                    # Timestamp invalide, nettoyer
                    keys_to_clean.append(key)
        
        for key in keys_to_clean:
            if key not in PhoenixLettersSessionCleaner.PROTECTED_KEYS:
                del st.session_state[key]
                cleaned_count += 1
        
        return cleaned_count
    
    @staticmethod
    def limit_session_size(max_keys: int = 50):
        """Limite le nombre total de clés en session"""
        current_keys = len(st.session_state.keys())
        
        if current_keys <= max_keys:
            return 0
        
        # Identifier les clés non protégées les plus anciennes
        non_protected_keys = [
            key for key in st.session_state.keys() 
            if key not in PhoenixLettersSessionCleaner.PROTECTED_KEYS
        ]
        
        # Supprimer l'excès (FIFO approximatif)
        keys_to_remove = current_keys - max_keys
        cleaned_count = 0
        
        for key in non_protected_keys[:keys_to_remove]:
            del st.session_state[key]
            cleaned_count += 1
        
        return cleaned_count
    
    @staticmethod
    def smart_cleanup():
        """Nettoyage intelligent combiné"""
        total_cleaned = 0
        cleanup_report = {}
        
        # 1. Nettoyer les clés temporaires
        temp_cleaned = PhoenixLettersSessionCleaner.clean_temporary_keys()
        total_cleaned += temp_cleaned
        cleanup_report["temporary_keys"] = temp_cleaned
        
        # 2. Nettoyer le cache ancien (30 min)
        cache_cleaned = PhoenixLettersSessionCleaner.clean_old_cache_entries(30)
        total_cleaned += cache_cleaned
        cleanup_report["old_cache"] = cache_cleaned
        
        # 3. Limiter la taille totale (50 clés max)
        size_cleaned = PhoenixLettersSessionCleaner.limit_session_size(50)
        total_cleaned += size_cleaned
        cleanup_report["size_limit"] = size_cleaned
        
        # 4. Enregistrer le timestamp du nettoyage
        st.session_state["_last_cleanup"] = datetime.now().isoformat()
        
        return total_cleaned, cleanup_report
    
    @staticmethod
    def auto_cleanup_trigger():
        """Déclenche automatiquement le nettoyage si nécessaire"""
        # Vérifier si nettoyage récent
        last_cleanup = st.session_state.get("_last_cleanup")
        if last_cleanup:
            try:
                last_time = datetime.fromisoformat(last_cleanup)
                if datetime.now() - last_time < timedelta(minutes=10):
                    return False, "Nettoyage récent"
            except (ValueError, TypeError):
                pass
        
        # Déclencher si trop de clés
        if len(st.session_state.keys()) > 40:
            cleaned, report = PhoenixLettersSessionCleaner.smart_cleanup()
            return True, f"Auto-nettoyage: {cleaned} éléments supprimés"
        
        return False, "Aucun nettoyage nécessaire"
    
    @staticmethod
    def get_session_stats() -> Dict[str, Any]:
        """Statistiques de la session"""
        total_keys = len(st.session_state.keys())
        protected_count = sum(1 for k in st.session_state.keys() 
                            if k in PhoenixLettersSessionCleaner.PROTECTED_KEYS)
        temp_count = sum(1 for k in st.session_state.keys() 
                        if k in PhoenixLettersSessionCleaner.TEMPORARY_KEYS)
        
        return {
            "total_keys": total_keys,
            "protected_keys": protected_count,
            "temporary_keys": temp_count,
            "other_keys": total_keys - protected_count - temp_count,
            "memory_usage": f"{total_keys * 50}B (approx)"  # estimation grossière
        }


# Fonction utilitaire pour intégration facile
def cleanup_session():
    """Fonction simple pour nettoyage session"""
    return PhoenixLettersSessionCleaner.smart_cleanup()


def auto_cleanup():
    """Fonction d'auto-nettoyage à appeler en début d'app"""
    return PhoenixLettersSessionCleaner.auto_cleanup_trigger()