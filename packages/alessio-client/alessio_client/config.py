import os
from typing import Dict, Optional
from dataclasses import dataclass
from enum import Enum

class Environment(str, Enum):
    """Environnements de déploiement"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

@dataclass
class AppConfig:
    """Configuration d'une application Phoenix"""
    name: str
    url: str
    iris_enabled: bool = True
    description: str = ""

class PhoenixEcosystemConfig:
    """Configuration centralisée de l'écosystème Phoenix"""
    
    def __init__(self, environment: Environment = Environment.DEVELOPMENT):
        self.environment = environment
        self._setup_apps_config()
        self._setup_iris_config()
    
    def _setup_apps_config(self):
        """Configure les URLs des applications selon l'environnement"""
        
        if self.environment == Environment.PRODUCTION:
            self.apps = {
                "phoenix-letters": AppConfig(
                    name="Phoenix Letters",
                    url="https://phoenix-letters.streamlit.app",
                    description="Générateur IA de lettres de motivation pour reconversions"
                ),
                "phoenix-cv": AppConfig(
                    name="Phoenix CV", 
                    url="https://phoenix-cv.streamlit.app",
                    description="Optimisation CV et templates professionnels"
                ),
                "phoenix-rise": AppConfig(
                    name="Phoenix Rise",
                    url="https://phoenix-rise.streamlit.app", 
                    description="Journal de développement personnel et coaching"
                ),
                "phoenix-website": AppConfig(
                    name="Phoenix Website",
                    url="https://phoenix-ecosystem.com",
                    description="Site vitrine et portail d'entrée de l'écosystème"
                )
            }
        elif self.environment == Environment.STAGING:
            self.apps = {
                "phoenix-letters": AppConfig(
                    name="Phoenix Letters",
                    url="https://phoenix-letters-staging.streamlit.app",
                    description="Générateur IA de lettres de motivation pour reconversions"
                ),
                "phoenix-cv": AppConfig(
                    name="Phoenix CV",
                    url="https://phoenix-cv-staging.streamlit.app",
                    description="Optimisation CV et templates professionnels"
                ),
                "phoenix-rise": AppConfig(
                    name="Phoenix Rise", 
                    url="https://phoenix-rise-staging.streamlit.app",
                    description="Journal de développement personnel et coaching"
                ),
                "phoenix-website": AppConfig(
                    name="Phoenix Website",
                    url="https://phoenix-staging.vercel.app",
                    description="Site vitrine et portail d'entrée de l'écosystème"
                )
            }
        else:  # DEVELOPMENT
            self.apps = {
                "phoenix-letters": AppConfig(
                    name="Phoenix Letters",
                    url="http://localhost:8501",
                    description="Générateur IA de lettres de motivation pour reconversions"
                ),
                "phoenix-cv": AppConfig(
                    name="Phoenix CV",
                    url="http://localhost:8502", 
                    description="Optimisation CV et templates professionnels"
                ),
                "phoenix-rise": AppConfig(
                    name="Phoenix Rise",
                    url="http://localhost:8503",
                    description="Journal de développement personnel et coaching"
                ),
                "phoenix-website": AppConfig(
                    name="Phoenix Website", 
                    url="http://localhost:3000",
                    description="Site vitrine et portail d'entrée de l'écosystème"
                )
            }
    
    def _setup_iris_config(self):
        """Configure les paramètres d'Iris selon l'environnement"""
        
        if self.environment == Environment.PRODUCTION:
            self.iris = {
                "api_url": "https://iris-api.phoenix-ecosystem.com/api/v1/chat",
                "health_url": "https://iris-api.phoenix-ecosystem.com/health",
                "timeout": 60,
                "rate_limits": {
                    "FREE": {"daily_messages": 5, "requests_per_minute": 2},
                    "PREMIUM": {"daily_messages": 50, "requests_per_minute": 10},
                    "ENTERPRISE": {"daily_messages": -1, "requests_per_minute": 20}
                }
            }
        elif self.environment == Environment.STAGING:
            self.iris = {
                "api_url": "https://iris-staging.phoenix-ecosystem.com/api/v1/chat",
                "health_url": "https://iris-staging.phoenix-ecosystem.com/health", 
                "timeout": 60,
                "rate_limits": {
                    "FREE": {"daily_messages": 10, "requests_per_minute": 5},
                    "PREMIUM": {"daily_messages": 100, "requests_per_minute": 15},
                    "ENTERPRISE": {"daily_messages": -1, "requests_per_minute": 30}
                }
            }
        else:  # DEVELOPMENT
            self.iris = {
                "api_url": os.getenv("IRIS_API_URL", "http://localhost:8003/api/v1/chat"),
                "health_url": os.getenv("IRIS_HEALTH_URL", "http://localhost:8003/health"),
                "timeout": 60,
                "rate_limits": {
                    "FREE": {"daily_messages": 50, "requests_per_minute": 10},
                    "PREMIUM": {"daily_messages": 200, "requests_per_minute": 20}, 
                    "ENTERPRISE": {"daily_messages": -1, "requests_per_minute": 50}
                }
            }
    
    def get_app_config(self, app_name: str) -> Optional[AppConfig]:
        """Récupère la configuration d'une application"""
        return self.apps.get(app_name)
    
    def get_iris_config(self) -> Dict:
        """Récupère la configuration d'Iris"""
        return self.iris
    
    def get_navigation_links(self, current_app: str) -> Dict[str, AppConfig]:
        """Récupère les liens de navigation vers les autres apps"""
        return {
            app_name: config 
            for app_name, config in self.apps.items() 
            if app_name != current_app
        }
    
    def generate_cross_app_urls(self, base_path: str = "") -> Dict[str, str]:
        """Génère les URLs cross-app pour la navigation"""
        urls = {}
        
        for app_name, config in self.apps.items():
            # URLs spéciales pour accès direct aux fonctionnalités
            urls[f"{app_name}_home"] = f"{config.url}{base_path}"
            
            # URLs Iris spécifiques
            if config.iris_enabled:
                if app_name in ["phoenix-letters", "phoenix-cv", "phoenix-rise"]:
                    # Streamlit apps - paramètres d'URL
                    urls[f"{app_name}_iris"] = f"{config.url}?page=iris{base_path}"
                elif app_name == "phoenix-website":
                    # Next.js app - route dédiée
                    urls[f"{app_name}_iris"] = f"{config.url}/iris{base_path}"
        
        return urls

