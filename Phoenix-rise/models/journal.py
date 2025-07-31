"""
Modèles de données pour le journal d'humeur et les sessions de coaching.
"""

from dataclasses import dataclass
from typing import List, Dict
from datetime import datetime

@dataclass
class MoodEntry:
    """Entrée d'humeur quotidienne."""
    id: int
    user_id: str
    created_at: str
    mood_score: int          # 1-10
    energy_level: int        # 1-10
    confidence_level: int    # 1-10
    notes: str
    tags: List[str]

@dataclass
class JournalEntry:
    """Entrée de journal avec encouragement IA."""
    id: int
    user_id: str
    created_at: str
    title: str
    content: str
    mood_before: int
    mood_after: int
    ai_encouragement: str

@dataclass
class CoachingSession:
    """Session d'entraînement aux entretiens."""
    id: str
    user_id: str
    created_at: str
    sector: str                    # cybersécurité, développement, etc.
    question: str
    user_response: str
    ai_feedback: Dict
    score: float
