"""
⚡ Phoenix Ecosystem - Tests de Charge et Stabilité
Tests de performance, charge et stabilité pour production

Author: Claude Phoenix DevSecOps Guardian  
Version: 1.0.0 - Production Testing Suite
"""

import asyncio
import aiohttp
import time
import json
import psutil
import statistics
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import logging
import concurrent.futures
import threading
import queue
import random

logger = logging.getLogger(__name__)


@dataclass
class LoadTestConfig:
    """Configuration des tests de charge."""
    phoenix_cv_url: str = "https://phoenix-cv.streamlit.app"
    phoenix_letters_url: str = "https://phoenix-letters.streamlit.app"
    max_concurrent_users: int = 50
    test_duration_minutes: int = 5
    ramp_up_time_seconds: int = 60
    endpoints_to_test: List[str] = field(default_factory=list)
    user_scenarios: List[Dict] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.endpoints_to_test:
            self.endpoints_to_test = [
                "/",
                "/pricing",
                "/premium",
                "/generate-letter",
                "/upload-cv"
            ]
        
        if not self.user_scenarios:
            self.user_scenarios = [
                {"name": "visitor", "weight": 40, "actions": ["home", "pricing"]},
                {"name": "free_user", "weight": 35, "actions": ["home", "generate_letter", "pricing"]},
                {"name": "premium_user", "weight": 20, "actions": ["home", "generate_letter", "premium_features"]},
                {"name": "converter", "weight": 5, "actions": ["home", "pricing", "upgrade"]}
            ]


