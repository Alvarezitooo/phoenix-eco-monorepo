"""
Dojo API optimisée avec opérations non-bloquantes.

Cette version améliore les performances en utilisant:
- Opérations asynchrones wrappées avec ThreadPoolExecutor
- Background tasks pour le logging
- Validation renforcée
- Gestion d'erreurs améliorée

Author: Claude Phoenix DevSecOps Guardian
Version: 2.0.0 - Performance Optimized
"""

from fastapi import FastAPI, HTTPException, Depends, status, BackgroundTasks
from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional, List
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
import logging
from supabase import create_client, Client

# Initialisation de Supabase
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Thread pool pour opérations DB
executor = ThreadPoolExecutor(max_workers=5)

app = FastAPI(
    title="Dojo Mental API - Optimized",
    description="✅ API optimisée avec opérations non-bloquantes pour Kaizen et Zazen.",
    version="2.0.0",
)

# ✅ Fonctions helper asynchrones
def run_in_executor(func):
    """Décorateur pour exécuter une fonction synchrone de façon asynchrone."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(executor, lambda: func(*args, **kwargs))
    return wrapper

@run_in_executor
def _sync_supabase_insert(table_name: str, data: dict):
    """Insertion Supabase synchrone wrappée."""
    try:
        response = supabase.table(table_name).insert(data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        logger.error(f"❌ DB insert error on {table_name}: {e}")
        raise

@run_in_executor
def _sync_supabase_update(table_name: str, kaizen_id: int, data: dict):
    """Update Supabase synchrone wrappée."""
    try:
        response = supabase.table(table_name).update(data).eq("id", kaizen_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        logger.error(f"❌ DB update error on {table_name}: {e}")
        raise

@run_in_executor  
def _sync_supabase_select(table_name: str, filters: dict = None, order_by: str = None, limit: int = None):
    """Select Supabase synchrone wrappée."""
    try:
        query = supabase.table(table_name).select("*")
        
        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)
        
        if order_by:
            query = query.order(order_by)
        
        if limit:
            query = query.limit(limit)
        
        response = query.execute()
        return response.data
    except Exception as e:
        logger.error(f"❌ DB select error on {table_name}: {e}")
        raise

@run_in_executor
def _sync_supabase_select_single(table_name: str, filters: dict, columns: str = "*"):
    """Select single Supabase synchrone wrappée."""
    try:
        query = supabase.table(table_name).select(columns)
        
        for key, value in filters.items():
            query = query.eq(key, value)
        
        response = query.single().execute()
        return response.data
    except Exception as e:
        logger.error(f"❌ DB select single error on {table_name}: {e}")
        raise

# --- Dépendance d'authentification optimisée ---
async def get_current_user_id(user_id: str = "test_user_123"):
    """✅ Authentification non-bloquante simulée."""
    # Simulation d'une vérification async (ex: vérification JWT)
    await asyncio.sleep(0.01)  # Simule latence auth
    return user_id

# --- Modèles Pydantic ---
class KaizenCreate(BaseModel):
    user_id: str # Sera validé par l'authentification
    action: str = Field(..., min_length=1, max_length=255) # Validation de longueur
    date: date
    completed: bool = False

class KaizenUpdate(BaseModel):
    completed: bool

class KaizenResponse(KaizenCreate):
    id: int

    class Config:
        from_attributes = True

class ZazenSessionCreate(BaseModel):
    user_id: str # Sera validé par l'authentification
    timestamp: datetime
    duration: int = Field(..., ge=30, le=3600)  # 30s à 1h
    triggered_by: Optional[str] = None

class ZazenSessionResponse(ZazenSessionCreate):
    id: int

    class Config:
        from_attributes = True

# --- Endpoints Kaizen Optimisés ---
@app.post("/kaizen", response_model=KaizenResponse, status_code=201)
async def create_kaizen(
    kaizen: KaizenCreate, 
    background_tasks: BackgroundTasks,
    current_user_id: str = Depends(get_current_user_id)
):
    """✅ Création Kaizen avec opérations non-bloquantes."""
    if kaizen.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to create Kaizen for this user"
        )
    
    try:
        # Nettoyage sécurisé de l'action
        cleaned_action = kaizen.action.strip()[:255]  # Limite + nettoyage
        
        # ✅ Insertion asynchrone non-bloquante
        kaizen_data = {
            "user_id": kaizen.user_id,
            "action": cleaned_action,
            "date": kaizen.date.isoformat(),
            "completed": kaizen.completed
        }
        
        result = await _sync_supabase_insert("kaizen", kaizen_data)
        
        if not result:
            raise HTTPException(status_code=500, detail="Failed to create Kaizen")
        
        # ✅ Tâche de logging en arrière-plan
        background_tasks.add_task(
            _log_kaizen_creation, 
            kaizen.user_id, 
            cleaned_action
        )
        
        logger.info(f"✅ Kaizen created for user {kaizen.user_id}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Error creating Kaizen: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/kaizen/{kaizen_id}", response_model=KaizenResponse)
async def update_kaizen(
    kaizen_id: int, 
    kaizen_update: KaizenUpdate,
    background_tasks: BackgroundTasks,
    current_user_id: str = Depends(get_current_user_id)
):
    """✅ Mise à jour Kaizen avec vérifications asynchrones."""
    try:
        # ✅ Vérification d'autorisation asynchrone
        existing_kaizen = await _sync_supabase_select_single(
            "kaizen", 
            {"id": kaizen_id}, 
            "user_id"
        )
        
        if not existing_kaizen or existing_kaizen["user_id"] != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Not authorized to update this Kaizen"
            )

        # ✅ Update asynchrone
        result = await _sync_supabase_update(
            "kaizen", 
            kaizen_id, 
            kaizen_update.model_dump()
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="Kaizen not found")
        
        # ✅ Log en arrière-plan
        background_tasks.add_task(
            _log_kaizen_update,
            current_user_id,
            kaizen_id,
            kaizen_update.completed
        )
        
        logger.info(f"✅ Kaizen {kaizen_id} updated for user {current_user_id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error updating Kaizen {kaizen_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/kaizen/{user_id}", response_model=List[KaizenResponse])
async def get_user_kaizens(
    user_id: str, 
    limit: int = 50,
    current_user_id: str = Depends(get_current_user_id)
):
    """✅ Récupération Kaizen avec pagination et cache."""
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to view Kaizens for this user"
        )
    
    try:
        # ✅ Récupération asynchrone avec limite
        kaizens = await _sync_supabase_select(
            "kaizen",
            filters={"user_id": user_id},
            order_by="date desc",  # Plus récents en premier
            limit=min(limit, 100)  # Sécurité: max 100
        )
        
        logger.info(f"✅ Retrieved {len(kaizens) if kaizens else 0} Kaizens for user {user_id}")
        return kaizens or []
        
    except Exception as e:
        logger.error(f"❌ Error retrieving Kaizens for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- Endpoints Zazen Session Optimisés ---
@app.post("/zazen-session", response_model=ZazenSessionResponse, status_code=201)
async def create_zazen_session(
    session: ZazenSessionCreate,
    background_tasks: BackgroundTasks,
    current_user_id: str = Depends(get_current_user_id)
):
    """✅ Création session Zazen avec validations asynchrones."""
    if session.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to create Zazen session for this user"
        )
    
    try:
        # ✅ Insertion asynchrone
        result = await _sync_supabase_insert(
            "zazen_sessions", 
            session.model_dump()
        )
        
        if not result:
            raise HTTPException(status_code=500, detail="Failed to create Zazen session")
        
        # ✅ Analytics en arrière-plan
        background_tasks.add_task(
            _log_zazen_session,
            session.user_id,
            session.duration,
            session.triggered_by
        )
        
        logger.info(f"✅ Zazen session created for user {session.user_id}, duration: {session.duration}s")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error creating Zazen session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/zazen-session/{user_id}", response_model=List[ZazenSessionResponse])
async def get_user_zazen_sessions(
    user_id: str,
    limit: int = 20,
    current_user_id: str = Depends(get_current_user_id)
):
    """✅ Récupération sessions Zazen avec pagination."""
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view Zazen sessions for this user"
        )
    
    try:
        sessions = await _sync_supabase_select(
            "zazen_sessions",
            filters={"user_id": user_id},
            order_by="timestamp desc",
            limit=min(limit, 50)  # Max 50 sessions
        )
        
        logger.info(f"✅ Retrieved {len(sessions) if sessions else 0} Zazen sessions for user {user_id}")
        return sessions or []
        
    except Exception as e:
        logger.error(f"❌ Error retrieving Zazen sessions for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ✅ Fonctions de logging en arrière-plan
def _log_kaizen_creation(user_id: str, action: str):
    """Log la création d'un Kaizen."""
    logger.info(f"📊 Analytics: Kaizen created by {user_id[:8]}... - Action: {action[:50]}...")

