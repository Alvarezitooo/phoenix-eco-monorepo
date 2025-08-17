# packages/phoenix_common/secrets_migration.py
# 🏛️ ORACLE PATTERN: Migration progressive des accès secrets vers centralisé

import os
import logging
import warnings
from typing import Optional, Any

logger = logging.getLogger(__name__)

class SecretsDeprecationWarning(UserWarning):
    """Warning pour utilisation déprécée des secrets"""
    pass

def get_secret_with_migration_warning(
    key: str, 
    default: Optional[str] = None,
    caller_file: str = "unknown"
) -> Optional[str]:
    """
    Récupère un secret avec warning de migration
    
    Args:
        key: Clé du secret
        default: Valeur par défaut si secret absent
        caller_file: Fichier appelant pour traçabilité
        
    Returns:
        Valeur du secret ou default
    """
    
    # Émettre warning de dépréciation
    warnings.warn(
        f"DEPRECATION: Direct secret access from {caller_file} for key '{key}'. "
        f"Please migrate to phoenix_common.settings.get_settings().{key.upper()}",
        SecretsDeprecationWarning,
        stacklevel=2
    )
    
    logger.warning(f"🚨 Direct secret access detected: {key} from {caller_file}")
    
    # Tenter d'abord le service centralisé
    try:
        from phoenix_common.settings import get_settings
        settings = get_settings()
        
        # Mapping des clés anciennes vers nouvelles
        key_mapping = {
            "SUPABASE_URL": "SUPABASE_URL",
            "SUPABASE_KEY": "SUPABASE_KEY", 
            "GOOGLE_API_KEY": "GEMINI_API_KEY",
            "GEMINI_API_KEY": "GEMINI_API_KEY",
            "STRIPE_PK": "STRIPE_PK",
            "STRIPE_SK": "STRIPE_SK",
            "DEV_MODE": "DEV_MODE"
        }
        
        mapped_key = key_mapping.get(key, key)
        value = getattr(settings, mapped_key, None)
        
        if value:
            logger.info(f"✅ Secret {key} retrieved via centralized service")
            return value
            
    except Exception as e:
        logger.warning(f"⚠️ Centralized settings unavailable, falling back to direct access: {e}")
    
    # Fallback vers accès direct (legacy)
    value = os.environ.get(key, default)
    logger.warning(f"🔄 Fallback direct access for {key}")
    
    return value

def patch_os_environ_for_migration():
    """
    Patch os.environ.get pour émettre des warnings automatiquement
    À utiliser temporairement pour identifier tous les accès directs
    """
    
    original_get = os.environ.get
    
    def patched_get(key: str, default=None):
        """Version patchée qui warn sur accès direct aux secrets Phoenix"""
        
        # Secrets Phoenix qui doivent être centralisés
        phoenix_secrets = [
            "SUPABASE_URL", "SUPABASE_KEY", 
            "GOOGLE_API_KEY", "GEMINI_API_KEY",
            "STRIPE_PK", "STRIPE_SK",
            "JWT_SECRET_KEY", "JWT_ALGORITHM"
        ]
        
        if key in phoenix_secrets:
            import inspect
            frame = inspect.currentframe()
            caller_file = "unknown"
            
            try:
                caller_frame = frame.f_back
                if caller_frame:
                    caller_file = caller_frame.f_code.co_filename
            finally:
                del frame
            
            return get_secret_with_migration_warning(key, default, caller_file)
        
        # Accès normal pour autres variables
        return original_get(key, default)
    
    # Appliquer le patch
    os.environ.get = patched_get
    logger.info("🔧 os.environ.get patched for Phoenix secrets migration")

# Helper pour streamlit secrets
def get_streamlit_secret_with_warning(secrets_path: str, default: Any = None, caller_file: str = "unknown"):
    """
    Wrapper pour st.secrets avec warning de migration
    
    Args:
        secrets_path: Chemin du secret dans st.secrets (ex: "app.website_url")
        default: Valeur par défaut
        caller_file: Fichier appelant
        
    Returns:
        Valeur du secret ou default
    """
    
    warnings.warn(
        f"DEPRECATION: Direct st.secrets access from {caller_file} for path '{secrets_path}'. "
        f"Please migrate to phoenix_common.settings.get_settings()",
        SecretsDeprecationWarning,
        stacklevel=2
    )
    
    try:
        import streamlit as st
        
        # Navigation dans st.secrets selon le path
        current = st.secrets
        for part in secrets_path.split('.'):
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return default
        
        return current
        
    except Exception as e:
        logger.warning(f"⚠️ Streamlit secrets access failed for {secrets_path}: {e}")
        return default

# Utilitaires pour faciliter la migration
class SecretsMigrationHelper:
    """Helper pour faciliter la migration des secrets"""
    
    @staticmethod
    def scan_file_for_direct_access(file_path: str) -> list:
        """
        Scanne un fichier pour détecter les accès directs aux secrets
        
        Returns:
            Liste des violations détectées
        """
        violations = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            lines = content.split('\n')
            
            patterns = [
                'os.environ.get(',
                'st.secrets.get(',
                'st.secrets[',
                'os.getenv('
            ]
            
            for line_num, line in enumerate(lines, 1):
                for pattern in patterns:
                    if pattern in line and not line.strip().startswith('#'):
                        violations.append({
                            'file': file_path,
                            'line': line_num,
                            'content': line.strip(),
                            'pattern': pattern
                        })
                        
        except Exception as e:
            logger.error(f"❌ Error scanning {file_path}: {e}")
            
        return violations
    
    @staticmethod
    def generate_migration_report(base_path: str) -> dict:
        """
        Génère un rapport complet des migrations nécessaires
        
        Returns:
            Dictionnaire avec le rapport de migration
        """
        import os
        import glob
        
        report = {
            'total_files_scanned': 0,
            'files_with_violations': 0,
            'total_violations': 0,
            'violations_by_pattern': {},
            'files_details': []
        }
        
        # Scanner tous les fichiers Python dans apps/
        pattern = os.path.join(base_path, 'apps', '**', '*.py')
        python_files = glob.glob(pattern, recursive=True)
        
        for file_path in python_files:
            report['total_files_scanned'] += 1
            
            violations = SecretsMigrationHelper.scan_file_for_direct_access(file_path)
            
            if violations:
                report['files_with_violations'] += 1
                report['total_violations'] += len(violations)
                
                file_detail = {
                    'file_path': file_path,
                    'violations_count': len(violations),
                    'violations': violations
                }
                report['files_details'].append(file_detail)
                
                # Comptage par pattern
                for violation in violations:
                    pattern = violation['pattern']
                    if pattern not in report['violations_by_pattern']:
                        report['violations_by_pattern'][pattern] = 0
                    report['violations_by_pattern'][pattern] += 1
        
        return report