"""
🤖 ALESSIO API - Assistant IA Phoenix Letters
API FastAPI pour l'agent conversationnel Alessio

Author: Claude Phoenix DevSecOps
Version: 1.0.0 - Railway Deploy Ready
"""

import os
import logging
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Configuration du logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 🔬 RECHERCHE-ACTION PHOENIX - Anonymiseur de logs
def anonymize_for_research_logs(text: str, user_id: str = None) -> dict:
    """Anonymise les logs de conversation pour la recherche-action Phoenix"""
    import hashlib
    import re
    
    # Hash de l'utilisateur (si fourni)
    user_hash = None
    if user_id:
        user_hash = hashlib.sha256(f"{user_id}_research".encode()).hexdigest()[:16]
    
    # Anonymisation basique du texte
    anonymized_text = text
    # Suppression des emails
    anonymized_text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', anonymized_text)
    # Suppression des téléphones
    anonymized_text = re.sub(r'(?:\+33|0)[1-9](?:[0-9]{8})', '[PHONE]', anonymized_text)
    
    return {
        "user_hash": user_hash,
        "anonymized_query": anonymized_text[:100],  # Première partie seulement
        "query_length": len(text),
        "timestamp": datetime.now().isoformat(),
        "source": "alessio_api"
    }

# Initialisation FastAPI
app = FastAPI(
    title="Phoenix Alessio API",
    description="API conversationnelle pour l'assistant IA Alessio - Phoenix Letters",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration CORS pilotée par variables d'environnement
# ALESSIO_ALLOWED_ORIGINS peut contenir une liste séparée par des virgules
_alessio_allowed_origins_env = os.getenv(
    "ALESSIO_ALLOWED_ORIGINS",
    "https://phoenix-eco-monorepo.vercel.app,https://phoenix-letters.streamlit.app,https://*.streamlit.app,http://localhost:3000,http://localhost:8501,http://localhost:8502",
)
ALESSIO_ALLOWED_ORIGINS = [origin.strip() for origin in _alessio_allowed_origins_env.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALESSIO_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# --- MODELS PYDANTIC ---

class ChatRequest(BaseModel):
    """Requête de chat vers Alessio"""
    message: str = Field(..., min_length=1, max_length=2000, description="Message utilisateur")
    user_id: Optional[str] = Field(None, description="ID utilisateur Phoenix (optionnel)")
    context: Optional[str] = Field(None, description="Contexte de la conversation")
    session_id: Optional[str] = Field(None, description="ID de session")

class ChatResponse(BaseModel):
    """Réponse d'Alessio"""
    response: str = Field(..., description="Réponse d'Alessio")
    confidence: float = Field(default=0.85, description="Niveau de confiance")
    suggestions: List[str] = Field(default_factory=list, description="Suggestions de suivi")
    timestamp: datetime = Field(default_factory=datetime.now)

# --- BASE DE CONNAISSANCES ALESSIO ---

ALESSIO_KNOWLEDGE_BASE = {
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

DEFAULT_RESPONSES = [
    "Je suis Alessio, votre copilote carrière IA ! Je vous aide à réussir votre reconversion professionnelle. Parlez-moi de vos défis.",
    "Bonjour ! En quoi puis-je vous accompagner dans votre projet de reconversion ? CV, lettre de motivation, stratégie carrière... je suis là !",
    "Alessio à votre service ! Que souhaitez-vous améliorer dans votre reconversion : votre candidature, votre préparation d'entretien ou votre stratégie ?",
    "Hello ! Prêt(e) à booster votre reconversion ? Dites-moi où vous en êtes et comment je peux vous aider à atteindre vos objectifs carrière."
]

# --- LOGIQUE CONVERSATIONNELLE ---

def get_alessio_response(message: str, user_context: Optional[str] = None) -> ChatResponse:
    """
    Génère une réponse Alessio basée sur la base de connaissances
    """
    message_lower = message.lower()
    
    # Recherche de correspondance dans la base de connaissances
    for topic, data in ALESSIO_KNOWLEDGE_BASE.items():
        for keyword in data["keywords"]:
            if keyword in message_lower:
                import secrets
                response_text = secrets.choice(data["responses"])
                suggestions = data["suggestions"][:3]  # Max 3 suggestions
                
                logger.info(f"Alessio response generated - Topic: {topic}, User: {user_context}")
                
                return ChatResponse(
                    response=response_text,
                    confidence=0.88,
                    suggestions=suggestions
                )
    
    # Réponse par défaut si aucune correspondance
    import secrets
    default_response = secrets.choice(DEFAULT_RESPONSES)
    
    return ChatResponse(
        response=default_response,
        confidence=0.75,
        suggestions=[
            "Parlez-moi de votre reconversion",
            "Besoin d'aide pour votre CV ?", 
            "Comment optimiser ma candidature ?",
            "Préparer un entretien"
        ]
    )

# --- ENDPOINTS API ---

@app.get("/")
async def root():
    """Endpoint racine - Statut de l'API"""
    return {
        "service": "Phoenix Alessio API",
        "status": "✅ Opérationnel",
        "version": "1.0.0",
        "description": "Assistant IA pour reconversions professionnelles",
        "endpoints": {
            "chat": "/api/v1/chat",
            "health": "/health",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check pour Railway et monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "service": "alessio-api",
        "environment": os.getenv("ENVIRONMENT", "production")
    }

@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Endpoint principal de chat avec Alessio
    """
    try:
        # 🔬 RECHERCHE-ACTION PHOENIX - Log anonymisé pour recherche
        research_log = anonymize_for_research_logs(request.message, request.user_id)
        logger.info(f"Research log: {research_log}")
        
        # Validation et logging
        logger.info(f"Chat request received - User: {request.user_id}, Message length: {len(request.message)}")
        
        # Vérification longueur message
        if len(request.message.strip()) < 1:
            raise HTTPException(status_code=400, detail="Message ne peut pas être vide")
        
        if len(request.message) > 2000:
            raise HTTPException(status_code=400, detail="Message trop long (max 2000 caractères)")
        
        # Génération de la réponse Alessio
        response = get_alessio_response(
            message=request.message,
            user_context=f"User: {request.user_id}, Session: {request.session_id}"
        )
        
        logger.info(f"Alessio response generated successfully - Confidence: {response.confidence}")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors du traitement chat: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erreur interne du serveur Alessio"
        )

@app.get("/api/v1/topics")
async def get_topics():
    """Liste des sujets que Alessio peut traiter"""
    topics = []
    for topic, data in ALESSIO_KNOWLEDGE_BASE.items():
        topics.append({
            "topic": topic,
            "keywords": data["keywords"],
            "description": f"Conseils et aide sur : {topic}"
        })
    
    return {
        "topics": topics,
        "total": len(topics),
        "description": "Sujets maîtrisés par Alessio pour les reconversions"
    }

# --- LANCEMENT DE L'APPLICATION ---

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8003))
    
    logger.info(f"🤖 Démarrage Alessio API sur le port {port}")
    logger.info("🚀 Phoenix Alessio API - Ready to help career transitions!")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=True
    )