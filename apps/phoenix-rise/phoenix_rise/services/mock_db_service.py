"""
Service de base de données simulé pour Phoenix Rise.

Ce module fournit une implémentation d'un service de base de données
utilisant st.session_state pour le stockage temporaire des données,
permettant un développement rapide sans dépendance à une base de données réelle.
"""

import uuid
from typing import Any, Dict, List

import streamlit as st
from models.journal_entry import JournalEntry


class MockDBService:
    """
    Service de base de données simulé utilisant st.session_state.
    Permet un développement rapide sans dépendance à Supabase.
    """

    def __init__(self):
        if "mock_db" not in st.session_state:
            st.session_state.mock_db = {
                "profiles": {},
                "objectives": {},
                "journal_entries": {},
            }

    def get_profile(self, user_id: str) -> Dict[str, Any]:
        """Récupère un profil utilisateur simulé."""
        return st.session_state.mock_db["profiles"].get(user_id)

    def create_profile(
        self, user_id: str, email: str, full_name: str = None
    ) -> Dict[str, Any]:
        """Crée un profil utilisateur simulé."""
        if user_id in st.session_state.mock_db["profiles"]:
            return st.session_state.mock_db["profiles"][user_id]

        new_profile = {
            "id": user_id,
            "email": email,
            "full_name": full_name or email.split("@")[0],
            "created_at": "now()",
        }
        st.session_state.mock_db["profiles"][user_id] = new_profile
        return new_profile

    def get_objectives(self, user_id: str) -> list:
        """Récupère les objectifs d'un utilisateur."""
        return st.session_state.mock_db["objectives"].get(user_id, [])

    def add_objective(self, user_id: str, objective: str) -> list:
        """Ajoute un objectif pour un utilisateur."""
        if user_id not in st.session_state.mock_db["objectives"]:
            st.session_state.mock_db["objectives"][user_id] = []
        st.session_state.mock_db["objectives"][user_id].append(objective)
        return st.session_state.mock_db["objectives"][user_id]

    def add_journal_entry(
        self, user_id: str, mood: int, confidence: int, notes: str
    ) -> JournalEntry:
        """Ajoute une entrée de journal pour un utilisateur."""
        if user_id not in st.session_state.mock_db["journal_entries"]:
            st.session_state.mock_db["journal_entries"][user_id] = []

        new_entry = JournalEntry(
            id=str(uuid.uuid4()),
            user_id=user_id,
            mood=mood,
            confidence=confidence,
            notes=notes,
        )

        st.session_state.mock_db["journal_entries"][user_id].insert(
            0, new_entry
        )  # Ajoute au début
        return new_entry

    def get_journal_entries(self, user_id: str) -> List[JournalEntry]:
        """Récupère les entrées de journal d'un utilisateur."""
        return st.session_state.mock_db["journal_entries"].get(user_id, [])
