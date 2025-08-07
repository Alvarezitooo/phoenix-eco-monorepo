from dataclasses import dataclass, field
from datetime import datetime, timedelta
import pytz
from collections import deque

@dataclass
class EmotionalVectorState:
    user_id: str
    last_updated: datetime = field(default_factory=lambda: datetime.now(pytz.utc))

    # Métriques émotionnelles agrégées sur 7 jours
    mood_sum_7d: float = 0.0
    mood_count_7d: int = 0
    mood_average_7d: float = 0.0

    # Pour le calcul de la tendance de confiance (ex: sur 30 jours)
    confidence_scores_30d: deque = field(default_factory=lambda: deque(maxlen=30)) # Stocke les scores quotidiens
    confidence_trend: float = 0.0 # Ex: pente de régression linéaire

    # Indicateurs de comportement
    last_action_type: str | None = None
    actions_count_7d: dict[str, int] = field(default_factory=dict) # Ex: {'CVGenerated': 5, 'SkillSuggested': 10}

    # Score de risque de burnout (calculé à partir de plusieurs facteurs)
    burnout_risk_score: float = 0.0

    # Historique des événements pertinents pour les calculs glissants
    # Chaque tuple: (timestamp, event_type, value)
    event_history_7d: deque = field(default_factory=deque)
    event_history_30d: deque = field(default_factory=deque)

    def update_mood(self, timestamp: datetime, mood_score: float):
        # Ajoute le nouvel événement
        self.event_history_7d.append((timestamp, 'MoodLogged', mood_score))
        self.mood_sum_7d += mood_score
        self.mood_count_7d += 1

        # Retire les événements trop anciens
        seven_days_ago = timestamp - timedelta(days=7)
        while self.event_history_7d and self.event_history_7d[0][0] < seven_days_ago:
            old_event_timestamp, old_event_type, old_event_value = self.event_history_7d.popleft()
            if old_event_type == 'MoodLogged':
                self.mood_sum_7d -= old_event_value
                self.mood_count_7d -= 1
        
        self.mood_average_7d = self.mood_sum_7d / self.mood_count_7d if self.mood_count_7d > 0 else 0.0

    def update_confidence(self, timestamp: datetime, confidence_score: float):
        # Pour simplifier, on suppose un score quotidien agrégé ou le dernier score du jour
        # Une implémentation réelle nécessiterait une agrégation quotidienne des scores de confiance
        # Ici, on ajoute simplement le score et on gère la fenêtre de 30 jours
        self.event_history_30d.append((timestamp, 'ConfidenceScore', confidence_score))
        
        thirty_days_ago = timestamp - timedelta(days=30)
        
        # Filter out old events from history
        new_event_history_30d = deque()
        for event_ts, event_type, event_val in self.event_history_30d:
            if event_ts >= thirty_days_ago:
                new_event_history_30d.append((event_ts, event_type, event_val))
        self.event_history_30d = new_event_history_30d

        # Update confidence scores deque
        self.confidence_scores_30d.clear()
        for _, _, score in self.event_history_30d:
            self.confidence_scores_30d.append(score)

        # Calcul de la tendance (simplifié pour l'exemple, une régression linéaire serait plus robuste)
        if len(self.confidence_scores_30d) > 1:
            # Très simplifié: différence entre la moyenne des 5 derniers et la moyenne des 5 premiers
            avg_last_5 = sum(list(self.confidence_scores_30d)[-5:]) / min(5, len(self.confidence_scores_30d))
            avg_first_5 = sum(list(self.confidence_scores_30d)[:5]) / min(5, len(self.confidence_scores_30d))
            self.confidence_trend = avg_last_5 - avg_first_5
        else:
            self.confidence_trend = 0.0

    def update_action(self, timestamp: datetime, action_type: str):
        self.last_action_type = action_type
        self.actions_count_7d[action_type] = self.actions_count_7d.get(action_type, 0) + 1
        # Gérer l'expiration des actions pour le compte 7d (similaire au mood)
        # Pour un système réel, il faudrait stocker les timestamps des actions pour les retirer après 7 jours.
        # Ici, on simplifie en supposant que le nettoyage est fait par un processus externe ou que la granularité est suffisante.

    def calculate_burnout_risk(self):
        # Algorithme heuristique pour le score de burnout
        # Ex: Faible humeur moyenne, tendance de confiance négative, faible activité
        risk = 0.0
        if self.mood_average_7d < 0.3: # Supposons une échelle de -1 à 1
            risk += 0.4
        if self.confidence_trend < -0.1:
            risk += 0.3
        if sum(self.actions_count_7d.values()) < 3: # Moins de 3 actions en 7 jours
            risk += 0.3
        self.burnout_risk_score = min(1.0, risk) # Score entre 0 et 1

    def update_from_event(self, event: dict):
        """
        Méthode générique pour mettre à jour l'EEV à partir d'un événement du PhoenixEventBridge.
        """
        event_type = event.get('type')
        timestamp = datetime.fromisoformat(event.get('timestamp')) # Assumer format ISO
        payload = event.get('payload', {})

        if event_type == 'MoodLogged':
            mood_score = payload.get('score')
            if mood_score is not None:
                self.update_mood(timestamp, mood_score)
        elif event_type == 'ConfidenceScoreLogged': # Nouvel événement pour la confiance
            confidence_score = payload.get('score')
            if confidence_score is not None:
                self.update_confidence(timestamp, confidence_score)
        elif event_type in ['CVGenerated', 'SkillSuggested', 'TrajectoryBuilt', 'GoalSet']:
            self.update_action(timestamp, event_type)
        
        self.calculate_burnout_risk()
        self.last_updated = datetime.now(pytz.utc)
