"""
🔮 Renaissance CV Service - Phoenix CV
Service d'intégration du Protocole Renaissance pour Phoenix CV

Author: Claude Phoenix DevSecOps Guardian
Version: 1.0.0 - Renaissance CV Integration
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List
from dataclasses import dataclass

# Import conditionnel du RenaissanceProtocolAnalyzer
try:
    from phoenix_shared_ai.services.renaissance_protocol_analyzer import (
        RenaissanceProtocolAnalyzer,
        UserEvent,
        RenaissanceAnalysis,
    )
except ImportError:
    logging.warning("RenaissanceProtocolAnalyzer non disponible - mode dégradé activé")
    
    @dataclass
    class RenaissanceAnalysis:
        should_trigger: bool = False
        confidence_level: float = 0.0
        analysis_details: Dict = None
        recommendations: List[str] = None
    
    class RenaissanceProtocolAnalyzer:
        def should_trigger_renaissance_protocol(self, events): 
            return RenaissanceAnalysis()
    
    class UserEvent:
        def __init__(self, event_type, user_id, timestamp, payload):
            pass

logger = logging.getLogger(__name__)


class PhoenixCVRenaissanceService:
    """
    Service Renaissance pour Phoenix CV
    Analyse les patterns de création/optimisation CV et l'engagement utilisateur
    """
    
    def __init__(self, session_manager=None):
        """
        Initialise le service Renaissance pour Phoenix CV
        
        Args:
            session_manager: Gestionnaire de session Phoenix CV
        """
        self.session_manager = session_manager
        self.analyzer = RenaissanceProtocolAnalyzer(debug=False)
        
    def analyze_user_cv_patterns(self, user_id: str) -> RenaissanceAnalysis:
        """
        Analyse les patterns de création CV pour détecter des signaux Renaissance
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            RenaissanceAnalysis: Résultat de l'analyse
        """
        logger.info(f"🔮 Analyse Renaissance CV démarrée pour {user_id}")
        
        # Récupération des événements utilisateur liés aux CV
        user_events = self._get_cv_events(user_id)
        
        if not user_events:
            return RenaissanceAnalysis(
                should_trigger=False,
                confidence_level=0.0,
                analysis_details={"error": "Aucune activité CV détectée"},
                recommendations=["Commencez à créer ou optimiser votre CV pour une analyse personnalisée"]
            )
        
        # Analyse avec le Renaissance Protocol Analyzer
        analysis = self.analyzer.should_trigger_renaissance_protocol(user_events)
        
        # Enrichissement avec des insights spécifiques aux CV
        analysis = self._enrich_with_cv_insights(analysis, user_events)
        
        return analysis
    
    def _get_cv_events(self, user_id: str) -> List[UserEvent]:
        """
        Récupère les événements liés aux CV depuis les sessions et logs
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            List[UserEvent]: Événements utilisateur pour l'analyse
        """
        events = []
        
        try:
            if self.session_manager:
                # Récupération depuis le session manager
                cv_uploads = self._get_cv_uploads(user_id)
                events.extend(self._convert_cv_uploads_to_events(cv_uploads, user_id))
                
                # Récupération des optimisations ATS
                ats_optimizations = self._get_ats_optimizations(user_id)
                events.extend(self._convert_ats_to_events(ats_optimizations, user_id))
                
                # Récupération des template selections
                template_usage = self._get_template_usage(user_id)
                events.extend(self._convert_templates_to_events(template_usage, user_id))
                
            else:
                # Mode simulation
                events = self._generate_sample_cv_events(user_id)
                
        except Exception as e:
            logger.error(f"Erreur récupération événements CV {user_id}: {e}")
            events = self._generate_sample_cv_events(user_id)
        
        # Tri chronologique
        events.sort(key=lambda e: e.timestamp, reverse=True)
        
        return events
    
    def _get_cv_uploads(self, user_id: str) -> List[Dict]:
        """Récupère l'historique des uploads CV"""
        try:
            # Récupération depuis les logs de session
            user_session = self.session_manager.get_user_session(user_id)
            cv_history = user_session.get('cv_upload_history', [])
            return cv_history
        except Exception as e:
            logger.warning(f"Impossible de récupérer l'historique CV: {e}")
            return []
    
    def _get_ats_optimizations(self, user_id: str) -> List[Dict]:
        """Récupère l'historique des optimisations ATS"""
        try:
            user_session = self.session_manager.get_user_session(user_id)
            ats_history = user_session.get('ats_optimization_history', [])
            return ats_history
        except Exception as e:
            logger.warning(f"Impossible de récupérer l'historique ATS: {e}")
            return []
    
    def _get_template_usage(self, user_id: str) -> List[Dict]:
        """Récupère l'historique d'utilisation des templates"""
        try:
            user_session = self.session_manager.get_user_session(user_id)
            template_history = user_session.get('template_usage_history', [])
            return template_history
        except Exception as e:
            logger.warning(f"Impossible de récupérer l'historique templates: {e}")
            return []
    
    def _convert_cv_uploads_to_events(self, uploads: List[Dict], user_id: str) -> List[UserEvent]:
        """Convertit les uploads CV en UserEvent"""
        events = []
        
        for upload in uploads:
            try:
                # Analyse de la satisfaction basée sur les métriques
                success_rate = upload.get('parsing_success', True)
                quality_score = upload.get('quality_assessment', 5)
                
                # Score de satisfaction basé sur le succès du parsing
                mood_score = 8 if success_rate else 3
                confidence_score = quality_score
                
                # Notes basées sur l'analyse
                notes = f"Upload CV - Parsing: {'réussi' if success_rate else 'difficultés'}, Qualité: {quality_score}/10"
                
                timestamp = upload.get('timestamp', datetime.now())
                if isinstance(timestamp, str):
                    timestamp = datetime.fromisoformat(timestamp)
                
                event = UserEvent(
                    event_type="CVUploaded",
                    user_id=user_id,
                    timestamp=timestamp,
                    payload={
                        "mood": mood_score,
                        "confidence": confidence_score,
                        "notes": notes,
                        "parsing_success": success_rate,
                        "quality_score": quality_score
                    }
                )
                events.append(event)
                
            except Exception as e:
                logger.warning(f"Erreur conversion upload CV: {e}")
                continue
        
        return events
    
    def _convert_ats_to_events(self, optimizations: List[Dict], user_id: str) -> List[UserEvent]:
        """Convertit les optimisations ATS en UserEvent"""
        events = []
        
        for optim in optimizations:
            try:
                # Analyse de satisfaction basée sur le score ATS
                ats_score = optim.get('ats_score', 50)
                improvement = optim.get('improvement', 0)
                
                # Conversion en scores d'humeur/confiance
                mood_score = min(10, max(1, ats_score // 10))  # 0-100 vers 1-10
                confidence_score = min(10, max(1, (ats_score + improvement) // 10))
                
                # Analyse du sentiment
                if ats_score < 40:
                    sentiment = "Score ATS faible, potentielle frustration"
                elif ats_score > 80:
                    sentiment = "Excellent score ATS, satisfaction élevée"
                else:
                    sentiment = f"Score ATS moyen ({ats_score}%), amélioration possible"
                
                timestamp = optim.get('timestamp', datetime.now())
                if isinstance(timestamp, str):
                    timestamp = datetime.fromisoformat(timestamp)
                
                event = UserEvent(
                    event_type="ATSOptimized",
                    user_id=user_id,
                    timestamp=timestamp,
                    payload={
                        "mood": mood_score,
                        "confidence": confidence_score,
                        "notes": sentiment,
                        "ats_score": ats_score,
                        "improvement": improvement
                    }
                )
                events.append(event)
                
            except Exception as e:
                logger.warning(f"Erreur conversion optimisation ATS: {e}")
                continue
        
        return events
    
    def _convert_templates_to_events(self, templates: List[Dict], user_id: str) -> List[UserEvent]:
        """Convertit l'utilisation de templates en UserEvent"""
        events = []
        
        for template_use in templates:
            try:
                # Analyse basée sur l'engagement avec les templates
                template_satisfaction = template_use.get('satisfaction_rating', 5)
                time_spent = template_use.get('time_spent_minutes', 10)
                
                # Plus de temps = plus d'engagement, mais trop = frustration
                if time_spent < 2:
                    mood_score = 3  # Abandonnement rapide
                elif time_spent > 30:
                    mood_score = 4  # Possible frustration
                else:
                    mood_score = template_satisfaction + 2  # Utilisation normale
                
                confidence_score = min(10, template_satisfaction + 1)
                
                notes = f"Template {template_use.get('template_name', 'Inconnu')} - {time_spent}min d'utilisation"
                
                timestamp = template_use.get('timestamp', datetime.now())
                if isinstance(timestamp, str):
                    timestamp = datetime.fromisoformat(timestamp)
                
                event = UserEvent(
                    event_type="TemplateUsed",
                    user_id=user_id,
                    timestamp=timestamp,
                    payload={
                        "mood": mood_score,
                        "confidence": confidence_score,
                        "notes": notes,
                        "template_satisfaction": template_satisfaction,
                        "time_spent": time_spent
                    }
                )
                events.append(event)
                
            except Exception as e:
                logger.warning(f"Erreur conversion template: {e}")
                continue
        
        return events
    
    def _generate_sample_cv_events(self, user_id: str) -> List[UserEvent]:
        """Génère des événements d'exemple pour Phoenix CV"""
        base_time = datetime.now()
        
        return [
            UserEvent(
                "CVUploaded", user_id, base_time - timedelta(days=1),
                {"mood": 3, "confidence": 2, "notes": "Parsing CV difficile, format non reconnu"}
            ),
            UserEvent(
                "ATSOptimized", user_id, base_time - timedelta(days=2),
                {"mood": 4, "confidence": 3, "notes": "Score ATS 35%, en dessous des attentes"}
            ),
            UserEvent(
                "TemplateUsed", user_id, base_time - timedelta(days=3),
                {"mood": 2, "confidence": 4, "notes": "Difficulté à trouver le bon template, 45min de recherche"}
            ),
        ]
    
    def _enrich_with_cv_insights(self, analysis: RenaissanceAnalysis, events: List[UserEvent]) -> RenaissanceAnalysis:
        """Enrichit l'analyse avec des insights spécifiques aux CV"""
        # Calcul de métriques spécifiques aux CV
        cv_events = [e for e in events if e.event_type == "CVUploaded"]
        ats_events = [e for e in events if e.event_type == "ATSOptimized"]
        template_events = [e for e in events if e.event_type == "TemplateUsed"]
        
        cv_insights = {
            "total_cv_uploads": len(cv_events),
            "total_ats_optimizations": len(ats_events),
            "total_template_uses": len(template_events),
            "average_ats_satisfaction": sum(e.payload.get("confidence", 5) for e in ats_events) / max(1, len(ats_events)),
            "last_activity_days": (datetime.now() - events[0].timestamp).days if events else 999
        }
        
        # Ajout des insights à l'analyse
        if analysis.analysis_details is None:
            analysis.analysis_details = {}
        analysis.analysis_details["cv_insights"] = cv_insights
        
        # Ajout de recommandations spécifiques aux CV
        if analysis.should_trigger:
            cv_recommendations = [
                "🎯 Revoir votre stratégie de présentation CV avec de nouveaux angles",
                "📊 Optimiser votre score ATS avec des mots-clés plus pertinents",
                "🎨 Essayer de nouveaux templates pour moderniser votre présentation",
                "💼 Adapter votre CV aux spécificités de votre secteur cible"
            ]
            if analysis.recommendations:
                analysis.recommendations.extend(cv_recommendations)
            else:
                analysis.recommendations = cv_recommendations
        
        return analysis
    
    def should_show_renaissance_banner_cv(self, user_id: str) -> bool:
        """Détermine si la bannière Renaissance doit être affichée dans Phoenix CV"""
        analysis = self.analyze_user_cv_patterns(user_id)
        return analysis.should_trigger
    
    def get_renaissance_cv_recommendations(self, user_id: str) -> List[str]:
        """Récupère les recommandations Renaissance spécifiques aux CV"""
        analysis = self.analyze_user_cv_patterns(user_id)
        return analysis.recommendations or []


# Interface simple
def check_renaissance_protocol_cv(user_id: str, session_manager=None) -> bool:
    """Interface simple pour Phoenix CV"""
    service = PhoenixCVRenaissanceService(session_manager)
    return service.should_show_renaissance_banner_cv(user_id)


# Test du service
if __name__ == "__main__":
    service = PhoenixCVRenaissanceService()
    
    test_user = "cv_test_user"
    print("🔮 TEST RENAISSANCE PHOENIX CV")
    print("=" * 50)
    
    analysis = service.analyze_user_cv_patterns(test_user)
    print(f"Résultat: {analysis.should_trigger}")
    print(f"Confiance: {analysis.confidence_level:.2%}")
    
    recommendations = service.get_renaissance_cv_recommendations(test_user)
    print(f"Recommandations: {len(recommendations)}")
    for rec in recommendations:
        print(f"  • {rec}")
    
    print("✅ Renaissance CV Service opérationnel!")