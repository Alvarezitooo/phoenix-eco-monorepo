import os
import time
import logging
from typing import List, Dict, Any

import google.generativeai as genai
from fastapi import FastAPI, Depends, HTTPException, Request
from pydantic import BaseModel, Field, validator

from prompt_template import IRIS_MASTER_PROMPT
from security import (
    PromptInjectionGuard, 
    RateLimiter, 
    validate_user_id, 
    secure_error_message
)
from auth_integration import get_current_user, get_optional_user, check_daily_limit, auth_manager

# --- Configuration & Security ---
# Configuration logging sécurisé
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('iris_agent.log')
    ]
)
logger = logging.getLogger(__name__)

# Load the Gemini API key from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set.")
genai.configure(api_key=GEMINI_API_KEY)

# Initialisation composants sécurité
injection_guard = PromptInjectionGuard()
rate_limiter = RateLimiter(max_requests=15, window_minutes=1)  # 15 req/min max

# --- Cache Implementation (in-memory) ---
CONTEXT_CACHE = {}
CACHE_DURATION_SECONDS = 300  # 5 minutes

# --- Enhanced PhoenixEventBridge with User Context ---
class PhoenixEventBridge:
    def get_user_events(self, user_id: str, user_tier: str = "FREE") -> List[Dict[str, Any]]:
        """Récupère les événements utilisateur avec contextualisation selon le tier"""
        logger.info(f"Fetching events for user: {user_id}, tier: {user_tier}")
        
        # Events de base pour tous les utilisateurs
        base_events = [
            {"event_type": "letter_generated", "score": 85, "timestamp": "2025-08-05T10:00:00Z"},
            {"event_type": "cv_updated", "ats_score": 92, "timestamp": "2025-08-05T10:05:00Z"},
        ]
        
        # Events enrichis pour les utilisateurs PREMIUM+
        if user_tier in ["PREMIUM", "ENTERPRISE"]:
            base_events.extend([
                {"event_type": "mood_tracked", "mood": "optimistic", "timestamp": "2025-08-05T10:10:00Z"},
                {"event_type": "trajectory_analyzed", "progress": 78, "timestamp": "2025-08-05T09:45:00Z"},
            ])
        
        return base_events

def get_event_bridge():
    return PhoenixEventBridge()

# --- AI & Post-Processing Logic ---
def post_process_response(text: str) -> str:
    """Cleans and refines the raw AI response."""
    # Simple rule: truncate to a max length to avoid overly long responses
    max_length = 350
    if len(text) > max_length:
        text = text[:max_length] + "..."
    # Add more rules here (e.g., remove repetitions)
    return text

class GeminiService:
    def __init__(self, model_name: str = "gemini-1.5-flash"):
        self.model = genai.GenerativeModel(model_name)

    def generate_reply(self, user_events: str, user_message: str) -> str:
        # Validation sécurité avant génération
        is_malicious, detected_patterns = injection_guard.is_potentially_malicious(user_message)
        if is_malicious:
            logger.warning(f"Tentative d'injection détectée: {detected_patterns}")
            return "Je ne peux pas traiter cette demande. Pouvez-vous reformuler votre question de manière plus claire ?"
        
        # Sanitisation de l'input
        sanitized_message = injection_guard.sanitize_input(user_message)
        
        prompt = IRIS_MASTER_PROMPT.format(
            user_events=user_events,
            user_message=sanitized_message
        )
        try:
            response = self.model.generate_content(prompt)
            processed_response = post_process_response(response.text)
            logger.info("Réponse IA générée avec succès")
            return processed_response
        except Exception as e:
            logger.error(f"Erreur API Gemini: {type(e).__name__}")
            raise HTTPException(status_code=500, detail=secure_error_message(e))

def get_gemini_service():
    return GeminiService()

# --- Context Builder Logic ---
def build_context_summary(events: List[Dict[str, Any]]) -> str:
    if not events:
        return "No recent activity found for the user."
    summary_parts = [f"- {event['event_type']} at {event['timestamp']}" for event in events]
    return "User's recent activity:\n" + "\n".join(summary_parts)

# --- Pydantic Models ---
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=500)
    context: Optional[Dict[str, Any]] = None  # Contexte additionnel optionnel
    
    @validator('message')
    def validate_message_content(cls, v):
        if not v.strip():
            raise ValueError('Message ne peut pas être vide')
        return v.strip()

class ChatResponse(BaseModel):
    reply: str

# --- FastAPI App ---
app = FastAPI(
    title="Iris Agent API",
    description="The AI consciousness of the Phoenix ecosystem.",
    version="0.1.0",
)

# --- API Endpoints ---
@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    http_request: Request,
    current_user = Depends(get_current_user),
    event_bridge: PhoenixEventBridge = Depends(get_event_bridge),
    gemini_service: GeminiService = Depends(get_gemini_service),
):
    user_id = str(current_user.id)
    user_tier = current_user.subscription.current_tier.value if current_user.subscription.current_tier else "FREE"
    
    # Rate limiting par utilisateur authentifié
    if rate_limiter.is_rate_limited(user_id):
        logger.warning(f"Rate limit dépassé pour user: {user_id}")
        raise HTTPException(
            status_code=429, 
            detail="Trop de requêtes. Veuillez patienter avant de réessayer."
        )
    
    # Vérification des limites quotidiennes selon le tier
    # Compteur de messages quotidiens (sera implémenté avec la base de données)
    current_daily_usage = 0  # Récupéré depuis la base de données
    if not check_daily_limit(current_user, current_daily_usage):
        limits = auth_manager.get_user_tier_limits(current_user)
        raise HTTPException(
            status_code=402,
            detail=f"Limite quotidienne atteinte ({limits['daily_messages']} messages/jour). Passez à PREMIUM pour plus d'accès."
        )
    
    # Log de la requête (sans contenu sensible)
    client_ip = http_request.client.host
    logger.info(f"Requête chat - User: {user_id}, Tier: {user_tier}, IP: {client_ip}")
    
    current_time = time.time()

    if user_id in CONTEXT_CACHE and (current_time - CONTEXT_CACHE[user_id]['timestamp']) < CACHE_DURATION_SECONDS:
        context_summary = CONTEXT_CACHE[user_id]['summary']
    else:
        user_events = event_bridge.get_user_events(user_id, user_tier)
        context_summary = build_context_summary(user_events)
        CONTEXT_CACHE[user_id] = {"summary": context_summary, "timestamp": current_time}

    ai_reply = gemini_service.generate_reply(
        user_events=context_summary,
        user_message=request.message
    )
    return ChatResponse(reply=ai_reply)

@app.get("/health")
async def health_check():
    return {"status": "Iris is awake and listening..."}