class PerformanceMetrics:
    """Collecteur de métriques de performance."""
    
    def __init__(self):
        self.response_times = []
        self.status_codes = {}
        self.errors = []
        self.throughput_data = []
        self.memory_usage = []
        self.cpu_usage = []
        self.start_time = None
        self.end_time = None
        self.concurrent_users = 0
        self.lock = threading.Lock()
    
    def record_request(self, response_time: float, status_code: int, endpoint: str, error: str = None):
        """Enregistre une requête."""
        with self.lock:
            self.response_times.append(response_time)
            
            if status_code not in self.status_codes:
                self.status_codes[status_code] = 0
            self.status_codes[status_code] += 1
            
            if error:
                self.errors.append({
                    "timestamp": datetime.now().isoformat(),
                    "endpoint": endpoint,
                    "error": error,
                    "status_code": status_code
                })
    
    def record_system_metrics(self):
        """Enregistre les métriques système."""
        with self.lock:
            self.memory_usage.append(psutil.virtual_memory().percent)
            self.cpu_usage.append(psutil.cpu_percent(interval=1))
    
    def calculate_statistics(self) -> Dict[str, Any]:
        """Calcule les statistiques de performance."""
        if not self.response_times:
            return {"error": "Aucune donnée de performance"}
        
        total_requests = len(self.response_times)
        test_duration = (self.end_time - self.start_time).total_seconds() if self.end_time and self.start_time else 0
        
        return {
            "test_duration_seconds": test_duration,
            "total_requests": total_requests,
            "requests_per_second": total_requests / test_duration if test_duration > 0 else 0,
            "response_times": {
                "min": min(self.response_times),
                "max": max(self.response_times),
                "mean": statistics.mean(self.response_times),
                "median": statistics.median(self.response_times),
                "p95": self._percentile(self.response_times, 95),
                "p99": self._percentile(self.response_times, 99)
            },
            "status_codes": self.status_codes,
            "error_rate": len(self.errors) / total_requests * 100 if total_requests > 0 else 0,
            "errors": self.errors[:10],  # Première 10 erreurs
            "system_metrics": {
                "max_memory_usage": max(self.memory_usage) if self.memory_usage else 0,
                "avg_memory_usage": statistics.mean(self.memory_usage) if self.memory_usage else 0,
                "max_cpu_usage": max(self.cpu_usage) if self.cpu_usage else 0,
                "avg_cpu_usage": statistics.mean(self.cpu_usage) if self.cpu_usage else 0
            }
        }
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calcule un percentile."""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]


class VirtualUser:
    """Utilisateur virtuel pour tests de charge."""
    
    def __init__(self, user_id: int, scenario: Dict, base_url: str, metrics: PerformanceMetrics):
        self.user_id = user_id
        self.scenario = scenario
        self.base_url = base_url
        self.metrics = metrics
        self.session = None
        self.is_running = False
    
    async def start_session(self):
        """Démarre la session utilisateur."""
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(timeout=timeout)
        self.is_running = True
    
    async def stop_session(self):
        """Arrête la session utilisateur."""
        self.is_running = False
        if self.session:
            await self.session.close()
    
    async def run_scenario(self, duration_seconds: int):
        """Exécute le scénario utilisateur."""
        if not self.session:
            await self.start_session()
        
        end_time = time.time() + duration_seconds
        
        while time.time() < end_time and self.is_running:
            action = random.choice(self.scenario["actions"])
            await self._execute_action(action)
            
            # Pause aléatoire entre actions (simule comportement humain)
            await asyncio.sleep(random.uniform(1, 5))
    
    async def _execute_action(self, action: str):
        """Exécute une action utilisateur."""
        endpoint_map = {
            "home": "/",
            "pricing": "/pricing",
            "generate_letter": "/generate-letter",
            "upload_cv": "/upload-cv",
            "premium_features": "/premium",
            "upgrade": "/upgrade"
        }
        
        endpoint = endpoint_map.get(action, "/")
        url = f"{self.base_url}{endpoint}"
        
        start_time = time.time()
        status_code = 0
        error = None
        
        try:
            async with self.session.get(url) as response:
                status_code = response.status
                await response.text()  # Consomme la réponse
                
        except Exception as e:
            error = str(e)
            status_code = 0
        
        response_time = time.time() - start_time
        self.metrics.record_request(response_time, status_code, endpoint, error)


class LoadTester:
    """Gestionnaire principal des tests de charge."""
    
    def __init__(self, config: LoadTestConfig):
        self.config = config
        self.metrics = PerformanceMetrics()
        self.virtual_users = []
        self.system_monitor_task = None
    
    async def run_load_test(self, app_url: str, app_name: str) -> Dict[str, Any]:
        """
        Exécute un test de charge complet.
        
        Args:
            app_url: URL de l'application à tester
            app_name: Nom de l'application
            
        Returns:
            Résultats du test de charge
        """
        print(f"🚀 Démarrage test de charge pour {app_name}...")
        
        self.metrics.start_time = datetime.now()
        
        # Démarrage du monitoring système
        self.system_monitor_task = asyncio.create_task(self._monitor_system())
        
        try:
            # Phase de montée en charge (ramp-up)
            await self._ramp_up_users(app_url)
            
            # Phase de test principal
            test_duration = self.config.test_duration_minutes * 60
            print(f"⏱️ Phase de test principal ({self.config.test_duration_minutes} minutes)...")
            
            # Exécution des scénarios utilisateur
            tasks = []
            for user in self.virtual_users:
                task = asyncio.create_task(user.run_scenario(test_duration))
                tasks.append(task)
            
            # Attente de la fin des tests
            await asyncio.gather(*tasks, return_exceptions=True)
            
            # Phase de descente (ramp-down)
            await self._ramp_down_users()
            
        finally:
            # Arrêt du monitoring
            if self.system_monitor_task:
                self.system_monitor_task.cancel()
            
            self.metrics.end_time = datetime.now()
        
        # Calcul et retour des résultats
        results = self.metrics.calculate_statistics()
        results["app_name"] = app_name
        results["app_url"] = app_url
        results["config"] = {
            "max_concurrent_users": self.config.max_concurrent_users,
            "test_duration_minutes": self.config.test_duration_minutes,
            "ramp_up_time_seconds": self.config.ramp_up_time_seconds
        }
        
        return results
    
    async def _ramp_up_users(self, app_url: str):
        """Phase de montée en charge progressive."""
        print(f"📈 Phase de montée en charge ({self.config.ramp_up_time_seconds}s)...")
        
        user_increment = self.config.max_concurrent_users / (self.config.ramp_up_time_seconds / 5)
        current_users = 0
        
        for step in range(0, self.config.ramp_up_time_seconds, 5):
            target_users = min(
                int(current_users + user_increment),
                self.config.max_concurrent_users
            )
            
            # Ajout de nouveaux utilisateurs
            while len(self.virtual_users) < target_users:
                user_id = len(self.virtual_users)
                scenario = self._select_user_scenario()
                
                virtual_user = VirtualUser(user_id, scenario, app_url, self.metrics)
                await virtual_user.start_session()
                self.virtual_users.append(virtual_user)
            
            current_users = target_users
            print(f"👥 Utilisateurs actifs: {current_users}")
            await asyncio.sleep(5)
        
        print(f"✅ Montée en charge terminée: {len(self.virtual_users)} utilisateurs")
    
    async def _ramp_down_users(self):
        """Phase de descente progressive."""
        print("📉 Phase de descente...")
        
        for user in self.virtual_users:
            await user.stop_session()
        
        self.virtual_users.clear()
        print("✅ Tous les utilisateurs virtuels arrêtés")
    
    def _select_user_scenario(self) -> Dict:
        """Sélectionne un scénario utilisateur basé sur les poids."""
        total_weight = sum(scenario["weight"] for scenario in self.config.user_scenarios)
        random_weight = random.randint(1, total_weight)
        
        current_weight = 0
        for scenario in self.config.user_scenarios:
            current_weight += scenario["weight"]
            if random_weight <= current_weight:
                return scenario
        
        return self.config.user_scenarios[0]  # Fallback
    
    async def _monitor_system(self):
        """Monitore les ressources système."""
        try:
            while True:
                self.metrics.record_system_metrics()
                await asyncio.sleep(5)
        except asyncio.CancelledError:
            pass


class StabilityTester:
    """Testeur de stabilité long terme."""
    
    def __init__(self, config: LoadTestConfig):
        self.config = config
        self.metrics = PerformanceMetrics()
    
    async def run_stability_test(self, app_url: str, duration_hours: int = 1) -> Dict[str, Any]:
        """
        Test de stabilité sur une durée prolongée.
        
        Args:
            app_url: URL de l'application
            duration_hours: Durée du test en heures
            
        Returns:
            Résultats du test de stabilité
        """
        print(f"🔄 Démarrage test de stabilité ({duration_hours}h)...")
        
        self.metrics.start_time = datetime.now()
        test_duration = duration_hours * 3600  # Conversion en secondes
        
        # Utilisateurs constants avec charge légère
        constant_users = max(5, self.config.max_concurrent_users // 10)
        
        try:
            async with aiohttp.ClientSession() as session:
                tasks = []
                
                # Création des tâches de test
                for i in range(constant_users):
                    task = asyncio.create_task(
                        self._stability_user_simulation(session, app_url, test_duration)
                    )
                    tasks.append(task)
                
                # Monitoring périodique
                monitor_task = asyncio.create_task(
                    self._stability_monitoring(test_duration)
                )
                tasks.append(monitor_task)
                
                # Attente de completion
                await asyncio.gather(*tasks, return_exceptions=True)
                
        finally:
            self.metrics.end_time = datetime.now()
        
        results = self.metrics.calculate_statistics()
        results["test_type"] = "stability"
        results["duration_hours"] = duration_hours
        results["constant_users"] = constant_users
        
        return results
    
    async def _stability_user_simulation(self, session: aiohttp.ClientSession, base_url: str, duration: int):
        """Simulation d'utilisateur pour test de stabilité."""
        end_time = time.time() + duration
        
        while time.time() < end_time:
            # Requête simple vers la page d'accueil
            start_time = time.time()
            status_code = 0
            error = None
            
            try:
                async with session.get(base_url) as response:
                    status_code = response.status
                    await response.text()
            except Exception as e:
                error = str(e)
                status_code = 0
            
            response_time = time.time() - start_time
            self.metrics.record_request(response_time, status_code, "/", error)
            
            # Pause entre requêtes (simulation trafic réel)
            await asyncio.sleep(random.uniform(30, 120))  # 30s à 2min
    
    async def _stability_monitoring(self, duration: int):
        """Monitoring pour test de stabilité."""
        end_time = time.time() + duration
        
        while time.time() < end_time:
            self.metrics.record_system_metrics()
            await asyncio.sleep(60)  # Monitoring chaque minute


