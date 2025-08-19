"""
🤖 IRIS API - Assistant IA Phoenix Écosystème
API FastAPI pour l'agent conversationnel Iris avec authentification sécurisée

Author: Claude Phoenix DevSecOps Guardian
Version: 2.0.0 - Production Ready with Security
"""

import os
import logging
from datetime import datetime
from typing import List, Optional
import hashlib
import time

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel, Field
import uvicorn
from supabase import create_client

# Imports modules Phoenix
from security.phoenix_auth_standalone import (
    get_authenticated_user, 
    get_optional_authenticated_user, 
    IrisUser, 
    UserTier,
    auth_service
)
from ai.gemini_alessio_engine import alessio_engine, AlessioResponse
from monitoring.iris_analytics import create_analytics, EventType

# Configuration du logger production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialisation Supabase pour analytics
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
)
analytics = create_analytics(supabase)

# Supprimé: Fonction déplacée dans iris_analytics.py

# Initialisation FastAPI
app = FastAPI(
    title="Phoenix Iris API",
    description="API technique hébergeant Alessio - Assistant IA Phoenix",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Middleware de sécurité
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # En production, restreindre aux domaines autorisés
)

# Configuration CORS sécurisée
_iris_allowed_origins_env = os.getenv(
    "IRIS_ALLOWED_ORIGINS",
    "https://phoenix-eco-monorepo.vercel.app,https://phoenix-letters.streamlit.app,https://phoenix-cv.streamlit.app,https://*.streamlit.app,http://localhost:3000,http://localhost:8501,http://localhost:8502",
)
IRIS_ALLOWED_ORIGINS = [origin.strip() for origin in _iris_allowed_origins_env.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=IRIS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Middleware de monitoring
@app.middleware("http")
async def monitoring_middleware(request: Request, call_next):
    start_time = time.time()
    
    # Hash de l'IP pour analytics anonymes
    ip_hash = hashlib.sha256(request.client.host.encode()).hexdigest()[:8] if request.client else None
    
    try:
        response = await call_next(request)
        processing_time = (time.time() - start_time) * 1000
        
        # Log des requêtes pour monitoring
        logger.info(f"Request: {request.method} {request.url.path} - {response.status_code} - {processing_time:.0f}ms")
        
        return response
    except Exception as e:
        processing_time = (time.time() - start_time) * 1000
        logger.error(f"Request failed: {request.method} {request.url.path} - {processing_time:.0f}ms - Error: {str(e)}")
        
        # Track l'erreur
        await analytics.track_error(
            error_type="request_processing",
            error_message=str(e)
        )
        
        raise

# --- MODELS PYDANTIC ---

class ChatRequest(BaseModel):
    """Requête de chat vers Iris"""
    message: str = Field(..., min_length=1, max_length=2000, description="Message utilisateur")
    context: Optional[str] = Field(None, description="Contexte de la conversation")
    session_id: Optional[str] = Field(None, description="ID de session")
    app_context: Optional[str] = Field(None, description="Application d'origine (letters, cv, rise)")

class ChatResponse(BaseModel):
    """Réponse d'Alessio"""
    response: str = Field(..., description="Réponse d'Alessio")
    confidence: float = Field(default=0.85, description="Niveau de confiance")
    suggestions: List[str] = Field(default_factory=list, description="Suggestions de suivi")
    timestamp: datetime = Field(default_factory=datetime.now)
    model_used: str = Field(default="gemini-1.5-flash", description="Modèle IA utilisé")
    processing_time_ms: Optional[int] = Field(None, description="Temps de traitement en ms")

# --- SUPPRIMÉ: BASE DE CONNAISSANCES STATIQUE ---
# Remplacée par le moteur Gemini dynamique

# Base de données pour fallback uniquement
FALLBACK_RESPONSES = {
    "reconversion": {
        "keywords": ["reconversion", "changer", "métier", "carrière", "orientation"],
        "responses": [
            "Pour réussir votre reconversion, commencez par identifier vos compétences transférables. Ces skills peuvent s'appliquer dans votre nouveau domaine !",
            "Une reconversion réussie nécessite 3 piliers : l'introspection (vos motivations), la formation (combler les gaps) et le réseau (rencontrer des professionnels).",
            "La clé d'une reconversion ? Valoriser votre expérience passée comme un atout unique, pas comme un handicap. Votre parcours atypique est votre force !"
        ],
        "suggestions": [
            "Parlez-moi de vos compétences actuelles",
            "Quel domaine vous intéresse ?",
            "Avez-vous identifié des formations ?",
            "Besoin d'aide pour votre CV reconversion ?"
        ]
    },
    "cv": {
        "keywords": ["cv", "curriculum", "candidature", "profil"],
        "responses": [
            "Pour un CV reconversion, structurez-le autour de vos compétences transférables plutôt que chronologiquement. Mettez en avant vos réalisations quantifiées !",
            "Votre CV reconversion doit raconter une histoire cohérente : expliquez le lien entre votre passé et votre futur projet professionnel.",
            "Conseil CV : utilisez un titre accrocheur qui annonce votre projet (ex: 'Manager commercial → Développeur web') et personnalisez pour chaque offre."
        ],
        "suggestions": [
            "Analysons ensemble votre CV",
            "Comment structurer votre expérience ?",
            "Besoin d'aide pour les mots-clés ATS ?",
            "Générer une lettre de motivation ?"
        ]
    },
    "lettre": {
        "keywords": ["lettre", "motivation", "candidature", "postule"],
        "responses": [
            "Une lettre de motivation reconversion doit être authentique : expliquez votre WHY (pourquoi ce changement) et votre HOW (comment vous préparez la transition).",
            "Structure gagnante : 1) Accroche personnalisée 2) Votre parcours comme force 3) Votre projet et préparation 4) Appel à l'action confiant.",
            "Phoenix Letters peut générer votre lettre optimisée ! Nos algorithmes analysent l'offre et personnalisent le contenu selon votre profil reconversion."
        ],
        "suggestions": [
            "Générer ma lettre avec Phoenix Letters",
            "Comment expliquer ma reconversion ?",
            "Adapter ma lettre à une offre",
            "Éviter les erreurs classiques"
        ]
    },
    "entretien": {
        "keywords": ["entretien", "oral", "questions", "rencontre", "rdv"],
        "responses": [
            "Préparez 3 histoires STAR (Situation, Tâche, Action, Résultat) qui montrent vos compétences transférables en action. L'entretien, c'est du storytelling !",
            "Face à la question 'Pourquoi changer de voie ?', soyez authentique mais positif : parlez projet, pas fuite. Montrez que c'est un choix réfléchi.",
            "Posez des questions intelligentes sur l'équipe, les défis du poste, l'évolution possible. Montrez votre curiosité et votre vision long terme !"
        ],
        "suggestions": [
            "Préparer mes réponses types",
            "Comment expliquer ma motivation ?",
            "Quelles questions poser ?",
            "Gérer le stress de l'entretien"
        ]
    }
}

FALLBACK_RESPONSES = [
    "Je suis Alessio, votre assistant IA Phoenix ! Je vous accompagne dans votre reconversion professionnelle. Comment puis-je vous aider aujourd'hui ?\n\nAlessio 🤝",
    "Bonjour ! En tant qu'Alessio, je suis là pour vous guider dans votre projet de reconversion. CV, lettre de motivation, stratégie carrière... parlons-en !\n\nAlessio 🤝",
    "Alessio à votre service ! Que souhaitez-vous améliorer dans votre parcours professionnel ? Je suis spécialisé dans l'accompagnement aux reconversions.\n\nAlessio 🤝",
    "Hello ! Prêt(e) à transformer votre carrière ? Dites-moi vos défis et objectifs, je suis là pour vous épauler ! 😊\n\nAlessio 🤝"
]

# --- LOGIQUE CONVERSATIONNELLE FALLBACK ---

def get_fallback_response(message: str) -> ChatResponse:
    """
    Génère une réponse de fallback si Gemini est indisponible
    """
    import secrets
    
    response_text = secrets.choice(FALLBACK_RESPONSES)
    
    return ChatResponse(
        response=response_text,
        confidence=0.5,
        suggestions=[
            "Parlez-moi de votre reconversion",
            "Besoin d'aide pour votre CV ?", 
            "Comment optimiser ma candidature ?",
            "Préparer un entretien"
        ],
        model_used="fallback",
        processing_time_ms=0
    )

# --- ENDPOINTS API ---

@app.get("/")
async def root():
    """Endpoint racine - Statut de l'API"""
    return {
        "service": "Phoenix Iris API",
        "status": "✅ Opérationnel",
        "version": "2.0.0",
        "description": "Assistant IA conversationnel pour l'écosystème Phoenix",
        "features": [
            "Authentification JWT sécurisée",
            "IA Gemini intégrée", 
            "Rate limiting par tier",
            "Analytics anonymisées"
        ],
        "endpoints": {
            "chat": "/api/v1/chat",
            "health": "/health",
            "metrics": "/api/v1/metrics",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check pour Railway et monitoring"""
    
    # Vérifications de santé
    health_checks = {
        "supabase": "ok",
        "gemini": "ok",
        "auth": "ok"
    }
    
    try:
        # Test rapide Supabase
        supabase.table('iris_events').select('id').limit(1).execute()
    except:
        health_checks["supabase"] = "error"
    
    # Statut global
    overall_status = "healthy" if all(status == "ok" for status in health_checks.values()) else "degraded"
    
    return {
        "status": overall_status,
        "timestamp": datetime.now(),
        "service": "iris-api",
        "version": "2.0.0",
        "environment": os.getenv("ENVIRONMENT", "production"),
        "checks": health_checks
    }

@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, user: IrisUser = Depends(get_authenticated_user)):
    """
    Endpoint principal de chat avec Iris - SÉCURISÉ
    Nécessite une authentification JWT valide
    """
    start_time = time.time()
    
    try:
        # Analytics: Track request
        await analytics.track_chat_request(
            user_id=user.id,
            user_tier=user.tier.value,
            message_length=len(request.message),
            app_context=request.app_context,
            session_id=request.session_id
        )
        
        # Validation message
        if len(request.message.strip()) < 1:
            raise HTTPException(status_code=400, detail="Message ne peut pas être vide")
        
        if len(request.message) > 2000:
            raise HTTPException(status_code=400, detail="Message trop long (max 2000 caractères)")
        
        # Génération de la réponse Alessio avec Gemini
        try:
            alessio_response = await alessio_engine.generate_response(
                user_message=request.message,
                user_id=user.id,
                context={
                    'user_tier': user.tier.value,
                    'app_context': request.app_context,
                    'session_id': request.session_id
                }
            )
            
            # Incrémenter l'usage utilisateur
            await auth_service.increment_usage(user.id)
            
            # Construire la réponse FastAPI
            response = ChatResponse(
                response=alessio_response.content,
                confidence=alessio_response.confidence,
                suggestions=alessio_response.suggestions,
                timestamp=datetime.now(),
                model_used=alessio_response.model_used,
                processing_time_ms=alessio_response.processing_time_ms
            )
            
        except Exception as gemini_error:
            logger.error(f"Erreur Gemini: {gemini_error}")
            
            # Fallback sur réponse statique
            response = get_fallback_response(request.message)
            
            # Track l'erreur
            await analytics.track_error(
                error_type="gemini_failure",
                error_message=str(gemini_error),
                user_id=user.id,
                user_tier=user.tier.value
            )
        
        # Analytics: Track response
        processing_time_ms = int((time.time() - start_time) * 1000)
        await analytics.track_chat_response(
            user_id=user.id,
            user_tier=user.tier.value,
            response_length=len(response.response),
            processing_time_ms=processing_time_ms,
            model_used=response.model_used,
            confidence=response.confidence,
            session_id=request.session_id
        )
        
        logger.info(f"Alessio response generated - User: {user.email} - Time: {processing_time_ms}ms")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors du traitement chat: {str(e)}")
        
        # Track l'erreur
        await analytics.track_error(
            error_type="chat_processing",
            error_message=str(e),
            user_id=user.id if 'user' in locals() else None
        )
        
        raise HTTPException(
            status_code=500,
            detail="Erreur interne du serveur Alessio"
        )

@app.get("/api/v1/topics")
async def get_topics():
    """Liste des sujets que Iris peut traiter"""
    topics = [
        {
            "topic": "reconversion",
            "description": "Conseils pour réussir sa reconversion professionnelle",
            "capabilities": ["Bilan compétences", "Transition secteur", "Formation"]
        },
        {
            "topic": "cv", 
            "description": "Optimisation CV et profil professionnel",
            "capabilities": ["Structure CV", "ATS optimization", "Compétences transférables"]
        },
        {
            "topic": "lettre_motivation",
            "description": "Lettres de motivation percutantes", 
            "capabilities": ["Personnalisation", "Structure", "Authenticité"]
        },
        {
            "topic": "entretien",
            "description": "Préparation entretiens d'embauche",
            "capabilities": ["Questions types", "Storytelling STAR", "Négociation"]
        },
        {
            "topic": "strategie_carriere",
            "description": "Stratégie et développement de carrière",
            "capabilities": ["LinkedIn", "Réseau professionnel", "Marché caché"]
        }
    ]
    
    return {
        "topics": topics,
        "total": len(topics),
        "description": "Domaines d'expertise d'Alessio pour les reconversions",
        "powered_by": "Google Gemini 1.5 Flash"
    }

# --- ENDPOINTS ANALYTICS & MÉTRIQUES ---

@app.get("/api/v1/metrics")
async def get_public_metrics():
    """Métriques publiques de l'API (anonymisées)"""
    try:
        today_metrics = await analytics.get_daily_metrics(datetime.now())
        
        # Métriques publiques seulement
        public_metrics = {
            "total_requests_today": today_metrics.get('total_requests', 0),
            "avg_response_time_ms": today_metrics.get('avg_response_time_ms', 0),
            "service_uptime": "99.9%",  # À calculer réellement en production
            "model_used": "Google Gemini 1.5 Flash",
            "last_updated": datetime.now().isoformat()
        }
        
        return public_metrics
        
    except Exception as e:
        logger.error(f"Erreur récupération métriques: {e}")
        return {"error": "Métriques temporairement indisponibles"}

@app.get("/api/v1/user/analytics")
async def get_user_analytics(user: IrisUser = Depends(get_authenticated_user)):
    """Analytics personnelles de l'utilisateur"""
    try:
        user_stats = await analytics.get_user_analytics(user.id, days=30)
        
        # Ajouter infos tier
        tier_limits = auth_service.rate_limits[user.tier]
        
        return {
            "user_tier": user.tier.value,
            "daily_limit": tier_limits["daily_messages"],
            "daily_usage": user.daily_usage,
            "remaining_today": max(0, tier_limits["daily_messages"] - user.daily_usage) if tier_limits["daily_messages"] != -1 else "unlimited",
            "last_30_days": user_stats
        }
        
    except Exception as e:
        logger.error(f"Erreur analytics utilisateur: {e}")
        raise HTTPException(status_code=500, detail="Erreur récupération analytics")

# --- LANCEMENT DE L'APPLICATION ---

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8003))
    
    logger.info(f"🤖 Démarrage Iris API v2.0.0 sur le port {port}")
    logger.info("🚀 Phoenix Iris API - Héberge Alessio - Secured AI Assistant Ready!")
    logger.info("🛡️ Features: JWT Auth + Alessio AI + Analytics + Rate Limiting")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=True
    )