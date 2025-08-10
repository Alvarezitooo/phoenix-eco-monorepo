"""
🔮 Phoenix Aube - Mock Providers for MVP Development
Providers simulés pour développement et tests
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import random
import logging

from ..core.models import ProfilExploration, RecommandationCarrière, AnalyseRésilienceIA
from ..core.events import ÉvénementPhoenixAube, PhoenixEcosystemBridge

logger = logging.getLogger(__name__)


# =============================================
# MOCK EVENT STORE
# =============================================

class MockEventStore:
    """Event Store simulé pour MVP"""
    
    def __init__(self):
        self.events: List[ÉvénementPhoenixAube] = []
        self.user_journeys: Dict[str, List[ÉvénementPhoenixAube]] = {}
    
    async def store_event(self, event: ÉvénementPhoenixAube) -> bool:
        """Stocke un événement (simulation)"""
        try:
            # Simuler delay réseau
            await asyncio.sleep(0.1)
            
            # Stocker événement
            self.events.append(event)
            
            # Indexer par user
            if event.user_id not in self.user_journeys:
                self.user_journeys[event.user_id] = []
            self.user_journeys[event.user_id].append(event)
            
            logger.info(f"Event stored: {event.event_type} for user {event.user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing event: {str(e)}")
            return False
    
    async def get_user_events(
        self, 
        user_id: str, 
        event_types: Optional[List[str]] = None
    ) -> List[ÉvénementPhoenixAube]:
        """Récupère événements utilisateur"""
        user_events = self.user_journeys.get(user_id, [])
        
        if event_types:
            user_events = [
                event for event in user_events 
                if event.event_type in event_types
            ]
        
        return sorted(user_events, key=lambda x: x.timestamp)
    
    async def get_user_journey_summary(self, user_id: str) -> Dict[str, Any]:
        """Résumé du parcours utilisateur"""
        events = await self.get_user_events(user_id)
        
        if not events:
            return {"user_id": user_id, "events_count": 0, "journey_status": "not_started"}
        
        # Analyser progression
        event_types = [event.event_type for event in events]
        
        journey_status = "started"
        if "recommandations_générées" in event_types:
            journey_status = "recommendations_received"
        if "validation_ia_effectuée" in event_types:
            journey_status = "ia_validation_completed"
        if "métier_choisi" in event_types:
            journey_status = "career_chosen"
        if "transition_écosystème" in event_types:
            journey_status = "ecosystem_transition"
        
        return {
            "user_id": user_id,
            "events_count": len(events),
            "journey_status": journey_status,
            "first_event": events[0].timestamp,
            "last_activity": events[-1].timestamp,
            "event_types": list(set(event_types))
        }


# =============================================
# MOCK RESEARCH PROVIDER (3IA)
# =============================================

class MockResearchProvider:
    """Provider de recherche 3IA simulé"""
    
    def __init__(self):
        self.job_database = {
            # Tech sector
            "Data Scientist": {
                "automation_risk": 0.35,
                "evolution_type": "enhanced",
                "timeline_years": "5-10 ans",
                "sector": "Tech",
                "key_human_skills": ["Interprétation business", "Storytelling données", "Éthique IA"],
                "automatable_tasks": ["Nettoyage données", "Modèles standardisés", "Rapports simples"],
                "future_opportunities": ["IA explicable", "AutoML supervision", "Gouvernance données"]
            },
            
            # Services sector
            "Coach": {
                "automation_risk": 0.15,
                "evolution_type": "resistant",
                "timeline_years": ">10 ans",
                "sector": "Services",
                "key_human_skills": ["Empathie", "Écoute active", "Intuition humaine"],
                "automatable_tasks": ["Planification basique", "Suivi KPI", "Reporting"],
                "future_opportunities": ["Coaching augmenté IA", "Analytics comportemental", "Personnalisation scale"]
            },
            
            "Chef de Projet": {
                "automation_risk": 0.45,
                "evolution_type": "transformed",
                "timeline_years": "3-7 ans",
                "sector": "Transversal",
                "key_human_skills": ["Leadership", "Négociation", "Vision stratégique"],
                "automatable_tasks": ["Planning automatique", "Reporting", "Suivi tâches"],
                "future_opportunities": ["PM augmenté", "Prédiction risques", "Optimisation ressources"]
            },
            
            # Creative sector
            "Designer UX": {
                "automation_risk": 0.30,
                "evolution_type": "enhanced",
                "timeline_years": "5-8 ans",
                "sector": "Créatif",
                "key_human_skills": ["Créativité", "Compréhension utilisateur", "Vision design"],
                "automatable_tasks": ["Wireframes basiques", "A/B testing", "Audit UX"],
                "future_opportunities": ["Design génératif", "UX prédictive", "Personnalisation masse"]
            },
            
            # Finance sector
            "Analyste Financier": {
                "automation_risk": 0.65,
                "evolution_type": "disrupted",
                "timeline_years": "2-5 ans",
                "sector": "Finance",
                "key_human_skills": ["Analyse complexe", "Conseil stratégique", "Gestion relation client"],
                "automatable_tasks": ["Calculs financiers", "Rapports standards", "Veille marché"],
                "future_opportunities": ["Finance prédictive", "Conseil augmenté", "Risk management IA"]
            }
        }
    
    async def analyze_job_automation_risk(self, job_title: str) -> Dict[str, Any]:
        """Analyse risque automation d'un métier"""
        await asyncio.sleep(0.2)  # Simuler appel API
        
        # Recherche exacte ou approximative
        job_data = self.job_database.get(job_title)
        
        if not job_data:
            # Fallback avec données génériques
            job_data = {
                "automation_risk": random.uniform(0.2, 0.7),
                "evolution_type": random.choice(["enhanced", "transformed", "resistant"]),
                "timeline_years": random.choice(["3-5 ans", "5-10 ans", ">10 ans"]),
                "sector": "Générique",
                "key_human_skills": ["Créativité", "Relations humaines", "Résolution complexe"],
                "automatable_tasks": ["Tâches répétitives", "Analyse simple", "Reporting"],
                "future_opportunities": ["Collaboration IA", "Augmentation capacités", "Nouveaux marchés"]
            }
        
        return {
            "job_title": job_title,
            "automation_data": job_data,
            "research_confidence": 0.85 if job_title in self.job_database else 0.6,
            "last_updated": datetime.now().isoformat()
        }
    
    async def get_sector_evolution_trends(self, sector: str) -> Dict[str, Any]:
        """Tendances évolution secteur"""
        await asyncio.sleep(0.3)
        
        sector_trends = {
            "Tech": {
                "growth_rate": 0.15,
                "ai_adoption_rate": 0.8,
                "job_creation": ["IA Ethics Officer", "Prompt Engineer", "AI Trainer"],
                "job_displacement": ["QA Manuel", "Analyste Junior", "Support Level 1"],
                "key_skills_future": ["IA Literacy", "Ethics", "Human-AI Collaboration"]
            },
            
            "Services": {
                "growth_rate": 0.08,
                "ai_adoption_rate": 0.4,
                "job_creation": ["Coach Digital", "Conseiller IA", "Experience Designer"],
                "job_displacement": ["Admin Standard", "Accueil Basique", "Support Simple"],
                "key_skills_future": ["Soft Skills", "Personnalisation", "Emotional Intelligence"]
            },
            
            "Finance": {
                "growth_rate": 0.05,
                "ai_adoption_rate": 0.7,
                "job_creation": ["Fintech Specialist", "Risk AI Analyst", "Robo-advisor Manager"],
                "job_displacement": ["Analyste Junior", "Comptable Standard", "Back Office"],
                "key_skills_future": ["Régulation IA", "Finance Complexe", "Client Advisory"]
            }
        }
        
        return {
            "sector": sector,
            "trends": sector_trends.get(sector, {
                "growth_rate": 0.06,
                "ai_adoption_rate": 0.5,
                "job_creation": ["Spécialiste IA Sectoriel"],
                "job_displacement": ["Tâches Routinières"],
                "key_skills_future": ["Adaptabilité", "IA Collaboration"]
            }),
            "forecast_horizon": "2025-2035"
        }


