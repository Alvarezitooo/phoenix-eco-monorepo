"""
Middleware de gestion d'erreurs centralisé
"""

import logging
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import traceback

logger = logging.getLogger(__name__)

class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware pour gérer les erreurs de manière centralisée"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
            
        except HTTPException as e:
            # Les HTTPException sont déjà gérées par FastAPI
            raise e
            
        except Exception as e:
            # Log de l'erreur complète
            logger.error(f"Unhandled exception: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            # Réponse d'erreur générique pour la production
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Erreur interne du serveur",
                    "type": "internal_server_error",
                    "timestamp": "now()"
                }
            )