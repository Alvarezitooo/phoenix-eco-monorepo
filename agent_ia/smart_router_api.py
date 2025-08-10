"""
🎯 SMART ROUTER API GATEWAY - Phoenix Letters
Orchestrateur intelligent des agents IA containerisés
"""

import asyncio
import os
import time
from datetime import datetime
from typing import Any, Dict, Optional

import httpx
import structlog
import uvicorn
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import System Consciousness
from system_consciousness import PhoenixConsciousnessOrchestrator

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


class PhoenixAnalysisRequest(BaseModel):
    """Requête analyse complète Phoenix"""

    cv_content: str
    job_offer: str
    generated_letter: str
    user_tier: str = "free"
    user_id: Optional[str] = None
    enable_learning: bool = True


class PhoenixAnalysisResponse(BaseModel):
    """Réponse analyse complète"""

    status: str
    security_passed: bool
    analysis_results: Dict[str, Any]
    learning_insights: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    recommendations: list[str]
    processing_time: float


class HealthResponse(BaseModel):
    """Santé du système complet"""

    status: str
    services_health: Dict[str, str]
    total_requests: int
    average_response_time: float
    uptime: str


# ========================================
# 🚀 APPLICATION FASTAPI
# ========================================

app = FastAPI(
    title="Phoenix Smart Router API",
    description="Gateway intelligent pour agents IA Phoenix Letters",
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

# Configuration services
SECURITY_GUARDIAN_URL = os.getenv(
    "SECURITY_GUARDIAN_URL", "http://security-guardian:8001"
)
DATA_FLYWHEEL_URL = os.getenv("DATA_FLYWHEEL_URL", "http://data-flywheel:8002")
MAX_RESPONSE_TIME = float(os.getenv("MAX_RESPONSE_TIME", "10"))
ENABLE_CLOUD_FALLBACK = os.getenv("ENABLE_CLOUD_FALLBACK", "true").lower() == "true"

# Métriques globales
startup_time = datetime.now()
total_requests = 0
total_response_time = 0.0

# System Consciousness
consciousness_orchestrator = None
circuit_breaker_enabled = False
max_concurrent_requests = 20
throttle_limit = 100  # requests per minute

# ========================================
# 🔧 CLIENT HTTP RÉUTILISABLE
# ========================================

http_client = None


@app.on_event("startup")
async def startup_event():
    """Initialisation du router"""
    global http_client, consciousness_orchestrator

    logger.info("🚀 Starting Phoenix Smart Router API Gateway...")

    # Client HTTP optimisé
    http_client = httpx.AsyncClient(
        timeout=httpx.Timeout(MAX_RESPONSE_TIME),
        limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
    )

    # Initialisation System Consciousness
    consciousness_orchestrator = PhoenixConsciousnessOrchestrator()

    # Démarrage monitoring conscience en arrière-plan
    asyncio.create_task(consciousness_orchestrator.start_consciousness_loop())

    # Test de connectivité des services
    await test_services_connectivity()

    logger.info("🧠 System Consciousness activated")
    logger.info("✅ Phoenix Smart Router ready!")


@app.on_event("shutdown")
async def shutdown_event():
    """Nettoyage"""
    global http_client, consciousness_orchestrator

    # Arrêt System Consciousness
    if consciousness_orchestrator:
        consciousness_orchestrator.stop_consciousness()

    if http_client:
        await http_client.aclose()

    logger.info("🔄 Phoenix Smart Router shutdown complete")


# ========================================
# 🎯 ENDPOINTS PRINCIPAUX
# ========================================


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Santé globale du système"""

    global total_requests, total_response_time

    try:
        # Test des services
        services_health = await check_services_health()

        uptime = datetime.now() - startup_time
        avg_response_time = total_response_time / max(total_requests, 1)

        overall_status = (
            "healthy"
            if all(status == "healthy" for status in services_health.values())
            else "degraded"
        )

        return HealthResponse(
            status=overall_status,
            services_health=services_health,
            total_requests=total_requests,
            average_response_time=avg_response_time,
            uptime=str(uptime).split(".")[0],
        )

    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Health check failed: {e}")


@app.post("/api/phoenix/analyze", response_model=PhoenixAnalysisResponse)
async def analyze_phoenix_interaction(
    request: PhoenixAnalysisRequest, background_tasks: BackgroundTasks
):
    """
    🎯 Analyse complète Phoenix Letters avec agents IA
    Point d'entrée principal pour Streamlit
    """

    global total_requests, total_response_time, circuit_breaker_enabled

    # Vérification circuit breaker
    if circuit_breaker_enabled:
        raise HTTPException(
            status_code=503,
            detail="🔌 Circuit breaker activated - System in protection mode",
        )

    start_time = time.time()
    total_requests += 1

    try:
        logger.info("🎯 Starting complete Phoenix analysis")

        analysis_results = {}
        recommendations = []

        # 1. 🛡️ ANALYSE SÉCURITÉ PRIORITAIRE
        logger.info("🛡️ Running security analysis...")

        security_result = await call_security_guardian(
            request.cv_content, request.job_offer
        )

        analysis_results["security"] = security_result

        # Blocage si critique
        if not security_result.get("safe_to_process", True):
            processing_time = time.time() - start_time
            total_response_time += processing_time

            return PhoenixAnalysisResponse(
                status="BLOCKED",
                security_passed=False,
                analysis_results=analysis_results,
                learning_insights={},
                performance_metrics={"processing_time": processing_time},
                recommendations=["🚨 Contenu bloqué pour raisons de sécurité"],
                processing_time=processing_time,
            )

        # 2. 🧠 APPRENTISSAGE FLYWHEEL (si activé)
        learning_insights = {}

        if request.enable_learning:
            logger.info("🧠 Capturing interaction for learning...")

            try:
                learning_result = await call_data_flywheel(request)
                learning_insights = learning_result
                analysis_results["learning"] = learning_result

            except Exception as e:
                logger.warning(f"⚠️ Learning capture failed (non-critical): {e}")
                learning_insights = {
                    "warning": "Apprentissage temporairement indisponible"
                }

        # 3. 📊 MÉTRIQUES PERFORMANCE
        processing_time = time.time() - start_time
        total_response_time += processing_time

        performance_metrics = {
            "processing_time": processing_time,
            "security_check": security_result.get("processing_time", 0),
            "services_used": ["security-guardian"]
            + (["data-flywheel"] if request.enable_learning else []),
            "efficiency_score": "excellent" if processing_time < 5 else "good",
        }

        # 4. 💡 RECOMMANDATIONS CONSOLIDÉES
        recommendations.extend(security_result.get("recommendations", []))
        recommendations.extend(learning_insights.get("optimization_suggestions", []))

        # Métriques en arrière-plan
        background_tasks.add_task(
            log_analysis_metrics, request, analysis_results, processing_time
        )

        return PhoenixAnalysisResponse(
            status="SUCCESS",
            security_passed=True,
            analysis_results=analysis_results,
            learning_insights=learning_insights,
            performance_metrics=performance_metrics,
            recommendations=recommendations[:5],  # Top 5
            processing_time=processing_time,
        )

    except Exception as e:
        processing_time = time.time() - start_time
        total_response_time += processing_time

        logger.error(f"❌ Phoenix analysis failed: {e}")

        # Mode dégradé avec fallback
        return PhoenixAnalysisResponse(
            status="DEGRADED",
            security_passed=True,  # Assume safe si pas de check
            analysis_results={"error": str(e)},
            learning_insights={"fallback": "Mode dégradé actif"},
            performance_metrics={"processing_time": processing_time, "error": True},
            recommendations=["⚠️ Analyse en mode dégradé - fonctionnalités limitées"],
            processing_time=processing_time,
        )


@app.get("/api/phoenix/optimize")
async def get_optimized_params(cv_content: str, job_offer: str):
    """🧠 Paramètres optimisés basés sur l'apprentissage"""

    try:
        optimization_result = await call_flywheel_optimization(cv_content, job_offer)
        return optimization_result

    except Exception as e:
        logger.error(f"❌ Optimization failed: {e}")
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")


@app.get("/api/phoenix/insights")
async def get_business_insights():
    """📈 Insights business Phoenix Letters"""

    try:
        insights = await call_flywheel_insights()
        return insights

    except Exception as e:
        logger.error(f"❌ Business insights failed: {e}")
        raise HTTPException(status_code=500, detail=f"Insights failed: {str(e)}")


# ========================================
# 🧠 ENDPOINTS SYSTEM CONSCIOUSNESS
# ========================================


@app.get("/api/consciousness/status")
async def get_consciousness_status():
    """État actuel de la conscience système"""

    if not consciousness_orchestrator:
        raise HTTPException(
            status_code=503, detail="System Consciousness not initialized"
        )

    try:
        dashboard = consciousness_orchestrator.get_dashboard()
        return {
            "consciousness_active": True,
            **dashboard,
            "circuit_breaker": circuit_breaker_enabled,
            "throttle_limit": throttle_limit,
            "max_concurrent": max_concurrent_requests,
        }

    except Exception as e:
        logger.error(f"❌ Consciousness status failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Consciousness status failed: {str(e)}"
        )


@app.get("/api/consciousness/metrics")
async def get_consciousness_metrics():
    """Métriques détaillées de la conscience système"""

    if not consciousness_orchestrator:
        raise HTTPException(
            status_code=503, detail="System Consciousness not initialized"
        )

    # Récupération métriques système actuelles
    current_metrics = (
        await consciousness_orchestrator.consciousness._collect_system_metrics()
    )

    return {
        "current_metrics": current_metrics.__dict__,
        "thresholds": consciousness_orchestrator.consciousness.thresholds,
        "monitoring_interval": consciousness_orchestrator.monitoring_interval,
        "decisions_history_count": len(
            consciousness_orchestrator.consciousness.decisions_history
        ),
        "last_5_decisions": [
            {
                "timestamp": decision.state.value,
                "actions": decision.actions,
                "confidence": decision.confidence,
                "reasoning": decision.reasoning,
            }
            for decision in consciousness_orchestrator.consciousness.decisions_history[
                -5:
            ]
        ],
    }


@app.post("/api/consciousness/manual-action")
async def trigger_manual_consciousness_action(
    action: str, parameters: Dict[str, Any] = None
):
    """Déclenchement manuel d'une action de conscience"""

    if not consciousness_orchestrator:
        raise HTTPException(
            status_code=503, detail="System Consciousness not initialized"
        )

    try:
        # Actions manuelles disponibles
        if action == "force_optimization":
            # Forcer une optimisation système
            await consciousness_orchestrator.consciousness._execute_action(
                "learn_from_optimal_conditions", None
            )
            return {"status": "success", "action": "optimization_triggered"}

        elif action == "emergency_throttle":
            # Throttling d'urgence
            global throttle_limit
            throttle_limit = parameters.get("limit", 10)
            return {
                "status": "success",
                "action": "emergency_throttle",
                "new_limit": throttle_limit,
            }

        elif action == "reset_circuit_breaker":
            # Reset circuit breaker
            global circuit_breaker_enabled
            circuit_breaker_enabled = False
            return {"status": "success", "action": "circuit_breaker_reset"}

        else:
            raise HTTPException(status_code=400, detail=f"Unknown action: {action}")

    except Exception as e:
        logger.error(f"❌ Manual consciousness action failed: {e}")
        raise HTTPException(status_code=500, detail=f"Action failed: {str(e)}")


# ========================================
# 🔧 ENDPOINTS AUTO-RÉGULATION (appelés par System Consciousness)
# ========================================


@app.post("/api/throttle")
async def set_throttle_limit(max_requests_per_minute: int):
    """Configuration throttling par System Consciousness"""

    global throttle_limit
    throttle_limit = max_requests_per_minute

    logger.info(f"🧠 Consciousness: Throttle limit set to {throttle_limit} req/min")

    return {"status": "success", "throttle_limit": throttle_limit}


@app.post("/api/circuit-breaker")
async def configure_circuit_breaker(enabled: bool, failure_threshold: int = 3):
    """Configuration circuit breaker par System Consciousness"""

    global circuit_breaker_enabled
    circuit_breaker_enabled = enabled

    logger.info(
        f"🧠 Consciousness: Circuit breaker {'enabled' if enabled else 'disabled'}"
    )

    return {
        "status": "success",
        "circuit_breaker_enabled": circuit_breaker_enabled,
        "failure_threshold": failure_threshold,
    }


@app.post("/api/concurrency")
async def set_max_concurrent(max_concurrent: int):
    """Configuration concurrence maximale par System Consciousness"""

    global max_concurrent_requests
    max_concurrent_requests = max_concurrent

    logger.info(
        f"🧠 Consciousness: Max concurrent requests set to {max_concurrent_requests}"
    )

    return {"status": "success", "max_concurrent": max_concurrent_requests}


# ========================================
# 🔧 FONCTIONS SERVICES
# ========================================


async def call_security_guardian(cv_content: str, job_offer: str) -> Dict[str, Any]:
    """Appel Security Guardian avec fallback"""

    try:
        # Analyse CV
        cv_response = await http_client.post(
            f"{SECURITY_GUARDIAN_URL}/api/security/analyze",
            json={"content": cv_content, "content_type": "cv"},
        )
        cv_response.raise_for_status()
        cv_result = cv_response.json()

        # Analyse offre
        job_response = await http_client.post(
            f"{SECURITY_GUARDIAN_URL}/api/security/analyze",
            json={"content": job_offer, "content_type": "job_offer"},
        )
        job_response.raise_for_status()
        job_result = job_response.json()

        # Consolidation résultats
        return {
            "safe_to_process": cv_result["safe_to_process"]
            and job_result["safe_to_process"],
            "cv_analysis": cv_result,
            "job_analysis": job_result,
            "overall_risk": max(cv_result["risk_score"], job_result["risk_score"]),
            "recommendations": cv_result["recommendations"]
            + job_result["recommendations"],
            "processing_time": cv_result["processing_time"]
            + job_result["processing_time"],
        }

    except Exception as e:
        logger.warning(f"⚠️ Security Guardian failed, using fallback: {e}")

        # Fallback sécurité basique
        return {
            "safe_to_process": True,  # Assume safe en fallback
            "fallback_used": True,
            "recommendations": ["⚠️ Analyse sécurité en mode dégradé"],
            "processing_time": 0.1,
        }


async def call_data_flywheel(request: PhoenixAnalysisRequest) -> Dict[str, Any]:
    """Appel Data Flywheel pour apprentissage"""

    try:
        response = await http_client.post(
            f"{DATA_FLYWHEEL_URL}/api/flywheel/capture",
            json={
                "cv_content": request.cv_content,
                "job_offer": request.job_offer,
                "generated_letter": request.generated_letter,
                "user_tier": request.user_tier,
                "provider_used": "local_docker",
                "generation_time": 3.0,  # Estimation
                "user_feedback": None,
                "user_id": request.user_id,
            },
        )
        response.raise_for_status()
        return response.json()

    except Exception as e:
        logger.warning(f"⚠️ Data Flywheel failed: {e}")
        raise


async def call_flywheel_optimization(cv_content: str, job_offer: str) -> Dict[str, Any]:
    """Appel optimisation flywheel"""

    response = await http_client.post(
        f"{DATA_FLYWHEEL_URL}/api/flywheel/optimize",
        json={"cv_content": cv_content, "job_offer": job_offer},
    )
    response.raise_for_status()
    return response.json()


async def call_flywheel_insights() -> Dict[str, Any]:
    """Appel insights business"""

    response = await http_client.get(f"{DATA_FLYWHEEL_URL}/api/flywheel/insights")
    response.raise_for_status()
    return response.json()


async def check_services_health() -> Dict[str, str]:
    """Vérification santé des services"""

    services_health = {}

    # Security Guardian
    try:
        response = await http_client.get(f"{SECURITY_GUARDIAN_URL}/health", timeout=5.0)
        services_health["security-guardian"] = (
            "healthy" if response.status_code == 200 else "unhealthy"
        )
    except:
        services_health["security-guardian"] = "unhealthy"

    # Data Flywheel
    try:
        response = await http_client.get(f"{DATA_FLYWHEEL_URL}/health", timeout=5.0)
        services_health["data-flywheel"] = (
            "healthy" if response.status_code == 200 else "unhealthy"
        )
    except:
        services_health["data-flywheel"] = "unhealthy"

    return services_health


async def test_services_connectivity():
    """Test initial de connectivité"""

    logger.info("🔍 Testing services connectivity...")

    services_health = await check_services_health()

    for service, health in services_health.items():
        if health == "healthy":
            logger.info(f"✅ {service} is healthy")
        else:
            logger.warning(f"⚠️ {service} is unhealthy")

    healthy_services = sum(1 for h in services_health.values() if h == "healthy")
    logger.info(f"📊 {healthy_services}/{len(services_health)} services are healthy")


async def log_analysis_metrics(
    request: PhoenixAnalysisRequest, results: Dict[str, Any], processing_time: float
):
    """Log métriques pour monitoring"""

    logger.info(
        "📊 Phoenix analysis completed",
        user_tier=request.user_tier,
        user_id=request.user_id,
        security_passed=results.get("security", {}).get("safe_to_process", True),
        learning_enabled=request.enable_learning,
        processing_time=processing_time,
    )


# ========================================
# 🚀 POINT D'ENTRÉE
# ========================================

if __name__ == "__main__":
    uvicorn.run(
        "smart_router_api:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=False,
        workers=1,
    )
