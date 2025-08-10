"""
Phoenix Aube - Modèles Pydantic Core
Architecture Trust by Design + Event Store Ready
"""

from datetime import datetime
from typing import List, Dict, Optional, Any, Union
from enum import Enum
from pydantic import BaseModel, Field, validator
import uuid

# =============================================
# ENUMS & TYPES
# =============================================

class ValeurProfondeProfil(str, Enum):
    """Valeurs profondes identifiées lors de l'exploration"""
    RESOLUTION_PROBLEMES = "résoudre_problèmes_complexes"
    AIDE_ACCOMPAGNEMENT = "aider_accompagner_autres"  
    CREATION_INNOVATION = "créer_innover"
    ORGANISATION_OPTIMISATION = "organiser_optimiser"
    TRANSMISSION_FORMATION = "transmettre_former"
    LEADERSHIP_INFLUENCE = "leadership_influence"
    AUTONOMIE_LIBERTÉ = "autonomie_liberté"

class EnvironnementTravail(str, Enum):
    """Préférences environnement de travail"""
    AUTONOME = "autonome"
    COLLABORATIF = "collaboratif"
    HYBRIDE = "hybride"
    BUREAU_FIXE = "bureau_fixe"
    TERRAIN = "terrain"
    TÉLÉTRAVAIL = "télétravail"
    INTERNATIONAL = "international"

class TypeEvolutionIA(str, Enum):
    """Type d'évolution du métier face à l'IA"""
    STABLE = "stable"
    ENHANCED = "enhanced"  # Amélioré par IA
    TRANSFORMED = "transformed"  # Transformé
    THREATENED = "threatened"  # Menacé
    CREATED = "created"  # Nouveau métier créé par IA

class NiveauConfiance(str, Enum):
    """Niveau de confiance des prédictions"""
    TRÈS_ÉLEVÉ = "très_élevé"  # 90-100%
    ÉLEVÉ = "élevé"  # 75-89%
    MOYEN = "moyen"  # 60-74%
    FAIBLE = "faible"  # <60%

# =============================================
# MODÈLES EXPLORATION (TEMPS 1)
# =============================================

