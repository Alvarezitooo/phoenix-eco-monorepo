"""
🎯 Mirror Match Engine - IA Synergique CV/Offre/Lettre
Algorithme avancé de correspondance et optimisation Phoenix

Author: Claude Phoenix DevSecOps Guardian
Version: 1.0.0 - Revolutionary Matching System
"""

import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List

# Imports conditionnels
try:
    from phoenix_cv.services.enhanced_gemini_client import get_enhanced_gemini_client
    from phoenix_cv.utils.exceptions import SecurityException
    from phoenix_cv.utils.secure_logging import secure_logger
except ImportError:
    import logging

    class MockSecureLogger:
        def log_security_event(self, event_type, data, level="INFO"):
            logging.info(f"MIRROR_MATCH | {event_type}: {data}")

    class SecurityException(Exception):
        pass

    def get_enhanced_gemini_client():
        return None

    secure_logger = MockSecureLogger()


class MatchType(Enum):
    """Types de correspondance Mirror Match"""

    CV_TO_JOB = "cv_to_job"
    LETTER_TO_JOB = "letter_to_job"
    CV_TO_LETTER = "cv_to_letter"
    SYNERGIC_FULL = "synergic_full"


class SkillCategory(Enum):
    """Catégories de compétences"""

    TECHNICAL = "technical"
    SOFT_SKILLS = "soft_skills"
    LEADERSHIP = "leadership"
    DOMAIN_SPECIFIC = "domain_specific"
    TRANSFERABLE = "transferable"


@dataclass
class MatchScore:
    """Score de correspondance détaillé"""

    overall_score: float  # Score global 0-100
    technical_match: float
    soft_skills_match: float
    experience_match: float
    keywords_match: float
    ats_compatibility: float
    reconversion_potential: float
    confidence_level: float

    def to_dict(self) -> Dict[str, float]:
        return {
            "overall_score": round(self.overall_score, 2),
            "technical_match": round(self.technical_match, 2),
            "soft_skills_match": round(self.soft_skills_match, 2),
            "experience_match": round(self.experience_match, 2),
            "keywords_match": round(self.keywords_match, 2),
            "ats_compatibility": round(self.ats_compatibility, 2),
            "reconversion_potential": round(self.reconversion_potential, 2),
            "confidence_level": round(self.confidence_level, 2),
        }


@dataclass
class OptimizationSuggestion:
    """Suggestion d'optimisation"""

    category: str
    priority: str  # high, medium, low
    suggestion: str
    impact_estimate: float  # Amélioration estimée en points
    examples: List[str]


@dataclass
class MirrorMatchResult:
    """Résultat complet du Mirror Match"""

    match_type: MatchType
    score: MatchScore
    missing_keywords: List[str]
    strong_points: List[str]
    optimization_suggestions: List[OptimizationSuggestion]
    synergy_opportunities: List[str]
    ats_recommendations: List[str]
    reconversion_insights: List[str]
    generated_at: datetime


