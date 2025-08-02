"""
🧠 Smart Coach - Assistant IA Contextuel Temps Réel
Système révolutionnaire de coaching intelligent pour reconversions

Author: Claude Phoenix DevSecOps Guardian
Version: 1.0.0 - Revolutionary AI Coaching System
"""

import hashlib
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
    from services.ai_trajectory_builder import ai_trajectory_builder
    from services.enhanced_gemini_client import get_enhanced_gemini_client
    from utils.exceptions import SecurityException
    from utils.secure_logging import secure_logger
except ImportError:
    import logging

    class MockSecureLogger:
        def log_security_event(self, event_type, data, level="INFO"):
            logging.info(f"SMART_COACH | {event_type}: {data}")

    class SecurityException(Exception):
        pass

    secure_logger = MockSecureLogger()


class CoachingContext(Enum):
    """Contextes de coaching disponibles"""

    ONBOARDING = "onboarding"  # Premier contact utilisateur
    CV_CREATION = "cv_creation"  # Pendant création CV
    CV_OPTIMIZATION = "cv_optimization"  # Optimisation CV existant
    TRAJECTORY_PLANNING = "trajectory"  # Planification reconversion
    JOB_SEARCH = "job_search"  # Recherche active emploi
    INTERVIEW_PREP = "interview_prep"  # Préparation entretiens
    ECOSYSTEM_NAVIGATION = "ecosystem"  # Navigation Phoenix
    MOTIVATION_BOOST = "motivation"  # Boost motivation
    OBSTACLE_SOLVING = "obstacles"  # Résolution problèmes


class CoachingTone(Enum):
    """Tonalités du coach"""

    MOTIVANT = "motivant"  # Encourageant et énergique
    EXPERT = "expert"  # Professionnel et précis
    BIENVEILLANT = "bienveillant"  # Empathique et rassurant
    COACH_SPORTIF = "sportif"  # Directif et challengeant
    MENTOR = "mentor"  # Sage et guidant


class UrgencyLevel(Enum):
    """Niveaux d'urgence des conseils"""

    INFO = "info"  # Information générale
    SUGGESTION = "suggestion"  # Suggestion d'amélioration
    IMPORTANT = "important"  # Action recommandée
    URGENT = "urgent"  # Action immédiate requise
    CRITICAL = "critical"  # Blocage critique à résoudre


@dataclass
class CoachingInsight:
    """Insight/conseil personnalisé du coach"""

    id: str
    context: CoachingContext
    title: str
    message: str
    tone: CoachingTone
    urgency: UrgencyLevel

    # Actions suggérées
    suggested_actions: List[str]
    quick_wins: List[str]  # Actions rapides 2-5 min

    # Personnalisation
    personalization_factors: List[str]
    confidence_score: float  # 0.0-1.0

    # Métadonnées
    created_at: datetime
    expires_at: datetime
    shown_count: int = 0
    user_reaction: Optional[str] = None  # "helpful", "not_helpful", "ignored"


@dataclass
class CoachingSession:
    """Session de coaching utilisateur"""

    user_id: str
    session_start: datetime
    last_activity: datetime

    # État utilisateur
    current_context: CoachingContext
    user_profile: Dict[str, Any]
    session_data: Dict[str, Any]

    # Historique coaching
    insights_given: List[CoachingInsight]
    user_actions_taken: List[str]
    success_metrics: Dict[str, float]

    # Préférences apprises
    preferred_tone: Optional[CoachingTone] = None
    response_patterns: Dict[str, Any] = None


