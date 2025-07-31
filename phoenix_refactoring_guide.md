# 🔥 PHOENIX LETTERS - GUIDE DE REFACTORING MODULAIRE
## Plan d'Action Complet pour Gemini CLI

> **Objectif** : Transformer l'architecture monolithique en système modulaire enterprise-grade  
> **Priorité** : CRITIQUE - Refactoring immédiat requis  
> **Timeline** : 4 semaines (3 phases)  

---

## 🎯 **ARCHITECTURE CIBLE - CLEAN MODULAR DESIGN**

### **Structure de Répertoires Finale**
```
phoenix_letters/
├── app.py                          # Entry point Streamlit (< 100 lignes)
├── config/
│   ├── __init__.py
│   ├── settings.py                 # Configuration centralisée
│   └── constants.py                # Constantes globales
├── core/                           # Business Logic Layer
│   ├── __init__.py
│   ├── entities/
│   │   ├── __init__.py
│   │   ├── letter.py              # Letter domain entity
│   │   ├── user.py                # User domain entity
│   │   └── generation_request.py  # Request domain entity
│   ├── use_cases/
│   │   ├── __init__.py
│   │   ├── generate_letter.py     # Letter generation use case
│   │   ├── analyze_culture.py     # Culture analysis use case
│   │   └── suggest_skills.py      # Skills suggestion use case
│   └── services/
│       ├── __init__.py
│       ├── letter_service.py      # Business logic service
│       ├── ai_service.py          # AI operations service
│       └── validation_service.py  # Input validation service
├── infrastructure/                 # External Services Layer
│   ├── __init__.py
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── gemini_client.py       # Google Gemini client
│   │   └── ai_interface.py        # AI abstraction interface
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── session_manager.py     # Session state management
│   │   └── file_handler.py        # File operations
│   ├── security/
│   │   ├── __init__.py
│   │   ├── input_validator.py     # Input sanitization
│   │   ├── anonymizer.py          # Data anonymization
│   │   └── security_scanner.py    # Security scanning
│   └── monitoring/
│       ├── __init__.py
│       ├── performance_monitor.py # Performance tracking
│       └── error_tracker.py       # Error monitoring
├── ui/                             # Presentation Layer
│   ├── __init__.py
│   ├── components/
│   │   ├── __init__.py
│   │   ├── file_uploader.py       # File upload component
│   │   ├── progress_bar.py        # Progress indicator
│   │   ├── letter_editor.py       # Letter editing component
│   │   └── settings_panel.py      # Settings component
│   ├── pages/
│   │   ├── __init__.py
│   │   ├── generator_page.py      # Main generator tab
│   │   ├── premium_features.py    # Premium features tabs
│   │   ├── settings_page.py       # Settings tab
│   │   └── about_page.py          # About/FAQ tab
│   ├── styles/
│   │   ├── __init__.py
│   │   ├── css_manager.py         # CSS management
│   │   └── themes.py              # Theme definitions
│   └── state/
│       ├── __init__.py
│       ├── state_manager.py       # UI state management
│       └── session_store.py       # Session persistence
├── shared/                         # Shared Utilities Layer
│   ├── __init__.py
│   ├── types/
│   │   ├── __init__.py
│   │   ├── enums.py               # Enums and constants
│   │   └── models.py              # Shared data models
│   ├── exceptions/
│   │   ├── __init__.py
│   │   ├── base_exceptions.py     # Base exception classes
│   │   └── specific_exceptions.py # Domain-specific exceptions
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── cache.py               # Caching utilities
│   │   ├── logging_config.py      # Logging configuration
│   │   └── helpers.py             # General helpers
│   └── interfaces/
│       ├── __init__.py
│       ├── ai_interface.py        # AI service interface
│       ├── storage_interface.py   # Storage interface
│       └── monitoring_interface.py # Monitoring interface
├── tests/                          # Test Suite
│   ├── __init__.py
│   ├── unit/
│   │   ├── test_core/
│   │   ├── test_infrastructure/
│   │   └── test_ui/
│   ├── integration/
│   │   ├── test_letter_generation.py
│   │   └── test_ai_integration.py
│   └── fixtures/
│       ├── sample_cv.py
│       └── sample_job_offers.py
├── requirements/
│   ├── base.txt                   # Base requirements
│   ├── dev.txt                    # Development requirements
│   └── prod.txt                   # Production requirements
├── scripts/
│   ├── setup.py                   # Setup script
│   ├── deploy.py                  # Deployment script
│   └── migrate.py                 # Migration script
└── docs/
    ├── architecture.md            # Architecture documentation
    ├── api.md                     # API documentation
    └── deployment.md              # Deployment guide
```

---

## 🚀 **PHASE 1 : EXTRACTION DES SERVICES CRITIQUES**

### **1.1 Configuration Centralisée**

**Fichier: `config/settings.py`**
```python
"""Configuration centralisée pour Phoenix Letters."""
import os
from dataclasses import dataclass
from typing import Optional
from pathlib import Path

@dataclass(frozen=True)
class Settings:
    """Configuration application."""
    
    # API Configuration
    google_api_key: str
    france_travail_client_id: Optional[str] = None
    france_travail_client_secret: Optional[str] = None
    
    # Security Configuration
    max_file_size: int = 5 * 1024 * 1024  # 5MB
    allowed_file_types: tuple = ('.pdf', '.txt')
    session_timeout: int = 3600  # 1 hour
    
    # Performance Configuration
    cache_ttl: int = 300  # 5 minutes
    max_concurrent_requests: int = 10
    
    # Feature Flags
    enable_mirror_match: bool = True
    enable_smart_coach: bool = True
    enable_trajectory_builder: bool = True
    
    @classmethod
    def from_env(cls) -> 'Settings':
        """Charge la configuration depuis les variables d'environnement."""
        google_api_key = os.getenv('GOOGLE_API_KEY')
        if not google_api_key:
            raise ValueError("GOOGLE_API_KEY is required")
            
        return cls(
            google_api_key=google_api_key,
            france_travail_client_id=os.getenv('FRANCETRAVAIL_CLIENT_ID'),
            france_travail_client_secret=os.getenv('FRANCETRAVAIL_CLIENT_SECRET'),
        )

# Instance globale
settings = Settings.from_env()
```

### **1.2 Entités Métier**

