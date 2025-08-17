"""
🤖 ALESSIO BASE CLIENT - Client de base pour l'agent Alessio
Client de base partagé entre toutes les implémentations (Streamlit, React, etc.)
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

import httpx
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class AlessioAppContext(str, Enum):
    """Contextes d'application pour personnaliser les réponses d'Alessio"""
    LETTERS = "phoenix-letters"      # Génération lettres de motivation
    CV = "phoenix-cv"               # Optimisation CV et templates
    RISE = "phoenix-rise"           # Journal développement personnel
    WEBSITE = "phoenix-website"     # Site vitrine et marketing

class AlessioMessage(BaseModel):
    """Message dans une conversation avec Alessio"""
    role: str = Field(..., description="Role: 'user' ou 'assistant'")
    content: str = Field(..., description="Contenu du message")
    timestamp: datetime = Field(default_factory=datetime.now)
    app_context: Optional[AlessioAppContext] = None

class AlessioResponse(BaseModel):
    """Réponse d'Alessio avec métadonnées"""
    reply: str
    status: str = "success"
    app_context: Optional[AlessioAppContext] = None
    suggestions: Optional[List[str]] = None
    rate_limit_remaining: Optional[int] = None

class AlessioBaseClient:
    """
    Client de base pour interagir avec l'agent Alessio.
    Utilisé par les implémentations spécifiques (Streamlit, React, etc.)
    """
    
    def __init__(
        self, 
        api_url: str = "http://localhost:8003/api/v1/chat",
        app_context: AlessioAppContext = AlessioAppContext.LETTERS,
        timeout: int = 60
    ):
        self.api_url = api_url
        self.app_context = app_context
        self.timeout = timeout
        self.session = httpx.AsyncClient(timeout=timeout)
    
    def _build_contextual_message(self, message: str) -> str:
        """
        Enrichit le message utilisateur avec le contexte de l'application.
        """
        context_prefixes = {
            AlessioAppContext.LETTERS: "Dans le contexte de génération de lettres de motivation: ",
            AlessioAppContext.CV: "Dans le contexte d'optimisation de CV: ",
            AlessioAppContext.RISE: "Dans le contexte de développement personnel et journal: ",
            AlessioAppContext.WEBSITE: "Dans le contexte général Phoenix: "
        }
        
        prefix = context_prefixes.get(self.app_context, "")
        return f"{prefix}{message}"
    
    async def send_message(
        self, 
        message: str, 
        auth_token: str,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> AlessioResponse:
        """
        Envoie un message à Alessio et retourne la réponse.
        
        Args:
            message: Message utilisateur
            auth_token: Token d'authentification Phoenix
            additional_context: Contexte additionnel spécifique à l'app
        
        Returns:
            AlessioResponse avec la réponse d'Alessio
        """
        try:
            # Construction du message contextuel
            contextual_message = self._build_contextual_message(message)
            
            # Headers avec authentification
            headers = {"Authorization": f"Bearer {auth_token}"}
            
            # Payload avec contexte app
            payload = {
                "message": contextual_message,
                "context": {
                    "app": self.app_context.value,
                    "additional": additional_context or {}
                }
            }
            
            logger.info(f"Envoi message à Alessio - App: {self.app_context.value}")
            
            response = await self.session.post(
                self.api_url,
                json=payload,
                headers=headers
            )
            
            # Gestion des différents codes de statut
            if response.status_code == 200:
                data = response.json()
                return AlessioResponse(
                    reply=data["reply"],
                    app_context=self.app_context,
                    rate_limit_remaining=response.headers.get("X-RateLimit-Remaining")
                )
            elif response.status_code == 401:
                return AlessioResponse(
                    reply="🔒 Session expirée. Reconnectez-vous pour continuer.",
                    status="auth_error"
                )
            elif response.status_code == 402:
                return AlessioResponse(
                    reply="📊 Limite quotidienne atteinte. Passez à PREMIUM pour un accès illimité.",
                    status="quota_exceeded"
                )
            elif response.status_code == 429:
                return AlessioResponse(
                    reply="⏳ Trop de requêtes. Patientez quelques instants.",
                    status="rate_limited"
                )
            elif response.status_code == 403:
                return AlessioResponse(
                    reply="💫 Accès refusé. Vérifiez votre email ou contactez le support.",
                    status="access_denied"
                )
            else:
                response.raise_for_status()
                
        except httpx.RequestError as e:
            logger.error(f"Erreur connexion Alessio: {e}")
            return AlessioResponse(
                reply="😢 Alessio est temporairement indisponible. Réessayez dans quelques minutes.",
                status="service_unavailable"
            )
        except Exception as e:
            logger.error(f"Erreur inattendue Alessio: {e}")
            return AlessioResponse(
                reply="😢 Une erreur inattendue s'est produite.",
                status="error"
            )
    
    def send_message_sync(
        self, 
        message: str, 
        auth_token: str,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> AlessioResponse:
        """Version synchrone de send_message pour compatibilité Streamlit"""
        return asyncio.run(self.send_message(message, auth_token, additional_context))
    
    def get_app_specific_suggestions(self) -> List[str]:
        """
        Retourne des suggestions de questions spécifiques au contexte de l'app.
        """
        suggestions = {
            AlessioAppContext.LETTERS: [
                "Comment personnaliser ma lettre pour ce poste ?",
                "Quels mots-clés ATS utiliser ?",
                "Comment structurer ma motivation ?",
                "Aide-moi à optimiser mon accroche"
            ],
            AlessioAppContext.CV: [
                "Comment améliorer mon CV pour l'ATS ?",
                "Quelles compétences mettre en avant ?",
                "Comment structurer mes expériences ?",
                "Aide-moi à choisir un template"
            ],
            AlessioAppContext.RISE: [
                "Comment progresser dans ma reconversion ?",
                "Quels objectifs me fixer cette semaine ?",
                "Comment gérer mes émotions ?",
                "Aide-moi à analyser mes progrès"
            ],
            AlessioAppContext.WEBSITE: [
                "Présente-moi l'écosystème Phoenix",
                "Quels sont les avantages de chaque app ?",
                "Comment Phoenix peut-il m'aider ?",
                "Quelle app commencer en premier ?"
            ]
        }
        
        return suggestions.get(self.app_context, [])
    
    async def close(self):
        """Ferme la session HTTP"""
        await self.session.aclose()
    
    def __del__(self):
        """Nettoyage automatique"""
        try:
            asyncio.run(self.close())
        except Exception:
            # Silently ignore cleanup errors in destructor
            pass