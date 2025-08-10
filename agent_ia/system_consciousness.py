"""
🧠 PHOENIX SYSTEM CONSCIOUSNESS
L'IA qui surveille sa propre santé et s'auto-régule
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List

import httpx


class SystemState(Enum):
    OPTIMAL = "optimal"
    STRESSED = "stressed"
    CRITICAL = "critical"
    DEGRADED = "degraded"


@dataclass
class SystemMetrics:
    """Métriques système temps réel"""

    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    response_time: float
    error_rate: float
    active_requests: int
    model_load_time: float


@dataclass
class ConsciousnessDecision:
    """Décision consciente du système"""

    state: SystemState
    actions: List[str]
    reasoning: str
    confidence: float
    metrics_used: Dict[str, float]


class SystemConsciousness:
    """
    🧠 Conscience système Phoenix
    Surveillance + Auto-régulation intelligente
    """

    def __init__(self):
        self.prometheus_url = "http://localhost:9090"
        self.smart_router_url = "http://localhost:8000"
        self.metrics_history = []
        self.decisions_history = []

        # Seuils critiques
        self.thresholds = {
            "cpu_critical": 85.0,
            "memory_critical": 90.0,
            "response_time_critical": 10.0,
            "error_rate_critical": 5.0,
        }

        logging.info("🧠 System Consciousness initialized")

    async def monitor_and_decide(self) -> ConsciousnessDecision:
        """
        🎯 Cycle principal : Monitor → Analyze → Decide → Act
        """

        # 1. Collecte métriques système
        current_metrics = await self._collect_system_metrics()
        self.metrics_history.append(current_metrics)

        # 2. Analyse état système
        system_state = self._analyze_system_state(current_metrics)

        # 3. Décision consciente
        decision = await self._make_conscious_decision(system_state, current_metrics)

        # 4. Exécution actions
        await self._execute_decision(decision)

        self.decisions_history.append(decision)

        return decision

    async def _collect_system_metrics(self) -> SystemMetrics:
        """Collecte métriques Prometheus + APIs"""

        try:
            async with httpx.AsyncClient() as client:
                # Métriques Prometheus
                prometheus_metrics = await self._query_prometheus(
                    [
                        "rate(http_requests_total[5m])",
                        "prometheus_notifications_total",
                        "process_resident_memory_bytes",
                        "rate(http_request_duration_seconds[5m])",
                    ]
                )

                # Métriques Smart Router
                router_health = await client.get(f"{self.smart_router_url}/health")
                router_data = router_health.json()

                return SystemMetrics(
                    timestamp=datetime.now(),
                    cpu_usage=prometheus_metrics.get("cpu_usage", 50.0),
                    memory_usage=prometheus_metrics.get("memory_usage", 60.0),
                    response_time=router_data.get("average_response_time", 2.0),
                    error_rate=prometheus_metrics.get("error_rate", 1.0),
                    active_requests=router_data.get("total_requests", 0),
                    model_load_time=prometheus_metrics.get("model_load_time", 5.0),
                )

        except Exception as e:
            logging.error(f"❌ Failed to collect metrics: {e}")
            # Métriques par défaut en cas d'erreur
            return SystemMetrics(
                timestamp=datetime.now(),
                cpu_usage=0.0,
                memory_usage=0.0,
                response_time=999.0,
                error_rate=100.0,
                active_requests=0,
                model_load_time=999.0,
            )

    def _analyze_system_state(self, metrics: SystemMetrics) -> SystemState:
        """Analyse intelligente état système"""

        critical_conditions = [
            metrics.cpu_usage > self.thresholds["cpu_critical"],
            metrics.memory_usage > self.thresholds["memory_critical"],
            metrics.response_time > self.thresholds["response_time_critical"],
            metrics.error_rate > self.thresholds["error_rate_critical"],
        ]

        if sum(critical_conditions) >= 2:
            return SystemState.CRITICAL
        elif sum(critical_conditions) == 1:
            return SystemState.STRESSED
        elif metrics.response_time > 5.0 or metrics.error_rate > 2.0:
            return SystemState.DEGRADED
        else:
            return SystemState.OPTIMAL

    async def _make_conscious_decision(
        self, state: SystemState, metrics: SystemMetrics
    ) -> ConsciousnessDecision:
        """Prise de décision consciente basée sur l'état"""

        actions = []
        reasoning = ""
        confidence = 0.0

        if state == SystemState.CRITICAL:
            actions = [
                "throttle_non_essential_requests",
                "activate_circuit_breaker",
                "scale_up_resources",
                "enable_degraded_mode",
            ]
            reasoning = f"Système critique: CPU {metrics.cpu_usage:.1f}%, RAM {metrics.memory_usage:.1f}%, RT {metrics.response_time:.1f}s"
            confidence = 0.95

        elif state == SystemState.STRESSED:
            actions = [
                "reduce_concurrent_requests",
                "optimize_model_loading",
                "prepare_scaling",
            ]
            reasoning = f"Système sous stress: {self._identify_bottleneck(metrics)}"
            confidence = 0.80

        elif state == SystemState.DEGRADED:
            actions = ["monitor_closely", "preemptive_optimization"]
            reasoning = f"Performance dégradée: RT {metrics.response_time:.1f}s"
            confidence = 0.70

        else:  # OPTIMAL
            actions = ["maintain_current_state", "learn_from_optimal_conditions"]
            reasoning = "Système optimal - apprentissage des conditions favorables"
            confidence = 0.60

        return ConsciousnessDecision(
            state=state,
            actions=actions,
            reasoning=reasoning,
            confidence=confidence,
            metrics_used={
                "cpu": metrics.cpu_usage,
                "memory": metrics.memory_usage,
                "response_time": metrics.response_time,
                "error_rate": metrics.error_rate,
            },
        )

    async def _execute_decision(self, decision: ConsciousnessDecision):
        """Exécution des actions décidées"""

        for action in decision.actions:
            try:
                await self._execute_action(action, decision)
                logging.info(f"✅ Action executed: {action}")
            except Exception as e:
                logging.error(f"❌ Action failed: {action} - {e}")

    async def _execute_action(self, action: str, decision: ConsciousnessDecision):
        """Exécution d'une action spécifique"""

        async with httpx.AsyncClient() as client:

            if action == "throttle_non_essential_requests":
                await client.post(
                    f"{self.smart_router_url}/api/throttle",
                    json={"max_requests_per_minute": 10},
                )

            elif action == "activate_circuit_breaker":
                await client.post(
                    f"{self.smart_router_url}/api/circuit-breaker",
                    json={"enabled": True, "failure_threshold": 3},
                )

            elif action == "scale_up_resources":
                # Commande Kubernetes pour scale up
                import subprocess

                subprocess.run(
                    [
                        "kubectl",
                        "scale",
                        "deployment",
                        "security-guardian",
                        "--replicas=2",
                        "-n",
                        "phoenix-letters",
                    ]
                )

            elif action == "reduce_concurrent_requests":
                await client.post(
                    f"{self.smart_router_url}/api/concurrency",
                    json={"max_concurrent": 3},
                )

            elif action == "learn_from_optimal_conditions":
                # Envoie métriques optimales au Data Flywheel
                await client.post(
                    "http://localhost:8002/api/flywheel/learn-optimal",
                    json={"metrics": decision.metrics_used},
                )

    def _identify_bottleneck(self, metrics: SystemMetrics) -> str:
        """Identification du goulot d'étranglement principal"""

        bottlenecks = []

        if metrics.cpu_usage > 70:
            bottlenecks.append("CPU surchargé")
        if metrics.memory_usage > 75:
            bottlenecks.append("RAM saturée")
        if metrics.response_time > 5:
            bottlenecks.append("Latence élevée")
        if metrics.model_load_time > 10:
            bottlenecks.append("Modèles IA lents")

        return ", ".join(bottlenecks) if bottlenecks else "Goulot non identifié"

    async def _query_prometheus(self, queries: List[str]) -> Dict[str, float]:
        """Requêtes Prometheus"""

        metrics = {}

        try:
            async with httpx.AsyncClient() as client:
                for query in queries:
                    response = await client.get(
                        f"{self.prometheus_url}/api/v1/query", params={"query": query}
                    )

                    if response.status_code == 200:
                        data = response.json()
                        # Parse résultat Prometheus
                        if data.get("status") == "success":
                            result = data.get("data", {}).get("result", [])
                            if result:
                                metrics[query] = float(result[0]["value"][1])

        except Exception as e:
            logging.error(f"❌ Prometheus query failed: {e}")

        return metrics

    def get_consciousness_dashboard(self) -> Dict[str, Any]:
        """Dashboard conscience système"""

        if not self.decisions_history:
            return {"status": "initializing"}

        latest_decision = self.decisions_history[-1]
        latest_metrics = self.metrics_history[-1] if self.metrics_history else None

        return {
            "system_state": latest_decision.state.value,
            "last_decision": {
                "actions": latest_decision.actions,
                "reasoning": latest_decision.reasoning,
                "confidence": latest_decision.confidence,
            },
            "current_metrics": latest_metrics.__dict__ if latest_metrics else {},
            "decisions_count": len(self.decisions_history),
            "uptime": "monitoring_active",
            "consciousness_level": (
                "active" if latest_decision.confidence > 0.7 else "learning"
            ),
        }