class MirrorMatchEngine:
    """
    Moteur IA de correspondance synergique pour l'écosystème Phoenix.
    Analyse et optimise la cohérence CV/Offre/Lettre.
    """

    def __init__(self):
        self.gemini_client = get_enhanced_gemini_client()

        # Dictionnaires de compétences par secteur
        self.skill_mappings = self._load_skill_mappings()
        self.keyword_weights = self._load_keyword_weights()
        self.reconversion_patterns = self._load_reconversion_patterns()

        secure_logger.log_security_event("MIRROR_MATCH_ENGINE_INITIALIZED", {})

    def analyze_cv_job_match(
        self, cv_content: str, job_description: str, user_context: Dict[str, Any] = None
    ) -> MirrorMatchResult:
        """
        Lance l'analyse complète de correspondance CV/Offre d'emploi.
        """
        try:
            # Extraction des données structurées
            cv_data = self._extract_cv_data(cv_content)
            job_data = self._extract_job_data(job_description)

            # Calcul des scores de correspondance
            score = self._calculate_match_score(cv_data, job_data, user_context)

            # Analyse des points forts
            strong_points = self._identify_strong_points(cv_data, job_data)

            # Mots-clés manquants critiques
            missing_keywords = self._find_missing_keywords(cv_data, job_data)

            # Suggestions d'optimisation
            suggestions = self._generate_optimization_suggestions(
                cv_data, job_data, score
            )

            # Recommandations ATS
            ats_recommendations = self._generate_ats_recommendations(cv_data, job_data)

            # Insights reconversion
            reconversion_insights = self._analyze_reconversion_potential(
                cv_data, job_data, user_context
            )

            # Opportunités de synergie (pour lettres)
            synergy_opportunities = self._identify_synergy_opportunities(
                cv_data, job_data
            )

            result = MirrorMatchResult(
                match_type=MatchType.CV_TO_JOB,
                score=score,
                missing_keywords=missing_keywords,
                strong_points=strong_points,
                optimization_suggestions=suggestions,
                synergy_opportunities=synergy_opportunities,
                ats_recommendations=ats_recommendations,
                reconversion_insights=reconversion_insights,
                generated_at=datetime.now(),
            )

            secure_logger.log_security_event(
                "MIRROR_MATCH_ANALYSIS_COMPLETED",
                {"score": score.overall_score, "match_type": MatchType.CV_TO_JOB.value},
            )

            return result

        except Exception as e:
            secure_logger.log_security_event(
                "MIRROR_MATCH_ANALYSIS_ERROR", {"error": str(e)[:200]}, "ERROR"
            )
            return self._create_fallback_result(MatchType.CV_TO_JOB)

    def analyze_synergic_full_match(
        self,
        cv_content: str,
        letter_content: str,
        job_description: str,
        user_context: Dict[str, Any] = None,
    ) -> MirrorMatchResult:
        """
        Analyse synergique complète CV + Lettre + Offre d'emploi.
        Le Saint Graal de l'optimisation candidature !
        """
        try:
            # Extraction des données
            cv_data = self._extract_cv_data(cv_content)
            letter_data = self._extract_letter_data(letter_content)
            job_data = self._extract_job_data(job_description)

            # Score synergique avancé
            score = self._calculate_synergic_score(
                cv_data, letter_data, job_data, user_context
            )

            # Analyse de cohérence CV/Lettre
            coherence_analysis = self._analyze_cv_letter_coherence(cv_data, letter_data)

            # Points forts unifiés
            strong_points = self._identify_synergic_strong_points(
                cv_data, letter_data, job_data
            )

            # Mots-clés manquants globaux
            missing_keywords = self._find_synergic_missing_keywords(
                cv_data, letter_data, job_data
            )

            # Suggestions d'optimisation synergiques
            suggestions = self._generate_synergic_suggestions(
                cv_data, letter_data, job_data, score
            )

            # Opportunités de synergie renforcées
            synergy_opportunities = self._identify_advanced_synergy_opportunities(
                cv_data, letter_data, job_data
            )

            # Recommandations ATS globales
            ats_recommendations = self._generate_synergic_ats_recommendations(
                cv_data, letter_data, job_data
            )

            # Insights reconversion avancés
            reconversion_insights = self._analyze_advanced_reconversion_potential(
                cv_data, letter_data, job_data, user_context
            )

            result = MirrorMatchResult(
                match_type=MatchType.SYNERGIC_FULL,
                score=score,
                missing_keywords=missing_keywords,
                strong_points=strong_points + coherence_analysis,
                optimization_suggestions=suggestions,
                synergy_opportunities=synergy_opportunities,
                ats_recommendations=ats_recommendations,
                reconversion_insights=reconversion_insights,
                generated_at=datetime.now(),
            )

            secure_logger.log_security_event(
                "SYNERGIC_MIRROR_MATCH_COMPLETED",
                {
                    "score": score.overall_score,
                    "coherence_bonus": score.confidence_level,
                },
            )

            return result

        except Exception as e:
            secure_logger.log_security_event(
                "SYNERGIC_MIRROR_MATCH_ERROR", {"error": str(e)[:200]}, "ERROR"
            )
            return self._create_fallback_result(MatchType.SYNERGIC_FULL)

    def _extract_cv_data(self, cv_content: str) -> Dict[str, Any]:
        """Extraction intelligente des données du CV"""
        data = {
            "skills": [],
            "experience_years": 0,
            "education": [],
            "certifications": [],
            "keywords": [],
            "soft_skills": [],
            "technical_skills": [],
            "achievements": [],
            "sectors": [],
        }

        cv_lower = cv_content.lower()

        # Extraction des compétences techniques
        technical_patterns = [
            "python",
            "javascript",
            "react",
            "nodejs",
            "sql",
            "excel",
            "powerbi",
            "photoshop",
            "illustrator",
            "figma",
            "sketch",
            "marketing digital",
            "seo",
            "sem",
            "google analytics",
            "facebook ads",
            "gestion de projet",
            "scrum",
            "agile",
            "jira",
            "confluence",
        ]

        for skill in technical_patterns:
            if skill in cv_lower:
                data["technical_skills"].append(skill)

        # Extraction des soft skills
        soft_skills_patterns = [
            "leadership",
            "communication",
            "gestion d'équipe",
            "autonomie",
            "créativité",
            "adaptabilité",
            "résolution de problèmes",
            "esprit d'équipe",
            "négociation",
            "présentation",
            "organisation",
            "rigueur",
        ]

        for skill in soft_skills_patterns:
            if skill in cv_lower:
                data["soft_skills"].append(skill)

        # Extraction années d'expérience
        experience_matches = re.findall(r"(\d+)\s*(?:ans?|années?)", cv_lower)
        if experience_matches:
            data["experience_years"] = max(int(match) for match in experience_matches)

        # Extraction des réalisations quantifiées
        achievement_patterns = [
            r"(\d+)%",
            r"(\d+)\s*k€",
            r"(\d+)\s*€",
            r"(\d+)\s*personnes?",
            r"(\d+)\s*équipes?",
            r"(\d+)\s*projets?",
        ]

        for pattern in achievement_patterns:
            matches = re.findall(pattern, cv_content)
            data["achievements"].extend(matches)

        # Extraction des secteurs/domaines
        sector_patterns = [
            "commerce",
            "marketing",
            "finance",
            "informatique",
            "développement",
            "design",
            "ressources humaines",
            "gestion",
            "vente",
            "communication",
            "éducation",
            "santé",
            "industrie",
            "logistique",
        ]

        for sector in sector_patterns:
            if sector in cv_lower:
                data["sectors"].append(sector)

        # Compilation de tous les mots-clés
        data["keywords"] = (
            data["technical_skills"] + data["soft_skills"] + data["sectors"]
        )
        data["skills"] = data["keywords"]

        return data

    def _extract_job_data(self, job_description: str) -> Dict[str, Any]:
        """Extraction intelligente des données de l'offre d'emploi"""
        data = {
            "required_skills": [],
            "preferred_skills": [],
            "experience_required": 0,
            "keywords": [],
            "sector": "",
            "job_title": "",
            "company_size": "",
            "requirements": [],
            "responsibilities": [],
        }

        job_lower = job_description.lower()

        # Extraction titre du poste
        title_patterns = [
            r"poste\s*:\s*([^\n]+)",
            r"titre\s*:\s*([^\n]+)",
            r"recherche\s+(?:un|une)\s+([^\n]+)",
        ]

        for pattern in title_patterns:
            match = re.search(pattern, job_lower)
            if match:
                data["job_title"] = match.group(1).strip()
                break

        # Extraction des compétences requises
        required_patterns = [
            "requis",
            "obligatoire",
            "indispensable",
            "nécessaire",
            "maîtrise",
            "connaissance",
            "expérience en",
        ]

        # Même logique que pour le CV mais adaptée aux offres
        technical_skills = [
            "python",
            "javascript",
            "react",
            "nodejs",
            "sql",
            "excel",
            "powerbi",
            "photoshop",
            "illustrator",
            "figma",
            "marketing digital",
            "seo",
            "sem",
            "google analytics",
            "gestion de projet",
            "scrum",
            "agile",
        ]

        for skill in technical_skills:
            if skill in job_lower:
                # Déterminer si c'est requis ou préféré selon le contexte
                context_window = 100
                skill_pos = job_lower.find(skill)
                context = job_lower[
                    max(0, skill_pos - context_window) : skill_pos + context_window
                ]

                if any(req_pattern in context for req_pattern in required_patterns):
                    data["required_skills"].append(skill)
                else:
                    data["preferred_skills"].append(skill)

        # Extraction années d'expérience requises
        exp_patterns = [
            r"(\d+)\s*(?:ans?|années?)\s*(?:d\'expérience|minimum)",
            r"minimum\s*(\d+)\s*(?:ans?|années?)",
            r"expérience\s*:\s*(\d+)\s*(?:ans?|années?)",
        ]

        for pattern in exp_patterns:
            match = re.search(pattern, job_lower)
            if match:
                data["experience_required"] = int(match.group(1))
                break

        # Compilation des mots-clés
        data["keywords"] = data["required_skills"] + data["preferred_skills"]

        return data

    def _extract_letter_data(self, letter_content: str) -> Dict[str, Any]:
        """Extraction des données de la lettre de motivation"""
        data = {
            "mentioned_skills": [],
            "company_research": [],
            "motivation_points": [],
            "keywords": [],
            "tone_analysis": "",
            "personalization_level": 0,
        }

        letter_lower = letter_content.lower()

        # Extraction des compétences mentionnées
        skill_patterns = [
            "compétence",
            "expérience",
            "maîtrise",
            "capacité",
            "expertise",
            "savoir-faire",
            "connaissance",
        ]

        # Analyse du niveau de personnalisation
        personalization_indicators = [
            "votre entreprise",
            "votre société",
            "votre équipe",
            "vos valeurs",
            "vos projets",
            "votre mission",
        ]

        personalization_count = sum(
            1 for indicator in personalization_indicators if indicator in letter_lower
        )
        data["personalization_level"] = min(personalization_count * 20, 100)

        # Extraction des points de motivation
        motivation_patterns = [
            r"motivé(?:e)?\s+par\s+([^.]+)",
            r"intéressé(?:e)?\s+par\s+([^.]+)",
            r"passionné(?:e)?\s+(?:par|de)\s+([^.]+)",
        ]

        for pattern in motivation_patterns:
            matches = re.findall(pattern, letter_lower)
            data["motivation_points"].extend(matches)

        return data

    def _calculate_match_score(
        self,
        cv_data: Dict[str, Any],
        job_data: Dict[str, Any],
        user_context: Dict[str, Any] = None,
    ) -> MatchScore:
        """Calcul du score de correspondance CV/Offre"""

        # Score technique (30%)
        technical_match = self._calculate_technical_match(cv_data, job_data)

        # Score soft skills (20%)
        soft_skills_match = self._calculate_soft_skills_match(cv_data, job_data)

        # Score expérience (20%)
        experience_match = self._calculate_experience_match(cv_data, job_data)

        # Score mots-clés (15%)
        keywords_match = self._calculate_keywords_match(cv_data, job_data)

        # Score ATS (10%)
        ats_compatibility = self._calculate_ats_compatibility(cv_data, job_data)

        # Potentiel reconversion (5%)
        reconversion_potential = self._calculate_reconversion_potential(
            cv_data, job_data, user_context
        )

        # Score global pondéré
        overall_score = (
            technical_match * 0.30
            + soft_skills_match * 0.20
            + experience_match * 0.20
            + keywords_match * 0.15
            + ats_compatibility * 0.10
            + reconversion_potential * 0.05
        )

        # Niveau de confiance basé sur la qualité des données
        confidence_level = self._calculate_confidence_level(cv_data, job_data)

        return MatchScore(
            overall_score=overall_score,
            technical_match=technical_match,
            soft_skills_match=soft_skills_match,
            experience_match=experience_match,
            keywords_match=keywords_match,
            ats_compatibility=ats_compatibility,
            reconversion_potential=reconversion_potential,
            confidence_level=confidence_level,
        )

    def _calculate_synergic_score(
        self,
        cv_data: Dict[str, Any],
        letter_data: Dict[str, Any],
        job_data: Dict[str, Any],
        user_context: Dict[str, Any] = None,
    ) -> MatchScore:
        """Calcul du score synergique CV + Lettre + Offre"""

        # Score de base CV/Offre
        base_score = self._calculate_match_score(cv_data, job_data, user_context)

        # Bonus de cohérence CV/Lettre (jusqu'à +15 points)
        coherence_bonus = self._calculate_cv_letter_coherence(cv_data, letter_data)

        # Bonus de personnalisation lettre (jusqu'à +10 points)
        personalization_bonus = letter_data.get("personalization_level", 0) * 0.1

        # Score synergique final
        synergic_overall = min(
            base_score.overall_score + coherence_bonus + personalization_bonus, 100
        )

        return MatchScore(
            overall_score=synergic_overall,
            technical_match=base_score.technical_match,
            soft_skills_match=base_score.soft_skills_match,
            experience_match=base_score.experience_match,
            keywords_match=base_score.keywords_match,
            ats_compatibility=base_score.ats_compatibility,
            reconversion_potential=base_score.reconversion_potential,
            confidence_level=min(
                base_score.confidence_level + coherence_bonus * 0.5, 95
            ),
        )

    def _calculate_technical_match(
        self, cv_data: Dict[str, Any], job_data: Dict[str, Any]
    ) -> float:
        """Calcul du score de correspondance technique"""
        cv_technical = set(cv_data.get("technical_skills", []))
        job_required = set(job_data.get("required_skills", []))
        job_preferred = set(job_data.get("preferred_skills", []))

        if not job_required and not job_preferred:
            return 70.0  # Score neutre si pas d'infos

        # Correspondance avec les compétences requises (poids 70%)
        required_match = len(cv_technical & job_required) / max(len(job_required), 1)

        # Correspondance avec les compétences préférées (poids 30%)
        preferred_match = len(cv_technical & job_preferred) / max(len(job_preferred), 1)

        return min((required_match * 70 + preferred_match * 30), 100.0)

    def _calculate_soft_skills_match(
        self, cv_data: Dict[str, Any], job_data: Dict[str, Any]
    ) -> float:
        """Calcul du score de correspondance soft skills"""
        cv_soft = set(cv_data.get("soft_skills", []))
        job_keywords = set(job_data.get("keywords", []))

        # Soft skills standards valorisés
        standard_soft_skills = {
            "communication",
            "leadership",
            "autonomie",
            "adaptabilité",
            "esprit d'équipe",
            "organisation",
            "créativité",
        }

        cv_standard = cv_soft & standard_soft_skills
        match_ratio = len(cv_standard) / len(standard_soft_skills)

        return min(match_ratio * 100 + 20, 100.0)  # Bonus de base de 20 points

    def _calculate_experience_match(
        self, cv_data: Dict[str, Any], job_data: Dict[str, Any]
    ) -> float:
        """Calcul du score de correspondance d'expérience"""
        cv_years = cv_data.get("experience_years", 0)
        required_years = job_data.get("experience_required", 0)

        if required_years == 0:
            return 80.0  # Score neutre

        if cv_years >= required_years:
            # Bonus pour expérience supérieure, mais plafonné
            excess = min((cv_years - required_years) / required_years, 0.5)
            return min(90 + excess * 10, 100.0)
        else:
            # Pénalité progressive pour expérience insuffisante
            deficit = (required_years - cv_years) / required_years
            return max(90 - deficit * 60, 20.0)

    def _calculate_keywords_match(
        self, cv_data: Dict[str, Any], job_data: Dict[str, Any]
    ) -> float:
        """Calcul du score de correspondance des mots-clés"""
        cv_keywords = set(word.lower() for word in cv_data.get("keywords", []))
        job_keywords = set(word.lower() for word in job_data.get("keywords", []))

        if not job_keywords:
            return 75.0

        intersection = cv_keywords & job_keywords
        union = cv_keywords | job_keywords

        # Score Jaccard pondéré
        jaccard = len(intersection) / len(union) if union else 0
        coverage = len(intersection) / len(job_keywords) if job_keywords else 0

        return min((jaccard * 40 + coverage * 60), 100.0)

    def _calculate_ats_compatibility(
        self, cv_data: Dict[str, Any], job_data: Dict[str, Any]
    ) -> float:
        """Calcul du score de compatibilité ATS"""
        score = 70.0  # Score de base

        # Bonus pour mots-clés techniques présents
        if len(cv_data.get("technical_skills", [])) >= 3:
            score += 10

        # Bonus pour réalisations quantifiées
        if len(cv_data.get("achievements", [])) >= 2:
            score += 10

        # Bonus pour correspondance de secteur
        cv_sectors = set(cv_data.get("sectors", []))
        if cv_sectors:
            score += 10

        return min(score, 100.0)

    def _calculate_reconversion_potential(
        self,
        cv_data: Dict[str, Any],
        job_data: Dict[str, Any],
        user_context: Dict[str, Any] = None,
    ) -> float:
        """Calcul du potentiel de reconversion"""
        score = 60.0  # Score de base pour reconversion

        # Bonus pour compétences transférables
        transferable_skills = [
            "gestion de projet",
            "communication",
            "leadership",
            "analyse",
        ]
        cv_transferable = [
            skill for skill in cv_data.get("skills", []) if skill in transferable_skills
        ]

        if len(cv_transferable) >= 2:
            score += 20

        # Bonus pour diversité d'expérience (reconversion)
        if len(cv_data.get("sectors", [])) >= 2:
            score += 15

        # Contexte utilisateur (si fourni)
        if user_context and user_context.get("is_reconversion"):
            score += 5  # Bonus contexte reconversion

        return min(score, 100.0)

    def _calculate_confidence_level(
        self, cv_data: Dict[str, Any], job_data: Dict[str, Any]
    ) -> float:
        """Calcul du niveau de confiance de l'analyse"""
        confidence = 50.0

        # Bonus pour richesse des données CV
        if len(cv_data.get("skills", [])) >= 5:
            confidence += 15
        if len(cv_data.get("achievements", [])) >= 1:
            confidence += 10
        if cv_data.get("experience_years", 0) > 0:
            confidence += 10

        # Bonus pour richesse des données offre
        if len(job_data.get("required_skills", [])) >= 3:
            confidence += 10
        if job_data.get("experience_required", 0) > 0:
            confidence += 5

        return min(confidence, 95.0)

    def _calculate_cv_letter_coherence(
        self, cv_data: Dict[str, Any], letter_data: Dict[str, Any]
    ) -> float:
        """Calcul de la cohérence entre CV et lettre"""
        coherence_score = 0.0

        # Correspondance des compétences mentionnées
        cv_skills = set(cv_data.get("skills", []))
        letter_skills = set(letter_data.get("mentioned_skills", []))

        if cv_skills and letter_skills:
            skill_overlap = len(cv_skills & letter_skills) / len(
                cv_skills | letter_skills
            )
            coherence_score += skill_overlap * 10

        # Bonus pour personnalisation élevée
        personalization = letter_data.get("personalization_level", 0)
        if personalization >= 60:
            coherence_score += 5

        return min(coherence_score, 15.0)

    def _find_missing_keywords(
        self, cv_data: Dict[str, Any], job_data: Dict[str, Any]
    ) -> List[str]:
        """Identifie les mots-clés manquants critiques"""
        cv_keywords = set(word.lower() for word in cv_data.get("keywords", []))
        job_required = set(word.lower() for word in job_data.get("required_skills", []))
        job_preferred = set(
            word.lower() for word in job_data.get("preferred_skills", [])
        )

        # Mots-clés manquants requis (priorité haute)
        missing_required = job_required - cv_keywords

        # Mots-clés manquants préférés (priorité moyenne)
        missing_preferred = job_preferred - cv_keywords

        # Retourner les plus importants en premier
        return list(missing_required)[:5] + list(missing_preferred)[:3]

    def _identify_strong_points(
        self, cv_data: Dict[str, Any], job_data: Dict[str, Any]
    ) -> List[str]:
        """Identifie les points forts de la candidature"""
        strong_points = []

        cv_skills = set(cv_data.get("technical_skills", []))
        job_required = set(job_data.get("required_skills", []))

        # Compétences techniques matchées
        matched_skills = cv_skills & job_required
        if matched_skills:
            strong_points.append(
                f"✅ Compétences techniques alignées: {', '.join(list(matched_skills)[:3])}"
            )

        # Expérience adéquate
        cv_years = cv_data.get("experience_years", 0)
        required_years = job_data.get("experience_required", 0)
        if cv_years >= required_years and required_years > 0:
            strong_points.append(
                f"✅ Expérience suffisante: {cv_years} ans (requis: {required_years})"
            )

        # Réalisations quantifiées
        if len(cv_data.get("achievements", [])) >= 2:
            strong_points.append("✅ Résultats quantifiés démontrés")

        # Soft skills valorisées
        if len(cv_data.get("soft_skills", [])) >= 3:
            strong_points.append("✅ Excellentes soft skills démontrées")

        return strong_points[:5]

    def _generate_optimization_suggestions(
        self, cv_data: Dict[str, Any], job_data: Dict[str, Any], score: MatchScore
    ) -> List[OptimizationSuggestion]:
        """Génère des suggestions d'optimisation personnalisées"""
        suggestions = []

        # Suggestion pour mots-clés manquants
        missing_keywords = self._find_missing_keywords(cv_data, job_data)
        if missing_keywords:
            suggestions.append(
                OptimizationSuggestion(
                    category="Mots-clés",
                    priority="high",
                    suggestion=f"Intégrer les mots-clés manquants: {', '.join(missing_keywords[:3])}",
                    impact_estimate=15.0,
                    examples=[
                        f"Ajouter '{kw}' dans la section compétences"
                        for kw in missing_keywords[:2]
                    ],
                )
            )

        # Suggestion pour expérience
        if score.experience_match < 70:
            suggestions.append(
                OptimizationSuggestion(
                    category="Expérience",
                    priority="high",
                    suggestion="Mettre en avant vos expériences transférables",
                    impact_estimate=12.0,
                    examples=[
                        "Reformuler vos expériences pour souligner les aspects pertinents",
                        "Quantifier vos réalisations avec des chiffres précis",
                    ],
                )
            )

        # Suggestion pour soft skills
        if score.soft_skills_match < 80:
            suggestions.append(
                OptimizationSuggestion(
                    category="Soft Skills",
                    priority="medium",
                    suggestion="Enrichir vos soft skills démontrées",
                    impact_estimate=8.0,
                    examples=[
                        "Ajouter 'leadership' avec exemple concret",
                        "Mentionner votre 'adaptabilité' avec contexte",
                    ],
                )
            )

        # Suggestion ATS
        if score.ats_compatibility < 85:
            suggestions.append(
                OptimizationSuggestion(
                    category="Optimisation ATS",
                    priority="medium",
                    suggestion="Améliorer la compatibilité ATS",
                    impact_estimate=6.0,
                    examples=[
                        "Utiliser les mots-clés exacts de l'offre",
                        "Structurer clairement les sections",
                    ],
                )
            )

        return suggestions

    def _generate_ats_recommendations(
        self, cv_data: Dict[str, Any], job_data: Dict[str, Any]
    ) -> List[str]:
        """Génère des recommandations spécifiques ATS"""
        recommendations = []

        # Mots-clés critiques
        missing_keywords = self._find_missing_keywords(cv_data, job_data)
        if missing_keywords:
            recommendations.append(
                f"🎯 Intégrer naturellement: {', '.join(missing_keywords[:3])}"
            )

        # Structure
        recommendations.append(
            "📋 Utiliser des titres de sections standards (Expérience, Compétences, Formation)"
        )

        # Format
        recommendations.append("📄 Privilégier un format texte lisible par les ATS")

        # Densité de mots-clés
        cv_keyword_count = len(cv_data.get("keywords", []))
        if cv_keyword_count < 8:
            recommendations.append(
                "🔤 Augmenter la densité de mots-clés pertinents (objectif: 8-12)"
            )

        return recommendations

    def _analyze_reconversion_potential(
        self,
        cv_data: Dict[str, Any],
        job_data: Dict[str, Any],
        user_context: Dict[str, Any] = None,
    ) -> List[str]:
        """Analyse le potentiel de reconversion"""
        insights = []

        # Compétences transférables identifiées
        transferable = [
            "gestion de projet",
            "communication",
            "leadership",
            "analyse",
            "organisation",
        ]
        cv_transferable = [
            skill for skill in cv_data.get("skills", []) if skill in transferable
        ]

        if cv_transferable:
            insights.append(
                f"🔄 Compétences transférables fortes: {', '.join(cv_transferable)}"
            )

        # Diversité d'expérience (atout reconversion)
        sectors = cv_data.get("sectors", [])
        if len(sectors) >= 2:
            insights.append("🌟 Parcours diversifié = adaptabilité démontrée")

        # Conseils spécifiques reconversion
        insights.append("💡 Mettez en avant votre motivation pour le changement")
        insights.append(
            "🎯 Créez des liens explicites entre votre passé et votre futur poste"
        )

        # Formation continue (si détectée)
        if cv_data.get("certifications"):
            insights.append("📚 Formation continue = engagement dans votre évolution")

        return insights

    def _identify_synergy_opportunities(
        self, cv_data: Dict[str, Any], job_data: Dict[str, Any]
    ) -> List[str]:
        """Identifie les opportunités de synergie pour la lettre de motivation"""
        opportunities = []

        # Points à développer dans la lettre
        matched_skills = set(cv_data.get("technical_skills", [])) & set(
            job_data.get("required_skills", [])
        )
        if matched_skills:
            opportunities.append(
                f"📝 Détailler dans la lettre: {', '.join(list(matched_skills)[:2])}"
            )

        # Expérience à contextualiser
        if cv_data.get("experience_years", 0) > 0:
            opportunities.append(
                "🎯 Expliquer comment votre expérience s'applique au poste"
            )

        # Motivation reconversion
        opportunities.append(
            "💫 Articuler votre motivation pour ce changement de carrière"
        )

        # Valeur ajoutée unique
        opportunities.append(
            "⚡ Mettre en avant votre perspective unique grâce à votre parcours"
        )

        return opportunities

    def _load_skill_mappings(self) -> Dict[str, List[str]]:
        """Charge les mappings de compétences par secteur"""
        return {
            "tech": ["python", "javascript", "react", "nodejs", "sql", "git"],
            "marketing": [
                "seo",
                "sem",
                "google analytics",
                "facebook ads",
                "content marketing",
            ],
            "design": ["photoshop", "illustrator", "figma", "sketch", "ui/ux"],
            "management": [
                "gestion de projet",
                "scrum",
                "agile",
                "leadership",
                "coaching",
            ],
            "finance": [
                "excel",
                "powerbi",
                "analyse financière",
                "comptabilité",
                "contrôle de gestion",
            ],
        }

    def _load_keyword_weights(self) -> Dict[str, float]:
        """Charge les poids des mots-clés"""
        return {
            "python": 1.2,
            "leadership": 1.1,
            "gestion de projet": 1.3,
            "communication": 1.0,
            "excel": 0.9,
        }

    def _load_reconversion_patterns(self) -> Dict[str, List[str]]:
        """Charge les patterns de reconversion courants"""
        return {
            "vers_tech": [
                "formation développement",
                "bootcamp",
                "autoformation",
                "projets personnels",
            ],
            "vers_marketing": [
                "certification google",
                "formation digital",
                "freelance marketing",
            ],
            "vers_management": [
                "formation management",
                "leadership",
                "encadrement équipe",
            ],
        }

    def _create_fallback_result(self, match_type: MatchType) -> MirrorMatchResult:
        """Crée un résultat de fallback en cas d'erreur"""
        return MirrorMatchResult(
            match_type=match_type,
            score=MatchScore(
                overall_score=65.0,
                technical_match=60.0,
                soft_skills_match=70.0,
                experience_match=65.0,
                keywords_match=60.0,
                ats_compatibility=70.0,
                reconversion_potential=65.0,
                confidence_level=40.0,
            ),
            missing_keywords=["Données insuffisantes pour analyse précise"],
            strong_points=["Profil analysable", "Potentiel identifié"],
            optimization_suggestions=[
                OptimizationSuggestion(
                    category="Général",
                    priority="medium",
                    suggestion="Enrichir le CV avec plus de détails pour une analyse plus précise",
                    impact_estimate=10.0,
                    examples=[
                        "Ajouter plus de compétences spécifiques",
                        "Détailler les expériences",
                    ],
                )
            ],
            synergy_opportunities=["Développer la lettre de motivation"],
            ats_recommendations=["Optimiser le format et les mots-clés"],
            reconversion_insights=["Mettre en avant les compétences transférables"],
            generated_at=datetime.now(),
        )

    # Méthodes pour l'analyse synergique avancée (continuent...)
    def _analyze_cv_letter_coherence(
        self, cv_data: Dict[str, Any], letter_data: Dict[str, Any]
    ) -> List[str]:
        """Analyse la cohérence entre CV et lettre"""
        coherence_points = []

        # Vérification cohérence compétences
        cv_skills = set(cv_data.get("skills", []))
        letter_mentioned = set(letter_data.get("mentioned_skills", []))

        common_skills = cv_skills & letter_mentioned
        if common_skills:
            coherence_points.append(
                f"🔗 Cohérence CV/Lettre: {', '.join(list(common_skills)[:3])}"
            )

        # Niveau de personnalisation
        personalization = letter_data.get("personalization_level", 0)
        if personalization >= 80:
            coherence_points.append("⭐ Lettre hautement personnalisée")
        elif personalization >= 60:
            coherence_points.append("✅ Lettre bien personnalisée")
        else:
            coherence_points.append("⚠️ Lettre à personnaliser davantage")

        return coherence_points

    def _identify_synergic_strong_points(
        self,
        cv_data: Dict[str, Any],
        letter_data: Dict[str, Any],
        job_data: Dict[str, Any],
    ) -> List[str]:
        """Identifie les points forts synergiques"""
        strong_points = self._identify_strong_points(cv_data, job_data)

        # Ajout des points forts spécifiques à la synergie
        personalization = letter_data.get("personalization_level", 0)
        if personalization >= 70:
            strong_points.append("💫 Excellente synergie CV/Lettre personnalisée")

        motivation_count = len(letter_data.get("motivation_points", []))
        if motivation_count >= 2:
            strong_points.append("🎯 Motivation clairement articulée dans la lettre")

        return strong_points

    def _find_synergic_missing_keywords(
        self,
        cv_data: Dict[str, Any],
        letter_data: Dict[str, Any],
        job_data: Dict[str, Any],
    ) -> List[str]:
        """Trouve les mots-clés manquants dans l'ensemble CV+Lettre"""
        # Mots-clés présents dans CV ou lettre
        cv_keywords = set(word.lower() for word in cv_data.get("keywords", []))
        letter_keywords = set(word.lower() for word in letter_data.get("keywords", []))
        combined_keywords = cv_keywords | letter_keywords

        # Mots-clés requis dans l'offre
        job_required = set(word.lower() for word in job_data.get("required_skills", []))

        # Mots-clés manquants globalement
        missing_global = job_required - combined_keywords

        return list(missing_global)[:5]

    def _generate_synergic_suggestions(
        self,
        cv_data: Dict[str, Any],
        letter_data: Dict[str, Any],
        job_data: Dict[str, Any],
        score: MatchScore,
    ) -> List[OptimizationSuggestion]:
        """Génère des suggestions d'optimisation synergiques"""
        suggestions = self._generate_optimization_suggestions(cv_data, job_data, score)

        # Suggestions spécifiques à la synergie CV/Lettre
        personalization = letter_data.get("personalization_level", 0)
        if personalization < 60:
            suggestions.append(
                OptimizationSuggestion(
                    category="Synergie CV/Lettre",
                    priority="high",
                    suggestion="Améliorer la personnalisation de la lettre",
                    impact_estimate=10.0,
                    examples=[
                        "Mentionner des éléments spécifiques à l'entreprise",
                        "Faire référence aux projets de l'entreprise",
                    ],
                )
            )

        # Cohérence compétences
        cv_skills = set(cv_data.get("skills", []))
        letter_skills = set(letter_data.get("mentioned_skills", []))
        if len(cv_skills & letter_skills) < 2:
            suggestions.append(
                OptimizationSuggestion(
                    category="Cohérence",
                    priority="medium",
                    suggestion="Renforcer la cohérence entre CV et lettre",
                    impact_estimate=8.0,
                    examples=[
                        "Mentionner dans la lettre les compétences clés du CV",
                        "Aligner le vocabulaire technique",
                    ],
                )
            )

        return suggestions

    def _identify_advanced_synergy_opportunities(
        self,
        cv_data: Dict[str, Any],
        letter_data: Dict[str, Any],
        job_data: Dict[str, Any],
    ) -> List[str]:
        """Identifie les opportunités de synergie avancées"""
        opportunities = self._identify_synergy_opportunities(cv_data, job_data)

        # Opportunités spécifiques synergie avancée
        opportunities.append(
            "🔮 Créer un storytelling cohérent CV → Lettre → Entretien"
        )
        opportunities.append(
            "🎭 Adapter le ton de la lettre au niveau de formalité du poste"
        )
        opportunities.append(
            "🌟 Utiliser la lettre pour contextualiser les points forts du CV"
        )

        # Analyse de la personnalisation
        personalization = letter_data.get("personalization_level", 0)
        if personalization >= 70:
            opportunities.append(
                "💎 Exploiter votre recherche d'entreprise approfondie"
            )
        else:
            opportunities.append(
                "🔍 Approfondir la recherche sur l'entreprise pour la lettre"
            )

        return opportunities

    def _generate_synergic_ats_recommendations(
        self,
        cv_data: Dict[str, Any],
        letter_data: Dict[str, Any],
        job_data: Dict[str, Any],
    ) -> List[str]:
        """Génère des recommandations ATS synergiques"""
        recommendations = self._generate_ats_recommendations(cv_data, job_data)

        # Recommandations spécifiques synergie
        recommendations.append("🔄 Utiliser les mêmes mots-clés dans CV et lettre")
        recommendations.append(
            "📊 Répartir stratégiquement les mots-clés entre CV et lettre"
        )
        recommendations.append("🎯 Adapter la densité de mots-clés selon le document")

        return recommendations

    def _analyze_advanced_reconversion_potential(
        self,
        cv_data: Dict[str, Any],
        letter_data: Dict[str, Any],
        job_data: Dict[str, Any],
        user_context: Dict[str, Any] = None,
    ) -> List[str]:
        """Analyse avancée du potentiel de reconversion"""
        insights = self._analyze_reconversion_potential(cv_data, job_data, user_context)

        # Insights spécifiques à la synergie
        motivation_points = letter_data.get("motivation_points", [])
        if motivation_points:
            insights.append("🎯 Motivation pour la reconversion clairement exprimée")

        personalization = letter_data.get("personalization_level", 0)
        if personalization >= 70:
            insights.append("🔍 Recherche approfondie démontrée = engagement réel")

        # Conseils avancés reconversion
        insights.append(
            "🚀 Utilisez votre lettre pour raconter votre 'pourquoi' de reconversion"
        )
        insights.append(
            "💫 Transformez votre parcours atypique en avantage concurrentiel"
        )

        return insights


# Instance globale du moteur Mirror Match
mirror_match_engine = MirrorMatchEngine()
