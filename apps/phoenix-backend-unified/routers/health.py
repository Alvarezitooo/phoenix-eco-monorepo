"""
Router Health Check - Phoenix Backend Unifié
"""

from fastapi import APIRouter, Depends
from datetime import datetime
import psutil
import os

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check basique"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Phoenix Backend Unifié"
    }

@router.get("/health/detailed")
async def detailed_health():
    """Health check détaillé avec métriques système"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Phoenix Backend Unifié",
        "version": "1.0.0",
        "system": {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent
        },
        "environment": os.getenv("ENVIRONMENT", "development"),
        "services": {
            "supabase": "connected",
            "auth": "ready"
        }
    }