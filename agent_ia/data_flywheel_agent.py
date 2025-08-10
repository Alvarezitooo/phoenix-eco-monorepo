"""
🧠 AGENT DATA FLYWHEEL PHOENIX LETTERS
Système d'apprentissage automatique local pour optimisation continue
"""

import asyncio
import hashlib
import json
import logging
import re
import sqlite3
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

# ========================================
# 📊 STRUCTURES DE DONNÉES FLYWHEEL
# ========================================


@dataclass
class InteractionData:
    """Structure données interaction utilisateur"""

    session_id: str
    timestamp: datetime
    cv_content: str
    job_offer: str
    generated_letter: str
    user_tier: str
    provider_used: str
    generation_time: float
    user_feedback: Optional[Dict[str, Any]] = None
    quality_metrics: Optional[Dict[str, Any]] = None
    reconversion_type: Optional[str] = None
    success_indicators: Optional[List[str]] = None


@dataclass
class LearningPattern:
    """Pattern appris par le flywheel"""

    pattern_id: str
    pattern_type: (
        str  # "prompt_optimization", "reconversion_success", "quality_improvement"
    )
    confidence_score: float
    usage_count: int
    success_rate: float
    pattern_data: Dict[str, Any]
    created_at: datetime
    last_updated: datetime


@dataclass
class FlywheelInsight:
    """Insight généré par analyse"""

    insight_id: str
    insight_type: str
    impact_level: str  # "high", "medium", "low"
    recommendation: str
    data_support: Dict[str, Any]
    implementation_priority: int
    estimated_improvement: str


# ========================================
# 🧠 AGENT DATA FLYWHEEL PRINCIPAL
# ========================================