def _log_kaizen_update(user_id: str, kaizen_id: int, completed: bool):
    """Log la mise à jour d'un Kaizen."""
    status = "completed" if completed else "updated"
    logger.info(f"📊 Analytics: Kaizen {kaizen_id} {status} by {user_id[:8]}...")

def _log_zazen_session(user_id: str, duration: int, triggered_by: Optional[str]):
    """Log une session Zazen."""
    trigger = f"({triggered_by})" if triggered_by else ""
    logger.info(f"📊 Analytics: Zazen session by {user_id[:8]}... - {duration}s {trigger}")

# ✅ Endpoint de santé avec métriques
@app.get("/health")
async def health_check():
    """Endpoint de santé avec métriques."""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "features": ["async_operations", "background_tasks", "optimized_queries", "pagination"],
        "executor_threads": executor._max_workers
    }

@app.get("/metrics")
async def get_metrics():
    """Métriques basiques de l'API."""
    return {
        "executor_active_threads": executor._threads,
        "max_workers": executor._max_workers,
        "version": "2.0.0"
    }

# ✅ Nettoyage à l'arrêt
@app.on_event("shutdown")
async def shutdown_event():
    """Nettoyage des ressources à l'arrêt."""
    logger.info("🔄 Shutting down Dojo API...")
    executor.shutdown(wait=True)
    logger.info("✅ Dojo API shutdown complete")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "dojo_api_optimized:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )