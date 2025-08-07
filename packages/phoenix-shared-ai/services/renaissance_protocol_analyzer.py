"""
🔮 Renaissance Protocol Analyzer - Déclencheur Intelligent Phoenix
Analyse l'historique utilisateur et décide l'activation du Protocole Renaissance

Author: Claude Phoenix DevSecOps Guardian  
Version: 1.0.0 - Renaissance Engine
"""

import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple
from enum import Enum
import logging

# Configuration du logger
logger = logging.getLogger(__name__)


class EventType(Enum):
    """Types d'événements Phoenix supportés"""
    MOOD_LOGGED = "MoodLogged"
    COACHING_SESSION_COMPLETED = "CoachingSessionCompleted"
    JOURNAL_ENTRY_CREATED = "JournalEntryCreated"
    GOAL_SET = "GoalSet"
    PROGRESS_TRACKED = "ProgressTracked"


@dataclass
class UserEvent:
    """Événement utilisateur standardisé pour l'analyse"""
    event_type: str
    user_id: str
    timestamp: datetime
    payload: Dict
    
    @property
    def mood_score(self) -> Optional[int]:
        """Extrait le score d'humeur de l'événement (1-10)"""
        return self.payload.get("mood") or self.payload.get("mood_score")
    
    @property 
    def confidence_score(self) -> Optional[int]:
        """Extrait le score de confiance de l'événement (1-10)"""
        return self.payload.get("confidence") or self.payload.get("confidence_score")
    
    @property
    def notes(self) -> Optional[str]:
        """Extrait les notes/texte de l'événement"""
        return (self.payload.get("notes") or 
                self.payload.get("content") or
                self.payload.get("message") or
                self.payload.get("description", ""))


@dataclass
class RenaissanceAnalysis:
    """Résultat de l'analyse pour le Protocole Renaissance"""
    should_trigger: bool
    confidence_level: float  # 0.0 à 1.0
    analysis_details: Dict[str, any]
    recommendations: List[str]
    
    def __str__(self) -> str:
        status = "🔮 DÉCLENCHÉ" if self.should_trigger else "⏳ En attente"
        return (f"Renaissance Protocol: {status}\n"
                f"Confiance: {self.confidence_level:.2%}\n"
                f"Indicateurs: {len(self.analysis_details)} analysés")


