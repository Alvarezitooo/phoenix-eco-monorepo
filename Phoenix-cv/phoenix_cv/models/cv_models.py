from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class Experience(BaseModel):
    poste: str
    entreprise: str
    description: str
    date_debut: str
    date_fin: Optional[str] = None
    lieu: str
    competences_developpees: List[str] = []
    reconversion_angle: Optional[str] = None

class Competence(BaseModel):
    nom: str
    categorie: str # Ex: "Technique", "Transversale"
    niveau: str # Ex: "Débutant", "Intermédiaire", "Avancé", "Expert"
    transferable: bool = False

class CVRequest(BaseModel):
    prenom: str
    nom: str
    email: Optional[str] = None
    telephone: Optional[str] = None
    titre_professionnel: Optional[str] = None
    est_reconversion: bool = False
    ancien_domaine: Optional[str] = None
    nouveau_domaine: Optional[str] = None
    secteur_cible: Optional[str] = None
    competences_transferables: List[str] = []
    style_ton: str = "professionnel" # Ex: "professionnel", "créatif", "direct"
    optimisation_ats: bool = False
    template_id: str = "default"
    experiences: List[Experience] = []
    competences: List[Competence] = []
    centres_interet: List[str] = []

class ATSOptimization(BaseModel):
    secteur_analyse: str
    mots_cles_detectes: List[str] = []
    mots_cles_manquants: List[str] = []
    score_global: int
    score_accroche: Optional[int] = None
    score_experiences: Optional[int] = None
    score_competences: Optional[int] = None
    recommandations: List[str] = []
    mots_cles_a_ajouter: List[str] = []

class AccrocheIA(BaseModel):
    accroche: str
    points_cles: List[str] = []

class CVResponse(BaseModel):
    accroche_ia: str
    experiences_optimisees: List[Dict[str, Any]] = []
    competences_mises_en_avant: List[str] = []
    mots_cles_ats: List[str] = []
    template_utilise: str
    score_ats: Optional[int] = None
    conseils_amelioration: List[str] = []
