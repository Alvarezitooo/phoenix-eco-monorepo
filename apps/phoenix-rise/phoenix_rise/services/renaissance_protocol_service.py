"""
🔮 Renaissance Protocol Service - Intégration Phoenix Rise
Service d'intégration du Protocole Renaissance avec Phoenix Rise

Author: Claude Phoenix DevSecOps Guardian
Version: 1.0.0 - Renaissance Integration
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
    # Mode dégradé si le module n'est pas disponible
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


class PhoenixRiseRenaissanceService:
    """
    Service Renaissance intégré à Phoenix Rise
    Analyse l'historique utilisateur et propose l'activation du Protocole Renaissance
    """
    
    def __init__(self, db_service=None):
        """
        Initialise le service Renaissance
        
        Args:
            db_service: Service de base de données Phoenix Rise (HybridDBService)
        """
        self.db_service = db_service
        self.analyzer = RenaissanceProtocolAnalyzer(debug=False)
        
    def analyze_user_for_renaissance(self, user_id: str) -> RenaissanceAnalysis:
        """
        Analyse un utilisateur pour déterminer s'il faut déclencher le Protocole Renaissance
        
        Args:
            user_id: ID de l'utilisateur à analyser
            
        Returns:
            RenaissanceAnalysis: Résultat complet de l'analyse
        """
        logger.info(f"🔮 Analyse Renaissance démarrée pour utilisateur {user_id}")
        
        # Récupération des événements utilisateur
        user_events = self._get_user_events(user_id)
        
        if not user_events:
            logger.warning(f"Aucun événement trouvé pour l'utilisateur {user_id}")
            return RenaissanceAnalysis(
                should_trigger=False,
                confidence_level=0.0,
                analysis_details={"error": "Aucun événement utilisateur disponible"},
                recommendations=["Commencez à utiliser Phoenix Rise régulièrement pour une analyse précise"]
            )
        
        # Analyse avec le Renaissance Protocol Analyzer
        analysis = self.analyzer.should_trigger_renaissance_protocol(user_events)
        
        # Log du résultat
        if analysis.should_trigger:
            logger.info(f"🔮 PROTOCOLE RENAISSANCE DÉCLENCHÉ pour {user_id} (confiance: {analysis.confidence_level:.2%})")
        else:
            logger.info(f"⏳ Protocole Renaissance non déclenché pour {user_id} (confiance: {analysis.confidence_level:.2%})")
            
        return analysis
    
    def _get_user_events(self, user_id: str) -> List[UserEvent]:
        """
        Récupère les événements utilisateur depuis la base de données
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            List[UserEvent]: Liste des événements utilisateur
        """
        events = []
        
        try:
            if self.db_service:
                # Récupération des entrées de journal (Phoenix Rise)
                journal_entries = self._get_journal_entries(user_id)
                events.extend(self._convert_journal_to_events(journal_entries, user_id))
                
                # Récupération des sessions de coaching (si disponible)
                coaching_sessions = self._get_coaching_sessions(user_id)
                events.extend(self._convert_coaching_to_events(coaching_sessions, user_id))
                
            else:
                # Mode simulation si pas de DB
                events = self._generate_sample_events(user_id)
                
        except Exception as e:
            logger.error(f"Erreur récupération événements utilisateur {user_id}: {e}")
            events = self._generate_sample_events(user_id)
        
        # Tri chronologique (plus récent en premier)
        events.sort(key=lambda e: e.timestamp, reverse=True)
        
        return events
    
    def _get_journal_entries(self, user_id: str) -> List[Dict]:
        """Récupère les entrées de journal depuis la DB"""
        try:
            if hasattr(self.db_service, 'get_user_journal_entries'):
                return self.db_service.get_user_journal_entries(user_id, limit=20)
            else:
                # Fallback pour les anciennes versions
                return []
        except Exception as e:
            logger.warning(f"Impossible de récupérer les entrées journal: {e}")
            return []
    
    def _get_coaching_sessions(self, user_id: str) -> List[Dict]:
        """Récupère les sessions de coaching depuis la DB"""
        try:
            if hasattr(self.db_service, 'get_user_coaching_sessions'):
                return self.db_service.get_user_coaching_sessions(user_id, limit=10)
            else:
                return []
        except Exception as e:
            logger.warning(f"Impossible de récupérer les sessions coaching: {e}")
            return []
    
    def _convert_journal_to_events(self, journal_entries: List[Dict], user_id: str) -> List[UserEvent]:
        """Convertit les entrées journal en UserEvent"""
        events = []
        
        for entry in journal_entries:
            try:
                # Parsing de la date
                timestamp_str = entry.get('created_at', datetime.now().isoformat())
                if isinstance(timestamp_str, str):
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                else:
                    timestamp = timestamp_str
                
                event = UserEvent(
                    event_type="MoodLogged",
                    user_id=user_id,
                    timestamp=timestamp,
                    payload={
                        "mood": entry.get('mood'),
                        "confidence": entry.get('confidence'),
                        "notes": entry.get('notes', "")
                    }
                )
                events.append(event)
                
            except Exception as e:
                logger.warning(f"Erreur conversion entrée journal: {e}")
                continue
        
        return events
    
    def _convert_coaching_to_events(self, coaching_sessions: List[Dict], user_id: str) -> List[UserEvent]:
        """Convertit les sessions coaching en UserEvent"""
        events = []
        
        for session in coaching_sessions:
            try:
                timestamp_str = session.get('completed_at', datetime.now().isoformat())
                if isinstance(timestamp_str, str):
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                else:
                    timestamp = timestamp_str
                
                event = UserEvent(
                    event_type="CoachingSessionCompleted",
                    user_id=user_id,
                    timestamp=timestamp,
                    payload={
                        "mood": session.get('mood_after'),
                        "confidence": session.get('confidence_after'),
                        "notes": session.get('session_summary', "")
                    }
                )
                events.append(event)
                
            except Exception as e:
                logger.warning(f"Erreur conversion session coaching: {e}")
                continue
        
        return events
    
    def _generate_sample_events(self, user_id: str) -> List[UserEvent]:
        """Génère des événements d'exemple pour la démo"""
        base_time = datetime.now()
        
        sample_events = [
            UserEvent(
                "MoodLogged", user_id, base_time - timedelta(days=1),
                {"mood": 6, "confidence": 7, "notes": "Journée productive mais stressante"}
            ),
            UserEvent(
                "MoodLogged", user_id, base_time - timedelta(days=2),
                {"mood": 4, "confidence": 5, "notes": "Difficultés à maintenir la motivation"}
            ),
            UserEvent(
                "MoodLogged", user_id, base_time - timedelta(days=3),
                {"mood": 7, "confidence": 8, "notes": "Bonne session de coaching aujourd'hui"}
            ),
        ]
        
        return sample_events
    
    def should_show_renaissance_banner(self, user_id: str) -> bool:
        """
        Détermine si la bannière Renaissance doit être affichée
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            bool: True si la bannière doit être montrée
        """
        analysis = self.analyze_user_for_renaissance(user_id)
        return analysis.should_trigger
    
    def get_renaissance_recommendations(self, user_id: str) -> List[str]:
        """
        Récupère les recommandations Renaissance pour un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            List[str]: Liste des recommandations
        """
        analysis = self.analyze_user_for_renaissance(user_id)
        return analysis.recommendations or []
    
    def get_renaissance_dashboard_data(self, user_id: str) -> Dict:
        """
        Prépare les données pour le dashboard Renaissance utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Dict: Données formatées pour le dashboard
        """
        analysis = self.analyze_user_for_renaissance(user_id)
        
        # Extraction des données d'analyse
        mood_data = analysis.analysis_details.get("mood_analysis", {})
        confidence_data = analysis.analysis_details.get("confidence_analysis", {})
        keyword_data = analysis.analysis_details.get("keyword_analysis", {})
        temporal_data = analysis.analysis_details.get("temporal_analysis", {})
        
        return {
            "should_trigger": analysis.should_trigger,
            "confidence_level": analysis.confidence_level,
            "recommendations": analysis.recommendations,
            "insights": {
                "average_mood": mood_data.get("average"),
                "average_confidence": confidence_data.get("average"),
                "mood_trend": mood_data.get("trend", "unknown"),
                "confidence_trend": confidence_data.get("trend", "unknown"),
                "negative_keywords_detected": len(keyword_data.get("detected_keywords", [])),
                "engagement_pattern": temporal_data.get("engagement_pattern", "unknown"),
                "days_since_last_activity": temporal_data.get("days_since_last_event", 0)
            },
            "metrics": {
                "events_analyzed": analysis.analysis_details.get("events_analyzed", 0),
                "mood_below_threshold": mood_data.get("below_threshold", False),
                "confidence_below_threshold": confidence_data.get("below_threshold", False),
                "keywords_above_threshold": keyword_data.get("above_threshold", False)
            }
        }