class DataFlywheelAgent:
    """
    🧠 Agent Data Flywheel - Cœur de l'apprentissage Phoenix
    Collecte, analyse et optimise automatiquement tout le système
    """

    def __init__(
        self, local_ai_endpoint: str, data_dir: str = "./phoenix_flywheel_data"
    ):
        self.endpoint = local_ai_endpoint
        self.model = "mistral:7b"
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        # Bases de données
        self.db_path = self.data_dir / "flywheel.db"
        self.knowledge_base = {}
        self.learned_patterns = {}
        self.optimization_queue = []

        # Métriques temps réel
        self.current_metrics = {
            "total_interactions": 0,
            "successful_generations": 0,
            "average_quality": 0.0,
            "reconversion_success_rate": 0.0,
            "cost_optimization": 0.0,
        }

        # Initialisation
        self._init_database()
        self._load_existing_patterns()

        logging.info("🧠 Data Flywheel Agent initialized")

    def _init_database(self):
        """Initialisation base de données flywheel"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Table interactions
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                timestamp TEXT,
                cv_hash TEXT,
                job_hash TEXT,
                letter_hash TEXT,
                user_tier TEXT,
                provider_used TEXT,
                generation_time REAL,
                quality_score REAL,
                reconversion_type TEXT,
                success_indicators TEXT,
                user_feedback TEXT
            )
        """
        )

        # Table patterns appris
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS learned_patterns (
                pattern_id TEXT PRIMARY KEY,
                pattern_type TEXT,
                confidence_score REAL,
                usage_count INTEGER,
                success_rate REAL,
                pattern_data TEXT,
                created_at TEXT,
                last_updated TEXT
            )
        """
        )

        # Table optimisations prompts
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS prompt_optimizations (
                optimization_id TEXT PRIMARY KEY,
                reconversion_type TEXT,
                original_prompt TEXT,
                optimized_prompt TEXT,
                improvement_score REAL,
                usage_count INTEGER,
                created_at TEXT
            )
        """
        )

        # Table insights business
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS business_insights (
                insight_id TEXT PRIMARY KEY,
                insight_type TEXT,
                impact_level TEXT,
                recommendation TEXT,
                data_support TEXT,
                implementation_status TEXT,
                created_at TEXT
            )
        """
        )

        conn.commit()
        conn.close()

    async def capture_interaction(self, interaction: InteractionData) -> str:
        """
        📊 Capture et analyse une interaction utilisateur
        Point d'entrée principal du flywheel
        """

        # Analyse immédiate de l'interaction
        analysis = await self._analyze_interaction(interaction)

        # Stockage en base
        interaction_id = self._store_interaction(interaction, analysis)

        # Mise à jour métriques temps réel
        self._update_real_time_metrics(interaction, analysis)

        # Déclenchement apprentissage asynchrone
        asyncio.create_task(self._trigger_learning_cycle(interaction, analysis))

        logging.info(f"🔄 Interaction captured: {interaction_id}")

        return interaction_id

    async def _analyze_interaction(
        self, interaction: InteractionData
    ) -> Dict[str, Any]:
        """Analyse immédiate de l'interaction"""

        analysis_prompt = f"""
        Analyse cette interaction Phoenix Letters pour apprentissage automatique.
        Réponds UNIQUEMENT en JSON valide.
        
        INTERACTION:
        - Type reconversion: {interaction.reconversion_type or 'à déterminer'}
        - Tier utilisateur: {interaction.user_tier}
        - Provider: {interaction.provider_used}
        - Temps génération: {interaction.generation_time}s
        - Feedback: {interaction.user_feedback or 'non disponible'}
        
        CV (extrait): {interaction.cv_content[:300]}...
        OFFRE (extrait): {interaction.job_offer[:300]}...
        LETTRE (extrait): {interaction.generated_letter[:300]}...
        
        Analyse:
        {{
            "reconversion_analysis": {{
                "type_detected": "aide_soignant_to_cyber|prof_to_dev|commerce_to_marketing|autre",
                "difficulty_level": "facile|moyen|difficile",
                "success_probability": 0-100,
                "key_challenges": ["défi1", "défi2"]
            }},
            "quality_assessment": {{
                "coherence_score": 0-10,
                "personalization_score": 0-10,
                "persuasion_score": 0-10,
                "overall_quality": 0-10
            }},
            "optimization_opportunities": [
                {{"area": "prompt", "improvement": "suggestion", "impact": "high|medium|low"}},
                {{"area": "matching", "improvement": "suggestion", "impact": "high"}}
            ],
            "success_patterns": [
                "pattern1: ce qui a bien fonctionné",
                "pattern2: autre point positif"
            ],
            "learning_insights": [
                "insight1: apprentissage pour futures générations",
                "insight2: optimisation système"
            ]
        }}
        """

        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.endpoint}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": analysis_prompt,
                        "stream": False,
                        "options": {"temperature": 0.1},
                    },
                    timeout=60.0,
                )

                if response.status_code == 200:
                    result = response.json()
                    try:
                        analysis = json.loads(result["response"])

                        # Enrichissement avec métriques computationnelles
                        analysis["computed_metrics"] = {
                            "cv_complexity": self._assess_cv_complexity(
                                interaction.cv_content
                            ),
                            "job_requirements_level": self._assess_job_complexity(
                                interaction.job_offer
                            ),
                            "letter_uniqueness": self._calculate_letter_uniqueness(
                                interaction.generated_letter
                            ),
                            "cost_efficiency": self._calculate_cost_efficiency(
                                interaction
                            ),
                            "generation_speed": (
                                "fast"
                                if interaction.generation_time < 5
                                else (
                                    "medium"
                                    if interaction.generation_time < 10
                                    else "slow"
                                )
                            ),
                        }

                        return analysis

                    except json.JSONDecodeError:
                        return self._fallback_analysis(interaction)
        except Exception as e:
            logging.error(f"❌ Interaction analysis failed: {e}")
            return self._fallback_analysis(interaction)

    def _store_interaction(
        self, interaction: InteractionData, analysis: Dict[str, Any]
    ) -> str:
        """Stockage interaction en base"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Hachage pour confidentialité
        cv_hash = hashlib.sha256(interaction.cv_content.encode()).hexdigest()[:16]
        job_hash = hashlib.sha256(interaction.job_offer.encode()).hexdigest()[:16]
        letter_hash = hashlib.sha256(interaction.generated_letter.encode()).hexdigest()[
            :16
        ]

        interaction_id = f"int_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{cv_hash[:8]}"

        cursor.execute(
            """
            INSERT INTO interactions 
            (session_id, timestamp, cv_hash, job_hash, letter_hash, user_tier, 
             provider_used, generation_time, quality_score, reconversion_type, 
             success_indicators, user_feedback)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                interaction.session_id,
                interaction.timestamp.isoformat(),
                cv_hash,
                job_hash,
                letter_hash,
                interaction.user_tier,
                interaction.provider_used,
                interaction.generation_time,
                analysis.get("quality_assessment", {}).get("overall_quality", 7.0),
                analysis.get("reconversion_analysis", {}).get("type_detected", "autre"),
                json.dumps(analysis.get("success_patterns", [])),
                json.dumps(interaction.user_feedback or {}),
            ),
        )

        conn.commit()
        conn.close()

        return interaction_id

    def _update_real_time_metrics(
        self, interaction: InteractionData, analysis: Dict[str, Any]
    ):
        """Mise à jour métriques temps réel"""
        self.current_metrics["total_interactions"] += 1

        # Qualité moyenne
        quality = analysis.get("quality_assessment", {}).get("overall_quality", 7.0)
        current_avg = self.current_metrics["average_quality"]
        total = self.current_metrics["total_interactions"]
        self.current_metrics["average_quality"] = (
            (current_avg * (total - 1)) + quality
        ) / total

        # Taux de succès reconversion
        success_prob = analysis.get("reconversion_analysis", {}).get(
            "success_probability", 70
        )
        if success_prob >= 75:
            self.current_metrics["successful_generations"] += 1

        self.current_metrics["reconversion_success_rate"] = (
            self.current_metrics["successful_generations"] / total * 100
        )

        # Optimisation coût (estimation)
        if interaction.provider_used.startswith("local"):
            self.current_metrics[
                "cost_optimization"
            ] += 0.002  # €0.002 économisés par call local

    async def _trigger_learning_cycle(
        self, interaction: InteractionData, analysis: Dict[str, Any]
    ):
        """Cycle d'apprentissage asynchrone"""

        # 1. Identification nouveaux patterns
        await self._identify_new_patterns(interaction, analysis)

        # 2. Optimisation prompts
        await self._optimize_prompts(interaction, analysis)

        # 3. Génération insights business
        await self._generate_business_insights()

        # 4. Mise à jour base de connaissance
        await self._update_knowledge_base(analysis)

    async def _identify_new_patterns(
        self, interaction: InteractionData, analysis: Dict[str, Any]
    ):
        """Identification et apprentissage nouveaux patterns"""

        reconversion_type = analysis.get("reconversion_analysis", {}).get(
            "type_detected", "autre"
        )
        quality_score = analysis.get("quality_assessment", {}).get(
            "overall_quality", 7.0
        )

        # Pattern de succès si qualité > 8
        if quality_score >= 8.0:
            pattern_id = (
                f"success_{reconversion_type}_{datetime.now().strftime('%Y%m')}"
            )

            # Vérifier si pattern existe
            if pattern_id not in self.learned_patterns:
                # Nouveau pattern de succès
                pattern = LearningPattern(
                    pattern_id=pattern_id,
                    pattern_type="success_pattern",
                    confidence_score=0.8,
                    usage_count=1,
                    success_rate=1.0,
                    pattern_data={
                        "reconversion_type": reconversion_type,
                        "success_factors": analysis.get("success_patterns", []),
                        "quality_indicators": analysis.get("quality_assessment", {}),
                        "provider_optimal": interaction.provider_used,
                        "generation_time_optimal": interaction.generation_time,
                    },
                    created_at=datetime.now(),
                    last_updated=datetime.now(),
                )

                self.learned_patterns[pattern_id] = pattern
                await self._store_pattern(pattern)

                logging.info(f"🧠 New success pattern learned: {pattern_id}")
            else:
                # Mise à jour pattern existant
                pattern = self.learned_patterns[pattern_id]
                pattern.usage_count += 1
                pattern.success_rate = (
                    pattern.success_rate + 1.0
                ) / 2  # Moyenne mobile
                pattern.last_updated = datetime.now()
                await self._store_pattern(pattern)

    async def _optimize_prompts(
        self, interaction: InteractionData, analysis: Dict[str, Any]
    ):
        """Optimisation automatique des prompts"""

        reconversion_type = analysis.get("reconversion_analysis", {}).get(
            "type_detected", "autre"
        )
        quality_score = analysis.get("quality_assessment", {}).get(
            "overall_quality", 7.0
        )

        # Si qualité sous-optimale, proposer optimisation
        if quality_score < 7.5:
            optimization_opportunities = analysis.get("optimization_opportunities", [])

            for opp in optimization_opportunities:
                if opp.get("area") == "prompt" and opp.get("impact") in [
                    "high",
                    "medium",
                ]:
                    # Générer prompt optimisé
                    optimized_prompt = await self._generate_optimized_prompt(
                        reconversion_type,
                        interaction.cv_content,
                        interaction.job_offer,
                        opp.get("improvement", ""),
                    )

                    if optimized_prompt:
                        await self._store_prompt_optimization(
                            reconversion_type, optimized_prompt
                        )

    async def _generate_optimized_prompt(
        self, reconversion_type: str, cv: str, job_offer: str, improvement: str
    ) -> Optional[str]:
        """Génération prompt optimisé via IA locale"""

        optimization_prompt = f"""
        Crée un prompt optimisé pour Phoenix Letters basé sur cette analyse.
        
        TYPE RECONVERSION: {reconversion_type}
        AMÉLIORATION CIBLE: {improvement}
        
        CV (contexte): {cv[:200]}...
        OFFRE (contexte): {job_offer[:200]}...
        
        Génère un prompt de génération de lettre optimisé qui:
        1. Met en valeur la reconversion comme atout
        2. Personnalise selon le profil
        3. Adresse spécifiquement {improvement}
        4. Reste professionnel et authentique
        
        PROMPT OPTIMISÉ:
        """

        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.endpoint}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": optimization_prompt,
                        "stream": False,
                        "options": {"temperature": 0.3},
                    },
                    timeout=45.0,
                )

                if response.status_code == 200:
                    result = response.json()
                    optimized_prompt = result["response"].strip()

                    # Validation basique
                    if (
                        len(optimized_prompt) > 100
                        and "reconversion" in optimized_prompt.lower()
                    ):
                        return optimized_prompt

        except Exception as e:
            logging.error(f"❌ Prompt optimization failed: {e}")

        return None

    async def _store_prompt_optimization(
        self, reconversion_type: str, optimized_prompt: str
    ):
        """Stockage optimisation prompt"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        optimization_id = (
            f"opt_{reconversion_type}_{datetime.now().strftime('%Y%m%d_%H%M')}"
        )

        cursor.execute(
            """
            INSERT OR REPLACE INTO prompt_optimizations 
            (optimization_id, reconversion_type, optimized_prompt, improvement_score, usage_count, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                optimization_id,
                reconversion_type,
                optimized_prompt,
                0.0,  # À mesurer lors usage
                0,
                datetime.now().isoformat(),
            ),
        )

        conn.commit()
        conn.close()

        logging.info(f"💡 Prompt optimized for {reconversion_type}")

    async def _generate_business_insights(self):
        """Génération insights business automatiques"""

        # Analyse tendances dernières 7 jours
        recent_data = self._get_recent_interactions(days=7)

        if len(recent_data) < 10:  # Pas assez de données
            return

        insights_prompt = f"""
        Analyse ces données Phoenix Letters et génère des insights business.
        Réponds UNIQUEMENT en JSON valide.
        
        DONNÉES (7 derniers jours):
        - Total interactions: {len(recent_data)}
        - Qualité moyenne: {sum(d['quality_score'] for d in recent_data) / len(recent_data):.2f}
        - Types reconversion: {Counter(d['reconversion_type'] for d in recent_data)}
        - Providers utilisés: {Counter(d['provider_used'] for d in recent_data)}
        
        Génère insights:
        {{
            "trends_analysis": {{
                "growing_reconversion_types": ["type1", "type2"],
                "declining_quality_areas": ["area1", "area2"],
                "cost_optimization_opportunities": "analyse"
            }},
            "strategic_recommendations": [
                {{"area": "product", "recommendation": "action", "impact": "high|medium|low"}},
                {{"area": "marketing", "recommendation": "action", "impact": "medium"}}
            ],
            "technical_optimizations": [
                {{"component": "prompts|routing|models", "action": "optimisation", "priority": 1-5}}
            ],
            "business_opportunities": [
                "opportunité1: description",
                "opportunité2: description"
            ]
        }}
        """

        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.endpoint}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": insights_prompt,
                        "stream": False,
                        "options": {"temperature": 0.2},
                    },
                    timeout=60.0,
                )

                if response.status_code == 200:
                    result = response.json()
                    try:
                        insights = json.loads(result["response"])
                        await self._store_business_insights(insights)
                    except json.JSONDecodeError:
                        pass
        except Exception as e:
            logging.error(f"❌ Business insights generation failed: {e}")

    def _get_recent_interactions(self, days: int = 7) -> List[Dict[str, Any]]:
        """Récupération interactions récentes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        since_date = (datetime.now() - timedelta(days=days)).isoformat()

        cursor.execute(
            """
            SELECT * FROM interactions 
            WHERE timestamp > ? 
            ORDER BY timestamp DESC
        """,
            (since_date,),
        )

        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        conn.close()
        return results

    async def _store_business_insights(self, insights: Dict[str, Any]):
        """Stockage insights business"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for recommendation in insights.get("strategic_recommendations", []):
            insight_id = f"insight_{datetime.now().strftime('%Y%m%d_%H%M')}_{recommendation['area']}"

            cursor.execute(
                """
                INSERT OR REPLACE INTO business_insights 
                (insight_id, insight_type, impact_level, recommendation, data_support, implementation_status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    insight_id,
                    recommendation["area"],
                    recommendation["impact"],
                    recommendation["recommendation"],
                    json.dumps(insights),
                    "pending",
                    datetime.now().isoformat(),
                ),
            )

        conn.commit()
        conn.close()

    async def _update_knowledge_base(self, analysis: Dict[str, Any]):
        """Mise à jour base de connaissance évolutive"""

        reconversion_type = analysis.get("reconversion_analysis", {}).get(
            "type_detected", "autre"
        )

        if reconversion_type not in self.knowledge_base:
            self.knowledge_base[reconversion_type] = {
                "total_cases": 0,
                "success_patterns": [],
                "common_challenges": [],
                "optimal_approaches": [],
                "quality_benchmarks": [],
            }

        kb_entry = self.knowledge_base[reconversion_type]
        kb_entry["total_cases"] += 1

        # Mise à jour patterns de succès
        success_patterns = analysis.get("success_patterns", [])
        for pattern in success_patterns:
            if pattern not in kb_entry["success_patterns"]:
                kb_entry["success_patterns"].append(pattern)

        # Défis identifiés
        challenges = analysis.get("reconversion_analysis", {}).get("key_challenges", [])
        for challenge in challenges:
            if challenge not in kb_entry["common_challenges"]:
                kb_entry["common_challenges"].append(challenge)

        # Sauvegarde périodique
        if kb_entry["total_cases"] % 10 == 0:  # Tous les 10 cas
            await self._save_knowledge_base()

    async def _save_knowledge_base(self):
        """Sauvegarde base de connaissance"""
        kb_file = self.data_dir / "knowledge_base.json"

        with open(kb_file, "w", encoding="utf-8") as f:
            json.dump(self.knowledge_base, f, indent=2, ensure_ascii=False, default=str)

    def _load_existing_patterns(self):
        """Chargement patterns existants au démarrage"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM learned_patterns")
            for row in cursor.fetchall():
                pattern_id = row[0]
                pattern = LearningPattern(
                    pattern_id=pattern_id,
                    pattern_type=row[1],
                    confidence_score=row[2],
                    usage_count=row[3],
                    success_rate=row[4],
                    pattern_data=json.loads(row[5]),
                    created_at=datetime.fromisoformat(row[6]),
                    last_updated=datetime.fromisoformat(row[7]),
                )
                self.learned_patterns[pattern_id] = pattern

            conn.close()
            logging.info(f"📚 Loaded {len(self.learned_patterns)} existing patterns")

        except Exception as e:
            logging.error(f"❌ Failed to load patterns: {e}")

    async def _store_pattern(self, pattern: LearningPattern):
        """Stockage pattern appris"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO learned_patterns 
            (pattern_id, pattern_type, confidence_score, usage_count, success_rate, 
             pattern_data, created_at, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                pattern.pattern_id,
                pattern.pattern_type,
                pattern.confidence_score,
                pattern.usage_count,
                pattern.success_rate,
                json.dumps(pattern.pattern_data, default=str),
                pattern.created_at.isoformat(),
                pattern.last_updated.isoformat(),
            ),
        )

        conn.commit()
        conn.close()

    # ========================================
    # 🎯 MÉTHODES UTILITAIRES
    # ========================================

    def _assess_cv_complexity(self, cv_content: str) -> str:
        """Évaluation complexité CV"""
        word_count = len(cv_content.split())

        if word_count > 500:
            return "complex"
        elif word_count > 200:
            return "medium"
        else:
            return "simple"

    def _assess_job_complexity(self, job_offer: str) -> str:
        """Évaluation complexité offre"""
        technical_keywords = [
            "expert",
            "senior",
            "lead",
            "manager",
            "architect",
            "specialist",
        ]

        if any(keyword in job_offer.lower() for keyword in technical_keywords):
            return "senior"
        elif any(
            keyword in job_offer.lower()
            for keyword in ["junior", "débutant", "formation"]
        ):
            return "junior"
        else:
            return "intermediate"

    def _calculate_letter_uniqueness(self, letter_content: str) -> float:
        """Calcul unicité lettre (anti-template)"""
        # Analyse diversité vocabulaire
        words = letter_content.lower().split()
        unique_words = set(words)

        if len(words) == 0:
            return 0.0

        uniqueness_ratio = len(unique_words) / len(words)
        return min(uniqueness_ratio * 100, 100.0)

    def _calculate_cost_efficiency(
        self, interaction: InteractionData
    ) -> Dict[str, Any]:
        """Calcul efficacité coût"""
        if interaction.provider_used.startswith("local"):
            cost = 0.0
            efficiency = "optimal"
        elif interaction.provider_used == "gemini":
            cost = 0.002  # Estimation
            efficiency = "good" if interaction.generation_time < 10 else "average"
        else:
            cost = 0.01  # Estimation Claude
            efficiency = "premium"

        return {
            "estimated_cost": cost,
            "efficiency_rating": efficiency,
            "cost_per_second": cost / max(interaction.generation_time, 1),
        }

    def _fallback_analysis(self, interaction: InteractionData) -> Dict[str, Any]:
        """Analyse fallback si IA locale indisponible"""
        return {
            "reconversion_analysis": {
                "type_detected": "autre",
                "difficulty_level": "moyen",
                "success_probability": 70,
            },
            "quality_assessment": {"overall_quality": 7.0},
            "computed_metrics": {"fallback_used": True},
        }

    # ========================================
    # 📊 API PUBLIQUE POUR PHOENIX LETTERS
    # ========================================

    async def get_optimized_prompt(self, reconversion_type: str) -> Optional[str]:
        """Récupération prompt optimisé pour type reconversion"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT optimized_prompt FROM prompt_optimizations 
            WHERE reconversion_type = ? 
            ORDER BY improvement_score DESC, created_at DESC 
            LIMIT 1
        """,
            (reconversion_type,),
        )

        result = cursor.fetchone()
        conn.close()

        return result[0] if result else None

    def get_flywheel_metrics(self) -> Dict[str, Any]:
        """Métriques flywheel pour dashboard Phoenix"""
        return {
            "current_metrics": self.current_metrics,
            "learned_patterns_count": len(self.learned_patterns),
            "knowledge_base_coverage": len(self.knowledge_base),
            "optimization_pipeline": len(self.optimization_queue),
            "last_update": datetime.now().isoformat(),
        }

    async def get_reconversion_insights(self, reconversion_type: str) -> Dict[str, Any]:
        """Insights spécifiques type reconversion"""
        if reconversion_type in self.knowledge_base:
            kb_entry = self.knowledge_base[reconversion_type]

            # Enrichir avec patterns appris
            related_patterns = [
                p
                for p in self.learned_patterns.values()
                if p.pattern_data.get("reconversion_type") == reconversion_type
            ]

            return {
                "knowledge_base": kb_entry,
                "learned_patterns": len(related_patterns),
                "success_rate": (
                    sum(p.success_rate for p in related_patterns)
                    / len(related_patterns)
                    if related_patterns
                    else 0.7
                ),
                "recommendations": await self._generate_reconversion_recommendations(
                    reconversion_type
                ),
            }

        return {"message": "Pas encore de données pour ce type de reconversion"}

    async def _generate_reconversion_recommendations(
        self, reconversion_type: str
    ) -> List[str]:
        """Génération recommandations spécifiques"""

        # Récupération données historiques
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT AVG(quality_score), AVG(generation_time), provider_used
            FROM interactions 
            WHERE reconversion_type = ?
            GROUP BY provider_used
        """,
            (reconversion_type,),
        )

        provider_stats = cursor.fetchall()
        conn.close()

        recommendations = []

        if provider_stats:
            # Meilleur provider
            best_provider = max(provider_stats, key=lambda x: x[0])
            recommendations.append(
                f"Provider optimal: {best_provider[2]} (qualité: {best_provider[0]:.1f}/10)"
            )

            # Vitesse optimale
            fastest = min(provider_stats, key=lambda x: x[1])
            recommendations.append(
                f"Génération la plus rapide: {fastest[2]} ({fastest[1]:.1f}s)"
            )

        # Recommandations depuis knowledge base
        if reconversion_type in self.knowledge_base:
            kb = self.knowledge_base[reconversion_type]
            if kb["success_patterns"]:
                recommendations.append(
                    f"Pattern de succès principal: {kb['success_patterns'][0]}"
                )

        return recommendations


