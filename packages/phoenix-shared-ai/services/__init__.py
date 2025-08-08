"""
Services d'IA partagés Phoenix
"""

# Import des services principaux pour faciliter les imports
try:
    from .nlp_tagger import EthicalNLPTagger, batch_analyze_notes, get_aggregated_insights
except ImportError:
    # Mode dégradé si dépendances manquantes
    pass

# ✅ Import optimiseur cache Gemini
from .gemini_cache_optimizer import (
    GeminiCacheOptimizer,
    CacheEntry,
    CachePriority,
    get_cache_optimizer,
    cache_gemini_call
)

__all__ = [
    "EthicalNLPTagger",
    "batch_analyze_notes", 
    "get_aggregated_insights",
    "GeminiCacheOptimizer",
    "CacheEntry", 
    "CachePriority",
    "get_cache_optimizer",
    "cache_gemini_call"
]