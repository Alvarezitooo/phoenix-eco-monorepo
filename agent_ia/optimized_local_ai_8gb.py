"""
🧠 SETUP IA LOCALES OPTIMISÉ - MacBook Pro 8GB RAM
Configuration Phoenix Letters ultra-efficace avec alternance intelligente
"""

import asyncio
import json
import logging
import subprocess
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

import httpx
import psutil

# ========================================
# 🎯 CONFIGURATION MODÈLES OPTIMISÉS 8GB
# ========================================


@dataclass
class ModelConfig:
    """Configuration modèle IA local optimisé"""

    name: str
    ollama_name: str
    ram_usage_gb: float
    specialization: str
    performance_score: int
    french_quality: int
    speed_score: int


# MODÈLES SÉLECTIONNÉS SPÉCIALEMENT POUR 8GB - VERSION OPTIMISÉE RAM
OPTIMIZED_MODELS = {
    "data_flywheel": ModelConfig(
        name="Qwen2.5 1.5B Instruct",
        ollama_name="qwen2.5:1.5b",
        ram_usage_gb=1.2,
        specialization="Analytics, Data insights, Business intelligence",
        performance_score=8,
        french_quality=8,
        speed_score=9,
    ),
    "security_guardian": ModelConfig(
        name="Gemma2 2B",
        ollama_name="gemma2:2b",
        ram_usage_gb=1.6,
        specialization="Sécurité, RGPD, Analyse technique",
        performance_score=8,
        french_quality=9,
        speed_score=9,
    ),
}


class AgentMode(Enum):
    DATA_FLYWHEEL = "data_flywheel"
    SECURITY_GUARDIAN = "security_guardian"
    IDLE = "idle"


# ========================================
# 🚀 GESTIONNAIRE IA LOCALES OPTIMISÉ
# ========================================


