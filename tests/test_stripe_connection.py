# tests/test_stripe_connection.py
# Test connexion Stripe centralisé

import pytest
from phoenix_common.settings import get_settings

def test_stripe_client_init():
    """Test initialisation client Stripe centralisé"""
    
    settings = get_settings()
    
    # Skip si config Stripe absente (normal en dev local)
    if not settings.STRIPE_PK or not settings.STRIPE_SK:
        pytest.skip("Configuration Stripe manquante (normal en dev local)")
    
    try:
        from phoenix_common.clients import get_stripe_client
        stripe = get_stripe_client()
        
        # Vérifications de base
        assert stripe is not None
        assert hasattr(stripe, 'api_key')
        
        print("✅ Client Stripe centralisé initialisé correctement")
        
    except Exception as e:
        pytest.fail(f"Échec initialisation client Stripe centralisé: {e}")

def test_stripe_utils_functions():
    """Test fonctions utilitaires Stripe"""
    
    try:
        from phoenix_common.stripe_utils import test_stripe_connection
        
        # La fonction doit être disponible même si config manque
        assert callable(test_stripe_connection)
        print("✅ Utilitaires Stripe disponibles")
        
    except ImportError as e:
        pytest.fail(f"Utilitaires Stripe non importables: {e}")

def test_stripe_webhook_verification():
    """Test vérification webhook Stripe"""
    
    try:
        from phoenix_common.security import verify_stripe_webhook
        
        # Test avec données fictives (doit retourner False)
        result = verify_stripe_webhook(b"test", "invalid_signature")
        assert result is False
        
        print("✅ Vérification webhook Stripe disponible")
        
    except ImportError as e:
        pytest.fail(f"Sécurité Stripe non importable: {e}")