**Fichier: `core/entities/letter.py`**
```python
"""Entité métier pour les lettres de motivation."""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any

class ToneType(Enum):
    """Types de ton pour la lettre."""
    FORMAL = "formel"
    DYNAMIC = "dynamique"
    SOBER = "sobre"
    CREATIVE = "créatif"
    STARTUP = "startup"
    ASSOCIATIVE = "associatif"

class UserTier(Enum):
    """Niveaux d'abonnement utilisateur."""
    FREE = "free"
    PREMIUM = "premium"
    PREMIUM_PLUS = "premium_plus"

@dataclass(frozen=True)
class GenerationRequest:
    """Requête de génération de lettre."""
    cv_content: str
    job_offer_content: str
    tone: ToneType
    user_tier: UserTier
    is_career_change: bool = False
    old_domain: Optional[str] = None
    new_domain: Optional[str] = None
    transferable_skills: Optional[str] = None
    company_insights: Optional[Dict[str, Any]] = None
    offer_details: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Validation des données."""
        if self.is_career_change and (not self.old_domain or not self.new_domain):
            raise ValueError("Career change requires old_domain and new_domain")
        
        if len(self.cv_content) < 50:
            raise ValueError("CV content too short")
            
        if len(self.job_offer_content) < 20:
            raise ValueError("Job offer content too short")

@dataclass
class Letter:
    """Entité lettre de motivation."""
    content: str
    generation_request: GenerationRequest
    created_at: datetime
    user_id: str
    quality_score: Optional[float] = None
    
    def __post_init__(self):
        """Validation de la lettre."""
        if len(self.content) < 100:
            raise ValueError("Letter content too short")
        
        if not self.user_id:
            raise ValueError("User ID is required")

@dataclass
class LetterAnalysis:
    """Analyse de la lettre générée."""
    letter_id: str
    ats_score: float
    readability_score: float
    keyword_match_score: float
    suggestions: list[str]
    strengths: list[str]
    improvements: list[str]
```

### **1.3 Service de Génération de Lettres**

**Fichier: `core/services/letter_service.py`**
```python
"""Service métier pour la génération de lettres."""
import logging
from typing import Protocol, Optional
from datetime import datetime

from core.entities.letter import Letter, GenerationRequest, LetterAnalysis
from shared.exceptions.specific_exceptions import (
    LetterGenerationError, 
    ValidationError,
    AIServiceError
)
from shared.interfaces.ai_interface import AIServiceInterface
from shared.interfaces.monitoring_interface import MonitoringInterface

logger = logging.getLogger(__name__)

class LetterServiceInterface(Protocol):
    """Interface du service de génération de lettres."""
    
    def generate_letter(self, request: GenerationRequest, user_id: str) -> Letter:
        """Génère une lettre de motivation."""
        ...
    
    def analyze_letter(self, letter: Letter) -> LetterAnalysis:
        """Analyse une lettre générée."""
        ...

class LetterService:
    """Service de génération de lettres de motivation."""
    
    def __init__(
        self, 
        ai_service: AIServiceInterface,
        monitoring: MonitoringInterface
    ):
        self.ai_service = ai_service
        self.monitoring = monitoring
    
    def generate_letter(self, request: GenerationRequest, user_id: str) -> Letter:
        """
        Génère une lettre de motivation personnalisée.
        
        Args:
            request: Requête de génération
            user_id: ID de l'utilisateur
            
        Returns:
            Letter: Lettre générée
            
        Raises:
            LetterGenerationError: En cas d'erreur de génération
            ValidationError: En cas d'erreur de validation
        """
        try:
            # Validation de la requête
            self._validate_request(request)
            
            # Monitoring
            with self.monitoring.track_operation("letter_generation"):
                # Construction du prompt
                prompt = self._build_prompt(request)
                
                # Génération IA
                content = self.ai_service.generate_content(
                    prompt=prompt,
                    user_tier=request.user_tier,
                    max_tokens=1000
                )
                
                # Création de l'entité Letter
                letter = Letter(
                    content=content,
                    generation_request=request,
                    created_at=datetime.now(),
                    user_id=user_id
                )
                
                logger.info(f"Letter generated successfully for user {user_id}")
                return letter
                
        except AIServiceError as e:
            logger.error(f"AI service error: {e}")
            raise LetterGenerationError(f"Erreur du service IA: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in letter generation: {e}")
            raise LetterGenerationError(f"Erreur inattendue: {e}")
    
    def analyze_letter(self, letter: Letter) -> LetterAnalysis:
        """
        Analyse une lettre générée.
        
        Args:
            letter: Lettre à analyser
            
        Returns:
            LetterAnalysis: Analyse de la lettre
        """
        try:
            with self.monitoring.track_operation("letter_analysis"):
                # Analyse ATS
                ats_score = self._calculate_ats_score(
                    letter.content, 
                    letter.generation_request.job_offer_content
                )
                
                # Analyse de lisibilité
                readability_score = self._calculate_readability_score(letter.content)
                
                # Correspondance mots-clés
                keyword_score = self._calculate_keyword_match(
                    letter.content,
                    letter.generation_request.job_offer_content
                )
                
                # Suggestions d'amélioration
                suggestions = self._generate_suggestions(letter)
                
                return LetterAnalysis(
                    letter_id=f"{letter.user_id}_{letter.created_at.timestamp()}",
                    ats_score=ats_score,
                    readability_score=readability_score,
                    keyword_match_score=keyword_score,
                    suggestions=suggestions,
                    strengths=self._identify_strengths(letter),
                    improvements=self._identify_improvements(letter)
                )
                
        except Exception as e:
            logger.error(f"Error analyzing letter: {e}")
            raise LetterGenerationError(f"Erreur d'analyse: {e}")
    
    def _validate_request(self, request: GenerationRequest) -> None:
        """Valide une requête de génération."""
        if not request.cv_content.strip():
            raise ValidationError("Le contenu du CV est requis")
        
        if not request.job_offer_content.strip():
            raise ValidationError("Le contenu de l'offre d'emploi est requis")
        
        if len(request.cv_content) > 50000:
            raise ValidationError("Le CV est trop long (max 50,000 caractères)")
    
    def _build_prompt(self, request: GenerationRequest) -> str:
        """Construit le prompt pour la génération IA."""
        if request.is_career_change:
            return self._build_career_change_prompt(request)
        else:
            return self._build_standard_prompt(request)
    
    def _build_career_change_prompt(self, request: GenerationRequest) -> str:
        """Construit le prompt spécifique aux reconversions."""
        base_prompt = f"""
Tu es Marie, experte en reconversion professionnelle avec 15 ans d'expérience.
Ta spécialité : transformer les parcours atypiques en super-pouvoirs.

MISSION : Génère une lettre de motivation RECONVERSION exceptionnelle.

CONTEXTE RECONVERSION :
- Ancien domaine : {request.old_domain}
- Nouveau domaine : {request.new_domain}
- Compétences transférables : {request.transferable_skills}

TONE REQUIS : {request.tone.value}

APPROCHE NARRATIVE :
1. HOOK : Ouvre sur la motivation de changement (pas sur l'excuse)
2. BRIDGE : Montre le lien logique ancien → nouveau métier
3. PROOF : Démontre la valeur des compétences transférables
4. VISION : Projette sur la contribution future

CV CANDIDAT :
---
{request.cv_content}
---

OFFRE CIBLE :
---
{request.job_offer_content}
---

CONSIGNES STRICTES :
- 280-350 mots maximum
- Ton {request.tone.value} authentique
- Valorise l'expérience passée comme atout unique
- Intègre naturellement les mots-clés de l'offre
- Termine par un appel à l'action confiant

Génère la lettre ci-dessous :
"""
        return base_prompt
    
    def _build_standard_prompt(self, request: GenerationRequest) -> str:
        """Construit le prompt standard."""
        # Implémentation du prompt standard
        pass
    
    def _calculate_ats_score(self, letter_content: str, job_offer: str) -> float:
        """Calcule le score ATS."""
        # Implémentation du calcul ATS
        return 85.0
    
    def _calculate_readability_score(self, content: str) -> float:
        """Calcule le score de lisibilité."""
        # Implémentation Flesch-Kincaid ou similaire
        return 75.0
    
    def _calculate_keyword_match(self, letter: str, job_offer: str) -> float:
        """Calcule la correspondance des mots-clés."""
        # Implémentation de matching keywords
        return 78.0
    
    def _generate_suggestions(self, letter: Letter) -> list[str]:
        """Génère des suggestions d'amélioration."""
        return [
            "Ajouter plus de mots-clés de l'offre d'emploi",
            "Renforcer l'accroche d'ouverture",
            "Quantifier davantage les réalisations"
        ]
    
    def _identify_strengths(self, letter: Letter) -> list[str]:
        """Identifie les points forts de la lettre."""
        return [
            "Ton approprié au secteur",
            "Structure claire et logique",
            "Bonne valorisation de l'expérience"
        ]
    
    def _identify_improvements(self, letter: Letter) -> list[str]:
        """Identifie les axes d'amélioration."""
        return [
            "Personnaliser davantage pour l'entreprise",
            "Ajouter un exemple concret de réalisation"
        ]
```

