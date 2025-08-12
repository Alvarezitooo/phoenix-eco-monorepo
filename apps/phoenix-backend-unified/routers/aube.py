"""
Router Phoenix Aube - Diagnostic et exploration carrière
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

from routers.auth import get_current_user
from services.supabase_client import SupabaseClient

router = APIRouter()

# Schemas Pydantic pour Aube
class DiagnosticQuestion(BaseModel):
    id: str
    question: str
    answer: str
    category: str

class DiagnosticSubmission(BaseModel):
    responses: List[DiagnosticQuestion]
    completion_time: int  # en secondes

class CareerMatch(BaseModel):
    title: str
    match_score: int
    ai_resilience: int
    description: str
    skills_required: List[str]
    growth_potential: str

class DiagnosticResult(BaseModel):
    user_id: str
    personality_profile: Dict[str, Any]
    career_matches: List[CareerMatch]
    recommendations: List[str]
    ai_insights: Dict[str, Any]

# Dependency
async def get_supabase() -> SupabaseClient:
    """Dependency pour récupérer le client Supabase"""
    from main import supabase_client
    if not supabase_client:
        raise HTTPException(
            status_code=500,
            detail="Supabase client not initialized"
        )
    return supabase_client

# Routes Phoenix Aube
@router.post("/diagnostic/submit")
async def submit_diagnostic(
    submission: DiagnosticSubmission,
    current_user: Dict[str, Any] = Depends(get_current_user),
    supabase: SupabaseClient = Depends(get_supabase)
):
    """Soumission d'un diagnostic carrière"""
    try:
        # Analyser les réponses (ici simulation)
        personality_profile = _analyze_responses(submission.responses)
        career_matches = _generate_career_matches(personality_profile)
        recommendations = _generate_recommendations(personality_profile, career_matches)
        
        # Sauvegarder en base
        exploration_data = {
            "responses": [r.dict() for r in submission.responses],
            "completion_time": submission.completion_time,
            "personality_profile": personality_profile,
            "career_matches": [m.dict() for m in career_matches],
            "recommendations": recommendations
        }
        
        result = await supabase.save_career_exploration(
            current_user["id"], 
            exploration_data
        )
        
        return DiagnosticResult(
            user_id=current_user["id"],
            personality_profile=personality_profile,
            career_matches=career_matches,
            recommendations=recommendations,
            ai_insights={
                "analysis_version": "1.0",
                "confidence_score": 0.85,
                "processing_time": submission.completion_time
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'analyse du diagnostic: {str(e)}"
        )

@router.get("/career/matches/{user_id}")
async def get_career_matches(
    user_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    supabase: SupabaseClient = Depends(get_supabase)
):
    """Récupérer les matches carrière d'un utilisateur"""
    if current_user["id"] != user_id and not current_user.get("isPremium"):
        raise HTTPException(
            status_code=403,
            detail="Accès non autorisé"
        )
    
    try:
        # Récupérer depuis Supabase (simulation)
        matches = [
            CareerMatch(
                title="Coach en transformation digitale",
                match_score=92,
                ai_resilience=85,
                description="Accompagnement des entreprises dans leur transformation numérique",
                skills_required=["Communication", "Leadership", "Tech"],
                growth_potential="Très élevé"
            ),
            CareerMatch(
                title="Consultant en conduite du changement",
                match_score=88,
                ai_resilience=90,
                description="Facilitation des changements organisationnels",
                skills_required=["Analyse", "Empathie", "Stratégie"],
                growth_potential="Élevé"
            )
        ]
        
        return {"matches": matches}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération des matches: {str(e)}"
        )

@router.post("/events")
async def track_event(
    event_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Tracking d'événements pour Phoenix Aube"""
    try:
        # Log de l'événement (à améliorer avec un vrai système)
        event_data.update({
            "user_id": current_user["id"],
            "timestamp": "now()",
            "app_source": "phoenix-aube"
        })
        
        return {"status": "event_tracked", "event": event_data}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du tracking: {str(e)}"
        )

# Fonctions utilitaires
def _analyze_responses(responses: List[DiagnosticQuestion]) -> Dict[str, Any]:
    """Analyse les réponses du diagnostic"""
    # Simulation d'analyse IA
    return {
        "dominant_traits": ["Créatif", "Analytique", "Leader"],
        "personality_type": "ENFP",
        "strengths": ["Innovation", "Communication", "Adaptabilité"],
        "growth_areas": ["Organisation", "Patience", "Détail"],
        "confidence_score": 0.87
    }

def _generate_career_matches(personality: Dict[str, Any]) -> List[CareerMatch]:
    """Génère des matches carrière basés sur la personnalité"""
    return [
        CareerMatch(
            title="Coach en transformation digitale",
            match_score=92,
            ai_resilience=85,
            description="Accompagnement des entreprises dans leur transformation numérique",
            skills_required=["Communication", "Leadership", "Tech"],
            growth_potential="Très élevé"
        ),
        CareerMatch(
            title="Product Owner",
            match_score=85,
            ai_resilience=75,
            description="Gestion de produits numériques et coordination équipes",
            skills_required=["Agilité", "Vision", "Communication"],
            growth_potential="Élevé"
        )
    ]

def _generate_recommendations(personality: Dict[str, Any], matches: List[CareerMatch]) -> List[str]:
    """Génère des recommandations personnalisées"""
    return [
        "Développez vos compétences en leadership pour maximiser votre potentiel",
        "Explorez les certifications en transformation digitale",
        "Renforcez votre réseau professionnel dans le domaine du coaching"
    ]