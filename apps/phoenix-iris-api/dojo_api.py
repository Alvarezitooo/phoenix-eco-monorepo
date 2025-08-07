from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
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

# --- Modèles Pydantic ---
class KaizenCreate(BaseModel):
    user_id: str
    action: str
    date: date
    completed: bool = False

class KaizenUpdate(BaseModel):
    completed: bool

class KaizenResponse(KaizenCreate):
    id: int

    class Config:
        from_attributes = True

class ZazenSessionCreate(BaseModel):
    user_id: str
    timestamp: datetime
    duration: int
    triggered_by: Optional[str] = None

class ZazenSessionResponse(ZazenSessionCreate):
    id: int

    class Config:
        from_attributes = True

# --- Endpoints Kaizen ---
@app.post("/kaizen", response_model=KaizenResponse, status_code=201)
async def create_kaizen(kaizen: KaizenCreate):
    try:
        response = supabase.table("kaizen").insert(kaizen.model_dump()).execute()
        if response.data:
            return response.data[0]
        raise HTTPException(status_code=500, detail="Failed to create Kaizen")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/kaizen/{kaizen_id}", response_model=KaizenResponse)
async def update_kaizen(kaizen_id: int, kaizen_update: KaizenUpdate):
    try:
        response = supabase.table("kaizen").update(kaizen_update.model_dump()).eq("id", kaizen_id).execute()
        if response.data:
            return response.data[0]
        raise HTTPException(status_code=404, detail="Kaizen not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/kaizen/{user_id}", response_model=list[KaizenResponse])
async def get_user_kaizens(user_id: str):
    try:
        response = supabase.table("kaizen").select("*").eq("user_id", user_id).order("date").execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Endpoints Zazen Session ---
@app.post("/zazen-session", response_model=ZazenSessionResponse, status_code=201)
async def create_zazen_session(session: ZazenSessionCreate):
    try:
        response = supabase.table("zazen_sessions").insert(session.model_dump()).execute()
        if response.data:
            return response.data[0]
        raise HTTPException(status_code=500, detail="Failed to create Zazen session")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