---

## 🏗️ **PHASE 2 : INFRASTRUCTURE & SERVICES EXTERNES**

### **2.1 Client IA Abstrait**

**Fichier: `infrastructure/ai/gemini_client.py`**
```python
"""Client Google Gemini avec gestion d'erreurs robuste."""
import google.generativeai as genai
from typing import Optional, Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential
import logging

from config.settings import settings
from shared.interfaces.ai_interface import AIServiceInterface
from shared.exceptions.specific_exceptions import AIServiceError, RateLimitError
from core.entities.letter import UserTier

logger = logging.getLogger(__name__)

class GeminiClient(AIServiceInterface):
    """Client pour Google Gemini AI."""
    
    def __init__(self):
        """Initialise le client Gemini."""
        try:
            genai.configure(api_key=settings.google_api_key)
            self.model = genai.GenerativeModel('models/gemini-1.5-flash')
            logger.info("Gemini client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            raise AIServiceError(f"Impossible d'initialiser le client IA: {e}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def generate_content(
        self, 
        prompt: str, 
        user_tier: UserTier,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> str:
        """
        Génère du contenu avec Gemini.
        
        Args:
            prompt: Prompt pour la génération
            user_tier: Niveau d'abonnement utilisateur
            max_tokens: Nombre maximum de tokens
            temperature: Température de génération
            
        Returns:
            str: Contenu généré
            
        Raises:
            AIServiceError: En cas d'erreur de génération
            RateLimitError: En cas de limite de débit atteinte
        """
        try:
            # Configuration selon le tier utilisateur
            generation_config = self._get_generation_config(user_tier, max_tokens, temperature)
            
            # Validation du prompt
            if not prompt or len(prompt) < 10:
                raise AIServiceError("Prompt trop court ou vide")
            
            if len(prompt) > 100000:
                raise AIServiceError("Prompt trop long (max 100k caractères)")
            
            # Génération
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config,
                request_options={"timeout": 30}
            )
            
            if not response.text:
                raise AIServiceError("Réponse vide du service IA")
            
            # Validation de la réponse
            if len(response.text) < 50:
                raise AIServiceError("Réponse trop courte du service IA")
            
            logger.info(f"Content generated successfully for {user_tier.value} user")
            return response.text.strip()
            
        except genai.types.BlockedPromptException:
            logger.warning("Prompt blocked by safety filters")
            raise AIServiceError("Contenu bloqué par les filtres de sécurité")
        
        except genai.types.StopCandidateException:
            logger.warning("Generation stopped by safety filters")
            raise AIServiceError("Génération interrompue par les filtres de sécurité")
        
        except Exception as e:
            if "quota" in str(e).lower() or "rate limit" in str(e).lower():
                logger.error(f"Rate limit exceeded: {e}")
                raise RateLimitError("Limite de débit API atteinte. Veuillez réessayer plus tard.")
            
            logger.error(f"Unexpected error in content generation: {e}")
            raise AIServiceError(f"Erreur inattendue du service IA: {e}")
    
    def _get_generation_config(
        self, 
        user_tier: UserTier, 
        max_tokens: int, 
        temperature: float
    ) -> Dict[str, Any]:
        """Configure la génération selon le tier utilisateur."""
        base_config = {
            "max_output_tokens": max_tokens,
            "temperature": temperature,
        }
        
        # Configuration spécifique par tier
        if user_tier == UserTier.PREMIUM_PLUS:
            base_config.update({
                "temperature": 0.8,  # Plus créatif
                "top_p": 0.9,
                "top_k": 40
            })
        elif user_tier == UserTier.PREMIUM:
            base_config.update({
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 30
            })
        else:  # FREE
            base_config.update({
                "temperature": 0.6,  # Plus conservateur
                "top_p": 0.7,
                "top_k": 20
            })
        
        return base_config
```

### **2.2 Gestionnaire de Session Sécurisé**

