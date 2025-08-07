"""
Composants UI partagés Phoenix
"""

# Import des composants principaux
try:
    from .research_consent import ResearchConsentComponent, get_research_ethics_info
except ImportError:
    # Mode dégradé si dépendances manquantes
    pass