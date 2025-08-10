"""
🔮 Phoenix Aube - FastAPI Application
API REST pour exploration métier + validation IA future-proof
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import logging
from typing import Dict, Any, List
import os

from ..core.models import AnalyseRésilienceIA, ParcoursExploration
from ..core import TransparencyEngine, PhoenixAubeEventStore, PhoenixAubeOrchestrator
from ..services.ia_validator import IAFutureValidator
from .schemas import (
    JobResilienceRequest, AnxietyScoreRequest, 
    ExplorationStartRequest, CareerRecommendationResponse
)
from .dependencies import get_ia_validator, get_current_user

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global services
ia_validator = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestionnaire du cycle de vie de l'application"""
    # Startup
    logger.info("🔮 Phoenix Aube API - Starting up...")
    
    global ia_validator
    # Mock providers pour MVP
    from ..utils.mock_providers import MockEventStore, MockResearchProvider
    
    event_store = MockEventStore()
    research_provider = MockResearchProvider()
    ia_validator = IAFutureValidator(event_store, research_provider)
    
    logger.info("✅ Phoenix Aube API - Ready to serve!")
    
    yield
    
    # Shutdown
    logger.info("🔮 Phoenix Aube API - Shutting down...")

# Application FastAPI
app = FastAPI(
    title="Phoenix Aube API",
    description="Premier outil européen d'exploration métier + validation IA future-proof",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Middleware de sécurité
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # À configurer pour production
)

# Security
security = HTTPBearer()

# =============================================
# ENDPOINTS VALIDATION IA (CŒUR INNOVATION)
# =============================================

@app.post("/api/v1/analyze/job-resilience", response_model=AnalyseRésilienceIA)
async def analyze_job_resilience(
    request: JobResilienceRequest,
    background_tasks: BackgroundTasks,
    validator: IAFutureValidator = Depends(get_ia_validator)
) -> AnalyseRésilienceIA:
    """
    🔮 Analyse de résistance IA pour un métier
    CŒUR DE L'INNOVATION PHOENIX AUBE
    """
    try:
        logger.info(f"Analyse IA demandée pour: {request.job_title}")
        
        # Analyse principale
        analysis = await validator.évaluer_résistance_métier(request.job_title)
        
        # Analytics en arrière-plan
        background_tasks.add_task(
            track_analysis_request,
            request.job_title,
            analysis.score_résistance_ia,
            request.user_context
        )
        
        logger.info(f"Analyse complétée - Score: {analysis.score_résistance_ia:.2f}")
        return analysis
        
    except Exception as e:
        logger.error(f"Erreur analyse IA: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Analyse failed: {str(e)}"
        )

@app.post("/api/v1/analyze/anxiety-score")
async def calculate_anxiety_score(
    request: AnxietyScoreRequest,
    validator: IAFutureValidator = Depends(get_ia_validator)
) -> Dict[str, Any]:
    """
    🧠 Calcul score d'anxiété IA (feature freemium)
    """
    try:
        anxiety_analysis = await validator.calculer_score_anxiété_ia(
            request.current_job
        )
        
        logger.info(f"Score anxiété calculé: {anxiety_analysis['score_anxiété']:.2f}")
        return anxiety_analysis
        
    except Exception as e:
        logger.error(f"Erreur calcul anxiété: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Anxiety calculation failed: {str(e)}"
        )

@app.get("/api/v1/analyze/sector/{sector_name}")
async def analyze_sector_evolution(
    sector_name: str,
    horizon_years: int = 10,
    validator: IAFutureValidator = Depends(get_ia_validator)
) -> Dict[str, Any]:
    """
    📊 Analyse évolution d'un secteur face à l'IA
    """
    try:
        sector_analysis = await validator.prédire_évolution_secteur(
            sector_name, horizon_années=horizon_years
        )
        
        return sector_analysis
        
    except Exception as e:
        logger.error(f"Erreur analyse secteur: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Sector analysis failed: {str(e)}"
        )

# =============================================
# ENDPOINTS EXPLORATION MÉTIER (TEMPS 1)
# =============================================