**Fichier: `infrastructure/storage/session_manager.py`**
```python
"""Gestionnaire de session sécurisé et performant."""
import streamlit as st
import time
import logging
from typing import Any, Optional, Dict, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta

from config.settings import settings
from shared.exceptions.specific_exceptions import SessionError, SecurityError

logger = logging.getLogger(__name__)

@dataclass
class SessionData:
    """Données de session structurées."""
    user_id: str
    created_at: datetime
    last_activity: datetime
    data: Dict[str, Any]
    
    @property
    def is_expired(self) -> bool:
        """Vérifie si la session est expirée."""
        return (datetime.now() - self.last_activity).total_seconds() > settings.session_timeout
    
    @property
    def session_duration(self) -> float:
        """Durée de la session en secondes."""
        return (datetime.now() - self.created_at).total_seconds()

class SecureSessionManager:
    """Gestionnaire de session sécurisé avec validation et nettoyage automatique."""
    
    # Clés sensibles qui nécessitent un nettoyage spécial
    SENSITIVE_KEYS: Set[str] = {
        'cv_content', 'job_offer_content', 'generated_letter',
        'api_key', 'personal_data', 'uploaded_files'
    }
    
    # Clés critiques qui doivent persister
    CRITICAL_KEYS: Set[str] = {
        'user_id', 'session_id', 'user_tier', 'generation_count'
    }
    
    def __init__(self):
        """Initialise le gestionnaire de session."""
        self._init_session()
    
    def _init_session(self) -> None:
        """Initialise une nouvelle session ou récupère l'existante."""
        try:
            if 'session_data' not in st.session_state:
                session_data = SessionData(
                    user_id=self._generate_user_id(),
                    created_at=datetime.now(),
                    last_activity=datetime.now(),
                    data={}
                )
                st.session_state.session_data = session_data
                logger.info(f"New session created: {session_data.user_id}")
            else:
                # Mise à jour de l'activité
                st.session_state.session_data.last_activity = datetime.now()
                
                # Vérification d'expiration
                if st.session_state.session_data.is_expired:
                    logger.warning(f"Session expired: {st.session_state.session_data.user_id}")
                    self._cleanup_expired_session()
                    self._init_session()
                    
        except Exception as e:
            logger.error(f"Error initializing session: {e}")
            raise SessionError(f"Impossible d'initialiser la session: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Récupère une valeur de session.
        
        Args:
            key: Clé à récupérer
            default: Valeur par défaut
            
        Returns:
            Any: Valeur de session ou défaut
        """
        try:
            session_data: SessionData = st.session_state.session_data
            return session_data.data.get(key, default)
        except (KeyError, AttributeError):
            logger.warning(f"Session data not found for key: {key}")
            return default
    
    def set(self, key: str, value: Any) -> None:
        """
        Définit une valeur de session avec validation.
        
        Args:
            key: Clé à définir
            value: Valeur à stocker
            
        Raises:
            SessionError: En cas d'erreur de stockage
            SecurityError: En cas de données sensibles non sécurisées
        """
        try:
            # Validation des données sensibles
            if key in self.SENSITIVE_KEYS:
                self._validate_sensitive_data(key, value)
            
            # Validation de la taille
            if isinstance(value, str) and len(value) > 100000:
                logger.warning(f"Large data stored in session for key: {key}")
            
            session_data: SessionData = st.session_state.session_data
            session_data.data[key] = value
            session_data.last_activity = datetime.now()
            
            logger.debug(f"Session value set for key: {key}")
            
        except Exception as e:
            logger.error(f"Error setting session value for key {key}: {e}")
            raise SessionError(f"Impossible de stocker la valeur: {e}")
    
    def delete(self, key: str) -> None:
        """
        Supprime une clé de session.
        
        Args:
            key: Clé à supprimer
        """
        try:
            session_data: SessionData = st.session_state.session_data
            if key in session_data.data:
                del session_data.data[key]
                logger.debug(f"Session key deleted: {key}")
        except Exception as e:
            logger.warning(f"Error deleting session key {key}: {e}")
    
    def clear_sensitive_data(self) -> None:
        """Nettoie toutes les données sensibles de la session."""
        try:
            session_data: SessionData = st.session_state.session_data
            for key in list(session_data.data.keys()):
                if key in self.SENSITIVE_KEYS:
                    del session_data.data[key]
            
            logger.info("Sensitive data cleared from session")
            
        except Exception as e:
            logger.error(f"Error clearing sensitive data: {e}")
    
    def reset_session(self) -> None:
        """Réinitialise complètement la session."""
        try:
            # Sauvegarde des données critiques
            critical_data = {}
            if 'session_data' in st.session_state:
                session_data: SessionData = st.session_state.session_data
                for key in self.CRITICAL_KEYS:
                    if key in session_data.data:
                        critical_data[key] = session_data.data[key]
            
            # Nettoyage complet
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            
            # Réinitialisation
            self._init_session()
            
            # Restauration des données critiques
            for key, value in critical_data.items():
                self.set(key, value)
            
            logger.info("Session reset successfully")
            
        except Exception as e:
            logger.error(f"Error resetting session: {e}")
            raise SessionError(f"Impossible de réinitialiser la session: {e}")
    
    def get_session_info(self) -> Dict[str, Any]:
        """Retourne les informations de session."""
        try:
            session_data: SessionData = st.session_state.session_data
            return {
                'user_id': session_data.user_id,
                'created_at': session_data.created_at.isoformat(),
                'last_activity': session_data.last_activity.isoformat(),
                'duration_seconds': session_data.session_duration,
                'data_keys': list(session_data.data.keys()),
                'data_size': len(str(session_data.data))
            }
        except Exception as e:
            logger.warning(f"Error getting session info: {e}")
            return {}
    
    def _generate_user_id(self) -> str:
        """Génère un ID utilisateur unique."""
        import secrets
        return f"user_{int(time.time())}_{secrets.token_hex(4)}"
    
    def _validate_sensitive_data(self, key: str, value: Any) -> None:
        """Valide les données sensibles avant stockage."""
        if key in {'api_key', 'personal_data'}:
            if not isinstance(value, str) or len(value) < 10:
                raise SecurityError(f"Invalid sensitive data for key: {key}")
        
        # Détection basique de données personnelles
        if isinstance(value, str):
            import re
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            if re.search(email_pattern, value):
                logger.warning(f"Potential email detected in session data for key: {key}")
    
    def _cleanup_expired_session(self) -> None:
        """Nettoie une session expirée."""
        try:
            self.clear_sensitive_data()
            logger.info("Expired session cleaned up")
        except Exception as e:
            logger.error(f"Error cleaning up expired session: {e}")
```

---

## 🎨 **PHASE 3 : COUCHE PRÉSENTATION MODULAIRE**

### **3.1 Composants UI Réutilisables**

