from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional
import os
from supabase import create_client, Client

# Initialisation de Supabase
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(
    title="Dojo Mental API",
    description="API pour la gestion des Kaizen et des sessions Zazen du Dojo Mental.",
    version="1.0.0",
)

# --- Dépendance d'authentification simulée ---
# Dans un système réel, ceci vérifierait un token JWT, une clé API, etc.
# Pour cette mission, nous simulons simplement la récupération d'un user_id.
async def get_current_user_id(user_id: str = "test_user_123"): # Simule un user_id par défaut
    # Ici, vous intégreriez la logique de vérification du token JWT
    # Par exemple, en extrayant l'ID utilisateur d'un en-tête Authorization
    # if not user_id: # Si l'ID n'est pas fourni ou invalide
    #    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
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
    duration: int
    triggered_by: Optional[str] = None

class ZazenSessionResponse(ZazenSessionCreate):
    id: int

    class Config:
        from_attributes = True

# --- Endpoints Kaizen ---
@app.post("/kaizen", response_model=KaizenResponse, status_code=201)
async def create_kaizen(kaizen: KaizenCreate, current_user_id: str = Depends(get_current_user_id)):
    if kaizen.user_id != current_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to create Kaizen for this user")
    try:
        # Nettoyage de l'action (exemple simple, un nettoyage plus robuste serait nécessaire)
        cleaned_action = kaizen.action.strip() # Supprime les espaces blancs
        # Vous pourriez ajouter ici un filtre pour les caractères spéciaux ou les injections

        response = supabase.table("kaizen").insert({"user_id": kaizen.user_id, "action": cleaned_action, "date": kaizen.date.isoformat(), "completed": kaizen.completed}).execute()
        if response.data:
            return response.data[0]
        raise HTTPException(status_code=500, detail="Failed to create Kaizen")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/kaizen/{kaizen_id}", response_model=KaizenResponse)
async def update_kaizen(kaizen_id: int, kaizen_update: KaizenUpdate, current_user_id: str = Depends(get_current_user_id)):
    try:
        # Vérifier que l'utilisateur est autorisé à modifier ce Kaizen
        existing_kaizen_response = supabase.table("kaizen").select("user_id").eq("id", kaizen_id).single().execute()
        if not existing_kaizen_response.data or existing_kaizen_response.data["user_id"] != current_user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this Kaizen")

        response = supabase.table("kaizen").update(kaizen_update.model_dump()).eq("id", kaizen_id).execute()
        if response.data:
            return response.data[0]
        raise HTTPException(status_code=404, detail="Kaizen not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/kaizen/{user_id}", response_model=list[KaizenResponse])
async def get_user_kaizens(user_id: str, current_user_id: str = Depends(get_current_user_id)):
    if user_id != current_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view Kaizens for this user")
    try:
        response = supabase.table("kaizen").select("*").eq("user_id", user_id).order("date").execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Endpoints Zazen Session ---
@app.post("/zazen-session", response_model=ZazenSessionResponse, status_code=201)
async def create_zazen_session(session: ZazenSessionCreate, current_user_id: str = Depends(get_current_user_id)):
    if session.user_id != current_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to create Zazen session for this user")
    try:
        response = supabase.table("zazen_sessions").insert(session.model_dump()).execute()
        if response.data:
            return response.data[0]
        raise HTTPException(status_code=500, detail="Failed to create Zazen session")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))