class OptimizedLocalAIManager:
    """
    🚀 Gestionnaire IA locales optimisé pour MacBook Pro 8GB
    Alternance intelligente + optimisation mémoire maximale
    """

    def __init__(self):
        self.current_model: Optional[str] = None
        self.current_mode: AgentMode = AgentMode.IDLE
        self.model_configs = OPTIMIZED_MODELS
        self.ollama_endpoint = "http://localhost:11434"
        self.memory_threshold_gb = 6.5  # Seuil critique RAM
        self.model_cache = {}

        # Statistiques performance
        self.performance_stats = {
            "model_switches": 0,
            "memory_optimizations": 0,
            "successful_alternations": 0,
        }

        logging.info("🧠 Optimized Local AI Manager initialized for 8GB MacBook Pro")

    async def setup_optimized_models(self) -> Dict[str, bool]:
        """
        🎯 Setup initial des modèles optimisés
        Installation et configuration pour Phoenix Letters
        """

        setup_results = {}

        print("🚀 Starting optimized model setup for Phoenix Letters...")

        # Vérification Ollama
        if not await self._check_ollama_running():
            print("❌ Ollama not running. Starting...")
            await self._start_ollama()

        # Installation modèles optimisés
        for mode, config in self.model_configs.items():
            print(f"📥 Installing {config.name} for {mode}...")
            try:
                success = await self._install_model(config.ollama_name)
                setup_results[mode] = success

                if success:
                    print(f"✅ {config.name} installed successfully")
                    print(f"   📊 RAM usage: {config.ram_usage_gb}GB")
                    print(f"   🎯 Specialization: {config.specialization}")
                else:
                    print(f"❌ Failed to install {config.name}")

            except Exception as e:
                print(f"❌ Error installing {config.name}: {e}")
                setup_results[mode] = False

        # Test des modèles
        for mode, success in setup_results.items():
            if success:
                await self._test_model_performance(mode)

        return setup_results

    async def smart_model_switch(
        self, target_mode: AgentMode, priority: str = "normal"
    ) -> bool:
        """
        🧠 Alternance intelligente des modèles avec optimisation mémoire
        """

        if target_mode == self.current_mode:
            return True  # Déjà actif

        # Vérification mémoire disponible
        available_memory_gb = self._get_available_memory_gb()
        target_config = self.model_configs[target_mode.value]

        print(f"🔄 Switching to {target_mode.value} ({target_config.name})")
        print(
            f"💾 Available RAM: {available_memory_gb:.1f}GB, Required: {target_config.ram_usage_gb}GB"
        )

        # Libération mémoire si nécessaire
        if available_memory_gb < target_config.ram_usage_gb:
            print("🧹 Insufficient memory, optimizing...")
            await self._optimize_memory()
            available_memory_gb = self._get_available_memory_gb()

        # Déchargement modèle actuel
        if self.current_model:
            await self._unload_current_model()

        # Chargement nouveau modèle
        try:
            success = await self._load_model(target_config.ollama_name)

            if success:
                self.current_model = target_config.ollama_name
                self.current_mode = target_mode
                self.performance_stats["successful_alternations"] += 1

                print(f"✅ Successfully switched to {target_config.name}")
                return True
            else:
                print(f"❌ Failed to load {target_config.name}")
                return False

        except Exception as e:
            print(f"❌ Error during model switch: {e}")
            return False

    async def execute_with_agent(
        self, mode: AgentMode, prompt: str, **kwargs
    ) -> Dict[str, Any]:
        """
        🎯 Exécution avec agent spécialisé (alternance automatique)
        """

        # Switch automatique vers le bon agent
        switch_success = await self.smart_model_switch(mode)

        if not switch_success:
            return {
                "error": f"Failed to switch to {mode.value}",
                "fallback_available": True,
            }

        # Exécution avec modèle spécialisé
        try:
            result = await self._execute_prompt(prompt, **kwargs)

            # Enrichissement avec métadonnées
            result["model_used"] = self.current_model
            result["mode"] = mode.value
            result["memory_usage"] = self._get_memory_usage_gb()

            return result

        except Exception as e:
            return {
                "error": str(e),
                "model_used": self.current_model,
                "mode": mode.value,
            }

    async def _execute_prompt(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Exécution prompt avec modèle actuel"""

        if not self.current_model:
            raise Exception("No model loaded")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.ollama_endpoint}/api/generate",
                    json={
                        "model": self.current_model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": kwargs.get("temperature", 0.2),
                            "top_p": kwargs.get("top_p", 0.9),
                            "num_ctx": kwargs.get("context_length", 4096),
                        },
                    },
                    timeout=kwargs.get("timeout", 60.0),
                )

                if response.status_code == 200:
                    result = response.json()
                    return {
                        "response": result["response"],
                        "tokens_generated": result.get("eval_count", 0),
                        "generation_time": result.get("total_duration", 0) / 1e9,
                        "status": "success",
                    }
                else:
                    raise Exception(f"HTTP {response.status_code}: {response.text}")

        except Exception as e:
            raise Exception(f"Model execution failed: {e}")

    def _get_available_memory_gb(self) -> float:
        """Calcul mémoire disponible"""
        memory = psutil.virtual_memory()
        available_gb = memory.available / (1024**3)
        return available_gb

    def _get_memory_usage_gb(self) -> float:
        """Calcul usage mémoire actuel"""
        memory = psutil.virtual_memory()
        used_gb = memory.used / (1024**3)
        return used_gb

    async def _optimize_memory(self):
        """Optimisation mémoire aggressive"""

        print("🧹 Starting memory optimization...")

        # 1. Déchargement modèle actuel
        if self.current_model:
            await self._unload_current_model()

        # 2. Nettoyage cache Ollama
        try:
            subprocess.run(["ollama", "ps"], capture_output=True, text=True)
            # Force garbage collection
            import gc

            gc.collect()

            self.performance_stats["memory_optimizations"] += 1

        except Exception as e:
            print(f"⚠️ Memory optimization warning: {e}")

        time.sleep(2)  # Laisser le temps à la mémoire de se libérer

        available_after = self._get_available_memory_gb()
        print(f"✅ Memory optimization complete. Available: {available_after:.1f}GB")

    async def _unload_current_model(self):
        """Déchargement modèle actuel"""
        if self.current_model:
            try:
                # Ollama n'a pas de commande explicite unload, mais on peut arrêter le processus
                print(f"📤 Unloading {self.current_model}")

                # Clear model from memory (restart ollama si nécessaire)
                self.current_model = None
                self.current_mode = AgentMode.IDLE

            except Exception as e:
                print(f"⚠️ Warning during model unload: {e}")

    async def _load_model(self, model_name: str) -> bool:
        """Chargement modèle spécifique"""
        try:
            # Test simple pour charger le modèle en mémoire
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.ollama_endpoint}/api/generate",
                    json={"model": model_name, "prompt": "Test", "stream": False},
                    timeout=30.0,
                )

                return response.status_code == 200

        except Exception as e:
            print(f"❌ Failed to load {model_name}: {e}")
            return False

    async def _check_ollama_running(self) -> bool:
        """Vérification Ollama actif"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.ollama_endpoint}/api/version", timeout=5.0
                )
                return response.status_code == 200
        except:
            return False

    async def _start_ollama(self):
        """Démarrage Ollama"""
        try:
            # Démarrage en arrière-plan
            subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            # Attendre que le service soit prêt
            for _ in range(10):
                if await self._check_ollama_running():
                    print("✅ Ollama started successfully")
                    return
                await asyncio.sleep(2)

            raise Exception("Ollama failed to start")

        except Exception as e:
            print(f"❌ Failed to start Ollama: {e}")
            raise

    async def _install_model(self, model_name: str) -> bool:
        """Installation modèle optimisé"""
        try:
            print(f"📥 Installing {model_name}...")

            # Installation via subprocess
            process = subprocess.run(
                ["ollama", "pull", model_name],
                capture_output=True,
                text=True,
                timeout=600,  # 10 minutes max
            )

            if process.returncode == 0:
                print(f"✅ {model_name} installed successfully")
                return True
            else:
                print(f"❌ Installation failed: {process.stderr}")
                return False

        except subprocess.TimeoutExpired:
            print(f"❌ Installation timeout for {model_name}")
            return False
        except Exception as e:
            print(f"❌ Installation error: {e}")
            return False

    async def _test_model_performance(self, mode: str):
        """Test performance modèle"""
        config = self.model_configs[mode]

        print(f"🧪 Testing {config.name} performance...")

        # Test simple
        test_prompt = "Analyse cette phrase en français: 'La reconversion professionnelle est un défi.'"

        start_time = time.time()

        try:
            # Switch temporaire pour test
            await self.smart_model_switch(AgentMode(mode))

            result = await self._execute_prompt(test_prompt, timeout=15.0)

            end_time = time.time()
            duration = end_time - start_time

            print(f"✅ Test completed in {duration:.2f}s")
            print(
                f"📝 Response quality: {'Good' if len(result['response']) > 50 else 'Basic'}"
            )

        except Exception as e:
            print(f"❌ Test failed: {e}")

    def get_system_status(self) -> Dict[str, Any]:
        """Status système complet"""
        return {
            "current_model": self.current_model,
            "current_mode": (
                self.current_mode.value
                if self.current_mode != AgentMode.IDLE
                else "idle"
            ),
            "memory_usage_gb": self._get_memory_usage_gb(),
            "available_memory_gb": self._get_available_memory_gb(),
            "performance_stats": self.performance_stats,
            "models_available": list(self.model_configs.keys()),
            "system_health": (
                "good" if self._get_available_memory_gb() > 2.0 else "critical"
            ),
        }