**Fichier: `ui/components/file_uploader.py`**
```python
"""Composant de téléchargement de fichiers sécurisé."""
import streamlit as st
from typing import Optional, List, Callable
import hashlib
import logging

from config.settings import settings
from shared.exceptions.specific_exceptions import FileValidationError
from infrastructure.security.input_validator import InputValidator

logger = logging.getLogger(__name__)

class SecureFileUploader:
    """Composant de téléchargement de fichiers avec validation sécurisée."""
    
    def __init__(self, validator: InputValidator):
        self.validator = validator
    
    def render(
        self,
        label: str,
        accepted_types: List[str],
        key: str,
        max_size: Optional[int] = None,
        help_text: Optional[str] = None,
        on_upload: Optional[Callable] = None
    ) -> Optional[bytes]:
        """
        Affiche un composant de téléchargement sécurisé.
        
        Args:
            label: Label du composant
            accepted_types: Types de fichiers acceptés
            key: Clé unique pour le composant
            max_size: Taille maximale en bytes
            help_text: Texte d'aide
            on_upload: Callback appelé après upload
            
        Returns:
            Optional[bytes]: Contenu du fichier ou None
            
        Raises:
            FileValidationError: En cas de fichier invalide
        """
        max_size = max_size or settings.max_file_size
        
        # Interface utilisateur
        uploaded_file = st.file_uploader(
            label,
            type=accepted_types,
            key=key,
            help=help_text or f"Formats acceptés: {', '.join(accepted_types).upper()}. Taille max: {max_size // (1024*1024)}MB"
        )
        
        if uploaded_file is None:
            return None
        
        try:
            # Validation sécurisée
            file_content = self._validate_and_process_file(
                uploaded_file, 
                accepted_types, 
                max_size
            )
            
            # Feedback utilisateur
            file_hash = hashlib.md5(file_content).hexdigest()[:8]
            st.success(f"✅ {uploaded_file.name} chargé (ID: {file_hash})")
            
            # Callback si défini
            if on_upload:
                on_upload(uploaded_file.name, file_content)
            
            return file_content
            
        except FileValidationError as e:
            st.error(f"❌ Erreur de fichier: {e}")
            logger.warning(f"File validation error for {uploaded_file.name}: {e}")
            return None
        except Exception as e:
            st.error(f"❌ Erreur inattendue lors du traitement du fichier")
            logger.error(f"Unexpected error processing file {uploaded_file.name}: {e}")
            return None
    
    def _validate_and_process_file(
        self, 
        uploaded_file, 
        accepted_types: List[str],
        max_size: int
    ) -> bytes:
        """
        Valide et traite un fichier uploadé.
        
        Args:
            uploaded_file: Fichier uploadé par Streamlit
            accepted_types: Types acceptés
            max_size: Taille maximale
            
        Returns:
            bytes: Contenu validé du fichier
            
        Raises:
            FileValidationError: En cas d'erreur de validation
        """
        # Validation du nom de fichier
        if not uploaded_file.name or len(uploaded_file.name) > 255:
            raise FileValidationError("Nom de fichier invalide")
        
        # Validation de l'extension
        file_extension = uploaded_file.name.split('.')[-1].lower()
        if file_extension not in accepted_types:
            raise FileValidationError(f"Type de fichier non autorisé: .{file_extension}")
        
        # Lecture du contenu
        file_content = uploaded_file.getvalue()
        
        # Validation de la taille
        if len(file_content) == 0:
            raise FileValidationError("Fichier vide")
        
        if len(file_content) > max_size:
            raise FileValidationError(f"Fichier trop volumineux ({len(file_content) // (1024*1024)}MB > {max_size // (1024*1024)}MB)")
        
        # Validation du contenu avec le service de validation
        self.validator.validate_file_content(file_content, file_extension)
        
        return file_content
```

### **3.2 Page Générateur Modulaire**

