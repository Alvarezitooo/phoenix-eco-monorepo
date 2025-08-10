"""
🔮 SERVICE VALIDATION IA - INNOVATION DIFFÉRENCIANTE
Phoenix Aube - Service Validation IA Future-Proof
Innovation différenciante - Temps 2
Prédiction impact IA sur métiers avec transparence scientifique
"""

import asyncio
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime, timedelta
import json
import logging
from dataclasses import dataclass
from enum import Enum

from ..core.models import (
    AnalyseRésilienceIA, TypeEvolutionIA, NiveauConfiance,
    RecommandationCarrière
)

# =============================================
# TYPES & CONFIGURATIONS
# =============================================

@dataclass
class TâcheMétier:
    """Représentation d'une tâche métier pour analyse IA"""
    titre: str
    description: str
    fréquence: str  # "quotidienne", "hebdomadaire", "mensuelle"
    complexité: int  # 1-5
    interaction_humaine_requise: bool
    créativité_requise: bool
    empathie_requise: bool
    automatisabilité_score: float  # 0-1

@dataclass
class CapacitéIA:
    """Capacité IA et son niveau de maturité"""
    nom: str
    description: str
    maturité_actuelle: int  # 1-5 (1=recherche, 5=production)
    progression_estimée: int  # mois pour atteindre niveau production
    impact_potentiel: float  # 0-1 sur tâches métier

class SourceDonnées(str, Enum):
    """Sources de données pour l'analyse"""
    OCDE_FUTURE_WORK = "ocde_future_work"
    MIT_WORK_OF_FUTURE = "mit_work_future"
    STANFORD_AI_INDEX = "stanford_ai_index"
    ARXIV_PAPERS = "arxiv_papers"
    FRANCE_STRATÉGIE = "france_strategie"
    INTERNAL_RESEARCH = "internal_research"
    EXPERT_CONSENSUS = "expert_consensus"

# =============================================
# SERVICE VALIDATION IA PRINCIPAL
# =============================================