class SmartCoach:
    """
    Coach IA contextuel temps réel pour reconversions.

    Analyse en permanence le comportement utilisateur et fournit
    des conseils personnalisés ultra-pertinents au bon moment.
    """

    def __init__(self):
        self.coaching_knowledge = self._load_coaching_knowledge()
        self.session_cache = {}
        self.insights_cache = {}

        # Patterns comportementaux appris
        self.behavioral_patterns = {
            "hesitation_signals": [
                "retour_page_precedente",
                "temps_inactivite_long",
                "formulaire_incomplet",
                "multiple_refresh",
            ],
            "engagement_signals": [
                "temps_lecture_long",
                "interaction_multiple",
                "partage_donnees_detaillees",
                "navigation_fluide",
            ],
            "frustration_signals": [
                "clics_rapides_multiples",
                "abandon_formulaire",
                "navigation_erratique",
                "erreurs_repetees",
            ],
        }

        secure_logger.log_security_event("SMART_COACH_INITIALIZED", {})

    def start_coaching_session(
        self,
        user_id: str,
        context: CoachingContext,
        user_profile: Dict[str, Any] = None,
    ) -> CoachingSession:
        """Démarre une nouvelle session de coaching."""

        session = CoachingSession(
            user_id=user_id,
            session_start=datetime.now(),
            last_activity=datetime.now(),
            current_context=context,
            user_profile=user_profile or {},
            session_data={},
            insights_given=[],
            user_actions_taken=[],
            success_metrics={},
            response_patterns={},
        )

        self.session_cache[user_id] = session

        # Insight d'accueil contextuel
        welcome_insight = self._generate_welcome_insight(session)
        if welcome_insight:
            session.insights_given.append(welcome_insight)

        secure_logger.log_security_event(
            "COACHING_SESSION_STARTED",
            {"user_id": user_id[:8], "context": context.value},
        )

        return session

    def get_contextual_insights(
        self,
        user_id: str,
        current_action: str,
        page_data: Dict[str, Any] = None,
        user_behavior: Dict[str, Any] = None,
    ) -> List[CoachingInsight]:
        """
        Génère des insights contextuels basés sur l'action utilisateur.

        Args:
            user_id: ID utilisateur
            current_action: Action actuelle (ex: "filling_cv_form", "viewing_results")
            page_data: Données de la page actuelle
            user_behavior: Signaux comportementaux détectés
        """

        if user_id not in self.session_cache:
            # Créer session par défaut
            self.start_coaching_session(user_id, CoachingContext.ONBOARDING)

        session = self.session_cache[user_id]
        session.last_activity = datetime.now()

        insights = []

        try:
            # 1. Analyse comportementale temps réel
            behavioral_insights = self._analyze_user_behavior(
                session, user_behavior or {}
            )
            insights.extend(behavioral_insights)

            # 2. Insights contextuels spécifiques
            context_insights = self._generate_context_specific_insights(
                session, current_action, page_data or {}
            )
            insights.extend(context_insights)

            # 3. Suggestions d'optimisation
            optimization_insights = self._generate_optimization_insights(
                session, page_data
            )
            insights.extend(optimization_insights)

            # 4. Motivation et encouragement
            motivation_insights = self._generate_motivation_insights(session)
            insights.extend(motivation_insights)

            # 5. Navigation écosystème
            ecosystem_insights = self._generate_ecosystem_insights(
                session, current_action
            )
            insights.extend(ecosystem_insights)

            # Filtrage et priorisation
            prioritized_insights = self._prioritize_insights(insights, session)

            # Mise à jour session
            session.insights_given.extend(prioritized_insights)

            secure_logger.log_security_event(
                "CONTEXTUAL_INSIGHTS_GENERATED",
                {
                    "user_id": user_id[:8],
                    "action": current_action,
                    "insights_count": len(prioritized_insights),
                },
            )

            return prioritized_insights

        except Exception as e:
            secure_logger.log_security_event(
                "INSIGHT_GENERATION_ERROR",
                {"error": str(e)[:200], "user_id": user_id[:8]},
                "ERROR",
            )

            # Insight de fallback
            return [self._create_fallback_insight(session)]

    def track_user_action(
        self,
        user_id: str,
        action: str,
        result: Dict[str, Any] = None,
        insight_id: str = None,
    ):
        """Tracking des actions utilisateur pour apprentissage."""

        if user_id not in self.session_cache:
            return

        session = self.session_cache[user_id]
        session.user_actions_taken.append(
            {
                "action": action,
                "timestamp": datetime.now().isoformat(),
                "result": result or {},
                "related_insight": insight_id,
            }
        )

        # Mise à jour métriques succès
        self._update_success_metrics(session, action, result)

        # Apprentissage patterns
        self._learn_user_patterns(session, action, result)

    def provide_feedback_on_insight(
        self,
        user_id: str,
        insight_id: str,
        feedback: str,  # "helpful", "not_helpful", "ignored"
    ):
        """Collecte feedback utilisateur sur les insights."""

        if user_id not in self.session_cache:
            return

        session = self.session_cache[user_id]

        # Recherche de l'insight
        for insight in session.insights_given:
            if insight.id == insight_id:
                insight.user_reaction = feedback
                break

        # Apprentissage pour personnalisation future
        self._learn_from_feedback(session, insight_id, feedback)

    def get_smart_recommendations(
        self, user_id: str, current_context: CoachingContext
    ) -> List[Dict[str, Any]]:
        """Génère des recommandations intelligentes selon le contexte."""

        if user_id not in self.session_cache:
            return []

        session = self.session_cache[user_id]
        recommendations = []

        context_recommendations = {
            CoachingContext.CV_CREATION: [
                {
                    "title": "🎯 Optimisez pour les ATS",
                    "description": "Utilisez des mots-clés sectoriels pour passer les filtres automatiques",
                    "action": "optimize_ats",
                    "urgency": "important",
                },
                {
                    "title": "📊 Quantifiez vos résultats",
                    "description": "Ajoutez des chiffres concrets à vos réalisations",
                    "action": "add_metrics",
                    "urgency": "suggestion",
                },
            ],
            CoachingContext.JOB_SEARCH: [
                {
                    "title": "📝 Créez votre lettre Phoenix",
                    "description": "Complétez votre candidature avec une lettre personnalisée",
                    "action": "create_letter",
                    "urgency": "important",
                }
            ],
            CoachingContext.TRAJECTORY_PLANNING: [
                {
                    "title": "🗺️ Planifiez votre roadmap",
                    "description": "Utilisez notre AI Trajectory Builder pour un plan détaillé",
                    "action": "build_trajectory",
                    "urgency": "critical",
                }
            ],
        }

        return context_recommendations.get(current_context, [])

    def _generate_welcome_insight(
        self, session: CoachingSession
    ) -> Optional[CoachingInsight]:
        """Génère un insight d'accueil personnalisé."""

        context = session.current_context
        profile = session.user_profile

        welcome_messages = {
            CoachingContext.ONBOARDING: {
                "title": "🚀 Bienvenue dans Phoenix CV !",
                "message": "Je suis votre coach IA personnel. Je vais vous accompagner étape par étape dans votre reconversion. Commençons par créer votre CV parfait !",
                "actions": ["Découvrir les fonctionnalités", "Créer mon premier CV"],
                "quick_wins": [
                    "Choisir votre niveau (gratuit/premium)",
                    "Remplir votre profil",
                ],
            },
            CoachingContext.CV_CREATION: {
                "title": "✨ Créons votre CV parfait !",
                "message": "Excellent choix ! Je vais vous guider pour créer un CV optimisé reconversion avec nos prompts magistraux Gemini Pro.",
                "actions": ["Remplir le formulaire complet", "Choisir le bon niveau"],
                "quick_wins": [
                    "Préciser votre poste cible",
                    "Lister vos compétences clés",
                ],
            },
        }

        welcome_data = welcome_messages.get(context)
        if not welcome_data:
            return None

        return CoachingInsight(
            id=f"welcome_{context.value}_{int(time.time())}",
            context=context,
            title=welcome_data["title"],
            message=welcome_data["message"],
            tone=CoachingTone.BIENVEILLANT,
            urgency=UrgencyLevel.INFO,
            suggested_actions=welcome_data["actions"],
            quick_wins=welcome_data["quick_wins"],
            personalization_factors=["new_user", "context_entry"],
            confidence_score=0.9,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=1),
        )

    def _analyze_user_behavior(
        self, session: CoachingSession, behavior_data: Dict[str, Any]
    ) -> List[CoachingInsight]:
        """Analyse comportementale temps réel."""

        insights = []

        # Détection hésitation
        if (
            behavior_data.get("time_on_page", 0) > 120
            and behavior_data.get("interactions", 0) < 3
        ):
            insights.append(
                CoachingInsight(
                    id=f"hesitation_{int(time.time())}",
                    context=session.current_context,
                    title="🤔 Besoin d'aide ?",
                    message="Vous semblez hésiter ! C'est normal pour une reconversion. Voulez-vous que je vous guide pas à pas ?",
                    tone=CoachingTone.BIENVEILLANT,
                    urgency=UrgencyLevel.SUGGESTION,
                    suggested_actions=["Voir la démonstration", "Poser une question"],
                    quick_wins=["Regarder les exemples", "Contacter le support"],
                    personalization_factors=["hesitation_detected", "low_interaction"],
                    confidence_score=0.75,
                    created_at=datetime.now(),
                    expires_at=datetime.now() + timedelta(minutes=30),
                )
            )

        # Détection engagement fort
        if behavior_data.get("form_completion", 0) > 0.7:
            insights.append(
                CoachingInsight(
                    id=f"engagement_{int(time.time())}",
                    context=session.current_context,
                    title="🔥 Excellent travail !",
                    message="Votre profil prend forme ! Plus vous donnez de détails, plus votre CV sera personnalisé et efficace.",
                    tone=CoachingTone.MOTIVANT,
                    urgency=UrgencyLevel.INFO,
                    suggested_actions=[
                        "Continuer le formulaire",
                        "Ajouter plus de détails",
                    ],
                    quick_wins=["Préciser votre motivation", "Ajouter vos soft skills"],
                    personalization_factors=["high_engagement", "form_progress"],
                    confidence_score=0.85,
                    created_at=datetime.now(),
                    expires_at=datetime.now() + timedelta(minutes=15),
                )
            )

        return insights

    def _generate_context_specific_insights(
        self, session: CoachingSession, action: str, page_data: Dict[str, Any]
    ) -> List[CoachingInsight]:
        """Insights spécifiques selon le contexte."""

        insights = []
        context = session.current_context

        if context == CoachingContext.CV_CREATION:
            if action == "form_filling" and page_data.get("target_job"):
                target_job = page_data["target_job"].lower()

                # Conseils spécifiques par métier
                if "développeur" in target_job or "tech" in target_job:
                    insights.append(
                        CoachingInsight(
                            id=f"tech_advice_{int(time.time())}",
                            context=context,
                            title="💻 Conseil Tech Reconversion",
                            message="Pour un poste tech, mettez en avant vos projets personnels, votre veille technologique et votre capacité d'apprentissage !",
                            tone=CoachingTone.EXPERT,
                            urgency=UrgencyLevel.IMPORTANT,
                            suggested_actions=[
                                "Créer un portfolio GitHub",
                                "Mentionner vos projets",
                            ],
                            quick_wins=[
                                "Lister vos langages connus",
                                "Préciser votre spécialisation",
                            ],
                            personalization_factors=["tech_career", "reconversion"],
                            confidence_score=0.9,
                            created_at=datetime.now(),
                            expires_at=datetime.now() + timedelta(hours=2),
                        )
                    )

                elif "commercial" in target_job:
                    insights.append(
                        CoachingInsight(
                            id=f"sales_advice_{int(time.time())}",
                            context=context,
                            title="📈 Conseil Commercial",
                            message="En commercial, quantifiez TOUT ! Chiffre d'affaires, nombre de clients, taux de conversion... Les recruteurs adorent les chiffres !",
                            tone=CoachingTone.COACH_SPORTIF,
                            urgency=UrgencyLevel.IMPORTANT,
                            suggested_actions=[
                                "Quantifier vos résultats",
                                "Mentionner vos techniques",
                            ],
                            quick_wins=[
                                "Ajouter vos performances",
                                "Préciser votre secteur",
                            ],
                            personalization_factors=["sales_career", "results_focus"],
                            confidence_score=0.85,
                            created_at=datetime.now(),
                            expires_at=datetime.now() + timedelta(hours=2),
                        )
                    )

        elif context == CoachingContext.TRAJECTORY_PLANNING:
            if action == "viewing_results":
                insights.append(
                    CoachingInsight(
                        id=f"trajectory_next_{int(time.time())}",
                        context=context,
                        title="🎯 Plan en main, action !",
                        message="Votre roadmap est prêt ! La prochaine étape : passer à l'action. Commencez par les 3 actions de cette semaine.",
                        tone=CoachingTone.COACH_SPORTIF,
                        urgency=UrgencyLevel.URGENT,
                        suggested_actions=["Commencer étape 1", "Planifier la semaine"],
                        quick_wins=[
                            "Noter vos 3 priorités",
                            "Fixer un rendez-vous avec vous-même",
                        ],
                        personalization_factors=["plan_ready", "action_needed"],
                        confidence_score=0.95,
                        created_at=datetime.now(),
                        expires_at=datetime.now() + timedelta(hours=6),
                    )
                )

        return insights

    def _generate_optimization_insights(
        self, session: CoachingSession, page_data: Dict[str, Any]
    ) -> List[CoachingInsight]:
        """Suggestions d'optimisation intelligentes."""

        insights = []

        # Analyse des données de formulaire
        if page_data.get("form_data"):
            form_data = page_data["form_data"]

            # Détection de champs importants manquants
            missing_fields = []
            if not form_data.get("competences_key"):
                missing_fields.append("compétences clés")
            if not form_data.get("motivation"):
                missing_fields.append("motivation")
            if not form_data.get("experience_details"):
                missing_fields.append("détails expérience")

            if missing_fields:
                insights.append(
                    CoachingInsight(
                        id=f"optimization_{int(time.time())}",
                        context=session.current_context,
                        title="⚡ Optimisez votre profil !",
                        message=f'Pour un CV plus percutant, ajoutez : {", ".join(missing_fields)}. Ces éléments font toute la différence !',
                        tone=CoachingTone.EXPERT,
                        urgency=UrgencyLevel.SUGGESTION,
                        suggested_actions=[
                            f"Compléter {field}" for field in missing_fields
                        ],
                        quick_wins=[
                            "Remplir un champ maintenant",
                            "Sauvegarder vos changements",
                        ],
                        personalization_factors=[
                            "profile_optimization",
                            "missing_data",
                        ],
                        confidence_score=0.8,
                        created_at=datetime.now(),
                        expires_at=datetime.now() + timedelta(hours=1),
                    )
                )

        return insights

    def _generate_motivation_insights(
        self, session: CoachingSession
    ) -> List[CoachingInsight]:
        """Génère des insights motivationnels."""

        insights = []

        # Motivation basée sur le progrès
        actions_count = len(session.user_actions_taken)

        if actions_count >= 5:
            insights.append(
                CoachingInsight(
                    id=f"motivation_progress_{int(time.time())}",
                    context=session.current_context,
                    title="🎉 Vous progressez magnifiquement !",
                    message=f"Déjà {actions_count} actions réalisées ! Votre reconversion prend forme. Continuez, vous êtes sur la bonne voie !",
                    tone=CoachingTone.MOTIVANT,
                    urgency=UrgencyLevel.INFO,
                    suggested_actions=[
                        "Continuer sur cette lancée",
                        "Partager vos progrès",
                    ],
                    quick_wins=["Célébrer cette étape", "Fixer le prochain objectif"],
                    personalization_factors=["progress_made", "encouragement"],
                    confidence_score=0.9,
                    created_at=datetime.now(),
                    expires_at=datetime.now() + timedelta(minutes=45),
                )
            )

        # Motivation contextuelle reconversion
        if session.user_profile.get("is_reconversion", True):
            insights.append(
                CoachingInsight(
                    id=f"motivation_reconversion_{int(time.time())}",
                    context=session.current_context,
                    title="💪 La reconversion, votre force !",
                    message="Votre parcours atypique est un ATOUT ! Les recruteurs cherchent des profils riches d'expériences diverses. Vous avez tout pour réussir !",
                    tone=CoachingTone.MENTOR,
                    urgency=UrgencyLevel.INFO,
                    suggested_actions=[
                        "Valoriser votre parcours",
                        "Identifier vos compétences transférables",
                    ],
                    quick_wins=[
                        "Lister 3 forces de votre parcours",
                        "Préparer votre storytelling",
                    ],
                    personalization_factors=["reconversion", "confidence_building"],
                    confidence_score=0.85,
                    created_at=datetime.now(),
                    expires_at=datetime.now() + timedelta(hours=3),
                )
            )

        return insights

    def _generate_ecosystem_insights(
        self, session: CoachingSession, current_action: str
    ) -> List[CoachingInsight]:
        """Suggestions de navigation dans l'écosystème Phoenix."""

        insights = []

        # Après génération CV, suggérer lettre
        if current_action == "cv_generated_successfully":
            insights.append(
                CoachingInsight(
                    id=f"ecosystem_letter_{int(time.time())}",
                    context=session.current_context,
                    title="📝 Complétez avec Phoenix Letters !",
                    message="CV parfait créé ! Pour une candidature complète, créez maintenant votre lettre de motivation personnalisée avec Phoenix Letters.",
                    tone=CoachingTone.EXPERT,
                    urgency=UrgencyLevel.IMPORTANT,
                    suggested_actions=[
                        "Créer ma lettre maintenant",
                        "Découvrir Phoenix Letters",
                    ],
                    quick_wins=[
                        "Cliquer sur Phoenix Letters",
                        "Transférer mes données",
                    ],
                    personalization_factors=["cv_completed", "ecosystem_flow"],
                    confidence_score=0.95,
                    created_at=datetime.now(),
                    expires_at=datetime.now() + timedelta(hours=4),
                )
            )

        # Si utilisateur hésite, suggérer trajectory
        if "hesitation" in str(session.insights_given):
            insights.append(
                CoachingInsight(
                    id=f"ecosystem_trajectory_{int(time.time())}",
                    context=session.current_context,
                    title="🗺️ Besoin de clarté ? Utilisez le Trajectory Builder !",
                    message="Vous semblez chercher votre direction. Notre AI Trajectory Builder vous créera un plan de reconversion étape par étape !",
                    tone=CoachingTone.BIENVEILLANT,
                    urgency=UrgencyLevel.SUGGESTION,
                    suggested_actions=[
                        "Découvrir Trajectory Builder",
                        "Planifier ma reconversion",
                    ],
                    quick_wins=["Voir une démo", "Commencer l'analyse"],
                    personalization_factors=["needs_guidance", "trajectory_needed"],
                    confidence_score=0.8,
                    created_at=datetime.now(),
                    expires_at=datetime.now() + timedelta(hours=2),
                )
            )

        return insights

    def _prioritize_insights(
        self, insights: List[CoachingInsight], session: CoachingSession
    ) -> List[CoachingInsight]:
        """Priorise et filtre les insights selon les préférences utilisateur."""

        if not insights:
            return []

        # Filtrage des insights expirés
        valid_insights = [
            insight for insight in insights if datetime.now() < insight.expires_at
        ]

        # Tri par urgence puis par score de confiance
        urgency_priority = {
            UrgencyLevel.CRITICAL: 5,
            UrgencyLevel.URGENT: 4,
            UrgencyLevel.IMPORTANT: 3,
            UrgencyLevel.SUGGESTION: 2,
            UrgencyLevel.INFO: 1,
        }

        valid_insights.sort(
            key=lambda x: (urgency_priority.get(x.urgency, 0), x.confidence_score),
            reverse=True,
        )

        # Limite à 3 insights max pour éviter l'overload
        return valid_insights[:3]

    def _create_fallback_insight(self, session: CoachingSession) -> CoachingInsight:
        """Insight de fallback en cas d'erreur."""

        return CoachingInsight(
            id=f"fallback_{int(time.time())}",
            context=session.current_context,
            title="💡 Je suis là pour vous aider !",
            message="Besoin d'aide ou d'un conseil ? N'hésitez pas, je suis votre coach personnel pour réussir votre reconversion !",
            tone=CoachingTone.BIENVEILLANT,
            urgency=UrgencyLevel.INFO,
            suggested_actions=["Poser une question", "Continuer votre parcours"],
            quick_wins=["Naviguer dans l'app", "Découvrir les fonctionnalités"],
            personalization_factors=["general_support"],
            confidence_score=0.7,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=1),
        )

    def _update_success_metrics(
        self, session: CoachingSession, action: str, result: Dict[str, Any]
    ):
        """Met à jour les métriques de succès."""

        success_actions = [
            "cv_generated",
            "form_completed",
            "letter_created",
            "trajectory_built",
            "interview_scheduled",
        ]

        if action in success_actions:
            session.success_metrics[action] = session.success_metrics.get(action, 0) + 1

    def _learn_user_patterns(
        self, session: CoachingSession, action: str, result: Dict[str, Any]
    ):
        """Apprentissage des patterns utilisateur."""

        if not session.response_patterns:
            session.response_patterns = {}

        # Apprentissage des préférences de tonalité
        if result and result.get("insight_helpful"):
            last_insight = (
                session.insights_given[-1] if session.insights_given else None
            )
            if last_insight:
                session.preferred_tone = last_insight.tone

    def _learn_from_feedback(
        self, session: CoachingSession, insight_id: str, feedback: str
    ):
        """Apprentissage à partir du feedback utilisateur."""

        # Logique d'apprentissage pour personnalisation future
        if feedback == "helpful":
            # Renforcer ce type d'insight
            pass
        elif feedback == "not_helpful":
            # Réduire ce type d'insight
            pass

    def _load_coaching_knowledge(self) -> Dict[str, Any]:
        """Charge la base de connaissances du coaching."""

        return {
            "reconversion_tips": {
                "tech": [
                    "Créez un portfolio visible",
                    "Participez à des projets open source",
                    "Obtenez des certifications reconnues",
                ],
                "commercial": [
                    "Quantifiez tous vos résultats",
                    "Développez votre réseau professionnel",
                    "Maîtrisez les outils CRM",
                ],
            },
            "motivation_phrases": [
                "Votre parcours unique est votre force !",
                "Chaque expert était un débutant un jour",
                "La reconversion est un acte de courage",
            ],
        }


# Instance globale
smart_coach = SmartCoach()