class ProfilExploration(BaseModel):
    """Profil d'exploration métier complet de l'utilisateur"""
    
    user_id: str = Field(..., description="Identifiant unique utilisateur")
    
    # Données personnelles de base
    age_range: str = Field(..., description="Tranche d'âge: 25-35, 35-45, 45-55, 55+")
    secteur_actuel: str = Field(..., description="Secteur d'activité actuel")
    poste_actuel: str = Field(..., description="Poste/métier actuel")
    années_expérience: int = Field(..., ge=0, le=50, description="Années d'expérience totales")
    
    # Exploration valeurs profondes
    valeurs_principales: List[ValeurProfondeProfil] = Field(
        ..., min_items=2, max_items=3, 
        description="2-3 valeurs profondes principales"
    )
    
    # Préférences environnement
    environnement_préféré: List[EnvironnementTravail] = Field(
        ..., min_items=1, max_items=3,
        description="Environnements de travail préférés"
    )
    
    # Compétences et talents
    compétences_transférables: List[str] = Field(
        ..., description="Compétences transférables identifiées"
    )
    talents_cachés: List[str] = Field(
        default=[], description="Talents révélés par l'exploration"
    )
    
    # Contraintes et motivations
    contraintes_géographiques: Optional[str] = Field(
        None, description="Contraintes géographiques si applicable"
    )
    contraintes_salariales: Optional[str] = Field(
        None, description="Contraintes salariales minimales"
    )
    motivations_reconversion: List[str] = Field(
        ..., description="Motivations principales pour la reconversion"
    )
    
    # Données psychométriques
    big_five_scores: Dict[str, float] = Field(
        ..., description="Scores Big Five (0-1): openness, conscientiousness, etc."
    )
    riasec_scores: Dict[str, float] = Field(
        ..., description="Scores RIASEC (0-1): realistic, investigative, etc."
    )
    
    # Métadonnées
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    @validator('big_five_scores')
    def validate_big_five(cls, v):
        required_traits = ['openness', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']
        for trait in required_traits:
            if trait not in v:
                raise ValueError(f"Missing Big Five trait: {trait}")
            if not 0 <= v[trait] <= 1:
                raise ValueError(f"Big Five score {trait} must be between 0 and 1")
        return v
    
    @validator('riasec_scores')
    def validate_riasec(cls, v):
        required_types = ['realistic', 'investigative', 'artistic', 'social', 'enterprising', 'conventional']
        for rtype in required_types:
            if rtype not in v:
                raise ValueError(f"Missing RIASEC type: {rtype}")
            if not 0 <= v[rtype] <= 1:
                raise ValueError(f"RIASEC score {rtype} must be between 0 and 1")
        return v

class RecommandationCarrière(BaseModel):
    """Recommandation de métier personnalisée avec justifications"""
    
    métier_titre: str = Field(..., description="Titre du métier recommandé")
    code_rome: Optional[str] = Field(None, description="Code ROME si disponible")
    secteur: str = Field(..., description="Secteur d'activité")
    
    # Scores de compatibilité
    score_compatibilité_global: float = Field(
        ..., ge=0, le=1, description="Score global de compatibilité (0-1)"
    )
    score_valeurs: float = Field(
        ..., ge=0, le=1, description="Alignement avec valeurs profondes"
    )
    score_compétences: float = Field(
        ..., ge=0, le=1, description="Utilisation compétences transférables"
    )
    score_environnement: float = Field(
        ..., ge=0, le=1, description="Fit avec environnement préféré"
    )
    score_personnalité: float = Field(
        ..., ge=0, le=1, description="Compatibilité profil psychométrique"
    )
    
    # Justifications transparentes
    justification_principale: str = Field(
        ..., description="Explication principale de la recommandation"
    )
    points_forts_match: List[str] = Field(
        ..., description="Points forts du matching"
    )
    défis_potentiels: List[str] = Field(
        default=[], description="Défis potentiels à anticiper"
    )
    
    # Informations métier
    description_métier: str = Field(..., description="Description du métier")
    compétences_requises: List[str] = Field(..., description="Compétences requises")
    formations_recommandées: List[str] = Field(
        default=[], description="Formations recommandées pour la transition"
    )
    
    # Success stories
    témoignages_reconversion: List[str] = Field(
        default=[], description="Témoignages de reconversions similaires"
    )
    
    created_at: datetime = Field(default_factory=datetime.now)

# =============================================
# MODÈLES VALIDATION IA (TEMPS 2)
# =============================================

class AnalyseRésilienceIA(BaseModel):
    """Analyse de résistance/évolution d'un métier face à l'IA"""
    
    métier_titre: str = Field(..., description="Titre du métier analysé")
    
    # Scores de résistance
    score_résistance_ia: float = Field(
        ..., ge=0, le=1, 
        description="Score résistance IA (1 = très résistant, 0 = très menacé)"
    )
    niveau_menace: str = Field(
        ..., description="Niveau menace: 'faible', 'modéré', 'élevé', 'critique'"
    )
    
    # Évolution prédite
    type_évolution: TypeEvolutionIA = Field(
        ..., description="Type d'évolution face à l'IA"
    )
    timeline_impact: str = Field(
        ..., description="Timeline impact: '1-3 ans', '3-5 ans', '5-10 ans', '10+ ans'"
    )
    
    # Détails techniques
    tâches_automatisables: List[str] = Field(
        ..., description="Tâches susceptibles d'être automatisées"
    )
    tâches_humaines_critiques: List[str] = Field(
        ..., description="Tâches restant humaines critiques"
    )
    
    # Opportunités collaboration IA
    opportunités_ia_collaboration: List[str] = Field(
        ..., description="Comment l'IA peut améliorer le métier"
    )
    compétences_ia_à_développer: List[str] = Field(
        ..., description="Compétences IA spécifiques à acquérir"
    )
    
    # Messages rassurants
    message_futur_positif: str = Field(
        ..., description="Message rassurant sur l'évolution du métier"
    )
    avantages_évolution: List[str] = Field(
        ..., description="Avantages de l'évolution avec IA"
    )
    
    # Métadonnées prédiction
    niveau_confiance: NiveauConfiance = Field(
        ..., description="Niveau de confiance de la prédiction"
    )
    sources_analyse: List[str] = Field(
        ..., description="Sources utilisées pour l'analyse"
    )
    dernière_mise_à_jour: datetime = Field(
        default_factory=datetime.now, description="Dernière mise à jour données"
    )
    
    created_at: datetime = Field(default_factory=datetime.now)

# =============================================
# MODÈLE PARCOURS COMPLET
# =============================================

class ParcoursExploration(BaseModel):
    """Parcours complet d'exploration Phoenix Aube"""
    
    parcours_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = Field(..., description="Identifiant utilisateur")
    
    # Données exploration
    profil_exploration: ProfilExploration = Field(
        ..., description="Profil d'exploration complet"
    )
    
    # Recommandations métiers
    recommandations_métiers: List[RecommandationCarrière] = Field(
        ..., min_items=3, max_items=5,
        description="3-5 recommandations métiers classées"
    )
    
    # Validations IA
    analyses_ia: List[AnalyseRésilienceIA] = Field(
        ..., description="Analyses IA pour chaque métier recommandé"
    )
    
    # Plan d'action
    métier_choisi: Optional[str] = Field(
        None, description="Métier choisi par l'utilisateur"
    )
    plan_transition: Optional[Dict[str, Any]] = Field(
        None, description="Plan de transition personnalisé"
    )
    prochaines_étapes: List[str] = Field(
        default=[], description="Prochaines étapes recommandées"
    )
    
    # Statut et métadonnées
    statut_completion: str = Field(
        default="en_cours", 
        description="'en_cours', 'recommandations_générées', 'métier_choisi', 'plan_créé'"
    )
    
    # Intégration écosystème Phoenix
    transitions_écosystème: Dict[str, Any] = Field(
        default={}, description="Transitions vers Phoenix CV/Letters/Rise"
    )
    
    # Recherche et consentements
    consentement_recherche_3ia: bool = Field(
        default=False, description="Consentement utilisation données recherche 3IA"
    )
    données_anonymisées: bool = Field(
        default=True, description="Données anonymisées pour recherche"
    )
    
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = Field(
        None, description="Date de completion du parcours"
    )

# =============================================
# MODÈLES TRANSPARENCE & EXPLICATIONS
# =============================================

class ExplicationRecommandation(BaseModel):
    """Explication transparente d'une recommandation métier"""
    
    recommandation_id: str = Field(..., description="ID de la recommandation")
    métier_titre: str = Field(..., description="Métier concerné")
    
    # Décomposition du scoring
    détail_scores: Dict[str, Dict[str, Union[float, str]]] = Field(
        ..., description="Détail de chaque composant du score"
    )
    
    # Explications en langage naturel
    pourquoi_recommandé: str = Field(
        ..., description="Explication en français simple"
    )
    
    # Facteurs clés
    facteurs_positifs: List[Dict[str, str]] = Field(
        ..., description="Facteurs qui jouent en faveur: [{'facteur': '', 'explication': ''}]"
    )
    facteurs_attention: List[Dict[str, str]] = Field(
        default=[], description="Facteurs d'attention ou défis"
    )
    
    # Ajustements possibles
    leviers_amélioration: List[str] = Field(
        default=[], description="Comment améliorer le match"
    )
    
    created_at: datetime = Field(default_factory=datetime.now)