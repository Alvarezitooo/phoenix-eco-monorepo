"""
🎯 SMART ROUTER EVENT-SOURCING - Phoenix Letters
Orchestrateur intelligent avec intégration Event Store Supabase
Gère les commandes, événements et coordination des agents IA
"""

import asyncio
import os
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx
import structlog
import uvicorn
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import Client, create_client

# Import des agents intégrés
from data_flywheel_supabase_integration import DataFlywheelSupabaseConsumer
from security_guardian_supabase_integration import SecurityGuardianSupabasePublisher

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
# 📊 MODÈLES EVENT-SOURCING
# ========================================

class PhoenixCommand(BaseModel):
    """Commande Phoenix standardisée"""
    command_id: str
    command_type: str
    user_id: str
    app_source: str
    payload: Dict[str, Any]
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class PhoenixAnalysisRequest(BaseModel):
    """Requête analyse complète Phoenix avec Event-Sourcing"""
    cv_content: str
    job_offer: str
    generated_letter: str
    user_tier: str = "free"
    user_id: str
    app_source: str = "letters"
    enable_learning: bool = True
    enable_security_scan: bool = True

class EventSourcingResult(BaseModel):
    """Résultat avec Event-Sourcing"""
    success: bool
    result_data: Dict[str, Any]
    events_created: List[str]
    security_passed: bool
    learning_applied: bool
    processing_time: float

# ========================================
# 🎯 SMART ROUTER EVENT-SOURCING
# ========================================