# ========================================
# 🚀 INTÉGRATION PHOENIX LETTERS
# ========================================


class PhoenixFlywheelIntegration:
    """
    🚀 Intégration transparente du flywheel dans Phoenix Letters
    """

    def __init__(self, local_ai_endpoint: str = "http://localhost:11434"):
        self.flywheel = DataFlywheelAgent(local_ai_endpoint)
        self.session_id = None

    def start_session(self, user_id: str = None) -> str:
        """Démarrage session utilisateur"""
        self.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_id or 'anonymous'}"
        return self.session_id

    async def capture_letter_generation(
        self,
        cv_content: str,
        job_offer: str,
        generated_letter: str,
        user_tier: str,
        provider_used: str,
        generation_time: float,
        user_feedback: Dict[str, Any] = None,
    ) -> str:
        """
        🎯 Méthode principale - à appeler après chaque génération de lettre
        """

        if not self.session_id:
            self.start_session()

        interaction = InteractionData(
            session_id=self.session_id,
            timestamp=datetime.now(),
            cv_content=cv_content,
            job_offer=job_offer,
            generated_letter=generated_letter,
            user_tier=user_tier,
            provider_used=provider_used,
            generation_time=generation_time,
            user_feedback=user_feedback,
        )

        # Capture et apprentissage automatique
        interaction_id = await self.flywheel.capture_interaction(interaction)

        return interaction_id

    async def get_optimized_generation_params(
        self, cv_content: str, job_offer: str
    ) -> Dict[str, Any]:
        """
        🧠 Paramètres optimisés basés sur l'apprentissage
        """

        # Analyse rapide type reconversion
        reconversion_type = await self._quick_reconversion_detection(
            cv_content, job_offer
        )

        # Récupération prompt optimisé
        optimized_prompt = await self.flywheel.get_optimized_prompt(reconversion_type)

        # Insights reconversion
        insights = await self.flywheel.get_reconversion_insights(reconversion_type)

        return {
            "reconversion_type": reconversion_type,
            "optimized_prompt": optimized_prompt,
            "success_probability": insights.get("success_rate", 0.7),
            "recommendations": insights.get("recommendations", []),
            "flywheel_metrics": self.flywheel.get_flywheel_metrics(),
        }

    async def _quick_reconversion_detection(self, cv: str, job_offer: str) -> str:
        """Détection rapide type reconversion"""

        # Patterns basiques
        if any(
            word in cv.lower() for word in ["aide-soignant", "infirmier", "médical"]
        ):
            if any(
                word in job_offer.lower()
                for word in ["cyber", "sécurité", "pentesting"]
            ):
                return "sante_to_cyber"
            elif any(
                word in job_offer.lower()
                for word in ["développ", "programmation", "code"]
            ):
                return "sante_to_dev"

        if any(word in cv.lower() for word in ["prof", "enseignant", "éducation"]):
            return "education_to_business"

        if any(word in cv.lower() for word in ["commercial", "vente", "magasin"]):
            return "commerce_to_marketing"

        return "autre"


