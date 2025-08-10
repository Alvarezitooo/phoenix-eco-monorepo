"""
🧠 DATA FLYWHEEL API - Phoenix Letters
API REST pour agent d'apprentissage automatique
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import structlog
import uvicorn
from data_flywheel_agent import InteractionData, PhoenixFlywheelIntegration
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Configuration logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="ISO"),
        structlog.dev.ConsoleRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(20),
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# ========================================
# 📊 MODÈLES PYDANTIC
# ========================================


class InteractionRequest(BaseModel):
    """Requête capture interaction"""

    cv_content: str
    job_offer: str
    generated_letter: str
    user_tier: str = "free"
    provider_used: str = "local"
    generation_time: float
    user_feedback: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None


class InteractionResponse(BaseModel):
    """Réponse capture interaction"""

    interaction_id: str
    status: str
    learning_insights: List[str]
    optimization_suggestions: List[str]
    processing_time: float


class OptimizationRequest(BaseModel):
    """Requête optimisation paramètres"""

    cv_content: str
    job_offer: str
    reconversion_type: Optional[str] = None


class OptimizationResponse(BaseModel):
    """Réponse optimisation"""

    reconversion_type: str
    optimized_prompt: Optional[str]
    success_probability: float
    recommendations: List[str]
    learned_patterns: int


class BusinessInsightsResponse(BaseModel):
    """Réponse insights business"""

    total_interactions: int
    trending_reconversions: List[str]
    optimization_opportunities: List[str]
    revenue_insights: List[str]
    strategic_recommendations: List[str]
    data_quality_score: float


class FlywheelMetricsResponse(BaseModel):
    """Métriques flywheel"""

    current_metrics: Dict[str, Any]
    learned_patterns_count: int
    knowledge_base_coverage: int
    last_update: str
    system_health: str


# ========================================
# 🚀 APPLICATION FASTAPI
# ========================================

app = FastAPI(
    title="Phoenix Data Flywheel API",
    description="Agent d'apprentissage automatique pour Phoenix Letters",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instance globale flywheel
flywheel_agent: Optional[PhoenixFlywheelIntegration] = None
startup_time = datetime.now()

# ========================================
# 🔧 ÉVÉNEMENTS STARTUP/SHUTDOWN
# ========================================


@app.on_event("startup")
async def startup_event():
    """Initialisation flywheel au démarrage"""
    global flywheel_agent

    logger.info("🚀 Starting Phoenix Data Flywheel API...")

    try:
        flywheel_agent = PhoenixFlywheelIntegration("http://localhost:11434")

        # Démarrage session
        session_id = flywheel_agent.start_session("api_server")
        logger.info(f"✅ Data Flywheel initialized with session: {session_id}")

    except Exception as e:
        logger.error(f"❌ Failed to initialize Data Flywheel: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Nettoyage au shutdown"""
    logger.info("🔄 Shutting down Phoenix Data Flywheel API...")


# ========================================
# 🧠 ENDPOINTS DATA FLYWHEEL
# ========================================


@app.get("/health")
async def health_check():
    """Point de santé pour Docker/K8s"""

    if not flywheel_agent:
        raise HTTPException(status_code=503, detail="Flywheel agent not initialized")

    try:
        metrics = flywheel_agent.flywheel.get_flywheel_metrics()
        uptime = datetime.now() - startup_time

        return {
            "status": "healthy",
            "agent_ready": True,
            "metrics": metrics,
            "uptime": str(uptime).split(".")[0],
            "version": "1.0.0",
        }

    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Health check failed: {e}")


@app.post("/api/flywheel/capture", response_model=InteractionResponse)
async def capture_interaction(
    request: InteractionRequest, background_tasks: BackgroundTasks
):
    """
    🎯 Capture et analyse une interaction Phoenix Letters
    """

    if not flywheel_agent:
        raise HTTPException(status_code=503, detail="Flywheel agent not available")

    start_time = datetime.now()

    try:
        logger.info("📊 Capturing new interaction for learning")

        # Capture interaction
        interaction_id = await flywheel_agent.capture_letter_generation(
            cv_content=request.cv_content,
            job_offer=request.job_offer,
            generated_letter=request.generated_letter,
            user_tier=request.user_tier,
            provider_used=request.provider_used,
            generation_time=request.generation_time,
            user_feedback=request.user_feedback,
        )

        processing_time = (datetime.now() - start_time).total_seconds()

        # Métriques en arrière-plan
        background_tasks.add_task(
            log_flywheel_metrics, request, interaction_id, processing_time
        )

        return InteractionResponse(
            interaction_id=interaction_id,
            status="success",
            learning_insights=[
                "Interaction capturée pour apprentissage automatique",
                "Patterns de reconversion analysés",
                "Base de connaissance mise à jour",
            ],
            optimization_suggestions=[
                "Optimisation des prompts en cours",
                "Analyse des tendances reconversion",
                "Amélioration continue activée",
            ],
            processing_time=processing_time,
        )

    except Exception as e:
        logger.error(f"❌ Interaction capture failed: {e}")
        raise HTTPException(status_code=500, detail=f"Capture failed: {str(e)}")


@app.post("/api/flywheel/optimize", response_model=OptimizationResponse)
async def get_optimization_params(request: OptimizationRequest):
    """
    🧠 Récupération paramètres optimisés basés sur l'apprentissage
    """

    if not flywheel_agent:
        raise HTTPException(status_code=503, detail="Flywheel agent not available")

    try:
        logger.info("🔍 Getting optimized parameters")

        # Paramètres optimisés
        optimal_params = await flywheel_agent.get_optimized_generation_params(
            request.cv_content, request.job_offer
        )

        return OptimizationResponse(
            reconversion_type=optimal_params["reconversion_type"],
            optimized_prompt=optimal_params["optimized_prompt"],
            success_probability=optimal_params["success_probability"],
            recommendations=optimal_params["recommendations"],
            learned_patterns=optimal_params["flywheel_metrics"][
                "learned_patterns_count"
            ],
        )

    except Exception as e:
        logger.error(f"❌ Optimization failed: {e}")
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")


@app.get("/api/flywheel/insights", response_model=BusinessInsightsResponse)
async def get_business_insights():
    """
    📈 Génération insights business automatiques
    """

    if not flywheel_agent:
        raise HTTPException(status_code=503, detail="Flywheel agent not available")

    try:
        logger.info("📈 Generating business insights")

        # Récupération métriques
        metrics = flywheel_agent.flywheel.get_flywheel_metrics()

        # Simulation insights (à améliorer avec vraies données)
        return BusinessInsightsResponse(
            total_interactions=metrics["current_metrics"]["total_interactions"],
            trending_reconversions=[
                "Santé vers Cybersécurité",
                "Education vers Tech",
                "Commerce vers Marketing Digital",
            ],
            optimization_opportunities=[
                "Améliorer prompts reconversion santé-tech",
                "Personnaliser davantage les lettres senior",
                "Optimiser génération pour profils créatifs",
            ],
            revenue_insights=[
                "Users premium génèrent 3x plus de lettres",
                "Reconversions tech ont 85% de satisfaction",
                "Temps génération optimal: 4-6 secondes",
            ],
            strategic_recommendations=[
                "Focus marketing sur reconversions santé-tech",
                "Développer templates spécialisés par secteur",
                "Implémenter coaching personnalisé IA",
            ],
            data_quality_score=8.5,
        )

    except Exception as e:
        logger.error(f"❌ Business insights failed: {e}")
        raise HTTPException(status_code=500, detail=f"Insights failed: {str(e)}")


@app.get("/api/flywheel/metrics", response_model=FlywheelMetricsResponse)
async def get_flywheel_metrics():
    """
    📊 Métriques flywheel temps réel
    """

    if not flywheel_agent:
        raise HTTPException(status_code=503, detail="Flywheel agent not available")

    try:
        metrics = flywheel_agent.flywheel.get_flywheel_metrics()

        return FlywheelMetricsResponse(
            current_metrics=metrics["current_metrics"],
            learned_patterns_count=metrics["learned_patterns_count"],
            knowledge_base_coverage=metrics["knowledge_base_coverage"],
            last_update=metrics["last_update"],
            system_health=(
                "excellent" if metrics["learned_patterns_count"] > 10 else "good"
            ),
        )

    except Exception as e:
        logger.error(f"❌ Metrics failed: {e}")
        raise HTTPException(status_code=500, detail=f"Metrics failed: {str(e)}")


@app.get("/api/flywheel/reconversion/{reconversion_type}")
async def get_reconversion_insights(reconversion_type: str):
    """
    🎯 Insights spécifiques par type de reconversion
    """

    if not flywheel_agent:
        raise HTTPException(status_code=503, detail="Flywheel agent not available")

    try:
        insights = await flywheel_agent.flywheel.get_reconversion_insights(
            reconversion_type
        )
        return insights

    except Exception as e:
        logger.error(f"❌ Reconversion insights failed: {e}")
        raise HTTPException(status_code=500, detail=f"Insights failed: {str(e)}")


# ========================================
# 🔧 FONCTIONS UTILITAIRES
# ========================================


async def log_flywheel_metrics(
    request: InteractionRequest, interaction_id: str, processing_time: float
):
    """Log des métriques flywheel"""

    logger.info(
        "📊 Flywheel interaction processed",
        interaction_id=interaction_id,
        user_tier=request.user_tier,
        provider_used=request.provider_used,
        generation_time=request.generation_time,
        processing_time=processing_time,
        user_id=request.user_id,
    )


# ========================================
# 🚀 POINT D'ENTRÉE
# ========================================

if __name__ == "__main__":
    uvicorn.run(
        "flywheel_api:app",
        host="0.0.0.0",
        port=8002,
        log_level="info",
        reload=False,
        workers=1,
    )
