from pydantic import BaseModel, Field
from typing import Optional, Literal

class LetterRequest(BaseModel):
    cv_contenu: str = Field(..., min_length=10, description="Contenu textuel du CV")
    annonce_contenu: str = Field(..., min_length=10, description="Contenu textuel de l'annonce")
    ton_souhaite: Literal["formel", "dynamique", "sobre", "créatif", "startup", "associatif"] = "formel"
    est_reconversion: bool = False
    ancien_domaine: str = ""
    nouveau_domaine: str = ""
    competences_transferables: str = ""
    offer_details: Optional[dict] = None
    company_insights: Optional[dict] = None
    user_tier: Literal["free", "premium", "premium_plus"] = "free"