# Instance globale de configuration
def get_phoenix_config() -> PhoenixEcosystemConfig:
    """Récupère la configuration Phoenix selon l'environnement"""
    env = Environment(os.getenv("PHOENIX_ENV", "development"))
    return PhoenixEcosystemConfig(env)

# Configuration par défaut pour développement
phoenix_config = get_phoenix_config()

# Utilitaires pour les applications
def get_iris_api_url() -> str:
    """URL de l'API Iris"""
    return phoenix_config.get_iris_config()["api_url"]

def get_app_url(app_name: str) -> Optional[str]:
    """URL d'une application spécifique"""
    config = phoenix_config.get_app_config(app_name)
    return config.url if config else None

def is_iris_enabled(app_name: str) -> bool:
    """Vérifie si Iris est activé pour une application"""
    config = phoenix_config.get_app_config(app_name)
    return config.iris_enabled if config else False

def get_cross_app_navigation() -> Dict[str, str]:
    """Liens de navigation cross-app"""
    return phoenix_config.generate_cross_app_urls()

# Constants pour l'intégration
ALESSIO_CONTEXTS = {
    "phoenix-letters": {
        "name": "Alessio Letters",
        "icon": "✍️",
        "color": "purple",
        "specialization": "Lettres de motivation et reconversions"
    },
    "phoenix-cv": {
        "name": "Alessio CV", 
        "icon": "📋",
        "color": "blue",
        "specialization": "Optimisation CV et carrière"
    },
    "phoenix-rise": {
        "name": "Alessio Coach",
        "icon": "🌱", 
        "color": "green",
        "specialization": "Développement personnel et coaching"
    },
    "phoenix-website": {
        "name": "Alessio Phoenix",
        "icon": "🚀",
        "color": "orange", 
        "specialization": "Guide écosystème et orientation"
    }
}