#!/usr/bin/env python3
"""
🧠 PHOENIX SYSTEM CONSCIOUSNESS SERVICE
Service autonome de surveillance et auto-régulation du système Phoenix
"""

import asyncio
from typing import Any, Dict

import structlog
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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
# 🚀 APPLICATION FASTAPI
# ========================================

app = FastAPI(
    title="Phoenix System Consciousness Service",
    description="🧠 Service autonome de conscience système Phoenix Letters",
    version="2.0.0",
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

# Orchestrateur conscience
consciousness_orchestrator = None

# ========================================
# 🔄 ÉVÉNEMENTS CYCLE DE VIE
# ========================================


@app.on_event("startup")
async def startup_event():
    """Initialisation service consciousness"""
    global consciousness_orchestrator

    logger.info("🧠 Starting Phoenix System Consciousness Service...")

    # Initialisation orchestrateur
    consciousness_orchestrator = PhoenixConsciousnessOrchestrator()

    # Démarrage boucle conscience en arrière-plan
    asyncio.create_task(consciousness_orchestrator.start_consciousness_loop())

    logger.info("✅ System Consciousness Service ready!")


@app.on_event("shutdown")
async def shutdown_event():
    """Arrêt service consciousness"""
    global consciousness_orchestrator

    if consciousness_orchestrator:
        consciousness_orchestrator.stop_consciousness()

    logger.info("🔄 System Consciousness Service shutdown complete")


# ========================================
# 🎯 ENDPOINTS PRINCIPAUX
# ========================================


@app.get("/health")
async def health_check():
    """Santé du service consciousness"""

    if not consciousness_orchestrator:
        raise HTTPException(status_code=503, detail="Consciousness not initialized")

    try:
        dashboard = consciousness_orchestrator.get_dashboard()

        return {
            "status": "healthy",
            "service": "phoenix-consciousness",
            "consciousness_active": consciousness_orchestrator.monitoring_active,
            "system_state": dashboard.get("system_state", "unknown"),
            "uptime": dashboard.get("uptime", "unknown"),
        }

    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Health check failed: {e}")


@app.get("/api/consciousness/dashboard")
async def get_consciousness_dashboard():
    """Dashboard complet conscience système"""

    if not consciousness_orchestrator:
        raise HTTPException(status_code=503, detail="Consciousness not initialized")

    try:
        dashboard = consciousness_orchestrator.get_dashboard()

        # Enrichissement avec métriques service
        dashboard["service_info"] = {
            "monitoring_interval": consciousness_orchestrator.monitoring_interval,
            "monitoring_active": consciousness_orchestrator.monitoring_active,
            "service_version": "2.0.0",
            "capabilities": [
                "real_time_monitoring",
                "auto_regulation",
                "predictive_scaling",
                "intelligent_throttling",
            ],
        }

        return dashboard

    except Exception as e:
        logger.error(f"❌ Dashboard failed: {e}")
        raise HTTPException(status_code=500, detail=f"Dashboard failed: {str(e)}")


@app.get("/api/consciousness/metrics/detailed")
async def get_detailed_metrics():
    """Métriques détaillées temps réel"""

    if not consciousness_orchestrator:
        raise HTTPException(status_code=503, detail="Consciousness not initialized")

    try:
        # Collecte métriques actuelles
        current_metrics = (
            await consciousness_orchestrator.consciousness._collect_system_metrics()
        )

        # Historique des décisions
        recent_decisions = consciousness_orchestrator.consciousness.decisions_history[
            -10:
        ]

        return {
            "current_metrics": {
                "timestamp": current_metrics.timestamp.isoformat(),
                "cpu_usage": current_metrics.cpu_usage,
                "memory_usage": current_metrics.memory_usage,
                "response_time": current_metrics.response_time,
                "error_rate": current_metrics.error_rate,
                "active_requests": current_metrics.active_requests,
                "model_load_time": current_metrics.model_load_time,
            },
            "thresholds": consciousness_orchestrator.consciousness.thresholds,
            "recent_decisions": [
                {
                    "state": decision.state.value,
                    "actions_count": len(decision.actions),
                    "confidence": decision.confidence,
                    "reasoning": (
                        decision.reasoning[:100] + "..."
                        if len(decision.reasoning) > 100
                        else decision.reasoning
                    ),
                }
                for decision in recent_decisions
            ],
            "metrics_history_size": len(
                consciousness_orchestrator.consciousness.metrics_history
            ),
            "total_decisions": len(
                consciousness_orchestrator.consciousness.decisions_history
            ),
        }

    except Exception as e:
        logger.error(f"❌ Detailed metrics failed: {e}")
        raise HTTPException(status_code=500, detail=f"Metrics failed: {str(e)}")


@app.post("/api/consciousness/configure")
async def configure_consciousness(configuration: Dict[str, Any]):
    """Configuration dynamique de la conscience"""

    if not consciousness_orchestrator:
        raise HTTPException(status_code=503, detail="Consciousness not initialized")

    try:
        # Mise à jour intervalle monitoring
        if "monitoring_interval" in configuration:
            consciousness_orchestrator.monitoring_interval = configuration[
                "monitoring_interval"
            ]
            logger.info(
                f"🧠 Monitoring interval updated: {consciousness_orchestrator.monitoring_interval}s"
            )

        # Mise à jour seuils
        if "thresholds" in configuration:
            consciousness_orchestrator.consciousness.thresholds.update(
                configuration["thresholds"]
            )
            logger.info(f"🧠 Thresholds updated: {configuration['thresholds']}")

        # Mise à jour URLs services
        if "prometheus_url" in configuration:
            consciousness_orchestrator.consciousness.prometheus_url = configuration[
                "prometheus_url"
            ]

        if "smart_router_url" in configuration:
            consciousness_orchestrator.consciousness.smart_router_url = configuration[
                "smart_router_url"
            ]

        return {
            "status": "success",
            "updated_configuration": configuration,
            "current_config": {
                "monitoring_interval": consciousness_orchestrator.monitoring_interval,
                "thresholds": consciousness_orchestrator.consciousness.thresholds,
                "prometheus_url": consciousness_orchestrator.consciousness.prometheus_url,
                "smart_router_url": consciousness_orchestrator.consciousness.smart_router_url,
            },
        }

    except Exception as e:
        logger.error(f"❌ Configuration failed: {e}")
        raise HTTPException(status_code=500, detail=f"Configuration failed: {str(e)}")


@app.post("/api/consciousness/emergency-stop")
async def emergency_stop():
    """Arrêt d'urgence de la conscience système"""

    if not consciousness_orchestrator:
        raise HTTPException(status_code=503, detail="Consciousness not initialized")

    try:
        consciousness_orchestrator.stop_consciousness()

        logger.warning("🚨 EMERGENCY STOP: System Consciousness manually stopped")

        return {
            "status": "success",
            "action": "emergency_stop",
            "message": "System Consciousness stopped - manual intervention required to restart",
        }

    except Exception as e:
        logger.error(f"❌ Emergency stop failed: {e}")
        raise HTTPException(status_code=500, detail=f"Emergency stop failed: {str(e)}")


@app.post("/api/consciousness/restart")
async def restart_consciousness():
    """Redémarrage de la conscience système"""

    global consciousness_orchestrator

    try:
        # Arrêt si actif
        if consciousness_orchestrator and consciousness_orchestrator.monitoring_active:
            consciousness_orchestrator.stop_consciousness()
            await asyncio.sleep(2)  # Attente arrêt complet

        # Réinitialisation
        consciousness_orchestrator = PhoenixConsciousnessOrchestrator()

        # Redémarrage
        asyncio.create_task(consciousness_orchestrator.start_consciousness_loop())

        logger.info("🔄 System Consciousness restarted successfully")

        return {
            "status": "success",
            "action": "restart",
            "message": "System Consciousness restarted successfully",
        }

    except Exception as e:
        logger.error(f"❌ Restart failed: {e}")
        raise HTTPException(status_code=500, detail=f"Restart failed: {str(e)}")


# ========================================
# 📊 ENDPOINTS MONITORING
# ========================================


@app.get("/api/consciousness/status/simple")
async def get_simple_status():
    """Status simplifié pour monitoring externe"""

    if not consciousness_orchestrator:
        return {"status": "down", "consciousness_active": False}

    try:
        dashboard = consciousness_orchestrator.get_dashboard()

        return {
            "status": "up",
            "consciousness_active": consciousness_orchestrator.monitoring_active,
            "system_state": dashboard.get("system_state", "unknown"),
            "consciousness_level": dashboard.get("consciousness_level", "unknown"),
            "last_decision_confidence": dashboard.get("last_decision", {}).get(
                "confidence", 0.0
            ),
        }

    except Exception:
        return {"status": "error", "consciousness_active": False}


@app.get("/api/consciousness/alerts")
async def get_system_alerts():
    """Alertes système actives"""

    if not consciousness_orchestrator:
        return {"alerts": [], "alert_count": 0}

    try:
        # Analyse des dernières décisions pour détecter alertes
        recent_decisions = consciousness_orchestrator.consciousness.decisions_history[
            -5:
        ]

        alerts = []
        for decision in recent_decisions:
            if decision.state.value in ["critical", "stressed"]:
                alerts.append(
                    {
                        "level": (
                            "warning"
                            if decision.state.value == "stressed"
                            else "critical"
                        ),
                        "message": decision.reasoning,
                        "actions_taken": decision.actions,
                        "confidence": decision.confidence,
                        "state": decision.state.value,
                    }
                )

        return {
            "alerts": alerts,
            "alert_count": len(alerts),
            "critical_alerts": len([a for a in alerts if a["level"] == "critical"]),
            "warning_alerts": len([a for a in alerts if a["level"] == "warning"]),
        }

    except Exception as e:
        logger.error("❌ Alerts retrieval failed")
        return {"alerts": [], "alert_count": 0, "error": "Service temporarily unavailable"}


# ========================================
# 🚀 POINT D'ENTRÉE
# ========================================

if __name__ == "__main__":
    uvicorn.run(
        "consciousness_service:app",
        host="0.0.0.0",
        port=8003,
        log_level="info",
        reload=False,
        workers=1,
    )
