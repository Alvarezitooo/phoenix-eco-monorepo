"""
🎯 AI Trajectory Builder - Planificateur Intelligent de Reconversion
Système révolutionnaire de parcours carrière personnalisé avec IA prédictive

Author: Claude Phoenix DevSecOps Guardian
Version: 1.0.0 - Revolutionary Career Planning
"""

import json
import os
import re
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

# Imports conditionnels
try:
    from .enhanced_gemini_client import get_enhanced_gemini_client
    from utils.exceptions import SecurityException
    from utils.secure_logging import secure_logger
except ImportError:
    import logging

    class MockSecureLogger:
        def log_security_event(self, event_type, data, level="INFO"):
            logging.info(f"AI_TRAJECTORY | {event_type}: {data}")

    class SecurityException(Exception):
        pass

    secure_logger = MockSecureLogger()


class CareerStage(Enum):
    """Étapes de la reconversion professionnelle"""

    EXPLORATION = "exploration"
    DECISION = "decision"
    FORMATION = "formation"
    TRANSITION = "transition"
    INTEGRATION = "integration"
    EXCELLENCE = "excellence"


class TrajectoryDifficulty(Enum):
    """Niveaux de difficulté de reconversion"""

    FACILE = "facile"  # Même secteur, poste similaire
    MODERE = "modéré"  # Secteur proche, nouvelles compétences
    DIFFICILE = "difficile"  # Nouveau secteur, formation longue
    EXPERT = "expert"  # Changement radical, expertise poussée


@dataclass
class CareerMilestone:
    """Étape clé du parcours de reconversion"""

    id: str
    title: str
    description: str
    stage: CareerStage
    duration_weeks: int
    difficulty: int  # 1-5
    prerequisites: List[str]
    deliverables: List[str]
    resources: List[Dict[str, str]]
    success_criteria: List[str]
    tips: List[str]
    estimated_cost: Optional[str] = None
    is_critical: bool = False


@dataclass
class TrajectoryAnalysis:
    """Analyse complète d'une trajectoire de reconversion"""

    user_id: str
    current_profile: Dict[str, Any]
    target_job: str
    target_sector: str

    # Analyse personnalisée
    trajectory_difficulty: TrajectoryDifficulty
    success_probability: float  # 0.0 - 1.0
    estimated_duration_months: int
    estimated_investment: str

    # Parcours personnalisé
    milestones: List[CareerMilestone]
    critical_path: List[str]  # IDs des milestones critiques

    # Recommandations IA
    strengths: List[str]
    challenges: List[str]
    key_recommendations: List[str]
    alternative_paths: List[Dict[str, Any]]

    # Métriques
    created_at: datetime
    last_updated: datetime


