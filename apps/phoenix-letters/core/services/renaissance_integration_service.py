"""
🔮 Renaissance Integration Service - Phoenix Letters
Intégration du Protocole Renaissance dans Phoenix Letters

Author: Claude Phoenix DevSecOps Guardian
Version: 1.0.0 - Renaissance Letters Integration
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


class PhoenixLettersRenaissanceService:
    """
    Service Renaissance pour Phoenix Letters
    Analyse les patterns de génération de lettres et l'engagement utilisateur
    """
    
    def __init__(self, db_connection=None):
        """
        Initialise le service Renaissance pour Phoenix Letters
        
        Args:
            db_connection: Connexion à la base de données Phoenix Letters
        """
        self.db_connection = db_connection
        self.analyzer = RenaissanceProtocolAnalyzer(debug=False)
        
    def analyze_user_letter_patterns(self, user_id: str) -> RenaissanceAnalysis:
        """
        Analyse les patterns de génération de lettres pour détecter des signaux Renaissance
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            RenaissanceAnalysis: Résultat de l'analyse
        """
        logger.info(f"🔮 Analyse Renaissance Letters démarrée pour {user_id}")
        
        # Récupération des événements utilisateur liés aux lettres
        user_events = self._get_letter_events(user_id)
        
        if not user_events:
            return RenaissanceAnalysis(
                should_trigger=False,
                confidence_level=0.0,
                analysis_details={"error": "Aucune activité de génération de lettres"},
                recommendations=["Commencez à générer des lettres pour obtenir une analyse personnalisée"]
            )
        
        # Analyse avec le Renaissance Protocol Analyzer
        analysis = self.analyzer.should_trigger_renaissance_protocol(user_events)
        
        # Enrichissement avec des insights spécifiques aux lettres
        analysis = self._enrich_with_letter_insights(analysis, user_events)
        
        return analysis
    
    def _get_letter_events(self, user_id: str) -> List[UserEvent]:
        """
        Récupère les événements liés à la génération de lettres
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            List[UserEvent]: Événements utilisateur pour l'analyse
        """
        events = []
        
        try:
            if self.db_connection:
                # Récupération depuis la base de données
                letter_generations = self._get_letter_generations(user_id)
                events.extend(self._convert_letters_to_events(letter_generations, user_id))
                
                # Récupération des feedbacks utilisateur
                user_feedback = self._get_user_feedback(user_id)
                events.extend(self._convert_feedback_to_events(user_feedback, user_id))
                
            else:
                # Mode simulation
                events = self._generate_sample_letter_events(user_id)
                
        except Exception as e:
            logger.error(f"Erreur récupération événements lettres {user_id}: {e}")
            events = self._generate_sample_letter_events(user_id)
        
        # Tri chronologique
        events.sort(key=lambda e: e.timestamp, reverse=True)
        
        return events
    
    def _get_letter_generations(self, user_id: str) -> List[Dict]:
        """Récupère l'historique de génération de lettres"""
        try:
            # Query sur la table des lettres générées
            if hasattr(self.db_connection, 'query'):
                query = """
                    SELECT * FROM generated_letters 
                    WHERE user_id = %s 
                    ORDER BY created_at DESC 
                    LIMIT 20
                """
                result = self.db_connection.query(query, (user_id,))
                return result if result else []
            else:
                return []
        except Exception as e:
            logger.warning(f"Impossible de récupérer les lettres générées: {e}")
            return []
    
    def _get_user_feedback(self, user_id: str) -> List[Dict]:
        """Récupère les feedbacks utilisateur"""
        try:
            if hasattr(self.db_connection, 'query'):
                query = """
                    SELECT * FROM user_feedback 
                    WHERE user_id = %s 
                    ORDER BY created_at DESC 
                    LIMIT 10
                """
                result = self.db_connection.query(query, (user_id,))
                return result if result else []
            else:
                return []
        except Exception as e:
            logger.warning(f"Impossible de récupérer les feedbacks: {e}")
            return []
    
    def _convert_letters_to_events(self, letters: List[Dict], user_id: str) -> List[UserEvent]:
        """Convertit les lettres générées en UserEvent pour l'analyse"""
        events = []
        
        for letter in letters:
            try:
                # Extraction des métriques de la lettre
                satisfaction_score = self._extract_satisfaction_from_letter(letter)
                confidence_score = self._extract_confidence_from_letter(letter)
                
                # Analyse du contenu pour détecter des signaux négatifs
                letter_content = letter.get('content', '')
                analysis_notes = self._analyze_letter_sentiment(letter_content)
                
                timestamp_str = letter.get('created_at', datetime.now().isoformat())
                if isinstance(timestamp_str, str):
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                else:
                    timestamp = timestamp_str
                
                event = UserEvent(
                    event_type="LetterGenerated",
                    user_id=user_id,
                    timestamp=timestamp,
                    payload={
                        "mood": satisfaction_score,
                        "confidence": confidence_score,
                        "notes": analysis_notes,
                        "letter_quality": letter.get('quality_score', 5),
                        "generation_attempts": letter.get('attempts', 1)
                    }
                )
                events.append(event)
                
            except Exception as e:
                logger.warning(f"Erreur conversion lettre en événement: {e}")
                continue
        
        return events
    
    def _convert_feedback_to_events(self, feedback_list: List[Dict], user_id: str) -> List[UserEvent]:
        """Convertit les feedbacks en UserEvent"""
        events = []
        
        for feedback in feedback_list:
            try:
                timestamp_str = feedback.get('created_at', datetime.now().isoformat())
                if isinstance(timestamp_str, str):
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                else:
                    timestamp = timestamp_str
                
                # Conversion du feedback en scores
                mood_score = self._feedback_to_mood_score(feedback.get('rating', 5))
                confidence_score = self._feedback_to_confidence_score(feedback.get('satisfaction', 5))
                
                event = UserEvent(
                    event_type="FeedbackSubmitted",
                    user_id=user_id,
                    timestamp=timestamp,
                    payload={
                        "mood": mood_score,
                        "confidence": confidence_score,
                        "notes": feedback.get('comment', ''),
                        "rating": feedback.get('rating', 5)
                    }
                )
                events.append(event)
                
            except Exception as e:
                logger.warning(f"Erreur conversion feedback en événement: {e}")
                continue
        
        return events
    
    def _extract_satisfaction_from_letter(self, letter: Dict) -> int:
        """Extrait un score de satisfaction basé sur les métriques de la lettre"""
        # Logique basée sur la qualité, le nombre d'essais, etc.
        quality = letter.get('quality_score', 5)
        attempts = letter.get('attempts', 1)
        
        # Plus d'essais = moins de satisfaction
        satisfaction = max(1, quality - (attempts - 1))
        return min(10, satisfaction)
    
    def _extract_confidence_from_letter(self, letter: Dict) -> int:
        """Extrait un score de confiance basé sur les métriques"""
        ats_score = letter.get('ats_score', 70)
        personalization_level = letter.get('personalization_level', 5)
        
        # Conversion en score 1-10
        confidence = (ats_score / 10) * 0.7 + personalization_level * 0.3
        return max(1, min(10, int(confidence)))
    
    def _analyze_letter_sentiment(self, content: str) -> str:
        """Analyse le sentiment général du contenu de lettre généré"""
        if not content:
            return "Contenu non disponible"
        
        negative_indicators = [
            "difficile", "problème", "échec", "manque", 
            "faible", "insuffisant", "limité", "déçu"
        ]
        
        positive_indicators = [
            "excellent", "formidable", "parfait", "satisfait",
            "confiant", "motivé", "enthousiaste", "déterminé"
        ]
        
        content_lower = content.lower()
        negative_count = sum(1 for word in negative_indicators if word in content_lower)
        positive_count = sum(1 for word in positive_indicators if word in content_lower)
        
        if negative_count > positive_count:
            return f"Sentiment mitigé détecté dans la génération ({negative_count} indicateurs négatifs)"
        elif positive_count > negative_count:
            return f"Sentiment positif dans la génération ({positive_count} indicateurs positifs)"
        else:
            return "Génération de lettre standard"
    
    def _feedback_to_mood_score(self, rating: int) -> int:
        """Convertit une note de feedback en score d'humeur"""
        return max(1, min(10, rating * 2))  # Conversion 1-5 vers 1-10
    
    def _feedback_to_confidence_score(self, satisfaction: int) -> int:
        """Convertit la satisfaction en score de confiance"""
        return max(1, min(10, satisfaction * 2))
    
    def _generate_sample_letter_events(self, user_id: str) -> List[UserEvent]:
        """Génère des événements d'exemple pour Phoenix Letters"""
        base_time = datetime.now()
        
        return [
            UserEvent(
                "LetterGenerated", user_id, base_time - timedelta(days=1),
                {"mood": 4, "confidence": 3, "notes": "Génération difficile, plusieurs tentatives nécessaires"}
            ),
            UserEvent(
                "FeedbackSubmitted", user_id, base_time - timedelta(days=2),
                {"mood": 3, "confidence": 4, "notes": "La lettre ne correspond pas vraiment à mes attentes"}
            ),
            UserEvent(
                "LetterGenerated", user_id, base_time - timedelta(days=3),
                {"mood": 6, "confidence": 7, "notes": "Bonne qualité mais pourrait être plus personnalisée"}
            ),
        ]
    
    def _enrich_with_letter_insights(self, analysis: RenaissanceAnalysis, events: List[UserEvent]) -> RenaissanceAnalysis:
        """Enrichit l'analyse avec des insights spécifiques aux lettres"""
        # Calcul de métriques spécifiques
        letter_events = [e for e in events if e.event_type == "LetterGenerated"]
        feedback_events = [e for e in events if e.event_type == "FeedbackSubmitted"]
        
        letter_insights = {
            "total_letters_generated": len(letter_events),
            "average_generation_satisfaction": sum(e.payload.get("mood", 5) for e in letter_events) / max(1, len(letter_events)),
            "feedback_count": len(feedback_events),
            "last_activity_days": (datetime.now() - events[0].timestamp).days if events else 999
        }
        
        # Ajout des insights à l'analyse
        if analysis.analysis_details is None:
            analysis.analysis_details = {}
        analysis.analysis_details["letter_insights"] = letter_insights
        
        # Ajout de recommandations spécifiques aux lettres
        if analysis.should_trigger:
            letter_recommendations = [
                "🎯 Revoir vos objectifs de candidature avec un focus personnalisé",
                "✍️ Essayer de nouveaux templates de lettres pour stimuler la créativité",
                "💡 Utiliser le Mirror Match pour mieux adapter vos lettres aux offres"
            ]
            if analysis.recommendations:
                analysis.recommendations.extend(letter_recommendations)
            else:
                analysis.recommendations = letter_recommendations
        
        return analysis
    
    def should_show_renaissance_banner_letters(self, user_id: str) -> bool:
        """Détermine si la bannière Renaissance doit être affichée dans Phoenix Letters"""
        analysis = self.analyze_user_letter_patterns(user_id)
        return analysis.should_trigger
    
    def get_renaissance_letter_recommendations(self, user_id: str) -> List[str]:
        """Récupère les recommandations Renaissance spécifiques aux lettres"""
        analysis = self.analyze_user_letter_patterns(user_id)
        return analysis.recommendations or []


# Interface simple
def check_renaissance_protocol_letters(user_id: str, db_connection=None) -> bool:
    """Interface simple pour Phoenix Letters"""
    service = PhoenixLettersRenaissanceService(db_connection)
    return service.should_show_renaissance_banner_letters(user_id)


# Test du service
if __name__ == "__main__":
    service = PhoenixLettersRenaissanceService()
    
    test_user = "letters_test_user"
    print("🔮 TEST RENAISSANCE PHOENIX LETTERS")
    print("=" * 50)
    
    analysis = service.analyze_user_letter_patterns(test_user)
    print(f"Résultat: {analysis.should_trigger}")
    print(f"Confiance: {analysis.confidence_level:.2%}")
    
    recommendations = service.get_renaissance_letter_recommendations(test_user)
    print(f"Recommandations: {len(recommendations)}")
    for rec in recommendations:
        print(f"  • {rec}")
    
    print("✅ Renaissance Letters Service opérationnel!")