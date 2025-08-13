"""
🏥 Phoenix Health Checker
Système de vérification de santé des services Phoenix

Author: Claude Phoenix DevSecOps Guardian
"""

import asyncio
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """États de santé des services"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ServiceHealth:
    """Informations de santé d'un service"""
    service_name: str
    status: HealthStatus
    response_time_ms: float
    last_check: datetime
    details: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class HealthChecker:
    """
    Vérificateur de santé pour l'écosystème Phoenix
    
    Surveille la santé des différents services et composants
    """
    
    def __init__(self):
        self.services: Dict[str, ServiceHealth] = {}
        self.check_functions: Dict[str, callable] = {}
        self.thresholds = {
            'response_time_warning_ms': 1000,
            'response_time_critical_ms': 5000
        }
    
    def register_service(
        self, 
        service_name: str, 
        check_function: callable,
        enabled: bool = True
    ):
        """
        Enregistre un service à surveiller
        
        Args:
            service_name: Nom du service
            check_function: Fonction de vérification (async ou sync)
            enabled: Si le service est activé pour surveillance
        """
        if enabled:
            self.check_functions[service_name] = check_function
            logger.info(f"✅ Service registered for health check: {service_name}")
    
    async def check_service_health(self, service_name: str) -> ServiceHealth:
        """
        Vérifie la santé d'un service spécifique
        
        Args:
            service_name: Nom du service à vérifier
            
        Returns:
            ServiceHealth: État de santé du service
        """
        if service_name not in self.check_functions:
            return ServiceHealth(
                service_name=service_name,
                status=HealthStatus.UNKNOWN,
                response_time_ms=0.0,
                last_check=datetime.now(),
                error_message="Service not registered"
            )
        
        start_time = time.time()
        check_function = self.check_functions[service_name]
        
        try:
            # Exécuter la fonction de vérification
            if asyncio.iscoroutinefunction(check_function):
                result = await check_function()
            else:
                result = check_function()
            
            response_time_ms = (time.time() - start_time) * 1000
            
            # Déterminer le statut basé sur le temps de réponse et le résultat
            if result is False:
                status = HealthStatus.UNHEALTHY
                error_message = "Health check failed"
            elif response_time_ms > self.thresholds['response_time_critical_ms']:
                status = HealthStatus.UNHEALTHY
                error_message = f"Response time too high: {response_time_ms:.2f}ms"
            elif response_time_ms > self.thresholds['response_time_warning_ms']:
                status = HealthStatus.DEGRADED
                error_message = f"Response time elevated: {response_time_ms:.2f}ms"
            else:
                status = HealthStatus.HEALTHY
                error_message = None
            
            # Créer l'objet de santé
            health = ServiceHealth(
                service_name=service_name,
                status=status,
                response_time_ms=response_time_ms,
                last_check=datetime.now(),
                details=result if isinstance(result, dict) else None,
                error_message=error_message
            )
            
            # Stocker dans le cache
            self.services[service_name] = health
            
            return health
            
        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            
            health = ServiceHealth(
                service_name=service_name,
                status=HealthStatus.UNHEALTHY,
                response_time_ms=response_time_ms,
                last_check=datetime.now(),
                error_message=f"Health check exception: {str(e)}"
            )
            
            self.services[service_name] = health
            logger.error(f"❌ Health check failed for {service_name}: {e}")
            
            return health
    
    async def check_all_services(self) -> Dict[str, ServiceHealth]:
        """
        Vérifie la santé de tous les services enregistrés
        
        Returns:
            Dict[str, ServiceHealth]: État de santé de tous les services
        """
        tasks = []
        for service_name in self.check_functions.keys():
            task = self.check_service_health(service_name)
            tasks.append(task)
        
        # Exécuter toutes les vérifications en parallèle
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Traiter les résultats
            for i, result in enumerate(results):
                service_name = list(self.check_functions.keys())[i]
                if isinstance(result, Exception):
                    self.services[service_name] = ServiceHealth(
                        service_name=service_name,
                        status=HealthStatus.UNHEALTHY,
                        response_time_ms=0.0,
                        last_check=datetime.now(),
                        error_message=f"Async check failed: {str(result)}"
                    )
        
        return self.services.copy()
    
    def get_overall_health(self) -> HealthStatus:
        """
        Détermine l'état de santé global de l'écosystème
        
        Returns:
            HealthStatus: État global
        """
        if not self.services:
            return HealthStatus.UNKNOWN
        
        statuses = [service.status for service in self.services.values()]
        
        # Si au moins un service est unhealthy, le global est unhealthy
        if HealthStatus.UNHEALTHY in statuses:
            return HealthStatus.UNHEALTHY
        
        # Si au moins un service est degraded, le global est degraded
        if HealthStatus.DEGRADED in statuses:
            return HealthStatus.DEGRADED
        
        # Si tous sont healthy, le global est healthy
        if all(status == HealthStatus.HEALTHY for status in statuses):
            return HealthStatus.HEALTHY
        
        # Cas par défaut
        return HealthStatus.UNKNOWN
    
    def get_health_summary(self) -> Dict[str, Any]:
        """
        Retourne un résumé de l'état de santé
        
        Returns:
            Dict: Résumé de santé pour API/monitoring
        """
        overall_status = self.get_overall_health()
        
        services_summary = {}
        for name, health in self.services.items():
            services_summary[name] = {
                'status': health.status.value,
                'response_time_ms': health.response_time_ms,
                'last_check': health.last_check.isoformat(),
                'error': health.error_message
            }
        
        return {
            'overall_status': overall_status.value,
            'timestamp': datetime.now().isoformat(),
            'services': services_summary,
            'healthy_services': sum(1 for s in self.services.values() if s.status == HealthStatus.HEALTHY),
            'total_services': len(self.services)
        }


# Fonctions de vérification prêtes à l'emploi
async def check_supabase_connection():
    """Vérifie la connexion Supabase"""
    try:
        from packages.phoenix_shared_auth.client import get_auth_manager
        auth_manager = get_auth_manager()
        
        # Test simple de connexion
        if auth_manager.client:
            return {'database': 'connected'}
        else:
            return False
            
    except Exception as e:
        logger.error(f"Supabase health check failed: {e}")
        return False


def check_stripe_connection():
    """Vérifie la connexion Stripe"""
    try:
        from packages.phoenix_shared_auth.stripe_manager import get_stripe_manager
        stripe_manager = get_stripe_manager()
        
        # Test simple - vérifier que les clés sont configurées
        if hasattr(stripe_manager, 'PRICE_IDS'):
            return {'payment_system': 'configured'}
        else:
            return False
            
    except Exception as e:
        logger.error(f"Stripe health check failed: {e}")
        return False


def check_system_resources():
    """Vérifie les ressources système"""
    try:
        import psutil
        
        # Vérifications de base
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        details = {
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'disk_percent': disk.percent
        }
        
        # Considérer unhealthy si ressources critiques
        if cpu_percent > 90 or memory.percent > 90 or disk.percent > 90:
            return False
            
        return details
        
    except ImportError:
        # psutil n'est pas installé
        return {'system_monitoring': 'unavailable'}
    except Exception as e:
        logger.error(f"System resources check failed: {e}")
        return False


# Instance globale pour l'application
phoenix_health_checker = HealthChecker()

# Enregistrement des services par défaut
phoenix_health_checker.register_service("supabase", check_supabase_connection)
phoenix_health_checker.register_service("stripe", check_stripe_connection) 
phoenix_health_checker.register_service("system", check_system_resources)