"""
🔥 Phoenix Backend Unifié - FastAPI Application
Backend centralisé pour Phoenix Aube + Phoenix Rise + Phoenix CV

Author: Claude Phoenix DevSecOps Guardian
Version: 1.0.0 - Production Ready
"""

import os
import logging
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer
import uvicorn

from routers import auth, aube, rise, health
from services.supabase_client import SupabaseClient
from services.auth_service import AuthService
from middleware.error_handler import ErrorHandlerMiddleware
from config.settings import settings

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Services globaux
supabase_client = None
auth_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestionnaire de cycle de vie de l'application"""
    global supabase_client, auth_service
    
    logger.info("🔥 Starting Phoenix Backend Unifié...")
    
    # Initialisation services
    supabase_client = SupabaseClient()
    auth_service = AuthService(supabase_client)
    
    logger.info("✅ Services initialized successfully")
    
    yield
    
    logger.info("🔄 Shutting down Phoenix Backend...")

# Application FastAPI
app = FastAPI(
    title="Phoenix Backend Unifié",
    description="Backend centralisé pour l'écosystème Phoenix (Aube, Rise, CV)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Middleware de sécurité
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Aube dev
        "http://localhost:3001",  # Rise dev
        "https://phoenix-aube.vercel.app",
        "https://phoenix-rise.vercel.app",
        "https://phoenix-cv.vercel.app",
        settings.allowed_origins
    ] if isinstance(settings.allowed_origins, list) else [settings.allowed_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if settings.environment == "development" else [
        "phoenix-backend.railway.app",
        "*.vercel.app"
    ]
)

# Middleware d'erreurs personnalisé
app.add_middleware(ErrorHandlerMiddleware)

# Inclusion des routers
app.include_router(health.router, tags=["Health"])
app.include_router(auth.router, prefix="/api/v1", tags=["Authentication"])
app.include_router(aube.router, prefix="/api/v1/aube", tags=["Phoenix Aube"])
app.include_router(rise.router, prefix="/api/v1/rise", tags=["Phoenix Rise"])

@app.get("/")
async def root():
    """Endpoint racine avec informations sur l'API"""
    return {
        "message": "🔥 Phoenix Backend Unifié",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "services": ["auth", "aube", "rise"],
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/status")
async def status():
    """Status détaillé des services"""
    return {
        "status": "operational",
        "services": {
            "supabase": "connected" if supabase_client else "disconnected",
            "auth": "ready" if auth_service else "not_ready"
        },
        "environment": settings.environment,
        "timestamp": datetime.utcnow().isoformat()
    }

# Point d'entrée pour développement local
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )