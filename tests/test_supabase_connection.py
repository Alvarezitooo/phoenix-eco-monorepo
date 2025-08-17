# tests/test_supabase_connection.py
# Test connexion Supabase centralisé

import pytest
from phoenix_common.settings import get_settings

def test_supabase_client_init():
    """Test initialisation client Supabase centralisé"""
    
    settings = get_settings()
    
    # Skip si config Supabase absente (normal en dev local)
    if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
        pytest.skip("Configuration Supabase manquante (normal en dev local)")
    
    try:
        from phoenix_common.clients import get_supabase_client
        client = get_supabase_client()
        
        # Vérifications de base
        assert client is not None
        assert hasattr(client, 'table')
        
        # Test simple de connectivité (doit passer même sans données)
        # Note: on ne fait pas de vraie requête pour éviter dépendances externes
        print("✅ Client Supabase centralisé initialisé correctement")
        
    except Exception as e:
        pytest.fail(f"Échec initialisation client Supabase centralisé: {e}")

def test_supabase_factory_db_connection():
    """Test factory database connection Phoenix Letters"""
    
    settings = get_settings()
    
    if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
        pytest.skip("Configuration Supabase manquante")
    
    try:
        # Test de la factory consolidée Letters
        import sys
        sys.path.append('apps/phoenix-letters')
        
        from infrastructure.database.db_connection import get_database_client
        client = get_database_client()
        
        assert client is not None
        print("✅ Factory database Phoenix Letters OK")
        
    except ImportError:
        pytest.skip("Infrastructure Phoenix Letters non disponible (normal)")
    except Exception as e:
        pytest.fail(f"Factory database client échec: {e}")