@app.post("/api/v1/exploration/start")
async def start_career_exploration(
    request: ExplorationStartRequest,
    background_tasks: BackgroundTasks,
    # current_user = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    🚀 Démarre une nouvelle exploration métier
    """
    try:
        # TODO: Implémenter ExplorationEngine
        exploration_id = "temp_" + request.user_id[:8]
        
        logger.info(f"Nouvelle exploration démarrée: {exploration_id}")
        
        return {
            "exploration_id": exploration_id,
            "status": "started",
            "next_step": "profile_assessment",
            "message": "Exploration métier démarrée ! 🔮"
        }
        
    except Exception as e:
        logger.error(f"Erreur démarrage exploration: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Exploration start failed: {str(e)}"
        )

@app.get("/api/v1/exploration/{exploration_id}/recommendations")
async def get_career_recommendations(
    exploration_id: str,
    # current_user = Depends(get_current_user)
) -> List[CareerRecommendationResponse]:
    """
    🎯 Récupère les recommandations métiers
    """
    try:
        # TODO: Implémenter RecommendationEngine
        # Mock response pour MVP
        mock_recommendations = [
            CareerRecommendationResponse(
                job_title="Data Scientist",
                compatibility_score=0.87,
                sector="Tech",
                justification="Forte compatibilité avec vos compétences analytiques",
                ia_resilience_score=0.72
            ),
            CareerRecommendationResponse(
                job_title="Coach en reconversion",
                compatibility_score=0.82,
                sector="Services",
                justification="Aligné avec votre valeur d'accompagnement",
                ia_resilience_score=0.91
            )
        ]
        
        return mock_recommendations
        
    except Exception as e:
        logger.error(f"Erreur récupération recommandations: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Recommendations retrieval failed: {str(e)}"
        )

# =============================================
# ENDPOINTS INTÉGRATION ÉCOSYSTÈME
# =============================================

@app.post("/api/v1/ecosystem/transition")
async def prepare_ecosystem_transition(
    chosen_career: str,
    target_app: str,  # "phoenix_cv", "phoenix_letters", "phoenix_rise"
    # current_user = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    🔗 Prépare transition vers autre app Phoenix
    """
    try:
        # TODO: Implémenter PhoenixEcosystemIntegrator
        transition_data = {
            "chosen_career": chosen_career,
            "target_app": target_app,
            "transition_url": f"https://{target_app}.streamlit.app/",
            "context_data": {
                "career_focus": chosen_career,
                "source_app": "phoenix_aube",
                "transition_type": "career_validated"
            }
        }
        
        logger.info(f"Transition préparée vers {target_app} pour {chosen_career}")
        return transition_data
        
    except Exception as e:
        logger.error(f"Erreur préparation transition: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Transition preparation failed: {str(e)}"
        )

# =============================================
# ENDPOINTS MONITORING & HEALTH
# =============================================

@app.get("/health")
async def health_check() -> Dict[str, str]:
    """🏥 Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "phoenix_aube_api"
    }

@app.get("/api/v1/metrics")
async def get_metrics(
    # admin_user = Depends(get_admin_user)
) -> Dict[str, Any]:
    """📊 Métriques business Phoenix Aube"""
    try:
        # TODO: Implémenter métriques réelles
        metrics = {
            "analyses_ia_today": 42,
            "explorations_started": 18,
            "career_choices_made": 7,
            "ecosystem_transitions": 12,
            "average_satisfaction": 4.3,
            "top_analyzed_jobs": [
                "Data Scientist", "Coach", "Chef de Projet", "Designer UX"
            ]
        }
        
        return metrics
        
    except Exception as e:
        logger.error(f"Erreur récupération métriques: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Metrics retrieval failed: {str(e)}"
        )


# =============================================
# ENDPOINTS TRANSPARENCE & ORCHESTRATION
# =============================================

@app.post("/api/v1/transparency/explain-recommendation")
async def explain_recommendation(
    recommendation_data: Dict[str, Any],
    # current_user = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    🔍 Explique une recommandation (Trust by Design)
    """
    try:
        # Initialiser services
        event_store = PhoenixAubeEventStore()
        transparency_engine = TransparencyEngine(event_store)
        
        # Mock pour MVP - en production utiliserait les vraies données
        explication = {
            "métier_titre": recommendation_data.get("job_title", "Data Scientist"),
            "pourquoi_recommandé": "Ce métier correspond parfaitement à votre profil analytique et vos valeurs d'autonomie",
            "facteurs_positifs": [
                {"facteur": "Compétences transférables", "score": 0.85},
                {"facteur": "Alignement valeurs", "score": 0.92}
            ],
            "facteurs_attention": [
                {"facteur": "Formation technique requise", "impact": "modéré"}
            ],
            "leviers_amélioration": [
                "Suivre formation Machine Learning",
                "Développer compétences Python"
            ],
            "niveau_confiance": "élevé",
            "sources_utilisées": ["Big Five", "RIASEC", "Analyse compétences"]
        }
        
        return explication
        
    except Exception as e:
        logger.error(f"Erreur explication transparence: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Transparency explanation failed: {str(e)}"
        )

@app.post("/api/v1/orchestration/complete-journey")
async def complete_user_journey(
    user_data: Dict[str, Any],
    # current_user = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    🚀 Orchestre un parcours complet utilisateur
    """
    try:
        # Initialiser orchestrateur
        from ..utils.mock_providers import MockEventStore, MockRecommendationEngine
        
        event_store = PhoenixAubeEventStore()
        ia_validator = get_ia_validator()
        transparency_engine = TransparencyEngine(event_store)
        exploration_engine = MockRecommendationEngine()
        
        orchestrator = PhoenixAubeOrchestrator(
            exploration_engine=exploration_engine,
            ia_validator=ia_validator,
            transparency_engine=transparency_engine,
            event_store=event_store
        )
        
        # Traiter parcours complet
        user_id = user_data.get("user_id", "demo_user")
        parcours = await orchestrator.traiter_parcours_complet(
            user_id=user_id,
            données_utilisateur=user_data
        )
        
        return {
            "parcours_id": parcours.parcours_id,
            "user_id": parcours.user_id,
            "statut": parcours.statut_completion,
            "recommandations_count": len(parcours.recommandations_métiers),
            "analyses_ia_count": len(parcours.analyses_ia),
            "message": "🔮 Parcours Phoenix Aube complété avec succès !"
        }
        
    except Exception as e:
        logger.error(f"Erreur orchestration parcours: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Journey orchestration failed: {str(e)}"
        )

@app.get("/api/v1/user/{user_id}/dashboard")
async def get_user_dashboard(
    user_id: str,
    # current_user = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    📊 Dashboard utilisateur complet
    """
    try:
        # Initialiser orchestrateur
        event_store = PhoenixAubeEventStore()
        orchestrator = PhoenixAubeOrchestrator(
            exploration_engine=None,
            ia_validator=get_ia_validator(),
            transparency_engine=TransparencyEngine(event_store),
            event_store=event_store
        )
        
        dashboard = await orchestrator.obtenir_dashboard_utilisateur(user_id)
        
        return dashboard
        
    except Exception as e:
        logger.error(f"Erreur dashboard utilisateur: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"User dashboard failed: {str(e)}"
        )

@app.post("/api/v1/user/{user_id}/choose-career")
async def choose_career(
    user_id: str,
    career_data: Dict[str, Any],
    # current_user = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    🎯 Traite choix de métier et prépare transitions écosystème
    """
    try:
        # Initialiser orchestrateur
        event_store = PhoenixAubeEventStore()
        orchestrator = PhoenixAubeOrchestrator(
            exploration_engine=None,
            ia_validator=get_ia_validator(),
            transparency_engine=TransparencyEngine(event_store),
            event_store=event_store
        )
        
        # Traiter choix
        résultat = await orchestrator.traiter_choix_métier(
            user_id=user_id,
            métier_choisi=career_data.get("chosen_career"),
            parcours_id=career_data.get("parcours_id", "demo_parcours")
        )
        
        return résultat
        
    except Exception as e:
        logger.error(f"Erreur choix métier: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Career choice failed: {str(e)}"
        )

# =============================================
# BACKGROUND TASKS
# =============================================

async def track_analysis_request(
    job_title: str,
    resistance_score: float,
    user_context: Dict[str, Any] = None
):
    """Track analytics pour amélioration continue"""
    try:
        # TODO: Implémenter analytics réel
        logger.info(f"📊 Analytics: {job_title} analysé, score: {resistance_score:.2f}")
        
        # Envoyer à système analytics
        # await analytics_service.track_event({
        #     "event": "ia_analysis_completed",
        #     "job_title": job_title,
        #     "resistance_score": resistance_score,
        #     "user_context": user_context
        # })
        
    except Exception as e:
        logger.error(f"Erreur tracking analytics: {str(e)}")

# =============================================
# ERROR HANDLERS
# =============================================

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {
        "error": "Endpoint not found",
        "message": "🔮 Phoenix Aube API - Endpoint introuvable",
        "suggestion": "Consultez /docs pour les endpoints disponibles"
    }

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {
        "error": "Internal server error",
        "message": "🔮 Phoenix Aube API - Erreur interne",
        "suggestion": "Veuillez réessayer dans quelques instants"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "phoenix_aube.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )