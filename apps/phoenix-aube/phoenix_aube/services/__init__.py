"""
Services layer - Business Logic Phoenix Aube
"""

from .ia_validator import IAFutureValidator
# Lazy/optional imports; keep explicit exports minimal for tests
try:
    from .exploration_engine import ExplorationEngine  # type: ignore
except Exception:
    ExplorationEngine = None  # type: ignore
try:
    from .recommendation_engine import RecommendationEngine  # type: ignore
except Exception:
    RecommendationEngine = None  # type: ignore

__all__ = [
    "IAFutureValidator",
    "ExplorationEngine",
    "RecommendationEngine",
]