# Interface simple pour compatibilité
def check_renaissance_protocol(user_id: str, db_service=None) -> bool:
    """
    Interface simple pour vérifier si le Protocole Renaissance doit être déclenché
    
    Args:
        user_id: ID de l'utilisateur
        db_service: Service de base de données (optionnel)
        
    Returns:
        bool: True si le protocole doit être activé
    """
    service = PhoenixRiseRenaissanceService(db_service)
    return service.should_show_renaissance_banner(user_id)


# Test du service
if __name__ == "__main__":
    
    # Test avec utilisateur exemple
    service = PhoenixRiseRenaissanceService()
    
    test_user_id = "test_user_123"
    print("🔮 TEST RENAISSANCE PROTOCOL SERVICE")
    print("=" * 50)
    
    # Test analyse complète
    analysis = service.analyze_user_for_renaissance(test_user_id)
    print(f"Résultat: {analysis.should_trigger}")
    print(f"Confiance: {analysis.confidence_level:.2%}")
    
    # Test bannière
    show_banner = service.should_show_renaissance_banner(test_user_id)
    print(f"Afficher bannière: {show_banner}")
    
    # Test recommandations
    recommendations = service.get_renaissance_recommendations(test_user_id)
    print(f"Recommandations: {len(recommendations)}")
    
    # Test dashboard data
    dashboard_data = service.get_renaissance_dashboard_data(test_user_id)
    print(f"Dashboard data: {dashboard_data['insights']}")
    
    print("✅ Renaissance Protocol Service opérationnel!")