**Fichier: `ui/pages/generator_page.py`**
```python
"""Page principale de génération de lettres."""
import streamlit as st
from typing import Optional
import logging

from core.entities.letter import GenerationRequest, ToneType, UserTier
from core.services.letter_service import LetterServiceInterface
from ui.components.file_uploader import SecureFileUploader
from ui.components.progress_bar import ProgressIndicator
from ui.components.letter_editor import LetterEditor
from infrastructure.storage.session_manager import SecureSessionManager
from shared.exceptions.specific_exceptions import LetterGenerationError, ValidationError

logger = logging.getLogger(__name__)

class GeneratorPage:
    """Page de génération de lettres modulaire."""
    
    def __init__(
        self,
        letter_service: LetterServiceInterface,
        file_uploader: SecureFileUploader,
        session_manager: SecureSessionManager,
        progress_indicator: ProgressIndicator,
        letter_editor: LetterEditor
    ):
        self.letter_service = letter_service
        self.file_uploader = file_uploader
        self.session_manager = session_manager
        self.progress_indicator = progress_indicator
        self.letter_editor = letter_editor
    
    def render(self) -> None:
        """Affiche la page de génération."""
        st.markdown("### 🚀 Générateur de Lettres Phoenix")
        
        # Indicateur de progression
        progress = self.session_manager.get('generation_progress', 0)
        self.progress_indicator.render(progress, "Progression de la génération")
        
        # Section d'upload de fichiers
        self._render_file_upload_section()
        
        # Configuration IA
        if self._has_required_files():
            self._render_ai_configuration()
            
            # Bouton de génération
            if self._render_generation_button():
                self._process_generation()
        
        # Affichage de la lettre générée
        self._render_generated_letter()
    
    def _render_file_upload_section(self) -> None:
        """Affiche la section d'upload de fichiers."""
        col1, col2 = st.columns(2)
        
        with col1:
            cv_content = self.file_uploader.render(
                label="📄 Votre CV",
                accepted_types=['pdf', 'txt'],
                key="cv_upload",
                help_text="Votre CV au format PDF ou TXT",
                on_upload=self._on_cv_upload
            )
            
            if cv_content:
                self.session_manager.set('cv_content', cv_content.decode('utf-8', errors='ignore'))
        
        with col2:
            job_offer_content = self.file_uploader.render(
                label="📋 Offre d'emploi",
                accepted_types=['txt', 'pdf'],
                key="job_offer_upload",
                help_text="L'offre d'emploi au format TXT ou PDF",
                on_upload=self._on_job_offer_upload
            )
            
            if job_offer_content:
                self.session_manager.set('job_offer_content', job_offer_content.decode('utf-8', errors='ignore'))
    
    def _render_ai_configuration(self) -> None:
        """Affiche la configuration IA."""
        st.markdown("### ⚙️ Configuration de l'IA")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Sélection du ton
            tone_options = [tone.value for tone in ToneType]
            selected_tone = st.selectbox(
                "🎭 Ton souhaité",
                options=tone_options,
                index=tone_options.index(self.session_manager.get('selected_tone', 'formel')),
                key="tone_selector"
            )
            self.session_manager.set('selected_tone', selected_tone)
        
        with col2:
            # Reconversion
            is_career_change = st.checkbox(
                "🔄 C'est une reconversion",
                value=self.session_manager.get('is_career_change', False),
                key="career_change_checkbox"
            )
            self.session_manager.set('is_career_change', is_career_change)
        
        # Configuration reconversion
        if is_career_change:
            self._render_career_change_config()
    
    def _render_career_change_config(self) -> None:
        """Affiche la configuration spécifique à la reconversion."""
        st.markdown("#### 🔄 Configuration Reconversion")
        
        col1, col2 = st.columns(2)
        
        with col1:
            old_domain = st.text_input(
                "📈 Ancien domaine",
                value=self.session_manager.get('old_domain', ''),
                placeholder="Ex: Marketing, Comptabilité",
                key="old_domain_input"
            )
            self.session_manager.set('old_domain', old_domain)
        
        with col2:
            new_domain = st.text_input(
                "🎯 Nouveau domaine",
                value=self.session_manager.get('new_domain', ''),
                placeholder="Ex: Cybersécurité, Développement",
                key="new_domain_input"
            )
            self.session_manager.set('new_domain', new_domain)
        
        # Compétences transférables
        transferable_skills = st.text_area(
            "🔧 Compétences transférables",
            value=self.session_manager.get('transferable_skills', ''),
            help="Listez les compétences de votre ancienne carrière pertinentes pour le nouveau poste",
            key="transferable_skills_input"
        )
        self.session_manager.set('transferable_skills', transferable_skills)
    
    def _render_generation_button(self) -> bool:
        """Affiche le bouton de génération et retourne True si cliqué."""
        # Vérification du cooldown
        last_generation = self.session_manager.get('last_generation_time', 0)
        current_time = time.time()
        cooldown_remaining = max(0, 60 - (current_time - last_generation))
        
        if cooldown_remaining > 0:
            st.button(
                f"⏳ Attendre {int(cooldown_remaining)}s",
                disabled=True,
                use_container_width=True
            )
            return False
        
        return st.button(
            "✨ Générer ma lettre",
            type="primary",
            use_container_width=True,
            key="generate_button"
        )
    
    def _process_generation(self) -> None:
        """Traite la génération de lettre."""
        try:
            # Mise à jour du progress
            self.session_manager.set('generation_progress', 25)
            
            with st.spinner("🤖 Génération en cours..."):
                # Construction de la requête
                request = self._build_generation_request()
                
                # Génération de la lettre
                self.session_manager.set('generation_progress', 75)
                user_id = self.session_manager.get('user_id')
                letter = self.letter_service.generate_letter(request, user_id)
                
                # Sauvegarde
                self.session_manager.set('generated_letter', letter.content)
                self.session_manager.set('generation_progress', 100)
                self.session_manager.set('last_generation_time', time.time())
                
                st.success("✅ Lettre générée avec succès!")
                
        except ValidationError as e:
            st.error(f"❌ Erreur de validation: {e}")
            logger.warning(f"Validation error in generation: {e}")
        except LetterGenerationError as e:
            st.error(f"❌ Erreur de génération: {e}")
            logger.error(f"Generation error: {e}")
        except Exception as e:
            st.error("❌ Erreur inattendue lors de la génération")
            logger.error(f"Unexpected error in generation: {e}")
        finally:
            # Reset du progress en cas d'erreur
            if self.session_manager.get('generation_progress', 0) != 100:
                self.session_manager.set('generation_progress', 0)
    
    def _render_generated_letter(self) -> None:
        """Affiche la lettre générée."""
        generated_letter = self.session_manager.get('generated_letter')
        
        if generated_letter:
            st.markdown("---")
            st.markdown("### ✨ Votre Lettre Phoenix Générée")
            
            # Éditeur de lettre
            edited_letter = self.letter_editor.render(
                content=generated_letter,
                key="letter_editor"
            )
            
            # Sauvegarde des modifications
            if edited_letter != generated_letter:
                self.session_manager.set('generated_letter', edited_letter)
    
    # Méthodes utilitaires
    def _has_required_files(self) -> bool:
        """Vérifie si les fichiers requis sont présents."""
        return (
            self.session_manager.get('cv_content') and 
            self.session_manager.get('job_offer_content')
        )
    
    def _build_generation_request(self) -> GenerationRequest:
        """Construit la requête de génération."""
        return GenerationRequest(
            cv_content=self.session_manager.get('cv_content'),
            job_offer_content=self.session_manager.get('job_offer_content'),
            tone=ToneType(self.session_manager.get('selected_tone', 'formel')),
            user_tier=UserTier(self.session_manager.get('user_tier', 'free')),
            is_career_change=self.session_manager.get('is_career_change', False),
            old_domain=self.session_manager.get('old_domain'),
            new_domain=self.session_manager.get('new_domain'),
            transferable_skills=self.session_manager.get('transferable_skills')
        )
    
    def _on_cv_upload(self, filename: str, content: bytes) -> None:
        """Callback appelé lors de l'upload du CV."""
        self.session_manager.set('generation_progress', 33)
        logger.info(f"CV uploaded: {filename}")
    
    def _on_job_offer_upload(self, filename: str, content: bytes) -> None:
        """Callback appelé lors de l'upload de l'offre."""
        current_progress = self.session_manager.get('generation_progress', 0)
        self.session_manager.set('generation_progress', max(current_progress, 66))
        logger.info(f"Job offer uploaded: {filename}")
```

---

## 🧪 **PHASE 4 : TESTS & VALIDATION**

### **4.1 Tests Unitaires**

**Fichier: `tests/unit/test_core/test_letter_service.py`**
```python
"""Tests unitaires pour le service de génération de lettres."""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from core.services.letter_service import LetterService
from core.entities.letter import GenerationRequest, ToneType, UserTier, Letter
from shared.exceptions.specific_exceptions import LetterGenerationError, ValidationError
from shared.interfaces.ai_interface import AIServiceInterface
from shared.interfaces.monitoring_interface import MonitoringInterface

class TestLetterService:
    """Tests pour LetterService."""
    
    @pytest.fixture
    def mock_ai_service(self):
        """Mock du service IA."""
        mock = Mock(spec=AIServiceInterface)
        mock.generate_content.return_value = "Lettre de motivation générée par l'IA"
        return mock
    
    @pytest.fixture
    def mock_monitoring(self):
        """Mock du service de monitoring."""
        mock = Mock(spec=MonitoringInterface)
        mock.track_operation.return_value.__enter__ = Mock()
        mock.track_operation.return_value.__exit__ = Mock()
        return mock
    
    @pytest.fixture
    def letter_service(self, mock_ai_service, mock_monitoring):
        """Instance du service de lettres."""
        return LetterService(mock_ai_service, mock_monitoring)
    
    @pytest.fixture
    def valid_request(self):
        """Requête valide de génération."""
        return GenerationRequest(
            cv_content="CV content with enough text to be valid for testing purposes",
            job_offer_content="Job offer content",
            tone=ToneType.FORMAL,
            user_tier=UserTier.FREE,
            is_career_change=False
        )
    
    def test_generate_letter_success(self, letter_service, valid_request, mock_ai_service):
        """Test de génération réussie."""
        # Arrange
        user_id = "test_user_123"
        expected_content = "Lettre de motivation générée"
        mock_ai_service.generate_content.return_value = expected_content
        
        # Act
        result = letter_service.generate_letter(valid_request, user_id)
        
        # Assert
        assert isinstance(result, Letter)
        assert result.content == expected_content
        assert result.user_id == user_id
        assert result.generation_request == valid_request
        assert isinstance(result.created_at, datetime)
        
        # Vérification des appels
        mock_ai_service.generate_content.assert_called_once()
    
    def test_generate_letter_empty_cv_raises_validation_error(self, letter_service):
        """Test avec CV vide lève ValidationError."""
        # Arrange
        invalid_request = GenerationRequest(
            cv_content="",  # CV vide
            job_offer_content="Job offer content",
            tone=ToneType.FORMAL,
            user_tier=UserTier.FREE
        )
        
        # Act & Assert
        with pytest.raises(ValidationError, match="Le contenu du CV est requis"):
            letter_service.generate_letter(invalid_request, "test_user")
    
    def test_generate_letter_empty_job_offer_raises_validation_error(self, letter_service):
        """Test avec offre vide lève ValidationError."""
        # Arrange
        invalid_request = GenerationRequest(
            cv_content="Valid CV content with enough text",
            job_offer_content="",  # Offre vide
            tone=ToneType.FORMAL,
            user_tier=UserTier.FREE
        )
        
        # Act & Assert
        with pytest.raises(ValidationError, match="Le contenu de l'offre d'emploi est requis"):
            letter_service.generate_letter(invalid_request, "test_user")
    
    def test_generate_letter_cv_too_long_raises_validation_error(self, letter_service):
        """Test avec CV trop long lève ValidationError."""
        # Arrange
        invalid_request = GenerationRequest(
            cv_content="x" * 50001,  # CV trop long
            job_offer_content="Job offer content",
            tone=ToneType.FORMAL,
            user_tier=UserTier.FREE
        )
        
        # Act & Assert
        with pytest.raises(ValidationError, match="Le CV est trop long"):
            letter_service.generate_letter(invalid_request, "test_user")
    
    def test_generate_letter_career_change_prompt(self, letter_service, mock_ai_service):
        """Test de génération avec reconversion."""
        # Arrange
        career_change_request = GenerationRequest(
            cv_content="Valid CV content with enough text",
            job_offer_content="Job offer content",
            tone=ToneType.DYNAMIC,
            user_tier=UserTier.PREMIUM,
            is_career_change=True,
            old_domain="Marketing",
            new_domain="Cybersécurité",
            transferable_skills="Communication, Gestion de projet"
        )
        
        # Act
        letter_service.generate_letter(career_change_request, "test_user")
        
        # Assert
        mock_ai_service.generate_content.assert_called_once()
        call_args = mock_ai_service.generate_content.call_args
        prompt = call_args[1]['prompt']
        
        # Vérifications du prompt de reconversion
        assert "reconversion" in prompt.lower()
        assert "Marketing" in prompt
        assert "Cybersécurité" in prompt
        assert "Communication, Gestion de projet" in prompt
    
    def test_generate_letter_ai_service_error_raises_letter_generation_error(
        self, letter_service, valid_request, mock_ai_service
    ):
        """Test avec erreur du service IA lève LetterGenerationError."""
        # Arrange
        from shared.exceptions.specific_exceptions import AIServiceError
        mock_ai_service.generate_content.side_effect = AIServiceError("API Error")
        
        # Act & Assert
        with pytest.raises(LetterGenerationError, match="Erreur du service IA"):
            letter_service.generate_letter(valid_request, "test_user")
    
    def test_analyze_letter_success(self, letter_service):
        """Test d'analyse de lettre réussie."""
        # Arrange
        letter = Letter(
            content="Contenu de lettre à analyser avec suffisamment de texte pour être valide",
            generation_request=GenerationRequest(
                cv_content="CV content",
                job_offer_content="Job offer with Python development keywords",
                tone=ToneType.FORMAL,
                user_tier=UserTier.FREE
            ),
            created_at=datetime.now(),
            user_id="test_user"
        )
        
        # Act
        analysis = letter_service.analyze_letter(letter)
        
        # Assert
        assert analysis.letter_id.startswith("test_user_")
        assert 0 <= analysis.ats_score <= 100
        assert 0 <= analysis.readability_score <= 100
        assert 0 <= analysis.keyword_match_score <= 100
        assert isinstance(analysis.suggestions, list)
        assert isinstance(analysis.strengths, list)
        assert isinstance(analysis.improvements, list)
    
    @pytest.mark.parametrize("user_tier,expected_in_prompt", [
        (UserTier.FREE, "expert en ressources humaines"),
        (UserTier.PREMIUM, "15 ans d'expérience"),
        (UserTier.PREMIUM_PLUS, "renommée internationale")
    ])
    def test_prompt_quality_by_tier(self, letter_service, mock_ai_service, user_tier, expected_in_prompt):
        """Test de la qualité du prompt selon le tier utilisateur."""
        # Arrange
        request = GenerationRequest(
            cv_content="Valid CV content with enough text",
            job_offer_content="Job offer content",
            tone=ToneType.FORMAL,
            user_tier=user_tier
        )
        
        # Act
        letter_service.generate_letter(request, "test_user")
        
        # Assert
        call_args = mock_ai_service.generate_content.call_args
        prompt = call_args[1]['prompt']
        assert expected_in_prompt in prompt
```

### **4.2 Tests d'Intégration**

