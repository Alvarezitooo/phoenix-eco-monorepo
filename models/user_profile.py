from pydantic import BaseModel, Field
from typing import List

class UserProfile(BaseModel):
    current_skills: List[str] = Field(default_factory=list, description="Liste des compétences actuelles de l'utilisateur.")
    current_experience: str = Field("", description="Description de l'expérience professionnelle actuelle ou passée.")
    aspirations: str = Field("", description="Description des aspirations de carrière ou du nouveau domaine souhaité.")
    # D'autres champs pourront être ajoutés ici au fur et à mesure