# ========================================
# 🚀 ORCHESTRATEUR CONSCIENCE SYSTÈME
# ========================================


class PhoenixConsciousnessOrchestrator:
    """Orchestrateur principal conscience Phoenix"""

    def __init__(self):
        self.consciousness = SystemConsciousness()
        self.monitoring_active = False
        self.monitoring_interval = 30  # secondes

    async def start_consciousness_loop(self):
        """Démarrage boucle conscience permanente"""

        self.monitoring_active = True
        logging.info("🧠 Phoenix System Consciousness started")

        while self.monitoring_active:
            try:
                decision = await self.consciousness.monitor_and_decide()

                logging.info(
                    f"🧠 Conscious Decision: {decision.state.value} | "
                    f"Actions: {len(decision.actions)} | "
                    f"Confidence: {decision.confidence:.2f}"
                )

                await asyncio.sleep(self.monitoring_interval)

            except Exception as e:
                logging.error(f"❌ Consciousness loop error: {e}")
                await asyncio.sleep(60)  # Retry après 1 minute

    def stop_consciousness(self):
        """Arrêt conscience système"""
        self.monitoring_active = False
        logging.info("🧠 Phoenix System Consciousness stopped")

    def get_dashboard(self) -> Dict[str, Any]:
        """Dashboard conscience pour monitoring"""
        return self.consciousness.get_consciousness_dashboard()


