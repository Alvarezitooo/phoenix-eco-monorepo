"""
🛡️ SECURITY GUARDIAN API - Phoenix Letters
API REST pour agent de sécurité containerisé
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, Optional

import structlog
import uvicorn
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from security_guardian_agent import PhoenixSecurityInterface

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


class SecurityAnalysisRequest(BaseModel):
    """Requête d'analyse sécurité"""

    content: str
    content_type: str = "general"
    user_id: Optional[str] = None
    session_id: Optional[str] = None


class SecurityAnalysisResponse(BaseModel):
    """Réponse analyse sécurité"""

    status: str
    safe_to_process: bool
    rgpd_compliant: bool
    threat_level: str
    risk_score: float
    threats_detected: int
    pii_detected: int
    recommendations: list[str]
    processing_time: float
    timestamp: datetime


class HealthResponse(BaseModel):
    """Réponse santé service"""

    status: str
    agent_ready: bool
    model_loaded: bool
    memory_usage: str
    uptime: str
    version: str


# ========================================
# 🚀 APPLICATION FASTAPI
# ========================================

app = FastAPI(
    title="Phoenix Security Guardian API",
    description="Agent de sécurité IA pour Phoenix Letters",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instance globale de l'agent sécurité
security_agent: Optional[PhoenixSecurityInterface] = None
startup_time = datetime.now()

# ========================================
# 🔧 ÉVÉNEMENTS STARTUP/SHUTDOWN
# ========================================


@app.on_event("startup")
async def startup_event():
    """Initialisation de l'agent au démarrage"""
    global security_agent

    logger.info("🚀 Starting Phoenix Security Guardian API...")

    try:
        security_agent = PhoenixSecurityInterface()

        # Initialisation avec retry
        for attempt in range(3):
            try:
                if await security_agent.initialize():
                    logger.info("✅ Security Guardian Agent initialized successfully")
                    break
            except Exception as e:
                logger.warning(f"❌ Initialization attempt {attempt + 1}/3 failed: {e}")
                if attempt == 2:
                    raise
                await asyncio.sleep(5)

    except Exception as e:
        logger.error(f"❌ Failed to initialize Security Guardian: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Nettoyage au shutdown"""
    logger.info("🔄 Shutting down Phoenix Security Guardian API...")


# ========================================
# 🛡️ ENDPOINTS SÉCURITÉ
# ========================================


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Point de santé pour Docker/K8s"""

    if not security_agent:
        raise HTTPException(status_code=503, detail="Security agent not initialized")

    try:
        agent_status = security_agent.guardian.get_agent_status()
        uptime = datetime.now() - startup_time

        return HealthResponse(
            status="healthy" if agent_status["model_loaded"] else "degraded",
            agent_ready=agent_status["model_loaded"],
            model_loaded=agent_status["model_loaded"],
            memory_usage=f"{agent_status.get('memory_usage', 0):.1f}GB",
            uptime=str(uptime).split(".")[0],
            version="1.0.0",
        )

    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Health check failed: {e}")


@app.post("/api/security/analyze", response_model=SecurityAnalysisResponse)
async def analyze_security(
    request: SecurityAnalysisRequest, background_tasks: BackgroundTasks
):
    """
    🎯 Analyse sécurité complète d'un contenu
    """

    if not security_agent:
        raise HTTPException(status_code=503, detail="Security agent not available")

    start_time = datetime.now()

    try:
        logger.info(f"🔍 Starting security analysis for {request.content_type}")

        # Analyse sécurité
        if request.content_type == "cv":
            result = await security_agent.check_cv_security(request.content)
        elif request.content_type == "job_offer":
            result = await security_agent.check_job_offer_security(request.content)
        else:
            # Analyse générique
            report = await security_agent.guardian.analyze_content_security(
                request.content, request.content_type
            )
            result = {
                "safe_to_process": report.threat_level.value
                not in ["high", "critical"],
                "rgpd_compliant": report.compliance_status.value != "non_compliant",
                "pii_detected": len(report.pii_detected),
                "threats_detected": len(report.threats_detected),
                "risk_score": report.risk_score,
                "recommendations": report.recommendations[:3],
            }

        processing_time = (datetime.now() - start_time).total_seconds()

        # Métriques en arrière-plan
        background_tasks.add_task(
            log_security_metrics, request, result, processing_time
        )

        return SecurityAnalysisResponse(
            status="success",
            safe_to_process=result["safe_to_process"],
            rgpd_compliant=result["rgpd_compliant"],
            threat_level=result.get("threat_level", "low"),
            risk_score=result["risk_score"],
            threats_detected=result["threats_detected"],
            pii_detected=result["pii_detected"],
            recommendations=result["recommendations"],
            processing_time=processing_time,
            timestamp=datetime.now(),
        )

    except Exception as e:
        logger.error(f"❌ Security analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.get("/api/security/quick-check")
async def quick_threat_check(content: str):
    """🚀 Vérification rapide de menaces (sans IA)"""

    if not security_agent:
        raise HTTPException(status_code=503, detail="Security agent not available")

    try:
        is_threat = await security_agent.guardian.quick_threat_check(content)

        return {
            "threat_detected": is_threat,
            "recommendation": "Block content" if is_threat else "Content appears safe",
            "processing_time": 0.1,  # Très rapide
        }

    except Exception as e:
        logger.error(f"❌ Quick check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Quick check failed: {str(e)}")


@app.get("/api/security/dashboard")
async def get_security_dashboard():
    """📊 Dashboard sécurité Phoenix"""

    if not security_agent:
        raise HTTPException(status_code=503, detail="Security agent not available")

    try:
        dashboard = security_agent.get_security_dashboard()
        return dashboard

    except Exception as e:
        logger.error(f"❌ Dashboard failed: {e}")
        raise HTTPException(status_code=500, detail=f"Dashboard failed: {str(e)}")


# ========================================
# 🔧 FONCTIONS UTILITAIRES
# ========================================


async def log_security_metrics(
    request: SecurityAnalysisRequest, result: Dict[str, Any], processing_time: float
):
    """Log des métriques pour monitoring"""

    logger.info(
        "📊 Security analysis completed",
        content_type=request.content_type,
        safe_to_process=result["safe_to_process"],
        threats_detected=result["threats_detected"],
        pii_detected=result["pii_detected"],
        processing_time=processing_time,
        user_id=request.user_id,
        session_id=request.session_id,
    )


# ========================================
# 🚀 POINT D'ENTRÉE
# ========================================

if __name__ == "__main__":
    uvicorn.run(
        "security_api:app",
        host="0.0.0.0",
        port=8001,
        log_level="info",
        reload=False,  # Pas de reload en production
        workers=1,  # Un seul worker pour l'IA
    )