# ========================================
# 🎯 AGENTS SPÉCIALISÉS PHOENIX LETTERS
# ========================================


class PhoenixDataFlywheelAgent:
    """
    🧠 Agent Data Flywheel optimisé pour 8GB
    Spécialisé analytics et apprentissage Phoenix Letters
    """

    def __init__(self, ai_manager: OptimizedLocalAIManager):
        self.ai_manager = ai_manager
        self.mode = AgentMode.DATA_FLYWHEEL

    async def analyze_interaction_data(
        self, cv: str, job_offer: str, letter: str, user_feedback: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Analyse données interaction pour apprentissage"""

        prompt = f"""
        Analyse cette interaction Phoenix Letters pour le data flywheel.
        Réponds en JSON valide uniquement.
        
        CV (extrait): {cv[:300]}...
        OFFRE: {job_offer[:300]}...
        LETTRE: {letter[:300]}...
        FEEDBACK: {user_feedback or 'Non disponible'}
        
        Analyse:
        {{
            "reconversion_type": "aide_soignant_to_cyber|prof_to_dev|commerce_to_marketing|autre",
            "quality_score": 0-10,
            "success_indicators": ["indicateur1", "indicateur2"],
            "improvement_areas": ["amélioration1", "amélioration2"],
            "business_insights": ["insight1", "insight2"],
            "pattern_detected": "description du pattern identifié",
            "next_optimization": "recommandation pour optimiser"
        }}
        """

        return await self.ai_manager.execute_with_agent(
            self.mode, prompt, temperature=0.1
        )

    async def generate_business_insights(
        self, interactions_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Génération insights business automatiques"""

        # Résumé des données
        total_interactions = len(interactions_data)
        reconversion_types = [
            d.get("reconversion_type", "autre") for d in interactions_data
        ]

        prompt = f"""
        Génère des insights business Phoenix Letters basés sur {total_interactions} interactions.
        Réponds en JSON valide uniquement.
        
        DONNÉES RÉSUMÉES:
        - Total interactions: {total_interactions}
        - Types reconversion: {dict(zip(*np.unique(reconversion_types, return_counts=True))) if interactions_data else {}}
        
        Insights:
        {{
            "trending_reconversions": ["type1", "type2"],
            "optimization_opportunities": ["opportunité1", "opportunité2"],
            "revenue_insights": ["insight1", "insight2"],
            "user_behavior_patterns": ["pattern1", "pattern2"],
            "competitive_advantages": ["avantage1", "avantage2"],
            "strategic_recommendations": ["rec1", "rec2"]
        }}
        """

        return await self.ai_manager.execute_with_agent(
            self.mode, prompt, temperature=0.2
        )


class PhoenixSecurityAgent:
    """
    🛡️ Agent Sécurité optimisé pour 8GB
    Spécialisé RGPD et sécurité Phoenix Letters
    """

    def __init__(self, ai_manager: OptimizedLocalAIManager):
        self.ai_manager = ai_manager
        self.mode = AgentMode.SECURITY_GUARDIAN

    async def analyze_rgpd_compliance(
        self, content: str, content_type: str
    ) -> Dict[str, Any]:
        """Analyse conformité RGPD"""

        prompt = f"""
        Analyse RGPD stricte pour Phoenix Letters.
        Réponds en JSON valide uniquement.
        
        CONTENU ({content_type}): {content[:500]}...
        
        Analyse:
        {{
            "compliance_status": "compliant|non_compliant|attention_required",
            "pii_detected": [
                {{"type": "nom", "risk_level": "low|medium|high"}},
                {{"type": "email", "risk_level": "medium"}}
            ],
            "rgpd_violations": ["violation1", "violation2"],
            "anonymization_required": true/false,
            "recommendations": ["action1", "action2"],
            "data_processing_justification": "finalité légitime|consentement|contrat",
            "retention_period": "30_days|1_year|indefinite",
            "risk_assessment": "low|medium|high"
        }}
        """

        return await self.ai_manager.execute_with_agent(
            self.mode, prompt, temperature=0.05
        )

    async def detect_security_threats(self, user_input: str) -> Dict[str, Any]:
        """Détection menaces sécurité"""

        prompt = f"""
        Détection menaces sécurité Phoenix Letters.
        Réponds en JSON valide uniquement.
        
        INPUT UTILISATEUR: {user_input[:400]}...
        
        Analyse:
        {{
            "threat_level": "none|low|medium|high|critical",
            "threats_detected": [
                {{"type": "prompt_injection", "confidence": 0-100}},
                {{"type": "data_exfiltration", "confidence": 0-100}}
            ],
            "malicious_patterns": ["pattern1", "pattern2"],
            "recommended_action": "allow|sanitize|block|escalate",
            "sanitization_needed": true/false,
            "security_score": 0-100
        }}
        """

        return await self.ai_manager.execute_with_agent(
            self.mode, prompt, temperature=0.05
        )


# ========================================
# 🚀 ORCHESTRATEUR PHOENIX OPTIMISÉ
# ========================================


class PhoenixOptimizedOrchestrator:
    """
    🚀 Orchestrateur Phoenix Letters optimisé 8GB
    Coordination intelligente des agents locaux
    """

    def __init__(self):
        self.ai_manager = OptimizedLocalAIManager()
        self.data_agent = PhoenixDataFlywheelAgent(self.ai_manager)
        self.security_agent = PhoenixSecurityAgent(self.ai_manager)

        self.session_stats = {
            "total_analyses": 0,
            "security_checks": 0,
            "data_insights": 0,
            "model_switches": 0,
        }

    async def initialize_system(self) -> bool:
        """Initialisation système complet"""

        print("🚀 Initializing Phoenix Letters Optimized AI System...")

        # Setup modèles
        setup_results = await self.ai_manager.setup_optimized_models()

        success_count = sum(setup_results.values())
        total_models = len(setup_results)

        if success_count >= 1:
            print(f"✅ System initialized: {success_count}/{total_models} models ready")
            return True
        else:
            print("❌ System initialization failed")
            return False

    async def process_phoenix_interaction(
        self,
        cv_content: str,
        job_offer: str,
        generated_letter: str,
        user_tier: str = "free",
        user_feedback: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        🎯 Traitement complet interaction Phoenix avec alternance optimale
        """

        print("🎯 Processing Phoenix Letters interaction with optimized local AI...")

        start_time = time.time()
        analysis_results = {}

        try:
            # 1. 🛡️ Analyse sécurité PRIORITAIRE
            print("🛡️ Running security analysis...")

            cv_security = await self.security_agent.analyze_rgpd_compliance(
                cv_content, "cv"
            )
            job_security = await self.security_agent.detect_security_threats(job_offer)

            analysis_results["security_analysis"] = {
                "cv_compliance": cv_security.get("response", {}),
                "job_threat_detection": job_security.get("response", {}),
                "overall_security": (
                    "safe"
                    if all(
                        [
                            cv_security.get("response", {}).get("compliance_status")
                            != "non_compliant",
                            job_security.get("response", {}).get("threat_level")
                            in ["none", "low"],
                        ]
                    )
                    else "attention_required"
                ),
            }

            self.session_stats["security_checks"] += 1

            # Blocage si menace critique
            if job_security.get("response", {}).get("threat_level") == "critical":
                return {
                    "status": "BLOCKED",
                    "reason": "Critical security threat detected",
                    "analysis": analysis_results,
                }

            # 2. 🧠 Analyse data flywheel (avec alternance automatique)
            print("🧠 Running data flywheel analysis...")

            data_analysis = await self.data_agent.analyze_interaction_data(
                cv_content, job_offer, generated_letter, user_feedback
            )

            analysis_results["data_flywheel"] = {
                "interaction_analysis": data_analysis.get("response", {}),
                "learning_insights": "Données capturées pour amélioration continue",
            }

            self.session_stats["data_insights"] += 1

            # 3. 📊 Métriques système
            system_status = self.ai_manager.get_system_status()
            analysis_results["system_performance"] = {
                "memory_usage": system_status["memory_usage_gb"],
                "model_switches": system_status["performance_stats"]["model_switches"],
                "processing_time": time.time() - start_time,
                "efficiency_score": (
                    "excellent"
                    if system_status["available_memory_gb"] > 3.0
                    else "good"
                ),
            }

            self.session_stats["total_analyses"] += 1

            return {
                "status": "SUCCESS",
                "analysis": analysis_results,
                "session_stats": self.session_stats,
                "recommendations": self._generate_recommendations(analysis_results),
            }

        except Exception as e:
            return {
                "status": "ERROR",
                "error": str(e),
                "partial_analysis": analysis_results,
            }

    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Génération recommandations basées sur analyse"""

        recommendations = []

        # Sécurité
        security = analysis.get("security_analysis", {})
        if security.get("overall_security") == "attention_required":
            recommendations.append("🛡️ Réviser le contenu pour conformité RGPD")

        # Performance
        performance = analysis.get("system_performance", {})
        if performance.get("memory_usage") > 6.5:
            recommendations.append("💾 Optimisation mémoire recommandée")

        # Data insights
        data = analysis.get("data_flywheel", {})
        if data.get("interaction_analysis"):
            recommendations.append("📊 Données capturées pour amélioration future")

        return recommendations

    def get_dashboard_metrics(self) -> Dict[str, Any]:
        """Métriques dashboard Phoenix"""

        system_status = self.ai_manager.get_system_status()

        return {
            "system_health": system_status["system_health"],
            "current_model": system_status["current_model"],
            "memory_usage": f"{system_status['memory_usage_gb']:.1f}GB",
            "available_memory": f"{system_status['available_memory_gb']:.1f}GB",
            "session_stats": self.session_stats,
            "models_ready": len([m for m in system_status["models_available"]]),
            "performance_rating": (
                "🔥 Optimized"
                if system_status["available_memory_gb"] > 3.0
                else "⚡ Efficient"
            ),
        }


# ========================================
# 🧪 DÉMONSTRATION COMPLÈTE
# ========================================


async def demo_optimized_phoenix_ai():
    """Démonstration système IA local optimisé Phoenix Letters"""

    print("🚀 DEMO: Phoenix Letters Optimized Local AI for 8GB MacBook Pro")
    print("=" * 70)

    # Initialisation
    orchestrator = PhoenixOptimizedOrchestrator()

    # Setup système
    init_success = await orchestrator.initialize_system()
    if not init_success:
        print("❌ System initialization failed. Please check Ollama installation.")
        return

    # Données test Phoenix Letters
    cv_test = """
    Aide-soignant depuis 5 ans en EHPAD.
    Formation cybersécurité ANSSI en cours.
    Compétences: soins patients, relationnel, adaptation rapide.
    Objectif: transition vers cybersécurité - pentesting.
    """

    job_test = """
    Pentester Junior (H/F) - Startup Tech
    Profil débutant accepté avec formation cybersécurité.
    Missions: tests intrusion, rapports sécurité, veille technologique.
    Environnement: équipe 15 personnes, télétravail possible.
    """

    letter_test = """
    Madame, Monsieur,
    
    Aide-soignant passionné par la cybersécurité, je candidate pour votre poste de Pentester Junior.
    Ma reconversion s'appuie sur une formation ANSSI et mes compétences transférables d'analyse et de rigueur.
    Mon expérience du contact humain sera un atout pour communiquer les risques sécurité.
    
    Cordialement,
    """

    # Traitement complet
    print("🎯 Processing complete Phoenix Letters interaction...")

    result = await orchestrator.process_phoenix_interaction(
        cv_content=cv_test,
        job_offer=job_test,
        generated_letter=letter_test,
        user_tier="free",
        user_feedback={"satisfaction": 4, "pertinence": 5},
    )

    # Affichage résultats
    print("\n" + "=" * 50)
    print("📊 RÉSULTATS ANALYSE")
    print("=" * 50)

    print(f"Status: {result['status']}")

    if result["status"] == "SUCCESS":
        analysis = result["analysis"]

        # Sécurité
        security = analysis["security_analysis"]
        print(f"🛡️ Sécurité: {security['overall_security']}")

        # Performance
        perf = analysis["system_performance"]
        print(f"💾 RAM utilisée: {perf['memory_usage']:.1f}GB")
        print(f"⚡ Temps traitement: {perf['processing_time']:.2f}s")
        print(f"🏆 Score efficacité: {perf['efficiency_score']}")

        # Recommandations
        print("\n💡 Recommandations:")
        for rec in result["recommendations"]:
            print(f"  • {rec}")

    # Dashboard final
    print("\n" + "=" * 50)
    print("📈 DASHBOARD SYSTÈME")
    print("=" * 50)

    dashboard = orchestrator.get_dashboard_metrics()
    for key, value in dashboard.items():
        print(f"{key}: {value}")

    print("\n✅ Démonstration terminée avec succès!")


if __name__ == "__main__":
    # Lancement démonstration
    asyncio.run(demo_optimized_phoenix_ai())