# ========================================
# 🧪 DEMO SYSTEM CONSCIOUSNESS
# ========================================


async def demo_system_consciousness():
    """Démonstration System Consciousness"""

    print("🧠 DEMO: Phoenix System Consciousness")
    print("=" * 50)

    orchestrator = PhoenixConsciousnessOrchestrator()

    # Simulation monitoring pendant 2 minutes
    print("🚀 Démarrage monitoring conscience système...")

    # Démarre la conscience en arrière-plan
    consciousness_task = asyncio.create_task(orchestrator.start_consciousness_loop())

    # Simulation pendant 2 minutes
    for i in range(4):  # 4 cycles de 30s
        await asyncio.sleep(30)

        dashboard = orchestrator.get_dashboard()
        print(f"\n📊 Cycle {i+1}/4:")
        print(f"État système: {dashboard.get('system_state', 'unknown')}")
        print(
            f"Dernière décision: {dashboard.get('last_decision', {}).get('reasoning', 'N/A')}"
        )
        print(f"Niveau conscience: {dashboard.get('consciousness_level', 'unknown')}")

    # Arrêt
    orchestrator.stop_consciousness()
    consciousness_task.cancel()

    print("\n✅ Démonstration terminée - System Consciousness validé !")


if __name__ == "__main__":
    asyncio.run(demo_system_consciousness())