# =============================================
# MOCK RECOMMENDATION ENGINE
# =============================================

class MockRecommendationEngine:
    """Moteur de recommandation simulé"""
    
    def __init__(self):
        self.career_templates = [
            {
                "title": "Data Scientist",
                "base_compatibility": 0.85,
                "sector": "Tech",
                "required_traits": ["Openness", "Conscientiousness"],
                "riasec_match": ["Investigative", "Conventional"],
                "skills_needed": ["Python", "Statistics", "ML", "Communication"],
                "ia_resistance": 0.65
            },
            {
                "title": "Coach en Reconversion",
                "base_compatibility": 0.90,
                "sector": "Services",
                "required_traits": ["Agreeableness", "Extraversion"],
                "riasec_match": ["Social", "Enterprising"],
                "skills_needed": ["Écoute", "Empathie", "Méthodes coaching", "Psychology"],
                "ia_resistance": 0.85
            },
            {
                "title": "Chef de Projet Digital",
                "base_compatibility": 0.75,
                "sector": "Tech/Management",
                "required_traits": ["Conscientiousness", "Extraversion"],
                "riasec_match": ["Enterprising", "Conventional"],
                "skills_needed": ["Leadership", "Agile", "Communication", "Tech literacy"],
                "ia_resistance": 0.55
            },
            {
                "title": "Designer UX/UI",
                "base_compatibility": 0.80,
                "sector": "Créatif",
                "required_traits": ["Openness", "Conscientiousness"],
                "riasec_match": ["Artistic", "Investigative"],
                "skills_needed": ["Design thinking", "Prototyping", "User research", "Tools"],
                "ia_resistance": 0.70
            },
            {
                "title": "Consultant en Transformation",
                "base_compatibility": 0.78,
                "sector": "Consulting",
                "required_traits": ["Openness", "Conscientiousness", "Extraversion"],
                "riasec_match": ["Enterprising", "Investigative"],
                "skills_needed": ["Analyse", "Présentation", "Change management", "Industry knowledge"],
                "ia_resistance": 0.72
            }
        ]
    
    async def generate_recommendations(
        self, 
        user_profile: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Génère recommandations personnalisées"""
        await asyncio.sleep(0.5)  # Simuler calcul
        
        # Extraire données profil
        big_five = user_profile.get("big_five", {})
        riasec = user_profile.get("riasec", {})
        constraints = user_profile.get("constraints", {})
        
        recommendations = []
        
        for career in self.career_templates:
            # Calculer score de compatibilité
            compatibility_score = career["base_compatibility"]
            
            # Ajuster selon Big Five (simulation)
            if big_five:
                trait_bonus = 0
                for trait in career["required_traits"]:
                    if trait.lower() in [t.lower() for t in big_five.keys()]:
                        trait_bonus += 0.05
                compatibility_score = min(1.0, compatibility_score + trait_bonus)
            
            # Ajuster selon RIASEC
            if riasec:
                riasec_bonus = 0
                for interest in career["riasec_match"]:
                    if interest in riasec:
                        riasec_bonus += 0.03
                compatibility_score = min(1.0, compatibility_score + riasec_bonus)
            
            # Appliquer contraintes (simulation basique)
            if constraints:
                if constraints.get("salary_min") and career["sector"] == "Services":
                    compatibility_score -= 0.1  # Services souvent moins payés
            
            # Ajouter variance réaliste
            compatibility_score += random.uniform(-0.05, 0.05)
            compatibility_score = max(0.1, min(1.0, compatibility_score))
            
            recommendations.append({
                "title": career["title"],
                "compatibility_score": round(compatibility_score, 2),
                "sector": career["sector"],
                "ia_resistance_score": career["ia_resistance"],
                "required_skills": career["skills_needed"],
                "justification": self._generate_justification(career, compatibility_score),
                "training_recommendations": self._generate_training_recs(career),
                "salary_range": self._estimate_salary_range(career["sector"])
            })
        
        # Trier par compatibilité et retourner top 5
        recommendations.sort(key=lambda x: x["compatibility_score"], reverse=True)
        return recommendations[:5]
    
    def _generate_justification(self, career: Dict, score: float) -> str:
        """Génère justification personnalisée"""
        justifications = [
            f"Excellente correspondance avec votre profil ({score:.0%})",
            f"Vos compétences s'alignent parfaitement avec {career['title']}",
            f"Secteur {career['sector']} en forte croissance et correspondance élevée",
            f"Métier résistant à l'IA ({career['ia_resistance']:.0%}) et adapté à vos traits"
        ]
        return random.choice(justifications)
    
    def _generate_training_recs(self, career: Dict) -> List[str]:
        """Génère recommandations formation"""
        all_training = {
            "Data Scientist": ["Formation ML/AI", "Certification Python", "Stats avancées"],
            "Coach en Reconversion": ["Certification coaching", "PNL", "Psychologie positive"],
            "Chef de Projet Digital": ["Certification Agile", "Leadership", "Digital transformation"],
            "Designer UX/UI": ["UX certification", "Design tools", "User research methods"],
            "Consultant en Transformation": ["Change management", "Industry expertise", "Consulting skills"]
        }
        return all_training.get(career["title"], ["Formation métier", "Soft skills", "Certification"])
    
    def _estimate_salary_range(self, sector: str) -> str:
        """Estimation fourchette salariale"""
        ranges = {
            "Tech": "45-70k€",
            "Services": "35-55k€",
            "Consulting": "50-80k€",
            "Créatif": "35-60k€",
            "Finance": "45-85k€"
        }
        return ranges.get(sector, "40-65k€")


# =============================================
# MOCK GEMINI CLIENT
# =============================================

class MockGeminiClient:
    """Client Gemini simulé pour développement"""
    
    async def analyze_job_resilience(self, job_title: str, context: Dict = None) -> Dict[str, Any]:
        """Analyse IA resilience avec prompts optimisés"""
        await asyncio.sleep(1.0)  # Simuler appel API
        
        # Base de données mock des analyses
        mock_analyses = {
            "Data Scientist": {
                "score_résistance_ia": 0.65,
                "niveau_menace": "modérée",
                "type_évolution": "enhanced",
                "timeline_impact": "5-10 ans",
                "message_futur_positif": "L'IA augmente vos capacités d'analyse ! Vous devenez le chef d'orchestre des algorithmes.",
                "tâches_automatisables": [
                    "Nettoyage de données (80%)",
                    "Modèles prédictifs simples (70%)",
                    "Rapports standardisés (85%)"
                ],
                "tâches_humaines_critiques": [
                    "Interprétation business (90%)",
                    "Éthique et biais IA (95%)",
                    "Storytelling données (85%)"
                ],
                "opportunités_ia_collaboration": [
                    "AutoML pour prototypage rapide",
                    "IA explicable pour transparence",
                    "Augmentation créativité analyse"
                ],
                "compétences_ia_à_développer": [
                    "Prompt engineering",
                    "MLOps et gouvernance IA",
                    "Éthique et fairness",
                    "IA explicable"
                ]
            }
        }
        
        # Utiliser données mock ou générer aléatoirement
        if job_title in mock_analyses:
            return mock_analyses[job_title]
        
        # Génération procédurale pour métiers non définis
        resistance_score = random.uniform(0.3, 0.9)
        
        return {
            "score_résistance_ia": round(resistance_score, 2),
            "niveau_menace": "faible" if resistance_score > 0.7 else "modérée" if resistance_score > 0.4 else "élevée",
            "type_évolution": random.choice(["enhanced", "transformed", "resistant"]),
            "timeline_impact": random.choice(["3-5 ans", "5-10 ans", ">10 ans"]),
            "message_futur_positif": f"Le métier de {job_title} évolue positivement avec l'IA. Nouvelles opportunités à saisir !",
            "tâches_automatisables": [
                "Tâches administratives (70%)",
                "Calculs répétitifs (80%)",
                "Reporting basique (75%)"
            ],
            "tâches_humaines_critiques": [
                "Relations humaines (90%)",
                "Décisions complexes (85%)",
                "Créativité stratégique (80%)"
            ],
            "opportunités_ia_collaboration": [
                "Automatisation tâches routinières",
                "Analyse augmentée",
                "Personnalisation scale"
            ],
            "compétences_ia_à_développer": [
                "IA literacy",
                "Collaboration human-AI",
                "Éthique numérique"
            ]
        }
    
    async def calculate_anxiety_score(self, current_job: str) -> Dict[str, Any]:
        """Calcul score anxiété IA"""
        await asyncio.sleep(0.5)
        
        # Scores d'anxiété par métier (simulation)
        anxiety_scores = {
            "Comptable": 0.8,
            "Traducteur": 0.7,
            "Analyste Junior": 0.75,
            "Téléconseiller": 0.85,
            "Data Scientist": 0.35,
            "Coach": 0.2,
            "Médecin": 0.15,
            "Enseignant": 0.3,
            "Designer": 0.4
        }
        
        score = anxiety_scores.get(current_job, random.uniform(0.2, 0.7))
        
        # Déterminer niveau et message
        if score < 0.3:
            level = "faible"
            message = f"Excellente nouvelle ! Votre métier {current_job} évolue positivement avec l'IA. 🚀"
            recommendation = "Explorez comment l'IA peut augmenter votre productivité"
        elif score < 0.6:
            level = "modéré"
            message = f"Votre métier {current_job} se transforme avec l'IA. Opportunité d'évolution ! ⚡"
            recommendation = "Développez des compétences complémentaires à l'IA"
        else:
            level = "élevé"
            message = f"Votre métier {current_job} nécessite une adaptation proactive face à l'IA. 🎯"
            recommendation = "Envisagez une reconversion ou une spécialisation"
        
        return {
            "métier": current_job,
            "score_anxiété": round(score, 2),
            "niveau_anxiété": level,
            "message_court": message,
            "recommandation_action": recommendation,
            "confiance_analyse": 0.85
        }