async def run_comprehensive_load_tests() -> Dict[str, Any]:
    """
    Lance les tests de charge complets pour l'écosystème Phoenix.
    
    Returns:
        Résultats consolidés des tests
    """
    config = LoadTestConfig()
    results = {}
    
    print("⚡ Démarrage des tests de charge Phoenix Ecosystem")
    
    # Test Phoenix CV
    print("\n🔍 Tests Phoenix CV...")
    cv_tester = LoadTester(config)
    cv_results = await cv_tester.run_load_test(
        config.phoenix_cv_url, 
        "Phoenix CV"
    )
    results["phoenix_cv_load"] = cv_results
    
    # Test Phoenix Letters
    print("\n📝 Tests Phoenix Letters...")
    letters_tester = LoadTester(config)
    letters_results = await letters_tester.run_load_test(
        config.phoenix_letters_url,
        "Phoenix Letters"
    )
    results["phoenix_letters_load"] = letters_results
    
    # Test de stabilité Phoenix Letters (test plus court pour démo)
    print("\n🔄 Test de stabilité Phoenix Letters...")
    stability_tester = StabilityTester(config)
    stability_results = await stability_tester.run_stability_test(
        config.phoenix_letters_url,
        duration_hours=0.5  # 30 minutes pour demo
    )
    results["phoenix_letters_stability"] = stability_results
    
    # Génération du rapport consolidé
    results["summary"] = generate_load_test_summary(results)
    
    return results