class RenaissanceProtocolAnalyzer:
    """
    Analyseur intelligent pour décider du déclenchement du Protocole Renaissance
    
    LOGIQUE:
    - Analyse les 5 derniers événements MoodLogged
    - Vérifie les seuils d'humeur et confiance (< 4/10) 
    - Détecte les mots-clés négatifs récurrents
    - Calcule un score de confiance global
    """
    
    # Mots-clés négatifs pour l'analyse textuelle
    NEGATIVE_KEYWORDS = {
        "échec", "échoue", "échouer", "échecs",
        "inutile", "inutiles", "inutilité",
        "bloqué", "bloque", "bloquer", "blocage",
        "désespoir", "désespéré", "désespère",
        "impossible", "jamais", "rien",
        "nul", "nulle", "mauvais", "mauvaise",
        "fatigué", "épuisé", "épuisement",
        "abandonner", "abandonne", "renonce",
        "perdu", "perdue", "confus", "confuse",
        "découragement", "découragé", "découragée",
        "stress", "stressé", "anxieux", "anxiété",
        "peur", "peurs", "inquiet", "inquiète"
    }
    
    # Seuils de déclenchement
    MOOD_THRESHOLD = 4.0      # Seuil humeur moyenne
    CONFIDENCE_THRESHOLD = 4.0  # Seuil confiance moyenne
    NEGATIVE_KEYWORD_THRESHOLD = 2  # Nombre minimum mots-clés négatifs
    ANALYSIS_WINDOW_DAYS = 14    # Fenêtre d'analyse (14 jours)
    MIN_EVENTS_REQUIRED = 3      # Minimum d'événements pour analyse
    
    def __init__(self, debug: bool = False):
        """
        Initialise l'analyseur Renaissance
        
        Args:
            debug: Active les logs détaillés
        """
        self.debug = debug
        if debug:
            logging.basicConfig(level=logging.DEBUG)
        
    def should_trigger_renaissance_protocol(self, user_events: List[UserEvent]) -> RenaissanceAnalysis:
        """
        Point d'entrée principal - Analyse si le Protocole Renaissance doit être déclenché
        
        Args:
            user_events: Liste des événements utilisateur (chronologique)
            
        Returns:
            RenaissanceAnalysis: Résultat complet de l'analyse
        """
        logger.info(f"🔮 Analyse Renaissance démarrée - {len(user_events)} événements")
        
        # Filtrage et préparation des données
        relevant_events = self._filter_relevant_events(user_events)
        
        if len(relevant_events) < self.MIN_EVENTS_REQUIRED:
            return RenaissanceAnalysis(
                should_trigger=False,
                confidence_level=0.0,
                analysis_details={"error": "Pas assez d'événements pour analyse"},
                recommendations=["Continuez à utiliser Phoenix régulièrement pour une analyse précise"]
            )
        
        # Analyse des métriques
        mood_analysis = self._analyze_mood_trends(relevant_events)
        confidence_analysis = self._analyze_confidence_trends(relevant_events)
        keyword_analysis = self._analyze_negative_keywords(relevant_events)
        temporal_analysis = self._analyze_temporal_patterns(relevant_events)
        
        # Calcul du score de déclenchement
        trigger_score = self._calculate_trigger_score(
            mood_analysis, confidence_analysis, keyword_analysis, temporal_analysis
        )
        
        # Décision finale
        should_trigger = trigger_score >= 0.7  # Seuil de 70%
        
        analysis_details = {
            "mood_analysis": mood_analysis,
            "confidence_analysis": confidence_analysis, 
            "keyword_analysis": keyword_analysis,
            "temporal_analysis": temporal_analysis,
            "trigger_score": trigger_score,
            "events_analyzed": len(relevant_events)
        }
        
        recommendations = self._generate_recommendations(analysis_details, should_trigger)
        
        result = RenaissanceAnalysis(
            should_trigger=should_trigger,
            confidence_level=trigger_score,
            analysis_details=analysis_details,
            recommendations=recommendations
        )
        
        if self.debug:
            logger.debug(f"Renaissance Analysis: {result}")
        
        return result
    
    def _filter_relevant_events(self, events: List[UserEvent]) -> List[UserEvent]:
        """Filtre les événements pertinents pour l'analyse Renaissance"""
        cutoff_date = datetime.now() - timedelta(days=self.ANALYSIS_WINDOW_DAYS)
        
        relevant_types = {
            EventType.MOOD_LOGGED.value,
            EventType.COACHING_SESSION_COMPLETED.value, 
            EventType.JOURNAL_ENTRY_CREATED.value
        }
        
        filtered = [
            event for event in events
            if (event.timestamp >= cutoff_date and 
                event.event_type in relevant_types and
                (event.mood_score is not None or event.confidence_score is not None or event.notes))
        ]
        
        # Tri chronologique (plus récent en premier)
        filtered.sort(key=lambda e: e.timestamp, reverse=True)
        
        # Limite aux 10 événements les plus récents
        return filtered[:10]
    
    def _analyze_mood_trends(self, events: List[UserEvent]) -> Dict:
        """Analyse les tendances d'humeur"""
        mood_scores = [e.mood_score for e in events if e.mood_score is not None]
        
        if not mood_scores:
            return {"average": None, "trend": "unknown", "below_threshold": False}
        
        # Prendre les 5 plus récents pour le calcul
        recent_moods = mood_scores[:5]
        avg_mood = sum(recent_moods) / len(recent_moods)
        
        # Analyse de tendance (comparaison première vs dernière moitié)
        if len(mood_scores) >= 4:
            recent_half = mood_scores[:len(mood_scores)//2]
            older_half = mood_scores[len(mood_scores)//2:]
            trend = "declining" if sum(recent_half)/len(recent_half) < sum(older_half)/len(older_half) else "stable_or_improving"
        else:
            trend = "insufficient_data"
        
        return {
            "average": round(avg_mood, 2),
            "recent_scores": recent_moods,
            "trend": trend,
            "below_threshold": avg_mood < self.MOOD_THRESHOLD,
            "lowest_score": min(mood_scores),
            "score_count": len(mood_scores)
        }
    
    def _analyze_confidence_trends(self, events: List[UserEvent]) -> Dict:
        """Analyse les tendances de confiance"""
        confidence_scores = [e.confidence_score for e in events if e.confidence_score is not None]
        
        if not confidence_scores:
            return {"average": None, "trend": "unknown", "below_threshold": False}
        
        # Prendre les 5 plus récents pour le calcul
        recent_confidence = confidence_scores[:5]
        avg_confidence = sum(recent_confidence) / len(recent_confidence)
        
        # Analyse de tendance
        if len(confidence_scores) >= 4:
            recent_half = confidence_scores[:len(confidence_scores)//2]
            older_half = confidence_scores[len(confidence_scores)//2:]
            trend = "declining" if sum(recent_half)/len(recent_half) < sum(older_half)/len(older_half) else "stable_or_improving"
        else:
            trend = "insufficient_data"
        
        return {
            "average": round(avg_confidence, 2),
            "recent_scores": recent_confidence,
            "trend": trend,
            "below_threshold": avg_confidence < self.CONFIDENCE_THRESHOLD,
            "lowest_score": min(confidence_scores),
            "score_count": len(confidence_scores)
        }
    
    def _analyze_negative_keywords(self, events: List[UserEvent]) -> Dict:
        """Analyse la présence de mots-clés négatifs dans les notes"""
        all_notes = [e.notes for e in events if e.notes]
        
        if not all_notes:
            return {"detected_keywords": [], "frequency": 0, "above_threshold": False}
        
        # Combinaison de toutes les notes
        combined_notes = " ".join(all_notes).lower()
        
        # Détection des mots-clés négatifs
        detected_keywords = []
        keyword_frequency = {}
        
        for keyword in self.NEGATIVE_KEYWORDS:
            # Utilisation de regex pour détecter les mots complets
            pattern = r'\b' + re.escape(keyword) + r'\b'
            matches = re.findall(pattern, combined_notes)
            if matches:
                detected_keywords.append(keyword)
                keyword_frequency[keyword] = len(matches)
        
        total_frequency = sum(keyword_frequency.values())
        
        return {
            "detected_keywords": detected_keywords,
            "keyword_frequency": keyword_frequency,
            "total_frequency": total_frequency,
            "unique_keywords_count": len(detected_keywords),
            "above_threshold": len(detected_keywords) >= self.NEGATIVE_KEYWORD_THRESHOLD,
            "notes_analyzed": len(all_notes)
        }
    
    def _analyze_temporal_patterns(self, events: List[UserEvent]) -> Dict:
        """Analyse les patterns temporels des événements"""
        if not events:
            return {"pattern": "no_data"}
        
        # Analyse de la fréquence d'utilisation
        now = datetime.now()
        days_since_last = (now - events[0].timestamp).days
        
        # Calcul de la fréquence moyenne
        if len(events) > 1:
            time_spans = []
            for i in range(len(events) - 1):
                delta = events[i].timestamp - events[i + 1].timestamp
                time_spans.append(delta.days)
            avg_gap = sum(time_spans) / len(time_spans) if time_spans else 0
        else:
            avg_gap = None
        
        # Détection de pattern d'engagement décroissant
        recent_events = [e for e in events if (now - e.timestamp).days <= 7]
        older_events = [e for e in events if (now - e.timestamp).days > 7]
        
        engagement_pattern = "stable"
        if len(older_events) > 0:
            recent_rate = len(recent_events) / 7  # événements par jour
            older_rate = len(older_events) / min(7, self.ANALYSIS_WINDOW_DAYS - 7)
            
            if recent_rate < older_rate * 0.5:  # 50% de diminution
                engagement_pattern = "declining"
            elif recent_rate > older_rate * 1.5:  # 50% d'augmentation
                engagement_pattern = "increasing"
        
        return {
            "days_since_last_event": days_since_last,
            "average_gap_days": round(avg_gap, 2) if avg_gap is not None else None,
            "recent_events_count": len(recent_events),
            "engagement_pattern": engagement_pattern,
            "total_events": len(events)
        }
    
    def _calculate_trigger_score(self, mood_analysis: Dict, confidence_analysis: Dict, 
                               keyword_analysis: Dict, temporal_analysis: Dict) -> float:
        """Calcule le score de déclenchement basé sur toutes les analyses"""
        score = 0.0
        max_score = 0.0
        
        # Score humeur (poids: 35%)
        if mood_analysis["average"] is not None:
            max_score += 0.35
            if mood_analysis["below_threshold"]:
                score += 0.25
                if mood_analysis["trend"] == "declining":
                    score += 0.10  # Bonus si tendance décroissante
        
        # Score confiance (poids: 35%)
        if confidence_analysis["average"] is not None:
            max_score += 0.35
            if confidence_analysis["below_threshold"]:
                score += 0.25
                if confidence_analysis["trend"] == "declining":
                    score += 0.10  # Bonus si tendance décroissante
        
        # Score mots-clés négatifs (poids: 20%)
        max_score += 0.20
        if keyword_analysis["above_threshold"]:
            score += 0.15
            # Bonus pour fréquence élevée
            if keyword_analysis["total_frequency"] >= 5:
                score += 0.05
        
        # Score patterns temporels (poids: 10%)
        max_score += 0.10
        if temporal_analysis["engagement_pattern"] == "declining":
            score += 0.05
        if temporal_analysis.get("days_since_last_event", 0) > 3:
            score += 0.05
        
        # Normalisation du score
        if max_score > 0:
            normalized_score = score / max_score
        else:
            normalized_score = 0.0
        
        return min(1.0, normalized_score)  # Cap à 1.0
    
    def _generate_recommendations(self, analysis: Dict, should_trigger: bool) -> List[str]:
        """Génère des recommandations basées sur l'analyse"""
        recommendations = []
        
        if should_trigger:
            recommendations.extend([
                "🔮 Activation du Protocole Renaissance recommandée",
                "📞 Envisager un accompagnement personnalisé renforcé", 
                "🎯 Revoir les objectifs et stratégies actuels",
                "💪 Mettre en place un plan d'action structuré"
            ])
        else:
            recommendations.append("✨ Continuer le parcours actuel avec Phoenix")
        
        # Recommandations spécifiques selon l'analyse
        mood_data = analysis.get("mood_analysis", {})
        if mood_data.get("below_threshold"):
            recommendations.append("🌱 Focus sur les activités qui améliorent l'humeur")
        
        confidence_data = analysis.get("confidence_analysis", {})
        if confidence_data.get("below_threshold"):
            recommendations.append("💎 Travailler sur le renforcement de la confiance en soi")
        
        keyword_data = analysis.get("keyword_analysis", {})
        if keyword_data.get("above_threshold"):
            recommendations.append("🗣️ Exprimer et traiter les émotions négatives identifiées")
        
        temporal_data = analysis.get("temporal_analysis", {})
        if temporal_data.get("engagement_pattern") == "declining":
            recommendations.append("📱 Maintenir un engagement régulier avec Phoenix")
        
        return recommendations


# Fonction utilitaire pour compatibilité
def should_trigger_renaissance_protocol(user_events: List[UserEvent]) -> bool:
    """
    Fonction simple pour décision binaire Renaissance Protocol
    
    Args:
        user_events: Liste des événements utilisateur
        
    Returns:
        bool: True si le protocole doit être déclenché
    """
    analyzer = RenaissanceProtocolAnalyzer()
    result = analyzer.should_trigger_renaissance_protocol(user_events)
    return result.should_trigger


# Factory pour créer des événements depuis différentes sources
class EventFactory:
    """Factory pour créer des UserEvent depuis différentes sources de données"""
    
    @staticmethod
    def from_journal_entry(journal_entry: Dict) -> UserEvent:
        """Crée un UserEvent depuis une JournalEntry Phoenix Rise"""
        return UserEvent(
            event_type=EventType.MOOD_LOGGED.value,
            user_id=journal_entry.get("user_id", ""),
            timestamp=datetime.fromisoformat(journal_entry.get("created_at", datetime.now().isoformat())),
            payload={
                "mood": journal_entry.get("mood"),
                "confidence": journal_entry.get("confidence"),
                "notes": journal_entry.get("notes", "")
            }
        )
    
    @staticmethod
    def from_phoenix_event(event_data: Dict) -> UserEvent:
        """Crée un UserEvent depuis un événement Phoenix Event Bridge"""
        return UserEvent(
            event_type=event_data.get("event_type", ""),
            user_id=event_data.get("user_id", ""),
            timestamp=datetime.fromisoformat(event_data.get("timestamp", datetime.now().isoformat())),
            payload=event_data.get("payload", {})
        )


if __name__ == "__main__":
    # Test simple
    from datetime import datetime, timedelta
    
    # Création d'événements de test
    test_events = [
        UserEvent(
            event_type="MoodLogged",
            user_id="test_user",
            timestamp=datetime.now() - timedelta(days=1),
            payload={"mood": 2, "confidence": 3, "notes": "Je me sens bloqué et inutile aujourd'hui"}
        ),
        UserEvent(
            event_type="MoodLogged", 
            user_id="test_user",
            timestamp=datetime.now() - timedelta(days=2),
            payload={"mood": 3, "confidence": 2, "notes": "Encore un échec dans ma recherche"}
        ),
        UserEvent(
            event_type="MoodLogged",
            user_id="test_user", 
            timestamp=datetime.now() - timedelta(days=3),
            payload={"mood": 1, "confidence": 4, "notes": "Désespoir total, rien ne marche"}
        )
    ]
    
    analyzer = RenaissanceProtocolAnalyzer(debug=True)
    result = analyzer.should_trigger_renaissance_protocol(test_events)
    
    print("🔮 RENAISSANCE PROTOCOL ANALYZER - TEST")
    print("=" * 50)
    print(result)
    print("\nRecommandations:")
    for rec in result.recommendations:
        print(f"  • {rec}")