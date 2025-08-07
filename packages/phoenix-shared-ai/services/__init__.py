"""
Services d'IA partagés Phoenix
"""

# Import des services principaux pour faciliter les imports
try:
    from .nlp_tagger import EthicalNLPTagger, batch_analyze_notes, get_aggregated_insights
except ImportError:
    # Mode dégradé si dépendances manquantes
    pass