# ========================================
# 🧪 EXEMPLE D'UTILISATION DANS PHOENIX
# ========================================


async def demo_flywheel_integration():
    """Démonstration intégration flywheel dans Phoenix Letters"""

    # Initialisation
    flywheel = PhoenixFlywheelIntegration()

    # Démarrage session
    session_id = flywheel.start_session("user_123")
    print(f"🚀 Session started: {session_id}")

    # Données test
    cv_test = """
    Aide-soignant depuis 5 ans en EHPAD.
    Formation cybersécurité en cours (ANSSI).
    Reconversion vers cybersécurité - pentesting.
    """

    job_test = """
    Recherche Pentester Junior (H/F)
    Débutant accepté, formation cybersec requise.
    """

    # 1. Récupération paramètres optimisés AVANT génération
    optimal_params = await flywheel.get_optimized_generation_params(cv_test, job_test)
    print(f"🧠 Type reconversion détecté: {optimal_params['reconversion_type']}")
    print(f"📈 Probabilité succès: {optimal_params['success_probability']:.1%}")

    # 2. Génération lettre (simulée)
    letter_generated = """
    Madame, Monsieur,
    
    Aide-soignant passionné par la cybersécurité, je candidate pour le poste de Pentester Junior.
    Ma reconversion s'appuie sur une formation ANSSI et mes compétences transférables.
    
    Cordialement,
    """

    # 3. Capture interaction pour apprentissage
    interaction_id = await flywheel.capture_letter_generation(
        cv_content=cv_test,
        job_offer=job_test,
        generated_letter=letter_generated,
        user_tier="free",
        provider_used="local_mistral",
        generation_time=4.2,
        user_feedback={"satisfaction": 4, "pertinence": 5},
    )

    print(f"📊 Interaction capturée: {interaction_id}")

    # 4. Métriques flywheel
    metrics = flywheel.flywheel.get_flywheel_metrics()
    print(f"🎯 Métriques flywheel: {metrics}")

    return flywheel


if __name__ == "__main__":
    # Test complet
    asyncio.run(demo_flywheel_integration())