class AITrajectoryBuilder:
    """
    Constructeur de trajectoires de reconversion alimenté par IA.

    Analyse le profil utilisateur et génère un parcours personnalisé
    avec étapes, ressources et probabilités de succès.
    """

    def __init__(self):
        self.trajectory_templates = self._load_trajectory_templates()
        self.industry_knowledge = self._load_industry_knowledge()
        self._trajectory_cache = {}

        secure_logger.log_security_event("AI_TRAJECTORY_BUILDER_INITIALIZED", {})

    def build_personalized_trajectory(
        self, user_profile: Dict[str, Any], target_job: str, target_sector: str = ""
    ) -> TrajectoryAnalysis:
        """
        Construit une trajectoire personnalisée de reconversion.

        Args:
            user_profile: Profil complet utilisateur
            target_job: Poste visé
            target_sector: Secteur cible (optionnel)

        Returns:
            TrajectoryAnalysis complète avec parcours personnalisé
        """
        try:
            # Génération ID unique pour cette trajectoire
            trajectory_id = self._generate_trajectory_id(user_profile, target_job)

            # Vérification cache
            if trajectory_id in self._trajectory_cache:
                cached = self._trajectory_cache[trajectory_id]
                if (datetime.now() - cached.last_updated).hours < 24:
                    secure_logger.log_security_event(
                        "TRAJECTORY_CACHE_HIT", {"id": trajectory_id[:8]}
                    )
                    return cached

            # Analyse du profil et du secteur cible
            profile_analysis = self._analyze_user_profile(user_profile)
            sector_analysis = self._analyze_target_sector(target_job, target_sector)

            # Calcul difficulté et probabilité de succès
            difficulty = self._calculate_trajectory_difficulty(
                profile_analysis, sector_analysis
            )
            success_prob = self._calculate_success_probability(
                profile_analysis, sector_analysis, difficulty
            )

            # Génération des milestones personnalisées
            milestones = self._generate_personalized_milestones(
                profile_analysis, sector_analysis, difficulty
            )

            # Identification du chemin critique
            critical_path = self._identify_critical_path(milestones)

            # Analyse des forces/défis
            strengths, challenges = self._analyze_strengths_challenges(
                profile_analysis, sector_analysis
            )

            # Recommandations IA
            recommendations = self._generate_ai_recommendations(
                profile_analysis, sector_analysis, difficulty
            )

            # Chemins alternatifs
            alternatives = self._suggest_alternative_paths(profile_analysis, target_job)

            # Estimations temporelles et financières
            duration_months = self._estimate_trajectory_duration(milestones)
            investment = self._estimate_investment(milestones, difficulty)

            # Construction de l'analyse finale
            trajectory = TrajectoryAnalysis(
                user_id=trajectory_id,
                current_profile=profile_analysis,
                target_job=target_job,
                target_sector=target_sector,
                trajectory_difficulty=difficulty,
                success_probability=success_prob,
                estimated_duration_months=duration_months,
                estimated_investment=investment,
                milestones=milestones,
                critical_path=critical_path,
                strengths=strengths,
                challenges=challenges,
                key_recommendations=recommendations,
                alternative_paths=alternatives,
                created_at=datetime.now(),
                last_updated=datetime.now(),
            )

            # Mise en cache
            self._trajectory_cache[trajectory_id] = trajectory

            secure_logger.log_security_event(
                "TRAJECTORY_BUILT_SUCCESS",
                {
                    "trajectory_id": trajectory_id[:8],
                    "difficulty": difficulty.value,
                    "success_probability": success_prob,
                    "milestones_count": len(milestones),
                },
            )

            return trajectory

        except Exception as e:
            secure_logger.log_security_event(
                "TRAJECTORY_BUILD_ERROR",
                {"error": str(e)[:200], "target_job": target_job},
                "ERROR",
            )
            raise SecurityException(f"Erreur construction trajectoire: {str(e)}")

    def get_next_milestone(
        self, trajectory: TrajectoryAnalysis, completed_milestones: List[str]
    ) -> Optional[CareerMilestone]:
        """Récupère la prochaine étape recommandée du parcours."""

        remaining_milestones = [
            m for m in trajectory.milestones if m.id not in completed_milestones
        ]

        if not remaining_milestones:
            return None

        # Priorité aux milestones critiques sans prérequis non satisfaits
        for milestone in remaining_milestones:
            if milestone.is_critical:
                prereqs_satisfied = all(
                    prereq in completed_milestones for prereq in milestone.prerequisites
                )
                if prereqs_satisfied:
                    return milestone

        # Sinon, première milestone avec prérequis satisfaits
        for milestone in remaining_milestones:
            prereqs_satisfied = all(
                prereq in completed_milestones for prereq in milestone.prerequisites
            )
            if prereqs_satisfied:
                return milestone

        # Par défaut, première milestone sans prérequis
        no_prereq_milestones = [m for m in remaining_milestones if not m.prerequisites]
        return (
            no_prereq_milestones[0] if no_prereq_milestones else remaining_milestones[0]
        )

    def update_trajectory_progress(
        self,
        trajectory_id: str,
        completed_milestones: List[str],
        user_feedback: Dict[str, Any] = None,
    ) -> TrajectoryAnalysis:
        """Met à jour le progrès de la trajectoire avec feedback utilisateur."""

        if trajectory_id not in self._trajectory_cache:
            raise SecurityException("Trajectoire non trouvée")

        trajectory = self._trajectory_cache[trajectory_id]

        # Calcul du progrès
        total_milestones = len(trajectory.milestones)
        completed_count = len(completed_milestones)
        progress_percentage = (completed_count / total_milestones) * 100

        # Mise à jour probabilité de succès basée sur le progrès
        if progress_percentage > 50:
            trajectory.success_probability = min(
                trajectory.success_probability + 0.1, 1.0
            )

        # Intégration feedback utilisateur
        if user_feedback:
            trajectory = self._integrate_user_feedback(trajectory, user_feedback)

        trajectory.last_updated = datetime.now()

        secure_logger.log_security_event(
            "TRAJECTORY_PROGRESS_UPDATED",
            {
                "trajectory_id": trajectory_id[:8],
                "progress": f"{progress_percentage:.1f}%",
                "completed_milestones": completed_count,
            },
        )

        return trajectory

    def generate_trajectory_report(
        self, trajectory: TrajectoryAnalysis
    ) -> Dict[str, Any]:
        """Génère un rapport complet de la trajectoire pour l'utilisateur."""

        report = {
            "executive_summary": {
                "target_position": trajectory.target_job,
                "difficulty_level": trajectory.trajectory_difficulty.value,
                "success_probability": f"{trajectory.success_probability*100:.0f}%",
                "estimated_duration": f"{trajectory.estimated_duration_months} mois",
                "estimated_investment": trajectory.estimated_investment,
            },
            "roadmap": {
                "total_milestones": len(trajectory.milestones),
                "critical_milestones": len(trajectory.critical_path),
                "milestones_by_stage": self._group_milestones_by_stage(
                    trajectory.milestones
                ),
            },
            "analysis": {
                "key_strengths": trajectory.strengths,
                "main_challenges": trajectory.challenges,
                "success_factors": trajectory.key_recommendations,
            },
            "alternatives": {
                "alternative_paths": trajectory.alternative_paths,
                "pivot_opportunities": self._identify_pivot_points(trajectory),
            },
            "next_steps": {
                "immediate_actions": self._get_immediate_actions(trajectory),
                "week_1_plan": self._generate_week_1_plan(trajectory),
                "month_1_objectives": self._generate_month_1_objectives(trajectory),
            },
        }

        return report

    def _analyze_user_profile(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse approfondie du profil utilisateur."""

        # Extraction et nettoyage des données
        current_sector = profile.get("current_sector", "").lower()
        experience_years = int(profile.get("experience_years", 0))
        education_level = profile.get("education_level", "bac").lower()
        skills = profile.get("competences_key", "").lower()

        # Analyse des compétences transférables
        transferable_skills = self._identify_transferable_skills(skills, current_sector)

        # Évaluation du potentiel de reconversion
        reconversion_readiness = self._assess_reconversion_readiness(profile)

        return {
            "current_sector": current_sector,
            "experience_years": experience_years,
            "education_level": education_level,
            "skills_analysis": transferable_skills,
            "reconversion_readiness": reconversion_readiness,
            "learning_capacity": self._assess_learning_capacity(profile),
            "risk_tolerance": self._assess_risk_tolerance(profile),
            "available_time": profile.get("available_time", "temps_partiel"),
            "budget_capacity": profile.get("budget_capacity", "limite"),
        }

    def _analyze_target_sector(
        self, target_job: str, target_sector: str
    ) -> Dict[str, Any]:
        """Analyse du secteur et poste cibles."""

        job_lower = target_job.lower()
        sector_lower = target_sector.lower()

        # Récupération des données sectorielles
        sector_data = self.industry_knowledge.get(sector_lower, {})

        return {
            "sector_name": target_sector,
            "job_title": target_job,
            "required_skills": self._extract_required_skills(job_lower),
            "entry_barriers": sector_data.get("entry_barriers", ["formation_requise"]),
            "market_demand": sector_data.get("market_demand", "moyenne"),
            "salary_range": sector_data.get("salary_range", "30k-50k"),
            "remote_friendly": sector_data.get("remote_friendly", True),
            "growth_potential": sector_data.get("growth_potential", "stable"),
        }

    def _calculate_trajectory_difficulty(
        self, profile_analysis: Dict[str, Any], sector_analysis: Dict[str, Any]
    ) -> TrajectoryDifficulty:
        """Calcule la difficulté de la reconversion."""

        difficulty_score = 0

        # Facteur secteur (0-3 points)
        current_sector = profile_analysis["current_sector"]
        target_sector = sector_analysis["sector_name"].lower()

        if current_sector == target_sector:
            difficulty_score += 0  # Même secteur
        elif self._are_sectors_related(current_sector, target_sector):
            difficulty_score += 1  # Secteurs proches
        else:
            difficulty_score += 3  # Secteurs différents

        # Facteur compétences (0-2 points)
        skill_gap = self._calculate_skill_gap(profile_analysis, sector_analysis)
        if skill_gap > 0.7:
            difficulty_score += 2
        elif skill_gap > 0.4:
            difficulty_score += 1

        # Facteur formation requise (0-2 points)
        entry_barriers = sector_analysis["entry_barriers"]
        if "formation_longue" in entry_barriers:
            difficulty_score += 2
        elif "certification" in entry_barriers:
            difficulty_score += 1

        # Facteur expérience (0-1 point)
        if profile_analysis["experience_years"] < 3:
            difficulty_score += 1

        # Mapping score vers difficulté
        if difficulty_score <= 2:
            return TrajectoryDifficulty.FACILE
        elif difficulty_score <= 4:
            return TrajectoryDifficulty.MODERE
        elif difficulty_score <= 6:
            return TrajectoryDifficulty.DIFFICILE
        else:
            return TrajectoryDifficulty.EXPERT

    def _calculate_success_probability(
        self,
        profile_analysis: Dict[str, Any],
        sector_analysis: Dict[str, Any],
        difficulty: TrajectoryDifficulty,
    ) -> float:
        """Calcule la probabilité de succès de la reconversion."""

        base_probability = {
            TrajectoryDifficulty.FACILE: 0.85,
            TrajectoryDifficulty.MODERE: 0.70,
            TrajectoryDifficulty.DIFFICILE: 0.55,
            TrajectoryDifficulty.EXPERT: 0.35,
        }[difficulty]

        # Ajustements basés sur le profil
        adjustments = 0

        # Expérience (+/- 0.1)
        if profile_analysis["experience_years"] > 5:
            adjustments += 0.1
        elif profile_analysis["experience_years"] < 2:
            adjustments -= 0.1

        # Niveau d'éducation (+/- 0.05)
        education = profile_analysis["education_level"]
        if "master" in education or "ingénieur" in education:
            adjustments += 0.05
        elif education == "bac":
            adjustments -= 0.05

        # Capacité d'apprentissage (+/- 0.1)
        learning_capacity = profile_analysis["learning_capacity"]
        if learning_capacity == "élevée":
            adjustments += 0.1
        elif learning_capacity == "faible":
            adjustments -= 0.1

        # Demande du marché (+/- 0.05)
        market_demand = sector_analysis["market_demand"]
        if market_demand == "forte":
            adjustments += 0.05
        elif market_demand == "faible":
            adjustments -= 0.05

        final_probability = max(0.2, min(0.95, base_probability + adjustments))
        return round(final_probability, 2)

    def _generate_personalized_milestones(
        self,
        profile_analysis: Dict[str, Any],
        sector_analysis: Dict[str, Any],
        difficulty: TrajectoryDifficulty,
    ) -> List[CareerMilestone]:
        """Génère les étapes personnalisées du parcours."""

        milestones = []

        # Étape 1: Exploration et validation
        milestones.append(
            CareerMilestone(
                id="exploration_validation",
                title="🔍 Exploration et validation du projet",
                description="Valider votre choix de reconversion par des enquêtes métier et des tests",
                stage=CareerStage.EXPLORATION,
                duration_weeks=2,
                difficulty=1,
                prerequisites=[],
                deliverables=[
                    "3 entretiens avec des professionnels du secteur",
                    "Bilan de compétences approfondi",
                    "Plan de reconversion validé",
                ],
                resources=[
                    {"type": "outil", "name": "LinkedIn pour networking", "url": "#"},
                    {
                        "type": "plateforme",
                        "name": "Pôle Emploi - Enquêtes métier",
                        "url": "#",
                    },
                ],
                success_criteria=[
                    "Confirmation de la motivation",
                    "Réalisme du projet validé",
                    "Premiers contacts secteur établis",
                ],
                tips=[
                    "Préparez des questions précises pour vos entretiens",
                    "Participez à des événements du secteur",
                    "Documentez tous vos échanges",
                ],
                is_critical=True,
            )
        )

        # Étape 2: Développement des compétences
        skill_gap = self._calculate_skill_gap(profile_analysis, sector_analysis)

        if skill_gap > 0.3:  # Formation nécessaire
            formation_duration = (
                8
                if difficulty
                in [TrajectoryDifficulty.DIFFICILE, TrajectoryDifficulty.EXPERT]
                else 4
            )

            milestones.append(
                CareerMilestone(
                    id="skill_development",
                    title="📚 Développement des compétences clés",
                    description="Acquérir les compétences essentielles pour votre nouveau métier",
                    stage=CareerStage.FORMATION,
                    duration_weeks=formation_duration,
                    difficulty=3 if difficulty == TrajectoryDifficulty.EXPERT else 2,
                    prerequisites=["exploration_validation"],
                    deliverables=[
                        "Certification(s) professionnelle(s)",
                        "Portfolio de projets pratiques",
                        "Réseau professionnel étendu",
                    ],
                    resources=self._get_formation_resources(
                        sector_analysis["job_title"]
                    ),
                    success_criteria=[
                        "Maîtrise des outils essentiels",
                        "Projets concrets réalisés",
                        "Feedback positif des formateurs",
                    ],
                    tips=[
                        "Privilégiez la pratique à la théorie",
                        "Créez des projets en lien avec vos objectifs",
                        "Participez activement aux communautés",
                    ],
                    is_critical=True,
                )
            )

        # Étape 3: Transition et recherche
        milestones.append(
            CareerMilestone(
                id="transition_search",
                title="🎯 Transition et recherche active",
                description="Optimiser votre profil et lancer votre recherche d'emploi",
                stage=CareerStage.TRANSITION,
                duration_weeks=6,
                difficulty=2,
                prerequisites=(
                    ["skill_development"]
                    if skill_gap > 0.3
                    else ["exploration_validation"]
                ),
                deliverables=[
                    "CV optimisé pour le nouveau secteur",
                    "Portfolio professionnel en ligne",
                    "Stratégie de recherche définie",
                ],
                resources=[
                    {"type": "app", "name": "Phoenix CV - Optimisation", "url": "#"},
                    {
                        "type": "app",
                        "name": "Phoenix Letters - Lettres motivation",
                        "url": "#",
                    },
                    {
                        "type": "plateforme",
                        "name": "Sites d'emploi spécialisés",
                        "url": "#",
                    },
                ],
                success_criteria=[
                    "10+ candidatures qualifiées envoyées",
                    "3+ entretiens obtenus",
                    "Feedback positif sur votre profil",
                ],
                tips=[
                    "Personnalisez chaque candidature",
                    "Utilisez votre réseau pour décrocher des entretiens",
                    "Préparez des exemples concrets de vos réalisations",
                ],
                is_critical=True,
            )
        )

        # Étape 4: Intégration
        milestones.append(
            CareerMilestone(
                id="integration_success",
                title="🚀 Intégration et montée en compétences",
                description="Réussir vos premiers mois dans votre nouveau poste",
                stage=CareerStage.INTEGRATION,
                duration_weeks=12,
                difficulty=2,
                prerequisites=["transition_search"],
                deliverables=[
                    "Objectifs des 3 premiers mois atteints",
                    "Relations professionnelles établies",
                    "Plan de développement défini",
                ],
                resources=[
                    {"type": "méthode", "name": "Plan 30-60-90 jours", "url": "#"},
                    {
                        "type": "formation",
                        "name": "Formation continue secteur",
                        "url": "#",
                    },
                ],
                success_criteria=[
                    "Intégration équipe réussie",
                    "Premiers résultats probants",
                    "Retours positifs hiérarchie",
                ],
                tips=[
                    "Soyez proactif dans votre apprentissage",
                    "Demandez régulièrement des retours",
                    "Documentez vos succès",
                ],
            )
        )

        # Étapes supplémentaires pour trajectoires expertes
        if difficulty == TrajectoryDifficulty.EXPERT:
            milestones.insert(
                1,
                CareerMilestone(
                    id="deep_specialization",
                    title="🎓 Spécialisation avancée",
                    description="Acquérir une expertise pointue dans votre domaine cible",
                    stage=CareerStage.FORMATION,
                    duration_weeks=16,
                    difficulty=4,
                    prerequisites=["exploration_validation"],
                    deliverables=[
                        "Diplôme/certification niveau expert",
                        "Mémoire ou projet de fin d'études",
                        "Stage en entreprise réalisé",
                    ],
                    resources=[
                        {
                            "type": "formation",
                            "name": "Formation certifiante longue",
                            "url": "#",
                        },
                        {
                            "type": "université",
                            "name": "Parcours universitaire spécialisé",
                            "url": "#",
                        },
                    ],
                    success_criteria=[
                        "Validation des acquis par des experts",
                        "Projet professionnel abouti",
                        "Recommandations de professionnels",
                    ],
                    tips=[
                        "Choisissez une formation reconnue dans le secteur",
                        "Alternez théorie et pratique",
                        "Constituez un réseau pendant la formation",
                    ],
                    is_critical=True,
                ),
            )

        return milestones

    def _identify_critical_path(self, milestones: List[CareerMilestone]) -> List[str]:
        """Identifie le chemin critique du parcours."""
        return [m.id for m in milestones if m.is_critical]

    def _analyze_strengths_challenges(
        self, profile_analysis: Dict[str, Any], sector_analysis: Dict[str, Any]
    ) -> Tuple[List[str], List[str]]:
        """Analyse les forces et défis de la reconversion."""

        strengths = []
        challenges = []

        # Analyse de l'expérience
        exp_years = profile_analysis["experience_years"]
        if exp_years > 5:
            strengths.append(f"💪 Solide expérience professionnelle ({exp_years} ans)")
        else:
            challenges.append("⚠️ Expérience limitée - nécessite valorisation")

        # Analyse des compétences transférables
        transferable_skills = profile_analysis["skills_analysis"]
        if transferable_skills["transferability_score"] > 0.6:
            strengths.append("🎯 Nombreuses compétences transférables")
        else:
            challenges.append("📚 Importantes nouvelles compétences à acquérir")

        # Analyse du marché
        market_demand = sector_analysis["market_demand"]
        if market_demand == "forte":
            strengths.append("📈 Secteur en forte demande")
        elif market_demand == "faible":
            challenges.append("📉 Marché concurrentiel avec faible demande")

        # Capacité d'apprentissage
        if profile_analysis["learning_capacity"] == "élevée":
            strengths.append("🧠 Excellente capacité d'apprentissage")
        elif profile_analysis["learning_capacity"] == "faible":
            challenges.append("📖 Amélioration des méthodes d'apprentissage nécessaire")

        return strengths, challenges

    def _generate_ai_recommendations(
        self,
        profile_analysis: Dict[str, Any],
        sector_analysis: Dict[str, Any],
        difficulty: TrajectoryDifficulty,
    ) -> List[str]:
        """Génère des recommandations IA personnalisées."""

        recommendations = []

        # Recommandations basées sur la difficulté
        if difficulty == TrajectoryDifficulty.FACILE:
            recommendations.append(
                "✅ Concentrez-vous sur la mise en valeur de vos acquis"
            )
            recommendations.append("🎯 Utilisez votre réseau professionnel existant")
        elif difficulty == TrajectoryDifficulty.EXPERT:
            recommendations.append(
                "🎓 Investissez dans une formation longue et certifiante"
            )
            recommendations.append("⏰ Prévoyez 12-18 mois pour votre reconversion")

        # Recommandations sectorielles
        job_title = sector_analysis["job_title"].lower()
        if "développeur" in job_title or "tech" in job_title:
            recommendations.append("💻 Créez un portfolio GitHub dès maintenant")
            recommendations.append("🏗️ Participez à des projets open source")
        elif "commercial" in job_title or "vente" in job_title:
            recommendations.append("📞 Développez votre réseau commercial")
            recommendations.append("📊 Maîtrisez les outils CRM modernes")

        # Recommandations générales
        recommendations.append(
            "🔄 Utilisez l'écosystème Phoenix pour optimiser votre transition"
        )
        recommendations.append(
            "📝 Documentez votre parcours pour inspiration d'autres candidats"
        )

        return recommendations

    def _suggest_alternative_paths(
        self, profile_analysis: Dict[str, Any], target_job: str
    ) -> List[Dict[str, Any]]:
        """Suggère des chemins alternatifs de reconversion."""

        alternatives = []
        current_sector = profile_analysis["current_sector"]

        # Logique simplifiée pour les alternatives
        alternative_jobs = {
            "développeur web": [
                "consultant digital",
                "chef de projet web",
                "product owner",
            ],
            "commercial": ["business developer", "account manager", "consultant vente"],
            "chef de projet": [
                "scrum master",
                "product manager",
                "consultant organisation",
            ],
        }

        target_lower = target_job.lower()
        for job_key, alternatives_list in alternative_jobs.items():
            if job_key in target_lower:
                for alt_job in alternatives_list:
                    alternatives.append(
                        {
                            "title": alt_job.title(),
                            "difficulty": "Modérée",
                            "reason": f"Compétences similaires à {target_job}",
                        }
                    )
                break

        return alternatives[:3]  # Max 3 alternatives

    def _estimate_trajectory_duration(self, milestones: List[CareerMilestone]) -> int:
        """Estime la durée totale en mois."""
        total_weeks = sum(m.duration_weeks for m in milestones)
        return max(3, int((total_weeks + 2) / 4))  # Conversion en mois avec marge

    def _estimate_investment(
        self, milestones: List[CareerMilestone], difficulty: TrajectoryDifficulty
    ) -> str:
        """Estime l'investissement financier."""

        base_costs = {
            TrajectoryDifficulty.FACILE: "500-1500€",
            TrajectoryDifficulty.MODERE: "1500-5000€",
            TrajectoryDifficulty.DIFFICILE: "5000-15000€",
            TrajectoryDifficulty.EXPERT: "15000-30000€",
        }

        return base_costs[difficulty]

    def _load_trajectory_templates(self) -> Dict[str, Any]:
        """Charge les templates de trajectoires préconfigurés."""
        return {
            "tech": {"formations": ["coding bootcamp", "certifications cloud"]},
            "commercial": {"formations": ["techniques de vente", "négociation"]},
            "rh": {"formations": ["droit social", "psychologie du travail"]},
        }

    def _load_industry_knowledge(self) -> Dict[str, Any]:
        """Charge la base de connaissances sectorielles."""
        return {
            "développement web": {
                "entry_barriers": ["formation_requise", "portfolio"],
                "market_demand": "forte",
                "salary_range": "35k-65k",
                "remote_friendly": True,
                "growth_potential": "excellent",
            },
            "commercial": {
                "entry_barriers": ["expérience_vente"],
                "market_demand": "moyenne",
                "salary_range": "30k-60k",
                "remote_friendly": False,
                "growth_potential": "stable",
            },
        }

    # Méthodes utilitaires simplifiées
    def _generate_trajectory_id(self, profile: Dict[str, Any], target_job: str) -> str:
        import hashlib

        data = f"{profile.get('current_sector', '')}{target_job}{datetime.now().strftime('%Y%m%d')}"
        # SÉCURITÉ: Utilisation de SHA-256 au lieu de MD5 (vulnérable)
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def _identify_transferable_skills(
        self, skills: str, current_sector: str
    ) -> Dict[str, Any]:
        return {
            "transferability_score": 0.7,  # Score simulé
            "transferable_skills": ["communication", "gestion projet", "leadership"],
            "skill_gaps": ["technique spécialisée", "outils secteur"],
        }

    def _assess_reconversion_readiness(self, profile: Dict[str, Any]) -> str:
        return "élevée"  # Simulation

    def _assess_learning_capacity(self, profile: Dict[str, Any]) -> str:
        return "élevée"  # Simulation

    def _assess_risk_tolerance(self, profile: Dict[str, Any]) -> str:
        return "moyenne"  # Simulation

    def _extract_required_skills(self, job_title: str) -> List[str]:
        skills_map = {
            "développeur": ["programmation", "git", "bases de données"],
            "commercial": ["prospection", "négociation", "crm"],
            "chef de projet": ["planification", "coordination", "communication"],
        }

        for job_key, skills in skills_map.items():
            if job_key in job_title:
                return skills
        return ["compétences générales"]

    def _are_sectors_related(self, sector1: str, sector2: str) -> bool:
        related_groups = [
            ["tech", "informatique", "numérique", "digital"],
            ["commerce", "vente", "commercial", "business"],
            ["rh", "ressources humaines", "recrutement"],
        ]

        for group in related_groups:
            if any(s in sector1 for s in group) and any(s in sector2 for s in group):
                return True
        return False

    def _calculate_skill_gap(
        self, profile_analysis: Dict[str, Any], sector_analysis: Dict[str, Any]
    ) -> float:
        return 0.5  # Score gap simulé

    def _get_formation_resources(self, job_title: str) -> List[Dict[str, str]]:
        return [
            {"type": "formation", "name": f"Formation {job_title}", "url": "#"},
            {
                "type": "certification",
                "name": "Certification professionnelle",
                "url": "#",
            },
        ]

    def _group_milestones_by_stage(
        self, milestones: List[CareerMilestone]
    ) -> Dict[str, int]:
        from collections import Counter

        return dict(Counter(m.stage.value for m in milestones))

    def _identify_pivot_points(self, trajectory: TrajectoryAnalysis) -> List[str]:
        return ["Après formation", "Si marché difficile", "En cas d'échec entretiens"]

    def _get_immediate_actions(self, trajectory: TrajectoryAnalysis) -> List[str]:
        return [
            "Confirmer votre motivation par 3 entretiens métier",
            "Évaluer précisément vos compétences transférables",
            "Définir votre budget et planning de reconversion",
        ]

    def _generate_week_1_plan(self, trajectory: TrajectoryAnalysis) -> List[str]:
        return [
            "Jour 1-2: Recherche de professionnels à interviewer",
            "Jour 3-4: Premiers entretiens exploratoires",
            "Jour 5-7: Synthèse et validation du projet",
        ]

    def _generate_month_1_objectives(self, trajectory: TrajectoryAnalysis) -> List[str]:
        return [
            "Validation définitive de votre projet de reconversion",
            "Plan de formation précis et budgété",
            "Premiers contacts secteur établis",
        ]

    def _integrate_user_feedback(
        self, trajectory: TrajectoryAnalysis, feedback: Dict[str, Any]
    ) -> TrajectoryAnalysis:
        # Logique d'intégration du feedback
        return trajectory

    def _cleanup_expired_cache(self):
        """Nettoie automatiquement les entrées expirées du cache"""
        current_time = datetime.now()
        expired_keys = []

        for key, value in self._trajectory_cache.items():
            if hasattr(value, "expires_at") and current_time > value.expires_at:
                expired_keys.append(key)

        for key in expired_keys:
            del self._trajectory_cache[key]


# Instance globale
ai_trajectory_builder = AITrajectoryBuilder()


def _cleanup_expired_cache(self):
    """Nettoie automatiquement les entrées expirées du cache"""
    current_time = datetime.now()
    expired_keys = []

    for key, value in self._cache.items():
        if hasattr(value, "expires_at") and current_time > value.expires_at:
            expired_keys.append(key)

    for key in expired_keys:
        del self._cache[key]
