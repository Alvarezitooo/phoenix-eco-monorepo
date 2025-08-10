"""
Service de base de données simulé pour Phoenix Rise.

Ce module fournit une implémentation d'un service de base de données
utilisant session_manager pour le stockage temporaire des données,
permettant un développement rapide sans dépendance à une base de données réelle.
"""

import uuid
from typing import Any, Dict, List

from phoenix_shared_ui.adapters.session_adapter import session_manager
from phoenix_rise.models.journal_entry import JournalEntry


class MockDBService:
    """
    Service de base de données simulé utilisant session_manager.
    Permet un développement rapide sans dépendance à Supabase.
    """

    def __init__(self):
        if not session_manager.contains("mock_db"):
            session_manager.set("mock_db", {
                "profiles": {},
                "objectives": {},
                "journal_entries": {},
            })

    def get_profile(self, user_id: str) -> Dict[str, Any]:
        """Récupère un profil utilisateur simulé."""
        mock_db = session_manager.get("mock_db", {})
        return mock_db["profiles"].get(user_id)

    def create_profile(
        self, user_id: str, email: str, full_name: str = None
    ) -> Dict[str, Any]:
        """Crée un profil utilisateur simulé."""
        mock_db = session_manager.get("mock_db", {})
        if user_id in mock_db["profiles"]:
            return mock_db["profiles"][user_id]

        new_profile = {
            "id": user_id,
            "email": email,
            "full_name": full_name or email.split("@")[0],
            "created_at": "now()",
        }
        mock_db["profiles"][user_id] = new_profile
        session_manager.set("mock_db", mock_db)
        return new_profile

    def get_objectives(self, user_id: str) -> list:
        """Récupère les objectifs d'un utilisateur."""
        mock_db = session_manager.get("mock_db", {})
        return mock_db["objectives"].get(user_id, [])

    def add_objective(self, user_id: str, objective: str) -> list:
        """Ajoute un objectif pour un utilisateur."""
        mock_db = session_manager.get("mock_db", {})
        if user_id not in mock_db["objectives"]:
            mock_db["objectives"][user_id] = []
        mock_db["objectives"][user_id].append(objective)
        session_manager.set("mock_db", mock_db)
        return mock_db["objectives"][user_id]

    def add_journal_entry(
        self, user_id: str, mood: int, confidence: int, notes: str
    ) -> JournalEntry:
        """Ajoute une entrée de journal pour un utilisateur."""
        mock_db = session_manager.get("mock_db", {})
        if user_id not in mock_db["journal_entries"]:
            mock_db["journal_entries"][user_id] = []

        new_entry = JournalEntry(
            id=str(uuid.uuid4()),
            user_id=user_id,
            mood=mood,
            confidence=confidence,
            notes=notes,
        )

        mock_db["journal_entries"][user_id].insert(
            0, new_entry
        )  # Ajoute au début
        session_manager.set("mock_db", mock_db)
        return new_entry

    def get_journal_entries(self, user_id: str, limit: int = 50) -> List[JournalEntry]:
        """Récupère les entrées de journal d'un utilisateur."""
        mock_db = session_manager.get("mock_db", {})
        entries = mock_db["journal_entries"].get(user_id, [])
        return entries[:limit]  # Limiter le nombre d'entrées retournées

    def create_journal_entry(
        self, user_id: str, mood: int, confidence: int, notes: str = None
    ) -> JournalEntry:
        """Crée une nouvelle entrée de journal (méthode manquante)."""
        return self.add_journal_entry(user_id, mood, confidence, notes)

    def create_objective(
        self,
        user_id: str,
        title: str,
        description: str = None,
        objective_type: str = "personal",
        target_date: str = None,
    ) -> Dict[str, Any]:
        """Crée un nouvel objectif."""
        objective = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": title,
            "description": description,
            "objective_type": objective_type,
            "target_date": target_date,
            "created_at": "now()",
            "status": "active"
        }
        
        mock_db = session_manager.get("mock_db", {})
        if user_id not in mock_db["objectives"]:
            mock_db["objectives"][user_id] = []
        
        mock_db["objectives"][user_id].append(objective)
        session_manager.set("mock_db", mock_db)
        return objective

    def update_objective(
        self, user_id: str, objective_id: str, updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Met à jour un objectif."""
        mock_db = session_manager.get("mock_db", {})
        objectives = mock_db["objectives"].get(user_id, [])
        for objective in objectives:
            if objective.get("id") == objective_id:
                objective.update(updates)
                session_manager.set("mock_db", mock_db)
                return objective
        return None

    def delete_objective(self, user_id: str, objective_id: str) -> bool:
        """Supprime un objectif."""
        mock_db = session_manager.get("mock_db", {})
        objectives = mock_db["objectives"].get(user_id, [])
        for i, objective in enumerate(objectives):
            if objective.get("id") == objective_id:
                del objectives[i]
                session_manager.set("mock_db", mock_db)
                return True
        return False

    def get_journal_stats(self, user_id: str) -> Dict[str, Any]:
        """Récupère les statistiques du journal d'un utilisateur."""
        entries = self.get_journal_entries(user_id)
        
        if not entries:
            return {
                "total_entries": 0,
                "avg_mood": 0.0,
                "avg_confidence": 0.0,
                "mood_trend": 0.0
            }
        
        moods = [entry.mood for entry in entries]
        confidences = [entry.confidence for entry in entries]
        
        return {
            "total_entries": len(entries),
            "avg_mood": sum(moods) / len(moods),
            "avg_confidence": sum(confidences) / len(confidences),
            "mood_trend": (moods[-1] - moods[0]) if len(moods) > 1 else 0.0
        }