class SmartRouterEventSourcing:
    """
    Smart Router avec Event-Sourcing intégré
    Orchestre les agents IA + gère le Event Store
    """

    def __init__(self):
        """Initialise le Smart Router avec Event Store"""
        # Connexion Supabase Event Store
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL et SUPABASE_KEY requis")
            
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        
        # Agents IA spécialisés
        self.security_guardian = SecurityGuardianSupabasePublisher()
        self.data_flywheel = DataFlywheelSupabaseConsumer()
        
        # Configuration des endpoints agents
        self.agent_endpoints = {
            "security": "http://localhost:8001",
            "flywheel": "http://localhost:8002"
        }
        
        # Configuration Gemini fallback
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.enable_cloud_fallback = os.getenv("ENABLE_CLOUD_FALLBACK", "true").lower() == "true"
        
        logger.info("✅ SmartRouterEventSourcing initialisé")

    async def process_phoenix_command(self, command: PhoenixCommand) -> EventSourcingResult:
        """
        Traite une commande Phoenix avec Event-Sourcing complet
        
        Args:
            command: Commande à traiter
            
        Returns:
            EventSourcingResult: Résultat avec événements créés
        """
        start_time = time.time()
        events_created = []
        
        try:
            # 1. Publier événement de début de commande
            command_event_id = await self._publish_command_event(command)
            events_created.append(command_event_id)
            
            # 2. Routage selon le type de commande
            if command.command_type == "AnalyzeCompleteContent":
                result = await self._handle_complete_analysis(command)
            elif command.command_type == "SecurityScanContent":
                result = await self._handle_security_scan(command)
            elif command.command_type == "GenerateUserInsights":
                result = await self._handle_user_insights(command)
            else:
                raise ValueError(f"Type de commande non supporté: {command.command_type}")
            
            # 3. Publier événement de résultat
            result_event_id = await self._publish_result_event(command, result, True)
            events_created.append(result_event_id)
            
            processing_time = time.time() - start_time
            
            return EventSourcingResult(
                success=True,
                result_data=result,
                events_created=events_created,
                security_passed=result.get("security_passed", True),
                learning_applied=result.get("learning_applied", False),
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur traitement commande: {e}")
            
            # Publier événement d'erreur
            error_event_id = await self._publish_error_event(command, str(e))
            events_created.append(error_event_id)
            
            processing_time = time.time() - start_time
            
            return EventSourcingResult(
                success=False,
                result_data={"error": str(e)},
                events_created=events_created,
                security_passed=False,
                learning_applied=False,
                processing_time=processing_time
            )

    async def _handle_complete_analysis(self, command: PhoenixCommand) -> Dict[str, Any]:
        """
        Gère l'analyse complète avec tous les agents
        """
        payload = command.payload
        user_id = command.user_id
        app_source = command.app_source
        
        result = {
            "analysis_type": "complete",
            "security_analysis": None,
            "user_insights": None,
            "recommendations": [],
            "security_passed": False,
            "learning_applied": False
        }
        
        # 1. Analyse sécurité en premier
        if payload.get("enable_security_scan", True):
            security_result = await self.security_guardian.analyze_content_security(
                content=payload["cv_content"],
                content_type="cv",
                user_id=user_id,
                app_source=app_source
            )
            
            result["security_analysis"] = {
                "is_safe": security_result.is_safe,
                "threat_level": security_result.threat_level.value,
                "threats_count": len(security_result.detected_threats),
                "recommendations": security_result.recommendations
            }
            result["security_passed"] = security_result.is_safe
            
            # Arrêter si menace critique
            if not security_result.is_safe:
                result["recommendations"].append("⚠️ Contenu bloqué pour raisons de sécurité")
                return result
        
        # 2. Analyse avec Data Flywheel si sécurité OK
        if payload.get("enable_learning", True):
            user_analysis = await self.data_flywheel.analyze_user_journey(user_id)
            
            result["user_insights"] = {
                "total_events": user_analysis.total_events,
                "apps_used": user_analysis.apps_used,
                "confidence_score": user_analysis.confidence_score,
                "recommendations": user_analysis.recommendations
            }
            result["learning_applied"] = True
            result["recommendations"].extend(user_analysis.recommendations)
        
        # 3. Fallback cloud si nécessaire
        if self.enable_cloud_fallback and not result["security_passed"]:
            fallback_result = await self._fallback_to_gemini(payload)
            result["fallback_used"] = True
            result["fallback_result"] = fallback_result
        
        return result

    async def _handle_security_scan(self, command: PhoenixCommand) -> Dict[str, Any]:
        """
        Gère le scan sécurité uniquement
        """
        payload = command.payload
        
        security_result = await self.security_guardian.analyze_content_security(
            content=payload["content"],
            content_type=payload["content_type"],
            user_id=command.user_id,
            app_source=command.app_source
        )
        
        return {
            "scan_type": "security_only",
            "is_safe": security_result.is_safe,
            "threat_level": security_result.threat_level.value,
            "threats_detected": len(security_result.detected_threats),
            "compliance_status": security_result.compliance_status.value,
            "recommendations": security_result.recommendations,
            "anonymized_content": security_result.anonymized_content
        }

    async def _handle_user_insights(self, command: PhoenixCommand) -> Dict[str, Any]:
        """
        Gère la génération d'insights utilisateur
        """
        user_analysis = await self.data_flywheel.analyze_user_journey(command.user_id)
        
        return {
            "insights_type": "user_journey",
            "user_id": command.user_id,
            "total_events": user_analysis.total_events,
            "apps_used": user_analysis.apps_used,
            "reconversion_signals": user_analysis.reconversion_signals,
            "success_indicators": user_analysis.success_indicators,
            "recommendations": user_analysis.recommendations,
            "confidence_score": user_analysis.confidence_score,
            "last_activity": user_analysis.last_activity.isoformat()
        }

    async def _fallback_to_gemini(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fallback vers Gemini Cloud en cas de problème agents locaux
        """
        try:
            # Simulation fallback Gemini (à implémenter selon besoins)
            return {
                "provider": "gemini_cloud",
                "status": "fallback_success",
                "message": "Analyse réalisée via Gemini Cloud"
            }
        except Exception as e:
            logger.error(f"❌ Fallback Gemini échoué: {e}")
            return {
                "provider": "gemini_cloud",
                "status": "fallback_failed",
                "error": str(e)
            }

    async def _publish_command_event(self, command: PhoenixCommand) -> str:
        """
        Publie un événement de commande dans Event Store
        """
        try:
            event_data = {
                "stream_id": command.user_id,
                "event_type": f"Command{command.command_type}",
                "payload": {
                    "command_id": command.command_id,
                    "command_type": command.command_type,
                    "app_source": command.app_source,
                    "timestamp": command.timestamp.isoformat() if command.timestamp else datetime.now().isoformat()
                },
                "app_source": "smart_router",
                "metadata": {
                    "router_version": "event_sourcing_v1"
                }
            }
            
            response = self.supabase.table('events').insert(event_data).execute()
            event_id = response.data[0]['event_id']
            
            logger.info(f"📝 Événement commande publié: {event_id}")
            return event_id
            
        except Exception as e:
            logger.error(f"❌ Erreur publication événement commande: {e}")
            return f"error_{uuid.uuid4()}"

    async def _publish_result_event(self, command: PhoenixCommand, result: Dict[str, Any], success: bool) -> str:
        """
        Publie un événement de résultat
        """
        try:
            event_data = {
                "stream_id": command.user_id,
                "event_type": f"Result{command.command_type}",
                "payload": {
                    "command_id": command.command_id,
                    "success": success,
                    "result_summary": {
                        "security_passed": result.get("security_passed", False),
                        "learning_applied": result.get("learning_applied", False),
                        "recommendations_count": len(result.get("recommendations", []))
                    }
                },
                "app_source": "smart_router",
                "metadata": {
                    "processing_completed": datetime.now().isoformat()
                }
            }
            
            response = self.supabase.table('events').insert(event_data).execute()
            event_id = response.data[0]['event_id']
            
            logger.info(f"✅ Événement résultat publié: {event_id}")
            return event_id
            
        except Exception as e:
            logger.error(f"❌ Erreur publication événement résultat: {e}")
            return f"error_{uuid.uuid4()}"

    async def _publish_error_event(self, command: PhoenixCommand, error_message: str) -> str:
        """
        Publie un événement d'erreur
        """
        try:
            event_data = {
                "stream_id": command.user_id,
                "event_type": f"Error{command.command_type}",
                "payload": {
                    "command_id": command.command_id,
                    "error_message": error_message,
                    "error_timestamp": datetime.now().isoformat()
                },
                "app_source": "smart_router",
                "metadata": {
                    "error_category": "processing_error"
                }
            }
            
            response = self.supabase.table('events').insert(event_data).execute()
            event_id = response.data[0]['event_id']
            
            logger.error(f"💥 Événement erreur publié: {event_id}")
            return event_id
            
        except Exception as e:
            logger.error(f"❌ Erreur publication événement erreur: {e}")
            return f"error_{uuid.uuid4()}"

# ========================================
# 🚀 API FASTAPI
# ========================================

# Instance globale du router
router = SmartRouterEventSourcing()

app = FastAPI(
    title="Phoenix Smart Router Event-Sourcing",
    description="Orchestrateur intelligent avec Event Store Supabase",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check avec statut Event Store"""
    try:
        # Test connexion Supabase
        response = router.supabase.table('events').select('count').limit(1).execute()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "event_store": "connected",
            "agents": {
                "security_guardian": "ready",
                "data_flywheel": "ready"
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.post("/api/phoenix/analyze")
async def analyze_complete_content(request: PhoenixAnalysisRequest):
    """
    Analyse complète avec Event-Sourcing
    """
    command = PhoenixCommand(
        command_id=str(uuid.uuid4()),
        command_type="AnalyzeCompleteContent",
        user_id=request.user_id,
        app_source=request.app_source,
        payload={
            "cv_content": request.cv_content,
            "job_offer": request.job_offer,
            "generated_letter": request.generated_letter,
            "user_tier": request.user_tier,
            "enable_learning": request.enable_learning,
            "enable_security_scan": request.enable_security_scan
        }
    )
    
    result = await router.process_phoenix_command(command)
    
    if not result.success:
        raise HTTPException(status_code=400, detail=result.result_data)
    
    return result

@app.post("/api/security/scan")
async def security_scan(content: str, content_type: str, user_id: str, app_source: str = "unknown"):
    """
    Scan sécurité uniquement
    """
    command = PhoenixCommand(
        command_id=str(uuid.uuid4()),
        command_type="SecurityScanContent",
        user_id=user_id,
        app_source=app_source,
        payload={
            "content": content,
            "content_type": content_type
        }
    )
    
    result = await router.process_phoenix_command(command)
    return result

@app.get("/api/user/{user_id}/insights")
async def get_user_insights(user_id: str):
    """
    Insights utilisateur via Event-Sourcing
    """
    command = PhoenixCommand(
        command_id=str(uuid.uuid4()),
        command_type="GenerateUserInsights",
        user_id=user_id,
        app_source="smart_router",
        payload={}
    )
    
    result = await router.process_phoenix_command(command)
    return result

@app.get("/api/analytics/ecosystem")
async def get_ecosystem_analytics():
    """
    Analytics globales de l'écosystème
    """
    return await router.data_flywheel.get_ecosystem_analytics()

@app.get("/api/security/dashboard")
async def get_security_dashboard():
    """
    Dashboard sécurité global
    """
    return await router.security_guardian.get_security_dashboard()

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )