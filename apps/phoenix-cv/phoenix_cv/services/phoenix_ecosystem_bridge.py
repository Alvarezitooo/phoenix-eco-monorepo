"""
🌟 Phoenix Ecosystem Bridge - Intégration Intelligente
Système de liaison entre Phoenix Letters, Phoenix CV et Phoenix Site

Author: Claude Phoenix DevSecOps Guardian
Version: 1.0.0 - Ecosystem Integration
"""

import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

# Imports conditionnels
try:
    from utils.exceptions import SecurityException
    from utils.secure_logging import secure_logger
except ImportError:
    import logging

    class MockSecureLogger:
        def log_security_event(self, event_type, data, level="INFO"):
            logging.info(f"ECOSYSTEM_BRIDGE | {event_type}: {data}")

    class SecurityException(Exception):
        pass

    secure_logger = MockSecureLogger()


class PhoenixApp(Enum):
    """Applications de l'écosystème Phoenix"""

    LETTERS = "phoenix-letters"
    CV = "phoenix-cv"
    SITE = "phoenix-site"


@dataclass
class UserJourney:
    """Parcours utilisateur dans l'écosystème"""

    user_id: str
    current_app: PhoenixApp
    last_action: str
    data_context: Dict[str, Any]
    timestamp: datetime
    next_recommended_app: Optional[PhoenixApp] = None
    confidence_score: float = 0.0


@dataclass
class CrossAppData:
    """Données partagées entre applications"""

    user_id: str
    profile_data: Dict[str, Any]
    preferences: Dict[str, Any]
    generated_content: Dict[str, Any]
    journey_history: List[Dict[str, Any]]
    created_at: datetime
    expires_at: datetime


