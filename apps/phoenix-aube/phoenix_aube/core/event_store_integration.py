"""
Phoenix Aube - Event Store Integration
Intégration avec event store central écosystème Phoenix
"""

import asyncio
from typing import List, Dict, Optional, Any, Union
from datetime import datetime, timedelta
import json
import uuid
from dataclasses import asdict
import logging

from .models import ParcoursExploration, ProfilExploration
from .events import (
    ÉvénementPhoenixAube, ExplorationCommencée, ValeursExplorées,
    CompétencesRévélées, RecommandationsGénérées, ValidationIAEffectuée,
    MétierChoisi, TransitionÉcosystème, PhoenixEcosystemBridge
)

logger = logging.getLogger(__name__)

# =============================================
# EVENT STORE INTEGRATION
# =============================================

class PhoenixAubeEventStore:
    """
    Gestionnaire d'événements Phoenix Aube
    Intégration avec event store central de l'écosystème
    """
    
    def __init__(self, central_event_store=None, redis_client=None):
        self.central_store = central_event_store
        self.redis = redis_client  # Pour cache et performance
        self.ecosystem_bridge = PhoenixEcosystemBridge(self)
        
    async def publier_événement_exploration(
        self, 
        user_id: str, 
        type_événement: str, 
        données: Dict[str, Any],
        métadonnées: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Publie un événement d'exploration Phoenix Aube
        """
        # Créer événement formaté
        événement = ÉvénementPhoenixAube(
            user_id=user_id,
            event_type=type_événement,
            data=données,
            session_id=métadonnées.get("session_id") if métadonnées else None,
            user_agent=métadonnées.get("user_agent") if métadonnées else None
        )
        
        # Publier dans event store central
        if self.central_store:
            await self.central_store.publish(asdict(événement))
        else:
            # Mock pour développement
            logger.info(f"Event publié (mock): {type_événement} pour user {user_id}")
        
        # Cache pour performance
        if self.redis:
            await self._cacher_événement_utilisateur(user_id, événement)
        
        return événement.event_id
    
    async def récupérer_historique_utilisateur(
        self, 
        user_id: str, 
        limite: int = 100
    ) -> List[ÉvénementPhoenixAube]:
        """
        Récupère l'historique d'événements d'un utilisateur
        """
        # Essayer cache d'abord
        if self.redis:
            événements_cachés = await self._récupérer_cache_utilisateur(user_id)
            if événements_cachés:
                return événements_cachés[:limite]
        
        # Fallback sur event store
        if self.central_store:
            événements_raw = await self.central_store.get_events_by_user(
                user_id, source_app="phoenix_aube", limit=limite
            )
            
            # Convertir en objets typés
            événements = [
                ÉvénementPhoenixAube(**evt) for evt in événements_raw
            ]
        else:
            # Mock pour développement
            événements = self._generate_mock_user_history(user_id, limite)
        
        return événements
    
    async def créer_snapshot_parcours(
        self, 
        parcours: ParcoursExploration
    ) -> str:
        """
        Crée un snapshot du parcours complet
        """
        snapshot_data = {
            "parcours_id": parcours.parcours_id,
            "user_id": parcours.user_id,
            "statut": parcours.statut_completion,
            "nombre_recommandations": len(parcours.recommandations_métiers),
            "métier_choisi": parcours.métier_choisi,
            "scores_moyens": {
                "compatibilité": self._calculer_score_moyen_compatibilité(parcours),
                "résistance_ia": self._calculer_score_moyen_ia(parcours)
            },
            "timestamp_snapshot": datetime.now().isoformat()
        }
        
        # Publier événement snapshot
        await self.publier_événement_exploration(
            user_id=parcours.user_id,
            type_événement="snapshot_parcours_créé",
            données=snapshot_data
        )
        
        logger.info(f"Snapshot créé pour parcours {parcours.parcours_id}")
        return parcours.parcours_id
    
    async def déclencher_transitions_écosystème(
        self, 
        user_id: str, 
        app_cible: str, 
        contexte_transition: Dict[str, Any]
    ) -> str:
        """
        Déclenche les transitions vers autres apps Phoenix
        """
        transition = TransitionÉcosystème(
            user_id=user_id,
            data={
                "app_cible": app_cible,
                "contexte": contexte_transition,
                "timestamp_transition": datetime.now().isoformat(),
                "source_app": "phoenix_aube"
            }
        )
        
        # Publier événement de transition
        if self.central_store:
            await self.central_store.publish(asdict(transition))
        
        # Notifier app cible (message queue)
        await self._notifier_app_cible(app_cible, user_id, contexte_transition)
        
        logger.info(f"Transition déclenchée: {app_cible} pour user {user_id}")
        return transition.event_id
    
    async def obtenir_métriques_utilisation(
        self, 
        période_jours: int = 30
    ) -> Dict[str, Any]:
        """
        Obtient métriques d'utilisation Phoenix Aube
        """
        date_début = datetime.now() - timedelta(days=période_jours)
        
        if self.central_store:
            métriques = await self.central_store.get_metrics(
                source_app="phoenix_aube",
                start_date=date_début
            )
        else:
            # Mock métriques pour développement
            métriques = self._generate_mock_metrics()
        
        return {
            "parcours_commencés": métriques.get("exploration_commencée", 0),
            "parcours_complétés": métriques.get("métier_choisi", 0),
            "taux_completion": self._calculer_taux_completion(métriques),
            "transitions_écosystème": métriques.get("transition_écosystème", 0),
            "temps_moyen_parcours": métriques.get("temps_moyen_minutes", 45),
            "satisfaction_moyenne": métriques.get("satisfaction_moyenne", 4.2),
            "métiers_populaires": métriques.get("top_métiers", ["Data Scientist", "Coach", "Designer UX"])
        }
    
    async def tracer_parcours_utilisateur(
        self, 
        user_id: str
    ) -> Dict[str, Any]:
        """
        Trace le parcours complet d'un utilisateur
        """
        événements = await self.récupérer_historique_utilisateur(user_id)
        
        # Analyser progression
        progression = {
            "étapes_complétées": [],
            "temps_par_étape": {},
            "blocages_identifiés": [],
            "points_de_sortie": []
        }
        
        étapes_clés = [
            "exploration_commencée",
            "valeurs_explorées", 
            "compétences_révélées",
            "tests_psychométriques_complétés",
            "recommandations_générées",
            "validation_ia_effectuée",
            "métier_choisi",
            "transition_écosystème"
        ]
        
        événements_par_type = {evt.event_type: evt for evt in événements}
        
        for i, étape in enumerate(étapes_clés):
            if étape in événements_par_type:
                progression["étapes_complétées"].append(étape)
                
                # Calculer temps entre étapes
                if i > 0 and étapes_clés[i-1] in événements_par_type:
                    temps_écoulé = (
                        événements_par_type[étape].timestamp - 
                        événements_par_type[étapes_clés[i-1]].timestamp
                    ).total_seconds() / 60  # en minutes
                    progression["temps_par_étape"][étape] = temps_écoulé
            else:
                # Point de sortie potentiel
                if i > 0 and étapes_clés[i-1] in événements_par_type:
                    progression["points_de_sortie"].append(étapes_clés[i-1])
                break
        
        return {
            "user_id": user_id,
            "progression": progression,
            "événements_total": len(événements),
            "durée_totale_minutes": self._calculer_durée_totale(événements),
            "statut_actuel": self._déterminer_statut_actuel(progression["étapes_complétées"]),
            "recommandations_amélioration": self._générer_recommandations_ux(progression)
        }
    
    # =============================================
    # MÉTHODES PRIVÉES EVENT STORE
    # =============================================
    
    async def _cacher_événement_utilisateur(
        self, 
        user_id: str, 
        événement: ÉvénementPhoenixAube
    ) -> None:
        """Cache événement pour performance"""
        if not self.redis:
            return
        
        try:
            key = f"phoenix_aube:events:{user_id}"
            
            # Ajouter au début de la liste
            await self.redis.lpush(key, json.dumps(asdict(événement), default=str))
            
            # Garder seulement les 50 derniers
            await self.redis.ltrim(key, 0, 49)
            
            # Expiration 24h
            await self.redis.expire(key, 86400)
            
        except Exception as e:
            logger.warning(f"Erreur cache événement: {e}")
    
    async def _récupérer_cache_utilisateur(self, user_id: str) -> Optional[List[ÉvénementPhoenixAube]]:
        """Récupère événements depuis cache"""
        if not self.redis:
            return None
        
        try:
            key = f"phoenix_aube:events:{user_id}"
            événements_json = await self.redis.lrange(key, 0, -1)
            événements = [
                ÉvénementPhoenixAube(**json.loads(evt)) 
                for evt in événements_json
            ]
            return événements
        except Exception as e:
            logger.warning(f"Erreur récupération cache: {e}")
            return None
    
    async def _notifier_app_cible(
        self, 
        app_cible: str, 
        user_id: str, 
        contexte: Dict[str, Any]
    ) -> None:
        """Notifie l'app cible de la transition"""
        # Préparer transition selon app cible
        if app_cible == "phoenix_cv":
            await self.ecosystem_bridge.prepare_cv_transition(user_id, contexte.get("métier_choisi"), contexte)
        elif app_cible == "phoenix_letters":
            await self.ecosystem_bridge.prepare_letters_transition(user_id, contexte.get("métier_choisi"), contexte)
        elif app_cible == "phoenix_rise":
            await self.ecosystem_bridge.prepare_rise_transition(user_id, contexte.get("métier_choisi"), contexte)
        
        # Implémentation message queue (RabbitMQ, Redis Pub/Sub, etc.)
        message = {
            "type": "transition_phoenix_aube",
            "user_id": user_id,
            "source_app": "phoenix_aube",
            "target_app": app_cible,
            "context": contexte,
            "timestamp": datetime.now().isoformat()
        }
        
        # Publier dans queue spécifique à l'app
        queue_name = f"phoenix_{app_cible}_transitions"
        # await self.message_queue.publish(queue_name, message)
        
        # Log pour debug
        logger.info(f"Transition notifiée: {app_cible} pour user {user_id}")
    
    def _calculer_taux_completion(self, métriques: Dict[str, int]) -> float:
        """Calcule taux de completion des parcours"""
        commencés = métriques.get("exploration_commencée", 0)
        complétés = métriques.get("métier_choisi", 0)
        
        if commencés == 0:
            return 0.0
        
        return (complétés / commencés) * 100
    
    def _calculer_score_moyen_compatibilité(self, parcours: ParcoursExploration) -> float:
        """Calcule score moyen de compatibilité"""
        if not parcours.recommandations_métiers:
            return 0.0
        
        scores = [rec.score_compatibilité_global for rec in parcours.recommandations_métiers]
        return sum(scores) / len(scores)
    
    def _calculer_score_moyen_ia(self, parcours: ParcoursExploration) -> float:
        """Calcule score moyen résistance IA"""
        if not parcours.analyses_ia:
            return 0.0
        
        scores = [analyse.score_résistance_ia for analyse in parcours.analyses_ia]
        return sum(scores) / len(scores)
    
    def _generate_mock_user_history(self, user_id: str, limite: int) -> List[ÉvénementPhoenixAube]:
        """Génère historique mock pour développement"""
        événements = []
        
        # Simulation d'événements typiques
        types_événements = [
            "exploration_commencée",
            "valeurs_explorées",
            "tests_psychométriques_complétés", 
            "recommandations_générées"
        ]
        
        for i, type_evt in enumerate(types_événements[:limite]):
            événement = ÉvénementPhoenixAube(
                user_id=user_id,
                event_type=type_evt,
                data={"mock": True, "étape": i+1},
                timestamp=datetime.now() - timedelta(hours=i)
            )
            événements.append(événement)
        
        return événements
    
    def _generate_mock_metrics(self) -> Dict[str, Any]:
        """Génère métriques mock pour développement"""
        return {
            "exploration_commencée": 150,
            "métier_choisi": 89,
            "transition_écosystème": 67,
            "temps_moyen_minutes": 42,
            "satisfaction_moyenne": 4.3,
            "top_métiers": ["Data Scientist", "Coach", "Designer UX", "Chef de Projet"]
        }
    
    def _calculer_durée_totale(self, événements: List[ÉvénementPhoenixAube]) -> float:
        """Calcule durée totale du parcours en minutes"""
        if len(événements) < 2:
            return 0.0
        
        # Trier par timestamp
        événements_triés = sorted(événements, key=lambda x: x.timestamp)
        
        durée = (événements_triés[-1].timestamp - événements_triés[0].timestamp).total_seconds() / 60
        return round(durée, 2)
    
    def _déterminer_statut_actuel(self, étapes_complétées: List[str]) -> str:
        """Détermine le statut actuel du parcours"""
        if not étapes_complétées:
            return "non_commencé"
        elif "métier_choisi" in étapes_complétées:
            if "transition_écosystème" in étapes_complétées:
                return "complété_avec_transition"
            else:
                return "métier_choisi"
        elif "recommandations_générées" in étapes_complétées:
            return "recommandations_reçues"
        elif "tests_psychométriques_complétés" in étapes_complétées:
            return "profil_complété"
        else:
            return "en_cours_exploration"
    
    def _générer_recommandations_ux(self, progression: Dict[str, Any]) -> List[str]:
        """Génère recommandations d'amélioration UX"""
        recommandations = []
        
        # Analyser points de friction
        if len(progression["points_de_sortie"]) > 0:
            dernière_étape = progression["points_de_sortie"][-1]
            
            if dernière_étape == "valeurs_explorées":
                recommandations.append("Simplifier le questionnaire de valeurs")
            elif dernière_étape == "tests_psychométriques_complétés":
                recommandations.append("Raccourcir les tests psychométriques")
            elif dernière_étape == "recommandations_générées":
                recommandations.append("Améliorer présentation des recommandations")
        
        # Analyser temps par étape
        temps_longs = {
            étape: temps for étape, temps in progression["temps_par_étape"].items()
            if temps > 10  # Plus de 10 minutes
        }
        
        if temps_longs:
            recommandations.append(f"Optimiser durée des étapes: {', '.join(temps_longs.keys())}")
        
        return recommandations


# =============================================
# ORCHESTRATEUR PRINCIPAL
# =============================================

class PhoenixAubeOrchestrator:
    """
    Orchestrateur principal Phoenix Aube
    Coordonne tous les services et le flux utilisateur
    """
    
    def __init__(
        self, 
        exploration_engine, 
        ia_validator, 
        transparency_engine, 
        event_store,
        data_provider=None
    ):
        self.exploration_engine = exploration_engine
        self.ia_validator = ia_validator
        self.transparency_engine = transparency_engine
        self.event_store = event_store
        self.data_provider = data_provider
    
    async def traiter_parcours_complet(
        self, 
        user_id: str, 
        données_utilisateur: Dict[str, Any]
    ) -> ParcoursExploration:
        """
        Traite un parcours d'exploration complet
        POINT D'ENTRÉE PRINCIPAL PHOENIX AUBE
        """
        # 1. Publier début d'exploration
        await self.event_store.publier_événement_exploration(
            user_id=user_id,
            type_événement="exploration_commencée",
            données={"données_initiales": données_utilisateur}
        )
        
        # 2. Créer profil exploration
        profil = await self._créer_profil_exploration(user_id, données_utilisateur)
        
        # 3. Publier profil créé
        await self.event_store.publier_événement_exploration(
            user_id=user_id,
            type_événement="profil_créé",
            données={"valeurs": len(profil.valeurs_principales), "compétences": len(profil.compétences_transférables)}
        )
        
        # 4. Générer recommandations métiers (mock pour MVP)
        recommandations = await self._générer_recommandations_mock(profil)
        
        # 5. Publier recommandations
        await self.event_store.publier_événement_exploration(
            user_id=user_id,
            type_événement="recommandations_générées",
            données={"nombre_recommandations": len(recommandations), "top_métier": recommandations[0].métier_titre if recommandations else ""}
        )
        
        # 6. Valider chaque recommandation avec IA
        analyses_ia = []
        for rec in recommandations:
            analyse = await self.ia_validator.évaluer_résistance_métier(rec.métier_titre)
            analyses_ia.append(analyse)
            
            # Publier validation IA
            await self.event_store.publier_événement_exploration(
                user_id=user_id,
                type_événement="validation_ia_effectuée",
                données={"métier": rec.métier_titre, "score_résistance": analyse.score_résistance_ia}
            )
        
        # 7. Créer parcours complet
        parcours = ParcoursExploration(
            user_id=user_id,
            profil_exploration=profil,
            recommandations_métiers=recommandations,
            analyses_ia=analyses_ia,
            statut_completion="recommandations_générées"
        )
        
        # 8. Créer snapshot
        await self.event_store.créer_snapshot_parcours(parcours)
        
        logger.info(f"Parcours complet généré pour user {user_id}")
        return parcours
    
    async def traiter_choix_métier(
        self, 
        user_id: str, 
        métier_choisi: str,
        parcours_id: str
    ) -> Dict[str, Any]:
        """
        Traite le choix final de métier et prépare transitions
        """
        # Publier événement choix
        await self.event_store.publier_événement_exploration(
            user_id=user_id,
            type_événement="métier_choisi",
            données={
                "métier": métier_choisi,
                "parcours_id": parcours_id,
                "timestamp_choix": datetime.now().isoformat()
            }
        )
        
        # Préparer transitions écosystème
        contexte_transitions = {
            "métier_choisi": métier_choisi,
            "compétences_à_valoriser": await self._identifier_compétences_cv(métier_choisi),
            "source": "phoenix_aube",
            "parcours_id": parcours_id
        }
        
        # Déclencher transitions disponibles
        for app_cible in ["phoenix_cv", "phoenix_letters", "phoenix_rise"]:
            await self.event_store.déclencher_transitions_écosystème(
                user_id=user_id,
                app_cible=app_cible,
                contexte_transition=contexte_transitions
            )
        
        prochaines_étapes = await self._générer_prochaines_étapes(métier_choisi)
        
        logger.info(f"Choix métier traité: {métier_choisi} pour user {user_id}")
        
        return {
            "métier_choisi": métier_choisi,
            "transitions_disponibles": ["phoenix_cv", "phoenix_letters", "phoenix_rise"],
            "prochaines_étapes": prochaines_étapes,
            "urls_transition": {
                "phoenix_cv": "https://phoenix-cv.streamlit.app/",
                "phoenix_letters": "https://phoenix-letters.streamlit.app/", 
                "phoenix_rise": "https://phoenix-rise.streamlit.app/"
            }
        }
    
    async def obtenir_dashboard_utilisateur(
        self, 
        user_id: str
    ) -> Dict[str, Any]:
        """
        Obtient dashboard complet utilisateur
        """
        # Récupérer données utilisateur
        parcours_trace = await self.event_store.tracer_parcours_utilisateur(user_id)
        métriques = await self.event_store.obtenir_métriques_utilisation()
        
        dashboard = {
            "utilisateur": {
                "user_id": user_id,
                "statut_parcours": parcours_trace["statut_actuel"],
                "progression": parcours_trace["progression"],
                "temps_investi": parcours_trace["durée_totale_minutes"]
            },
            "contexte_global": {
                "utilisateurs_actifs": métriques["parcours_commencés"],
                "taux_succès": métriques["taux_completion"],
                "métiers_populaires": métriques["métiers_populaires"]
            },
            "recommandations_ux": parcours_trace["recommandations_amélioration"],
            "prochaines_actions": await self._suggérer_prochaines_actions(user_id, parcours_trace["statut_actuel"])
        }
        
        return dashboard
    
    # =============================================
    # MÉTHODES PRIVÉES ORCHESTRATEUR
    # =============================================
    
    async def _créer_profil_exploration(self, user_id: str, données: Dict[str, Any]) -> ProfilExploration:
        """Crée le profil d'exploration à partir des données utilisateur"""
        # Mock pour MVP - en production utiliserait exploration_engine
        from .models import ValeursPersonnelles, EnvironnementTravail
        
        profil = ProfilExploration(
            user_id=user_id,
            valeurs_principales=[ValeursPersonnelles.AUTONOMIE, ValeursPersonnelles.CRÉATIVITÉ],
            compétences_transférables=données.get("compétences", ["Communication", "Analyse", "Leadership"]),
            environnement_préféré=[EnvironnementTravail.FLEXIBLE, EnvironnementTravail.COLLABORATIF],
            motivations_reconversion=données.get("motivations", ["Sens du travail", "Évolution"]),
            contraintes=données.get("contraintes", {})
        )
        
        return profil
    
    async def _générer_recommandations_mock(self, profil: ProfilExploration) -> List:
        """Génère recommandations mock pour MVP"""
        # Import local pour éviter circularité
        from .models import RecommandationCarrière
        
        # Mock recommendations basées sur le profil
        recommandations = [
            RecommandationCarrière(
                métier_titre="Coach en Reconversion",
                score_compatibilité_global=0.92,
                score_valeurs=0.95,
                score_compétences=0.88,
                score_environnement=0.94,
                score_personnalité=0.90,
                justifications_scoring=["Valeurs alignées", "Compétences relationnelles"],
                formations_recommandées=["Certification coaching", "PNL"],
                défis_potentiels=["Développement commercial"]
            ),
            RecommandationCarrière(
                métier_titre="Data Scientist",
                score_compatibilité_global=0.78,
                score_valeurs=0.75,
                score_compétences=0.80,
                score_environnement=0.75,
                score_personnalité=0.82,
                justifications_scoring=["Profil analytique", "Créativité technique"],
                formations_recommandées=["Machine Learning", "Python"],
                défis_potentiels=["Compétences techniques à développer"]
            )
        ]
        
        return recommandations
    
    async def _identifier_compétences_cv(self, métier: str) -> List[str]:
        """Identifie compétences à valoriser pour CV"""
        # Mock mapping métier -> compétences clés
        compétences_métiers = {
            "Coach en Reconversion": ["Écoute active", "Accompagnement", "Empathie", "Méthodes coaching"],
            "Data Scientist": ["Python", "Machine Learning", "Analyse de données", "Statistiques"],
            "Designer UX": ["Design thinking", "Prototypage", "User research", "Figma"],
            "Chef de Projet": ["Gestion projet", "Leadership", "Coordination", "Méthodologies Agile"]
        }
        
        return compétences_métiers.get(métier, ["Communication", "Analyse", "Résolution problèmes"])
    
    async def _générer_prochaines_étapes(self, métier: str) -> List[str]:
        """Génère les prochaines étapes recommandées"""
        étapes_base = [
            f"Créer CV optimisé pour {métier}",
            f"Rédiger lettre motivation personnalisée pour {métier}",
            "Commencer networking dans le secteur",
            "Identifier formations complémentaires"
        ]
        
        # Personnalisation selon métier
        if "Coach" in métier:
            étapes_base.append("Obtenir certification coaching")
        elif "Data" in métier:
            étapes_base.append("Renforcer compétences techniques Python/ML")
        elif "Designer" in métier:
            étapes_base.append("Constituer portfolio design")
        
        return étapes_base[:4]  # Limiter à 4 étapes
    
    async def _suggérer_prochaines_actions(self, user_id: str, statut: str) -> List[str]:
        """Suggère prochaines actions selon statut"""
        actions_par_statut = {
            "non_commencé": [
                "Commencer votre exploration métier",
                "Remplir le questionnaire de valeurs"
            ],
            "en_cours_exploration": [
                "Continuer les tests psychométriques",
                "Compléter votre profil de compétences"  
            ],
            "profil_complété": [
                "Découvrir vos recommandations métiers",
                "Analyser la compatibilité des métiers suggérés"
            ],
            "recommandations_reçues": [
                "Effectuer l'analyse IA des métiers",
                "Choisir votre métier cible"
            ],
            "métier_choisi": [
                "Créer votre CV avec Phoenix CV",
                "Rédiger lettres motivation avec Phoenix Letters",
                "Commencer coaching avec Phoenix Rise"
            ],
            "complété_avec_transition": [
                "Suivre votre progression sur les autres apps",
                "Continuer développement compétences"
            ]
        }
        
        return actions_par_statut.get(statut, ["Contactez le support pour assistance"])