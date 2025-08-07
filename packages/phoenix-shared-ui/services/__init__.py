"""
Services partagés Phoenix UI
"""

# Import du service d'anonymisation
try:
    from .data_anonymizer import DataAnonymizer
except ImportError:
    # Mode dégradé - utilisation du DataAnonymizer de Phoenix Rise
    try:
        from apps.phoenix_rise.phoenix_rise.utils.security import DataAnonymizer
    except ImportError:
        pass