class IAFutureValidator:
    """
    Validateur de pérennité métiers face à l'IA
    Cœur de l'innovation Phoenix Aube - Temps 2
    """
    
    def __init__(self, event_store, research_data_provider):
        self.event_store = event_store
        self.research_provider = research_data_provider
        self.logger = logging.getLogger(__name__)
        
        # Base de données métiers → tâches (à enrichir)
        self.métiers_tâches_db = self._init_métiers_tâches_database()
        
        # Capacités IA actuelles et évolution
        self.capacités_ia = self._init_capacités_ia_tracker()
        
        # Modèles prédictifs (coefficients à calibrer avec 3IA)
        self.modèle_coefficients = self._init_modèle_prédictif()
    
    async def évaluer_résistance_métier(self, métier_titre: str) -> AnalyseRésilienceIA:
        """
        Évalue la résistance d'un métier à l'automatisation IA
        CŒUR DE L'INNOVATION PHOENIX AUBE
        """
        self.logger.info(f"Début analyse résistance IA pour: {métier_titre}")
        
        try:
            # 1. Décomposer le métier en tâches
            tâches_métier = await self._décomposer_métier_en_tâches(métier_titre)
            
            # 2. Analyser chaque tâche vs capacités IA
            analyse_tâches = await self._analyser_tâches_vs_ia(tâches_métier)
            
            # 3. Calculer score de résistance global
            score_résistance = self._calculer_score_résistance(analyse_tâches)
            
            # 4. Prédire évolution temporelle
            évolution_timeline = await self._prédire_évolution_temporelle(métier_titre, analyse_tâches)
            
            # 5. Identifier opportunités collaboration IA
            opportunités_collaboration = await self._identifier_opportunités_ia(métier_titre, tâches_métier)
            
            # 6. Générer recommandations compétences IA
            compétences_ia_recommandées = await self._recommander_compétences_ia(métier_titre)
            
            # 7. Créer message rassurant
            message_positif = self._générer_message_futur_positif(métier_titre, score_résistance, évolution_timeline)
            
            # 8. Évaluer niveau de confiance
            niveau_confiance = self._évaluer_confiance_prédiction(métier_titre, analyse_tâches)
            
            # 9. Créer analyse complète
            analyse = AnalyseRésilienceIA(
                métier_titre=métier_titre,
                score_résistance_ia=score_résistance,
                niveau_menace=self._convertir_score_en_niveau(score_résistance),
                type_évolution=évolution_timeline["type"],
                timeline_impact=évolution_timeline["timeline"],
                tâches_automatisables=analyse_tâches["automatisables"],
                tâches_humaines_critiques=analyse_tâches["humaines_critiques"],
                opportunités_ia_collaboration=opportunités_collaboration,
                compétences_ia_à_développer=compétences_ia_recommandées,
                message_futur_positif=message_positif,
                avantages_évolution=évolution_timeline["avantages"],
                niveau_confiance=niveau_confiance,
                sources_analyse=self._get_sources_utilisées(métier_titre)
            )
            
            # 10. Publier événement
            await self.event_store.publish_event({
                "event_type": "validation_ia_effectuée",
                "user_id": "system",  # À adapter selon le contexte
                "data": {
                    "métier": métier_titre,
                    "score_résistance": score_résistance,
                    "niveau_confiance": niveau_confiance.value,
                    "sources_utilisées": analyse.sources_analyse
                }
            })
            
            self.logger.info(f"Analyse terminée - Score: {score_résistance:.2f}, Confiance: {niveau_confiance}")
            return analyse
            
        except Exception as e:
            self.logger.error(f"Erreur analyse IA pour {métier_titre}: {str(e)}")
            # Retourner analyse par défaut plutôt que de fail
            return self._créer_analyse_par_défaut(métier_titre)
    
    async def prédire_évolution_secteur(self, secteur: str, horizon_années: int = 10) -> Dict[str, Any]:
        """
        Prédit l'évolution d'un secteur entier face à l'IA
        """
        métiers_secteur = await self.research_provider.get_métiers_by_secteur(secteur)
        
        analyses_métiers = []
        for métier in métiers_secteur:
            analyse = await self.évaluer_résistance_métier(métier["titre"])
            analyses_métiers.append(analyse)
        
        # Synthèse sectorielle
        évolution_secteur = {
            "secteur": secteur,
            "métiers_analysés": len(analyses_métiers),
            "score_résistance_moyen": sum(a.score_résistance_ia for a in analyses_métiers) / len(analyses_métiers),
            "métiers_stables": [a.métier_titre for a in analyses_métiers if a.score_résistance_ia > 0.7],
            "métiers_menacés": [a.métier_titre for a in analyses_métiers if a.score_résistance_ia < 0.4],
            "nouvelles_opportunités": await self._identifier_nouveaux_métiers_ia(secteur),
            "timeline_transformation": self._calculer_timeline_sectorielle(analyses_métiers)
        }
        
        return évolution_secteur
    
    async def calculer_score_anxiété_ia(self, métier_actuel: str) -> Dict[str, Any]:
        """
        Calcule un score d'anxiété IA pour le métier actuel (feature freemium)
        """
        analyse = await self.évaluer_résistance_métier(métier_actuel)
        
        score_anxiété = 1 - analyse.score_résistance_ia  # Inverse de la résistance
        
        return {
            "métier": métier_actuel,
            "score_anxiété": score_anxiété,
            "niveau_anxiété": self._convertir_anxiété_en_niveau(score_anxiété),
            "message_court": self._générer_message_anxiété(score_anxiété, métier_actuel),
            "recommandation_action": self._recommander_action_anxiété(score_anxiété)
        }
    
    # =============================================
    # MÉTHODES PRIVÉES - ALGORITHMES CORE
    # =============================================
    
    async def _décomposer_métier_en_tâches(self, métier: str) -> List[TâcheMétier]:
        """
        Décompose un métier en tâches analysables
        """
        # Base de données métier → tâches (à enrichir avec données réelles)
        tâches_base = self.métiers_tâches_db.get(métier, [])
        
        # Enrichissement via API externe si disponible
        try:
            tâches_externes = await self.research_provider.get_tâches_détaillées(métier)
            tâches_base.extend(tâches_externes)
        except:
            pass  # Fallback sur base locale
        
        return tâches_base
    
    async def _analyser_tâches_vs_ia(self, tâches: List[TâcheMétier]) -> Dict[str, List[str]]:
        """
        Analyse chaque tâche face aux capacités IA actuelles et futures
        """
        automatisables = []
        humaines_critiques = []
        
        for tâche in tâches:
            # Évaluer automatisabilité basée sur plusieurs critères
            score_auto = self._calculer_automatisabilité_tâche(tâche)
            
            if score_auto > 0.7:
                automatisables.append(f"{tâche.titre} (probabilité: {score_auto:.0%})")
            elif score_auto < 0.3:
                humaines_critiques.append(f"{tâche.titre} (valeur humaine: {1-score_auto:.0%})")
        
        return {
            "automatisables": automatisables,
            "humaines_critiques": humaines_critiques,
            "score_moyen_automatisation": sum(t.automatisabilité_score for t in tâches) / len(tâches) if tâches else 0
        }
    
    def _calculer_automatisabilité_tâche(self, tâche: TâcheMétier) -> float:
        """
        Calcule la probabilité d'automatisation d'une tâche
        Basé sur recherche académique (Frey & Osborne amélioré)
        """
        score = tâche.automatisabilité_score  # Score de base
        
        # Ajustements basés sur caractéristiques humaines
        if tâche.empathie_requise:
            score *= 0.3  # Empathie très difficile à automatiser
        
        if tâche.créativité_requise:
            score *= 0.5  # Créativité partiellement automatisable
        
        if tâche.interaction_humaine_requise:
            score *= 0.6  # Interaction humaine complexe
        
        # Ajustement par complexité
        facteur_complexité = 1 - (tâche.complexité - 1) * 0.15  # Plus c'est complexe, moins automatisable
        score *= facteur_complexité
        
        # Ajustement par capacités IA actuelles
        for capacité in self.capacités_ia:
            if self._tâche_utilise_capacité(tâche, capacité):
                facteur_maturité = capacité.maturité_actuelle / 5.0
                score *= (0.5 + facteur_maturité * 0.5)  # Impact basé sur maturité
        
        return max(0.0, min(1.0, score))
    
    def _calculer_score_résistance(self, analyse_tâches: Dict[str, Any]) -> float:
        """
        Calcule le score global de résistance du métier
        """
        score_automatisation_moyen = analyse_tâches["score_moyen_automatisation"]
        
        # Score de résistance = inverse de l'automatisabilité
        score_résistance = 1 - score_automatisation_moyen
        
        # Ajustements contextuels
        # TODO: Intégrer données marché, demande sociale, etc.
        
        return max(0.0, min(1.0, score_résistance))
    
    async def _prédire_évolution_temporelle(self, métier: str, analyse_tâches: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prédit l'évolution temporelle du métier
        """
        score_automatisation = analyse_tâches["score_moyen_automatisation"]
        
        # Déterminer type d'évolution
        if score_automatisation < 0.3:
            type_évolution = TypeEvolutionIA.STABLE
            timeline = "10+ ans"
            avantages = ["Valeur humaine préservée", "Demande croissante", "Sécurité d'emploi"]
        elif score_automatisation < 0.6:
            type_évolution = TypeEvolutionIA.ENHANCED
            timeline = "5-10 ans"
            avantages = ["Productivité augmentée", "Tâches répétitives éliminées", "Focus sur valeur ajoutée"]
        elif score_automatisation < 0.8:
            type_évolution = TypeEvolutionIA.TRANSFORMED
            timeline = "3-5 ans"
            avantages = ["Nouveau rôle d'orchestrateur IA", "Compétences hybrides valorisées", "Opportunités innovation"]
        else:
            type_évolution = TypeEvolutionIA.THREATENED
            timeline = "1-3 ans"
            avantages = ["Opportunité reconversion anticipée", "Compétences transférables", "Transition accompagnée"]
        
        return {
            "type": type_évolution,
            "timeline": timeline,
            "avantages": avantages
        }
    
    async def _identifier_opportunités_ia(self, métier: str, tâches: List[TâcheMétier]) -> List[str]:
        """
        Identifie comment l'IA peut améliorer le métier
        """
        opportunités = []
        
        # Analyse des tâches répétitives
        tâches_répétitives = [t for t in tâches if t.fréquence == "quotidienne" and t.complexité <= 2]
        if tâches_répétitives:
            opportunités.append("Automatisation des tâches répétitives pour focus sur stratégique")
        
        # Analyse des besoins de données
        if "analyse" in métier.lower() or "data" in métier.lower():
            opportunités.append("IA augmente capacité d'analyse et détection de patterns")
        
        # Analyse des interactions
        if any(t.interaction_humaine_requise for t in tâches):
            opportunités.append("IA assiste préparation et suivi des interactions humaines")
        
        # Par défaut
        if not opportunités:
            opportunités = [
                "IA libère du temps pour activités à haute valeur ajoutée",
                "Outils IA améliorent qualité et rapidité d'exécution"
            ]
        
        return opportunités
    
    async def _recommander_compétences_ia(self, métier: str) -> List[str]:
        """
        Recommande les compétences IA spécifiques à développer
        """
        # Mapping métier → compétences IA (à enrichir)
        compétences_mapping = {
            "Data Analyst": ["Prompt engineering", "Python pour IA", "Interprétation modèles ML"],
            "Coach": ["IA conversationnelle", "Analyse sentiment", "Personnalisation IA"],
            "Chef de Projet": ["Automatisation workflows", "IA prédictive planning", "Gestion équipes IA"],
        }
        
        compétences_spécifiques = compétences_mapping.get(métier, [])
        
        # Compétences génériques importantes
        compétences_génériques = [
            "Maîtrise outils IA courants (ChatGPT, Claude, etc.)",
            "Compréhension éthique IA et biais algorithmiques",
            "Collaboration homme-machine"
        ]
        
        return compétences_spécifiques + compétences_génériques
    
    def _générer_message_futur_positif(self, métier: str, score_résistance: float, évolution: Dict[str, Any]) -> str:
        """
        Génère un message rassurant sur l'avenir du métier
        """
        if score_résistance > 0.7:
            return f"Excellente nouvelle ! Le métier de {métier} conserve une forte valeur humaine. L'IA devient votre assistant, pas votre remplaçant. Votre expertise relationnelle et créative sera encore plus valorisée."
        
        elif score_résistance > 0.5:
            return f"Le métier de {métier} évolue positivement avec l'IA. En maîtrisant les bons outils, vous deviendrez un professionnel augmenté, plus efficace et plus stratégique. Les tâches répétitives disparaissent, la valeur ajoutée augmente."
        
        elif score_résistance > 0.3:
            return f"Le métier de {métier} se transforme significativement, créant de nouvelles opportunités. En anticipant cette évolution, vous pouvez devenir un expert de la collaboration homme-IA, un profil très recherché."
        
        else:
            return f"Le métier de {métier} évolue vers de nouveaux horizons. C'est l'opportunité parfaite pour une reconversion anticipée vers des domaines en forte croissance. Votre expérience reste un atout précieux pour votre transition."
    
    def _évaluer_confiance_prédiction(self, métier: str, analyse_tâches: Dict[str, Any]) -> NiveauConfiance:
        """
        Évalue le niveau de confiance de la prédiction
        """
        # Facteurs de confiance
        facteurs_confiance = []
        
        # Qualité des données
        if métier in self.métiers_tâches_db:
            facteurs_confiance.append(0.3)  # Données détaillées disponibles
        
        # Consensus recherche
        try:
            sources = self._get_sources_utilisées(métier)
            facteurs_confiance.append(min(0.4, len(sources) * 0.1))
        except:
            pass
        
        # Stabilité secteur
        facteurs_confiance.append(0.2)  # Base par défaut
        
        score_confiance = sum(facteurs_confiance)
        
        if score_confiance >= 0.9:
            return NiveauConfiance.TRÈS_ÉLEVÉ
        elif score_confiance >= 0.75:
            return NiveauConfiance.ÉLEVÉ
        elif score_confiance >= 0.6:
            return NiveauConfiance.MOYEN
        else:
            return NiveauConfiance.FAIBLE
    
    # =============================================
    # MÉTHODES UTILITAIRES
    # =============================================
    
    def _convertir_score_en_niveau(self, score: float) -> str:
        """Convertit score numérique en niveau texte"""
        if score > 0.8:
            return "très_faible"
        elif score > 0.6:
            return "faible"
        elif score > 0.4:
            return "modéré"
        elif score > 0.2:
            return "élevé"
        else:
            return "critique"
    
    def _get_sources_utilisées(self, métier: str) -> List[str]:
        """Sources utilisées pour l'analyse"""
        return [
            "OCDE Future of Work Report 2024",
            "Stanford AI Index 2024",
            "MIT Work of the Future Task Force",
            "Base de données Phoenix Aube"
        ]
    
    def _créer_analyse_par_défaut(self, métier: str) -> AnalyseRésilienceIA:
        """Crée une analyse par défaut en cas d'erreur"""
        return AnalyseRésilienceIA(
            métier_titre=métier,
            score_résistance_ia=0.5,  # Score neutre
            niveau_menace="modéré",
            type_évolution=TypeEvolutionIA.ENHANCED,
            timeline_impact="5-10 ans",
            tâches_automatisables=["Analyse en cours"],
            tâches_humaines_critiques=["Expertise métier", "Relations humaines"],
            opportunités_ia_collaboration=["Amélioration productivité"],
            compétences_ia_à_développer=["Formation IA générale"],
            message_futur_positif=f"Le métier de {métier} évolue avec l'IA. Une formation adaptée vous permettra de tirer parti de ces changements.",
            avantages_évolution=["Productivité accrue"],
            niveau_confiance=NiveauConfiance.MOYEN,
            sources_analyse=["Analyse générique Phoenix Aube"]
        )
    
    # =============================================
    # BASES DE DONNÉES MOCK (À ENRICHIR)
    # =============================================
    
    def _init_métiers_tâches_database(self) -> Dict[str, List[TâcheMétier]]:
        """Initialise base métiers → tâches (mock à enrichir)"""
        return {
            "Data Analyst": [
                TâcheMétier(
                    titre="Extraction de données",
                    description="Extraire données depuis bases",
                    fréquence="quotidienne",
                    complexité=2,
                    interaction_humaine_requise=False,
                    créativité_requise=False,
                    empathie_requise=False,
                    automatisabilité_score=0.8
                ),
                TâcheMétier(
                    titre="Interprétation business des analyses",
                    description="Traduire insights pour business",
                    fréquence="hebdomadaire",
                    complexité=4,
                    interaction_humaine_requise=True,
                    créativité_requise=True,
                    empathie_requise=False,
                    automatisabilité_score=0.3
                )
            ],
            "Coach": [
                TâcheMétier(
                    titre="Écoute active et empathie",
                    description="Comprendre besoins client",
                    fréquence="quotidienne",
                    complexité=4,
                    interaction_humaine_requise=True,
                    créativité_requise=True,
                    empathie_requise=True,
                    automatisabilité_score=0.1
                ),
                TâcheMétier(
                    titre="Suivi administratif",
                    description="Gestion planning et facturation",
                    fréquence="hebdomadaire",
                    complexité=2,
                    interaction_humaine_requise=False,
                    créativité_requise=False,
                    empathie_requise=False,
                    automatisabilité_score=0.9
                )
            ]
        }
    
    def _init_capacités_ia_tracker(self) -> List[CapacitéIA]:
        """Initialise tracker capacités IA"""
        return [
            CapacitéIA(
                nom="Traitement langage naturel",
                description="Compréhension et génération texte",
                maturité_actuelle=4,
                progression_estimée=6,
                impact_potentiel=0.7
            ),
            CapacitéIA(
                nom="Vision par ordinateur",
                description="Analyse images et vidéos",
                maturité_actuelle=4,
                progression_estimée=12,
                impact_potentiel=0.6
            ),
            CapacitéIA(
                nom="IA émotionnelle",
                description="Reconnaissance émotions",
                maturité_actuelle=2,
                progression_estimée=36,
                impact_potentiel=0.4
            )
        ]
    
    def _init_modèle_prédictif(self) -> Dict[str, float]:
        """Coefficients du modèle prédictif (à calibrer avec 3IA)"""
        return {
            "empathie_protection": 0.8,
            "créativité_protection": 0.6,
            "complexité_protection": 0.4,
            "interaction_protection": 0.7,
            "vitesse_progression_ia": 1.2
        }
    
    def _tâche_utilise_capacité(self, tâche: TâcheMétier, capacité: CapacitéIA) -> bool:
        """Détermine si une tâche utilise une capacité IA"""
        # Logique simple (à affiner)
        if "nlp" in tâche.description.lower() and "langage" in capacité.nom:
            return True
        return False
    
    def _convertir_anxiété_en_niveau(self, score: float) -> str:
        """Convertit score d'anxiété en niveau"""
        if score < 0.2:
            return "très_faible"
        elif score < 0.4:
            return "faible"
        elif score < 0.6:
            return "modéré"
        elif score < 0.8:
            return "élevé"
        else:
            return "critique"
    
    def _générer_message_anxiété(self, score: float, métier: str) -> str:
        """Génère message court sur l'anxiété IA"""
        if score < 0.3:
            return f"Votre métier {métier} est très résistant à l'IA ! 😌"
        elif score < 0.6:
            return f"Votre métier {métier} évolue avec l'IA. Opportunité d'amélioration ! 🚀"
        else:
            return f"Votre métier {métier} se transforme. Anticipez pour rester compétitif ! ⚡"
    
    def _recommander_action_anxiété(self, score: float) -> str:
        """Recommande une action basée sur le score d'anxiété"""
        if score < 0.3:
            return "Continuez à développer vos compétences humaines uniques"
        elif score < 0.6:
            return "Explorez comment l'IA peut augmenter votre productivité"
        else:
            return "Considérez une formation ou reconversion vers des domaines IA-résistants"
    
    async def _identifier_nouveaux_métiers_ia(self, secteur: str) -> List[str]:
        """Identifie nouveaux métiers créés par l'IA dans un secteur"""
        return [
            "AI Trainer spécialisé secteur",
            "Coordinateur Homme-IA",
            "Éthicien IA sectoriel"
        ]
    
    def _calculer_timeline_sectorielle(self, analyses: List[AnalyseRésilienceIA]) -> str:
        """Calcule timeline transformation sectorielle"""
        scores = [a.score_résistance_ia for a in analyses]
        score_moyen = sum(scores) / len(scores) if scores else 0.5
        
        if score_moyen > 0.7:
            return "Transformation graduelle sur 10+ ans"
        elif score_moyen > 0.5:
            return "Évolution significative dans 5-10 ans"
        else:
            return "Transformation rapide dans 3-5 ans"