def generate_load_test_summary(results: Dict[str, Any]) -> Dict[str, Any]:
    """Génère un résumé des tests de charge."""
    summary = {
        "timestamp": datetime.now().isoformat(),
        "total_tests": len([k for k in results.keys() if k != "summary"]),
        "applications_tested": [],
        "overall_performance": {},
        "recommendations": []
    }
    
    total_requests = 0
    total_errors = 0
    response_times = []
    
    for test_name, test_results in results.items():
        if test_name == "summary":
            continue
        
        if "app_name" in test_results:
            summary["applications_tested"].append(test_results["app_name"])
        
        if "total_requests" in test_results:
            total_requests += test_results["total_requests"]
        
        if "errors" in test_results:
            total_errors += len(test_results["errors"])
        
        if "response_times" in test_results and "mean" in test_results["response_times"]:
            response_times.append(test_results["response_times"]["mean"])
    
    # Calcul des métriques globales
    summary["overall_performance"] = {
        "total_requests_processed": total_requests,
        "total_errors": total_errors,
        "overall_error_rate": (total_errors / total_requests * 100) if total_requests > 0 else 0,
        "average_response_time": statistics.mean(response_times) if response_times else 0
    }
    
    # Génération de recommandations
    error_rate = summary["overall_performance"]["overall_error_rate"]
    avg_response_time = summary["overall_performance"]["average_response_time"]
    
    if error_rate > 5:
        summary["recommendations"].append("Taux d'erreur élevé - Vérifier la stabilité de l'infrastructure")
    
    if avg_response_time > 3:
        summary["recommendations"].append("Temps de réponse lent - Optimiser les performances")
    
    if error_rate < 1 and avg_response_time < 2:
        summary["recommendations"].append("Performances excellentes - Prêt pour la production")
    
    return summary


def save_load_test_report(results: Dict[str, Any], filename: str = "phoenix_load_test_report.json"):
    """Sauvegarde le rapport de tests de charge."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)


if __name__ == "__main__":
    # Exécution des tests
    print("🧪 Phoenix Ecosystem - Tests de Charge et Stabilité")
    print("=" * 60)
    
    try:
        # Lancement des tests asynchrones
        test_results = asyncio.run(run_comprehensive_load_tests())
        
        # Sauvegarde des résultats
        save_load_test_report(test_results)
        
        # Affichage du résumé
        summary = test_results.get("summary", {})
        print(f"\n✅ Tests terminés:")
        print(f"📊 {summary.get('total_tests', 0)} tests exécutés")
        print(f"🎯 Applications testées: {', '.join(summary.get('applications_tested', []))}")
        print(f"📈 Total requêtes: {summary.get('overall_performance', {}).get('total_requests_processed', 0)}")
        print(f"❌ Taux d'erreur global: {summary.get('overall_performance', {}).get('overall_error_rate', 0):.2f}%")
        print(f"⏱️ Temps de réponse moyen: {summary.get('overall_performance', {}).get('average_response_time', 0):.2f}s")
        
        if summary.get("recommendations"):
            print(f"\n💡 Recommandations:")
            for rec in summary["recommendations"]:
                print(f"   • {rec}")
        
        print(f"\n📁 Rapport détaillé sauvegardé: phoenix_load_test_report.json")
        
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrompus par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur lors des tests: {e}")
        logger.exception("Erreur tests de charge")