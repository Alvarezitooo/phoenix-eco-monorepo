from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class Resource(BaseModel):
    type: Literal["cours_en_ligne", "livre", "certification", "mentorat", "projet_pratique", "article", "outil", "autre"] = "autre"
    name: str = Field(..., description="Nom de la ressource.")
    link: Optional[str] = Field(None, description="Lien vers la ressource.")
    description: Optional[str] = Field(None, description="Description de la ressource.")

class ReconversionStep(BaseModel):
    title: str = Field(..., description="Titre de l'étape (ex: Formation Python, Certification Cloud).")
    description: str = Field(..., description="Description détaillée de l'étape.")
    duration_weeks: Optional[int] = Field(None, description="Durée estimée de l'étape en semaines.")
    resources: List[Resource] = Field(default_factory=list, description="Ressources suggérées.")

class ReconversionPlan(BaseModel):
    goal: str = Field(..., description="L'objectif de reconversion défini.")
    summary: str = Field(..., description="Résumé du plan de reconversion.")
    skills_gap_analysis: Optional[str] = Field(None, description="Analyse des écarts de compétences identifiés.")
    steps: List[ReconversionStep] = Field(default_factory=list, description="Liste des étapes du plan.")
    estimated_total_duration_weeks: Optional[int] = Field(None, description="Durée totale estimée du plan en semaines.")
    success_probability: Optional[float] = Field(None, ge=0, le=1, description="Probabilité de succès estimée (0 à 1).")