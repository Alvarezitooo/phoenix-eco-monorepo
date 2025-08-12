"""
Router Phoenix Rise - Kaizen et Zazen
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import date, datetime

from routers.auth import get_current_user
from services.supabase_client import SupabaseClient

router = APIRouter()

# Schemas Pydantic pour Rise
class KaizenEntry(BaseModel):
    action: str
    date: Optional[str] = None
    completed: bool = False

class KaizenUpdate(BaseModel):
    completed: bool

class ZazenSession(BaseModel):
    duration: int  # en secondes
    triggered_by: Optional[str] = None
    notes: Optional[str] = None

class KaizenResponse(BaseModel):
    id: int
    user_id: str
    action: str
    date: str
    completed: bool

class ZazenResponse(BaseModel):
    id: int
    user_id: str
    timestamp: str
    duration: int
    triggered_by: Optional[str]

# Dependency
async def get_supabase() -> SupabaseClient:
    """Dependency pour récupérer le client Supabase"""
    from main import supabase_client
    if not supabase_client:
        raise HTTPException(
            status_code=500,
            detail="Supabase client not initialized"
        )
    return supabase_client

# Routes Kaizen
@router.post("/kaizen", response_model=Dict[str, Any])
async def create_kaizen(
    kaizen: KaizenEntry,
    current_user: Dict[str, Any] = Depends(get_current_user),
    supabase: SupabaseClient = Depends(get_supabase)
):
    """Créer une nouvelle action Kaizen"""
    try:
        result = await supabase.create_kaizen_entry(
            current_user["id"],
            kaizen.action,
            kaizen.completed
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Action Kaizen créée avec succès"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la création du Kaizen: {str(e)}"
        )

@router.get("/kaizen/{user_id}")
async def get_user_kaizen(
    user_id: str,
    limit: int = 50,
    current_user: Dict[str, Any] = Depends(get_current_user),
    supabase: SupabaseClient = Depends(get_supabase)
):
    """Récupérer l'historique Kaizen d'un utilisateur"""
    if current_user["id"] != user_id:
        raise HTTPException(
            status_code=403,
            detail="Accès non autorisé à ces données"
        )
    
    try:
        history = await supabase.get_user_kaizen_history(user_id, limit)
        
        return {
            "success": True,
            "data": history,
            "total": len(history)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération: {str(e)}"
        )

@router.put("/kaizen/{kaizen_id}")
async def update_kaizen(
    kaizen_id: int,
    update: KaizenUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    supabase: SupabaseClient = Depends(get_supabase)
):
    """Mettre à jour le statut d'un Kaizen"""
    try:
        # Vérifier que le Kaizen appartient à l'utilisateur
        response = supabase.client.table('kaizen').select('user_id').eq('id', kaizen_id).single().execute()
        
        if not response.data or response.data.get('user_id') != current_user["id"]:
            raise HTTPException(
                status_code=404,
                detail="Kaizen non trouvé"
            )
        
        # Mettre à jour
        update_response = supabase.client.table('kaizen').update({
            'completed': update.completed
        }).eq('id', kaizen_id).execute()
        
        return {
            "success": True,
            "data": update_response.data[0] if update_response.data else {},
            "message": "Kaizen mis à jour avec succès"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la mise à jour: {str(e)}"
        )

# Routes Zazen
@router.post("/zazen-session", response_model=Dict[str, Any])
async def create_zazen_session(
    session: ZazenSession,
    current_user: Dict[str, Any] = Depends(get_current_user),
    supabase: SupabaseClient = Depends(get_supabase)
):
    """Créer une session de méditation Zazen"""
    try:
        result = await supabase.create_zazen_session(
            current_user["id"],
            session.duration,
            session.triggered_by
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Session Zazen enregistrée avec succès"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'enregistrement: {str(e)}"
        )

@router.get("/zazen-sessions/{user_id}")
async def get_zazen_sessions(
    user_id: str,
    limit: int = 30,
    current_user: Dict[str, Any] = Depends(get_current_user),
    supabase: SupabaseClient = Depends(get_supabase)
):
    """Récupérer les sessions Zazen d'un utilisateur"""
    if current_user["id"] != user_id:
        raise HTTPException(
            status_code=403,
            detail="Accès non autorisé à ces données"
        )
    
    try:
        response = supabase.client.table('zazen_sessions').select('*').eq('user_id', user_id).limit(limit).order('timestamp', desc=True).execute()
        
        return {
            "success": True,
            "data": response.data or [],
            "total": len(response.data or [])
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération: {str(e)}"
        )

# Routes Analytics et Stats
@router.get("/stats/{user_id}")
async def get_user_stats(
    user_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    supabase: SupabaseClient = Depends(get_supabase)
):
    """Statistiques utilisateur Phoenix Rise"""
    if current_user["id"] != user_id:
        raise HTTPException(
            status_code=403,
            detail="Accès non autorisé à ces statistiques"
        )
    
    try:
        # Statistiques Kaizen
        kaizen_response = supabase.client.table('kaizen').select('*').eq('user_id', user_id).execute()
        kaizen_data = kaizen_response.data or []
        
        # Statistiques Zazen
        zazen_response = supabase.client.table('zazen_sessions').select('duration').eq('user_id', user_id).execute()
        zazen_data = zazen_response.data or []
        
        total_kaizens = len(kaizen_data)
        completed_kaizens = len([k for k in kaizen_data if k.get('completed')])
        total_zazen_minutes = sum(session.get('duration', 0) for session in zazen_data) // 60
        
        # Calcul du streak (simulation)
        streak = _calculate_streak(kaizen_data)
        
        return {
            "success": True,
            "data": {
                "totalKaizens": total_kaizens,
                "completedKaizens": completed_kaizens,
                "completionRate": round(completed_kaizens / total_kaizens * 100, 1) if total_kaizens > 0 else 0,
                "totalZazenMinutes": total_zazen_minutes,
                "totalSessions": len(zazen_data),
                "averageSessionDuration": round(sum(s.get('duration', 0) for s in zazen_data) / len(zazen_data) / 60, 1) if zazen_data else 0,
                "currentStreak": streak
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du calcul des stats: {str(e)}"
        )

# Fonctions utilitaires
def _calculate_streak(kaizen_data: List[Dict]) -> int:
    """Calcule la streak actuelle de Kaizen"""
    # Simulation de calcul de streak
    # À améliorer avec la vraie logique basée sur les dates
    completed_recent = [k for k in kaizen_data if k.get('completed')]
    return min(len(completed_recent), 7)  # Max 7 jours de streak pour l'exemple