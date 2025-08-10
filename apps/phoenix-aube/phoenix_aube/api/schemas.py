"""
Schémas Pydantic pour API requests/responses
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime

# =============================================
# REQUEST SCHEMAS
# =============================================

class JobResilienceRequest(BaseModel):
    """Requête d'analyse de résistance IA d'un métier"""
    job_title: str = Field(..., description="Titre du métier à analyser")
    user_context: Optional[Dict[str, Any]] = Field(
        None, description="Contexte utilisateur pour personnalisation"
    )
    include_explanations: bool = Field(
        True, description="Inclure explications détaillées"
    )

class AnxietyScoreRequest(BaseModel):
    """Requête de calcul du score d'anxiété IA"""
    current_job: str = Field(..., description="Métier actuel de l'utilisateur")
    user_id: Optional[str] = Field(None, description="ID utilisateur si connecté")
    context: Optional[Dict[str, Any]] = Field(
        None, description="Contexte additionnel"
    )

class ExplorationStartRequest(BaseModel):
    """Requête de démarrage d'exploration métier"""
    user_id: str = Field(..., description="Identifiant utilisateur")
    current_job: Optional[str] = Field(None, description="Métier actuel")
    motivation: List[str] = Field(
        default=[], description="Motivations de reconversion"
    )
    constraints: Optional[Dict[str, Any]] = Field(
        None, description="Contraintes (géographiques, salariales, etc.)"
    )

class ProfileAssessmentRequest(BaseModel):
    """Requête d'évaluation de profil psychométrique"""
    user_id: str
    big_five_responses: Dict[str, int] = Field(
        ..., description="Réponses test Big Five"
    )
    riasec_responses: Dict[str, int] = Field(
        ..., description="Réponses test RIASEC"
    )
    values_assessment: List[str] = Field(
        ..., description="Valeurs profondes identifiées"
    )

# =============================================
# RESPONSE SCHEMAS
# =============================================

class CareerRecommendationResponse(BaseModel):
    """Réponse de recommandation métier simplifiée"""
    job_title: str
    compatibility_score: float = Field(..., ge=0, le=1)
    sector: str
    justification: str
    ia_resilience_score: float = Field(..., ge=0, le=1)
    
    # Informations additionnelles
    required_skills: List[str] = Field(default=[])
    training_recommendations: List[str] = Field(default=[])
    average_salary: Optional[str] = None
    
    # Métadonnées
    generated_at: datetime = Field(default_factory=datetime.now)

class ExplorationStatusResponse(BaseModel):
    """Statut d'une exploration en cours"""
    exploration_id: str
    user_id: str
    status: str  # "started", "profile_completed", "recommendations_ready", "completed"
    progress_percentage: float = Field(..., ge=0, le=100)
    
    # Étapes complétées
    steps_completed: List[str] = Field(default=[])
    current_step: str
    next_step: Optional[str] = None
    
    # Résultats partiels
    preliminary_insights: Optional[Dict[str, Any]] = None
    
    # Timeline
    started_at: datetime
    estimated_completion: Optional[datetime] = None
    last_activity: datetime = Field(default_factory=datetime.now)

class EcosystemTransitionResponse(BaseModel):
    """Réponse de préparation de transition écosystème"""
    transition_id: str
    target_app: str
    chosen_career: str
    
    # URLs et contexte
    transition_url: str
    context_data: Dict[str, Any]
    
    # Instructions utilisateur
    instructions: List[str] = Field(default=[])
    benefits: List[str] = Field(default=[])
    
    # Métadonnées
    prepared_at: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None

class MetricsResponse(BaseModel):
    """Métriques business Phoenix Aube"""
    
    # Métriques d'usage
    analyses_completed_today: int
    explorations_started_today: int
    career_choices_made_today: int
    ecosystem_transitions_today: int
    
    # Métriques qualité
    average_satisfaction_score: float
    completion_rate: float  # % explorations complétées
    
    # Top insights
    most_analyzed_jobs: List[Dict[str, Any]]
    most_chosen_careers: List[Dict[str, Any]]
    highest_resilience_jobs: List[Dict[str, Any]]
    
    # Timeline
    period: str = "24h"
    generated_at: datetime = Field(default_factory=datetime.now)

# =============================================
# ERROR SCHEMAS
# =============================================

class ErrorResponse(BaseModel):
    """Réponse d'erreur standardisée"""
    error_code: str
    error_message: str
    details: Optional[Dict[str, Any]] = None
    suggestions: List[str] = Field(default=[])
    timestamp: datetime = Field(default_factory=datetime.now)

# =============================================
# PAGINATION & FILTERING
# =============================================

class PaginationParams(BaseModel):
    """Paramètres de pagination"""
    page: int = Field(1, ge=1)
    size: int = Field(20, ge=1, le=100)

class FilterParams(BaseModel):
    """Paramètres de filtrage"""
    sector: Optional[str] = None
    resilience_min: Optional[float] = Field(None, ge=0, le=1)
    compatibility_min: Optional[float] = Field(None, ge=0, le=1)
    skills_required: Optional[List[str]] = None