class PhoenixEcosystemBridge:
    """
    Bridge intelligent pour l'intégration Phoenix Ecosystem.
    Gère les redirections, partage de données et parcours utilisateur.
    """

    def __init__(self):
        self.app_urls = {
            PhoenixApp.LETTERS: "https://phoenix-letters.streamlit.app/",
            PhoenixApp.CV: "https://phoenix-cv.streamlit.app/",  # URL future
            PhoenixApp.SITE: "https://phoenix-ecosystem.fr/",  # URL future
        }

        self.dev_urls = {
            PhoenixApp.LETTERS: "http://localhost:8501",
            PhoenixApp.CV: "http://localhost:8502",
            PhoenixApp.SITE: "http://localhost:3000",
        }

        # Cache temporaire pour les données cross-app
        self._user_cache = {}
        self._journey_cache = {}

        secure_logger.log_security_event("PHOENIX_ECOSYSTEM_BRIDGE_INITIALIZED", {})

    def is_dev_mode(self) -> bool:
        """Vérifie si on est en mode développement"""
        return os.environ.get("DEV_MODE", "false").lower() == "true"

    def get_app_url(self, app: PhoenixApp) -> str:
        """Récupère l'URL de l'application selon l'environnement"""
        if self.is_dev_mode():
            return self.dev_urls.get(app, "#")
        return self.app_urls.get(app, "#")

    def analyze_user_journey(
        self, user_data: Dict[str, Any], current_app: PhoenixApp
    ) -> UserJourney:
        """
        Analyse le parcours utilisateur et recommande la prochaine application.
        """
        try:
            user_id = self._generate_anonymous_user_id(user_data)

            # Analyse contextuelle selon l'application actuelle
            if current_app == PhoenixApp.CV:
                return self._analyze_cv_journey(user_id, user_data)
            elif current_app == PhoenixApp.LETTERS:
                return self._analyze_letters_journey(user_id, user_data)
            else:
                return self._analyze_site_journey(user_id, user_data)

        except Exception as e:
            secure_logger.log_security_event(
                "JOURNEY_ANALYSIS_ERROR",
                {"error": str(e)[:100], "current_app": current_app.value},
                "ERROR",
            )
            return self._create_default_journey(user_data, current_app)

    def _analyze_cv_journey(
        self, user_id: str, user_data: Dict[str, Any]
    ) -> UserJourney:
        """Analyse spécifique depuis Phoenix CV"""

        # Si CV généré avec succès → recommander Phoenix Letters
        if user_data.get("cv_generated_successfully"):
            return UserJourney(
                user_id=user_id,
                current_app=PhoenixApp.CV,
                last_action="cv_generated",
                data_context={
                    "target_job": user_data.get("target_job", ""),
                    "user_tier": user_data.get("user_tier", "gratuit"),
                    "cv_optimization_score": user_data.get("optimization_score", 0),
                },
                timestamp=datetime.now(),
                next_recommended_app=PhoenixApp.LETTERS,
                confidence_score=0.85,
            )

        # Si formulaire rempli mais pas encore généré → encourager completion
        elif user_data.get("form_partially_filled"):
            return UserJourney(
                user_id=user_id,
                current_app=PhoenixApp.CV,
                last_action="form_filling",
                data_context=user_data,
                timestamp=datetime.now(),
                next_recommended_app=None,  # Rester sur CV
                confidence_score=0.95,
            )

        # Utilisateur explore → suggérer Phoenix Letters pour compléter
        else:
            return UserJourney(
                user_id=user_id,
                current_app=PhoenixApp.CV,
                last_action="exploring",
                data_context=user_data,
                timestamp=datetime.now(),
                next_recommended_app=PhoenixApp.LETTERS,
                confidence_score=0.65,
            )

    def _analyze_letters_journey(
        self, user_id: str, user_data: Dict[str, Any]
    ) -> UserJourney:
        """Analyse spécifique depuis Phoenix Letters"""

        # Si lettre générée → recommander Phoenix CV pour cohérence
        if user_data.get("letter_generated_successfully"):
            return UserJourney(
                user_id=user_id,
                current_app=PhoenixApp.LETTERS,
                last_action="letter_generated",
                data_context={
                    "target_company": user_data.get("target_company", ""),
                    "target_job": user_data.get("target_job", ""),
                    "user_tier": user_data.get("user_tier", "gratuit"),
                },
                timestamp=datetime.now(),
                next_recommended_app=PhoenixApp.CV,
                confidence_score=0.80,
            )

        # Exploration → rester sur Letters mais mentionner CV
        else:
            return UserJourney(
                user_id=user_id,
                current_app=PhoenixApp.LETTERS,
                last_action="exploring",
                data_context=user_data,
                timestamp=datetime.now(),
                next_recommended_app=PhoenixApp.CV,
                confidence_score=0.60,
            )

    def _analyze_site_journey(
        self, user_id: str, user_data: Dict[str, Any]
    ) -> UserJourney:
        """Analyse spécifique depuis Phoenix Site"""

        # Depuis le site → recommander selon l'intention
        page_viewed = user_data.get("page_viewed", "")

        if "cv" in page_viewed.lower():
            recommended_app = PhoenixApp.CV
            confidence = 0.75
        elif "lettre" in page_viewed.lower() or "letter" in page_viewed.lower():
            recommended_app = PhoenixApp.LETTERS
            confidence = 0.75
        else:
            # Par défaut, commencer par CV (plus foundational)
            recommended_app = PhoenixApp.CV
            confidence = 0.50

        return UserJourney(
            user_id=user_id,
            current_app=PhoenixApp.SITE,
            last_action=f"viewed_{page_viewed}",
            data_context=user_data,
            timestamp=datetime.now(),
            next_recommended_app=recommended_app,
            confidence_score=confidence,
        )

    def generate_cross_app_redirect_url(
        self,
        target_app: PhoenixApp,
        user_data: Dict[str, Any],
        utm_source: Optional[str] = None,
    ) -> str:
        """
        Génère une URL de redirection avec données pré-remplies.
        """
        try:
            base_url = self.get_app_url(target_app)

            # Génération du token de transfert de données
            transfer_token = self._generate_transfer_token(user_data)

            # Construction des paramètres URL
            params = []

            # UTM tracking pour analytics
            if utm_source:
                params.append(f"utm_source={utm_source}")
                params.append("utm_medium=ecosystem_redirect")
                params.append("utm_campaign=phoenix_integration")

            # Token de transfert de données
            if transfer_token:
                params.append(f"phoenix_transfer={transfer_token}")

            # Données directes (limitées pour sécurité URL)
            if user_data.get("target_job"):
                # Token chiffré au lieu de données directes
                if user_data.get("target_job"):
                    token = self._encrypt_url_data(user_data["target_job"][:50])
                    params.append(f"prefill_token={token}")

            if user_data.get("user_tier"):
                params.append(f"tier={user_data['user_tier']}")

            # Construction URL finale
            if params:
                separator = "?" if "?" not in base_url else "&"
                return f"{base_url}{separator}{'&'.join(params)}"

            return base_url

        except Exception as e:
            secure_logger.log_security_event(
                "REDIRECT_URL_GENERATION_ERROR",
                {"error": str(e)[:100], "target_app": target_app.value},
                "ERROR",
            )
            return self.get_app_url(target_app)

    def store_cross_app_data(
        self, user_data: Dict[str, Any], expires_in_hours: int = 24
    ) -> str:
        """
        Stocke les données pour transfert cross-app et retourne un token.
        """
        try:
            user_id = self._generate_anonymous_user_id(user_data)

            cross_app_data = CrossAppData(
                user_id=user_id,
                profile_data=self._sanitize_profile_data(user_data),
                preferences=user_data.get("preferences", {}),
                generated_content=user_data.get("generated_content", {}),
                journey_history=self._get_user_journey_history(user_id),
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(hours=expires_in_hours),
            )

            # Stockage en cache (en production, utiliser Redis/Database)
            self._user_cache[user_id] = cross_app_data

            secure_logger.log_security_event(
                "CROSS_APP_DATA_STORED",
                {"user_id": user_id[:8], "expires_in_hours": expires_in_hours},
            )

            return user_id

        except Exception as e:
            secure_logger.log_security_event(
                "CROSS_APP_DATA_STORAGE_ERROR", {"error": str(e)[:100]}, "ERROR"
            )
            return ""

    def retrieve_cross_app_data(self, token: str) -> Optional[CrossAppData]:
        """
        Récupère les données cross-app via token.
        """
        try:
            if token not in self._user_cache:
                return None

            data = self._user_cache[token]

            # Vérification expiration
            if datetime.now() > data.expires_at:
                del self._user_cache[token]
                return None

            secure_logger.log_security_event(
                "CROSS_APP_DATA_RETRIEVED", {"user_id": token[:8]}
            )

            return data

        except Exception as e:
            secure_logger.log_security_event(
                "CROSS_APP_DATA_RETRIEVAL_ERROR",
                {"error": str(e)[:100], "token": token[:8]},
                "ERROR",
            )
            return None

    def get_ecosystem_recommendations(
        self, current_app: PhoenixApp, user_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Génère des recommandations pour l'écosystème Phoenix.
        """
        journey = self.analyze_user_journey(user_data, current_app)
        recommendations = []

        if journey.next_recommended_app and journey.confidence_score > 0.5:
            target_app = journey.next_recommended_app

            if target_app == PhoenixApp.LETTERS:
                recommendations.append(
                    {
                        "title": "📝 Créer votre lettre de motivation",
                        "description": "Complétez votre candidature avec une lettre personnalisée",
                        "app": target_app.value,
                        "url": self.generate_cross_app_redirect_url(
                            target_app, user_data, "phoenix_cv"
                        ),
                        "confidence": journey.confidence_score,
                        "cta": "Créer ma lettre →",
                    }
                )
            elif target_app == PhoenixApp.CV:
                recommendations.append(
                    {
                        "title": "📄 Optimiser votre CV",
                        "description": "Créez un CV parfait qui correspond à votre lettre",
                        "app": target_app.value,
                        "url": self.generate_cross_app_redirect_url(
                            target_app, user_data, "phoenix_letters"
                        ),
                        "confidence": journey.confidence_score,
                        "cta": "Optimiser mon CV →",
                    }
                )

        # Toujours proposer le site principal pour découvrir l'écosystème
        if current_app != PhoenixApp.SITE:
            recommendations.append(
                {
                    "title": "🌟 Découvrir l'écosystème Phoenix",
                    "description": "Toutes nos solutions pour réussir votre reconversion",
                    "app": PhoenixApp.SITE.value,
                    "url": self.get_app_url(PhoenixApp.SITE),
                    "confidence": 0.7,
                    "cta": "Découvrir →",
                }
            )

        return recommendations

    def _generate_anonymous_user_id(self, user_data: Dict[str, Any]) -> str:
        """Génère un ID utilisateur anonyme basé sur les données"""
        # Utilise des données non-PII pour créer un ID stable
        identifier_data = {
            "timestamp_hour": datetime.now().strftime(
                "%Y%m%d%H"
            ),  # Change chaque heure
            "target_job": user_data.get("target_job", "")[:20],
            "user_tier": user_data.get("user_tier", ""),
            "session_marker": user_data.get("session_id", "anonymous")[:10],
        }

        identifier_string = json.dumps(identifier_data, sort_keys=True)
        # SÉCURITÉ: Utilisation de SHA-256 au lieu de MD5 (vulnérable)
        return hashlib.sha256(identifier_string.encode()).hexdigest()[:16]

    def _generate_transfer_token(self, user_data: Dict[str, Any]) -> str:
        """Génère un token sécurisé pour le transfert de données"""
        user_id = self._generate_anonymous_user_id(user_data)
        self.store_cross_app_data(user_data)
        return user_id

    def _sanitize_profile_data(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Nettoie les données profil pour stockage sécurisé"""
        safe_fields = [
            "target_job",
            "target_sector",
            "current_sector",
            "user_tier",
            "experience_years",
            "motivation",
            "competences_key",
        ]

        sanitized = {}
        for field in safe_fields:
            if field in user_data:
                value = str(user_data[field])[:200]  # Limite de longueur
                sanitized[field] = value

        return sanitized

    def _get_user_journey_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Récupère l'historique du parcours utilisateur"""
        if user_id not in self._journey_cache:
            self._journey_cache[user_id] = []

        return self._journey_cache[user_id][-10:]  # Derniers 10 événements

    def _create_default_journey(
        self, user_data: Dict[str, Any], current_app: PhoenixApp
    ) -> UserJourney:
        """Crée un parcours par défaut en cas d'erreur"""
        return UserJourney(
            user_id=self._generate_anonymous_user_id(user_data),
            current_app=current_app,
            last_action="default",
            data_context=user_data,
            timestamp=datetime.now(),
            next_recommended_app=(
                PhoenixApp.LETTERS if current_app == PhoenixApp.CV else PhoenixApp.CV
            ),
            confidence_score=0.5,
        )


# Instance globale pour l'application
phoenix_bridge = PhoenixEcosystemBridge()