**Fichier: `tests/integration/test_letter_generation.py`**
```python
"""Tests d'intégration pour la génération de lettres."""
import pytest
from unittest.mock import patch
import tempfile
import os

from core.services.letter_service import LetterService
from core.entities.letter import GenerationRequest, ToneType, UserTier
from infrastructure.ai.gemini_client import GeminiClient
from infrastructure.monitoring.performance_monitor import PerformanceMonitor

@pytest.mark.integration
class TestLetterGenerationIntegration:
    """Tests d'intégration pour la génération de lettres."""
    
    @pytest.fixture(scope="class")
    def letter_service_with_real_ai(self):
        """Service de lettres avec vrai client IA (si API key disponible)."""
        if not os.getenv('GOOGLE_API_KEY'):
            pytest.skip("GOOGLE_API_KEY not available for integration tests")
        
        ai_client = GeminiClient()
        monitoring = PerformanceMonitor()
        return LetterService(ai_client, monitoring)
    
    def test_full_letter_generation_flow(self, letter_service_with_real_ai):
        """Test du flux complet de génération de lettre."""
        # Arrange
        request = GenerationRequest(
            cv_content="""
            Matthieu Rubia
            Aide-soignant expérimenté, 7 ans d'expérience dans l'accompagnement
            de personnes en situation de handicap. Compétences en gestion de crise,
            communication avec les familles, travail en équipe pluridisciplinaire.
            """,
            job_offer_content="""
            Recherche Opérateur en Cybersécurité junior.
            Missions: surveillance des systèmes, analyse des incidents,
            application des procédures de sécurité.
            Profil: rigueur, capacité d'adaptation, travail en équipe.
            """,
            tone=ToneType.FORMAL,
            user_tier=UserTier.FREE,
            is_career_change=True,
            old_domain="Aide-soignant",
            new_domain="Cybersécurité",
            transferable_skills="Gestion de crise, Rigueur, Travail en équipe"
        )
        
        # Act
        letter = letter_service_with_real_ai.generate_letter(request, "integration_test_user")
        
        # Assert
        assert letter is not None
        assert len(letter.content) > 100
        assert "cybersécurité" in letter.content.lower() or "sécurité" in letter.content.lower()
        assert letter.user_id == "integration_test_user"
        
        # Vérifications spécifiques à la reconversion
        content_lower = letter.content.lower()
        assert any(skill.lower() in content_lower for skill in ["rigueur", "équipe", "crise"])
    
    def test_letter_analysis_integration(self, letter_service_with_real_ai):
        """Test d'intégration de l'analyse de lettre."""
        # Arrange - Générer d'abord une lettre
        request = GenerationRequest(
            cv_content="Développeur Python avec 3 ans d'expérience",
            job_offer_content="Recherche développeur Python senior pour projets IA",
            tone=ToneType.DYNAMIC,
            user_tier=UserTier.PREMIUM
        )
        
        letter = letter_service_with_real_ai.generate_letter(request, "test_user")
        
        # Act
        analysis = letter_service_with_real_ai.analyze_letter(letter)
        
        # Assert
        assert analysis is not None
        assert 0 <= analysis.ats_score <= 100
        assert 0 <= analysis.readability_score <= 100
        assert 0 <= analysis.keyword_match_score <= 100
        assert len(analysis.suggestions) > 0
        assert len(analysis.strengths) > 0
    
    @pytest.mark.parametrize("user_tier", [UserTier.FREE, UserTier.PREMIUM, UserTier.PREMIUM_PLUS])
    def test_generation_quality_by_tier(self, letter_service_with_real_ai, user_tier):
        """Test de la qualité de génération selon le tier."""
        # Arrange
        request = GenerationRequest(
            cv_content="Manager avec 5 ans d'expérience en gestion d'équipe",
            job_offer_content="Recherche chef de projet pour startup innovante",
            tone=ToneType.STARTUP,
            user_tier=user_tier
        )
        
        # Act
        letter = letter_service_with_real_ai.generate_letter(request, f"test_user_{user_tier.value}")
        
        # Assert
        assert letter is not None
        assert len(letter.content) > 200  # Plus long pour les tiers supérieurs
        
        # Les tiers supérieurs devraient avoir du contenu plus sophistiqué
        if user_tier == UserTier.PREMIUM_PLUS:
            assert len(letter.content) > 300
        elif user_tier == UserTier.PREMIUM:
            assert len(letter.content) > 250
```

---

## 📋 **INSTRUCTIONS DE MIGRATION**

### **Étapes d'Exécution pour Gemini CLI**

1. **BACKUP COMPLET**
   ```bash
   # Créer une branche de sauvegarde
   git checkout -b backup-monolith
   git add . && git commit -m "Backup avant refactoring"
   git checkout main
   git checkout -b refactoring-modular
   ```

2. **CRÉATION DE LA STRUCTURE**
   ```bash
   # Créer tous les répertoires de la nouvelle architecture
   mkdir -p {config,core/{entities,use_cases,services},infrastructure/{ai,storage,security,monitoring},ui/{components,pages,styles,state},shared/{types,exceptions,utils,interfaces},tests/{unit,integration,fixtures},requirements,scripts,docs}
   ```

3. **MIGRATION PROGRESSIVE**
   - **Jour 1-2** : Extraire les entités et exceptions
   - **Jour 3-4** : Migrer les services core
   - **Jour 5-7** : Refactorer l'infrastructure
   - **Jour 8-10** : Moduler l'interface utilisateur
   - **Jour 11-14** : Tests et validation

4. **VALIDATION CONTINUE**
   ```bash
   # À chaque étape, s'assurer que l'app fonctionne
   streamlit run app.py
   # Lancer les tests
   pytest tests/ -v
   ```

### **Points d'Attention Critiques**

1. **Gestion des Imports** : Mettre à jour tous les imports progressivement
2. **State Management** : Migrer délicatement le session state
3. **Dépendances** : Vérifier la compatibilité des packages
4. **Tests** : Implémenter les tests au fur et à mesure
5. **Configuration** : Centraliser toute la configuration

---

## 🎯 **RÉSULTATS ATTENDUS POST-REFACTORING**

### **Métriques de Qualité Cibles**
- **Cyclomatic Complexity** : < 10 par fonction
- **Lines per Function** : < 50 lignes
- **Test Coverage** : > 80%
- **Documentation** : > 90%
- **Performance** : +50% temps de chargement
- **Maintenabilité** : Équipe 5+ développeurs possible

### **Bénéfices Business**
- **Scalabilité** : Support 10,000+ utilisateurs simultanés
- **Développement** : Nouvelles features 3x plus rapides
- **Debugging** : Résolution bugs 5x plus rapide
- **Onboarding** : Nouveau développeur opérationnel en 2 jours

---

**PRÊT POUR LE REFACTORING ? 🚀**

Ce guide fournit une roadmap complète pour transformer Phoenix Letters en application enterprise-grade. Suivre cette architecture garantira un code maintenable, scalable et de qualité professionnelle.