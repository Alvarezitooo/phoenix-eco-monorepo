"""
Entité métier pour les lettres de motivation.
🏛️ CONSOLIDATION: Import modèles depuis phoenix-shared-models
"""

from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

# 🏛️ CONSOLIDATION: Utilisation modèles partagés
try:
    from phoenix_shared_models import Letter as SharedLetter
except ImportError:
    # Fallback si package non disponible
    SharedLetter = None



class ToneType(Enum):
    """Types de ton pour la lettre."""

    FORMAL = "formel"
    DYNAMIC = "dynamique"
    SOBER = "sobre"
    CREATIVE = "créatif"
    STARTUP = "startup"
    ASSOCIATIVE = "associatif"


class UserTier(Enum):
    """Niveaux d'abonnement utilisateur."""

    FREE = "free"
    PREMIUM = "premium"


@dataclass(frozen=True)
class GenerationRequest:
    """Requête de génération de lettre."""

    cv_content: str
    job_offer_content: str
    job_title: str
    company_name: str
    tone: ToneType
    user_tier: UserTier
    is_career_change: bool = False
    old_domain: Optional[str] = None
    new_domain: Optional[str] = None
    transferable_skills: Optional[str] = None
    company_insights: Optional[Dict[str, Any]] = None
    offer_details: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Validation des données."""
        if self.is_career_change and (not self.old_domain or not self.new_domain):
            raise ValueError("Career change requires old_domain and new_domain")


# 🏛️ CONSOLIDATION: Utilisation du modèle partagé avec extension
if SharedLetter:
    # Héritage du modèle partagé
    @dataclass  
    class Letter(SharedLetter):
        """Entité lettre de motivation étendue."""
        generation_request: Optional[GenerationRequest] = None
        
        def __post_init__(self):
            """Validation de la lettre."""
            if not self.user_id:
                raise ValueError("User ID is required")
else:
    # Fallback si modèle partagé indisponible
    @dataclass
    class Letter:
        """Entité lettre de motivation (fallback)."""
        content: str
        generation_request: GenerationRequest
        created_at: datetime
        user_id: str
        quality_score: Optional[float] = None

        def __post_init__(self):
            """Validation de la lettre."""
            if not self.user_id:
                raise ValueError("User ID is required")


@dataclass
class LetterAnalysis:
    """Analyse de la lettre générée."""

    letter_id: str
    ats_score: float
    readability_score: float
    keyword_match_score: float
    suggestions: list[str]
    strengths: list[str]
    improvements: list[str]


@dataclass
class CompanyCulture:
    """Analyse de la culture d'entreprise - Mirror Match."""

    company_name: str
    industry: str
    company_size: Optional[str] = None
    values: list[str] = None
    communication_style: str = "formal"  # formal, casual, innovative, traditional
    work_environment: str = "traditional"  # startup, corporate, remote, hybrid
    tone_recommendations: list[str] = None
    cultural_keywords: list[str] = None
    leadership_style: str = "hierarchical"  # flat, hierarchical, collaborative
    innovation_level: str = "moderate"  # conservative, moderate, innovative
    confidence_score: float = 0.0  # 0-1 score de confiance de l'analyse

    def to_dict(self):
        return asdict(self)


@dataclass
class SmartCoachFeedback:
    """Feedback IA temps réel - Smart Coach."""

    letter_content: str
    overall_score: float  # 0-100
    clarity_score: float
    impact_score: float
    personalization_score: float
    professional_tone_score: float
    specific_suggestions: list[
        Dict[str, str]
    ]  # {"type": "improvement", "text": "...", "priority": "high"}
    positive_points: list[str]
    critical_issues: list[str]
    next_steps: list[str]
    estimated_read_time: int  # en secondes

    def to_dict(self):
        return asdict(self)


@dataclass
class TrajectoryStep:
    """Étape d'un plan de reconversion."""

    step_number: int
    title: str
    description: str
    duration_weeks: int
    priority: str  # critical, important, optional
    resources: list[str]
    milestones: list[str]
    skills_to_develop: list[str]

    def to_dict(self):
        return asdict(self)


@dataclass
class ReconversionPlan:
    """Plan de reconversion personnalisé - Trajectory Builder."""

    user_id: str
    current_role: str
    target_role: str
    current_skills: list[str]
    target_skills: list[str]
    skill_gaps: list[str]
    trajectory_steps: list[TrajectoryStep]
    estimated_duration_months: int
    difficulty_level: str  # easy, moderate, challenging, expert
    success_probability: float  # 0-1
    recommended_resources: list[
        Dict[str, str]
    ]  # {"type": "course|book|certification", "name": "...", "url": "..."}
    industry_insights: Dict[str, Any]
    created_at: datetime
    last_updated: datetime

    def to_dict(self):
        return asdict(self)


@dataclass
class ATSAnalysis:
    """Analyse ATS - Optimisation mots-clés."""

    letter_content: str
    job_keywords: list[str]
    matched_keywords: list[str]
    missing_keywords: list[str]
    keyword_density: Dict[str, float]
    ats_compatibility_score: float  # 0-100
    formatting_score: float  # Structure, lisibilité ATS
    recommendations: list[str]
    optimized_suggestions: Dict[str, str]  # {"original": "improved"}
    industry_specific_terms: list[str]
    action_verbs_score: float
    quantifiable_achievements_count: int

    def to_dict(self):
        return asdict(self)
