"""
Service de base de données pour Phoenix Rise.
Gère toutes les interactions avec Supabase PostgreSQL.
"""

import streamlit as st
from supabase import Client
from typing import List, Dict
from datetime import timedelta
from utils.security import InputValidator, DataAnonymizer

class DBService:
    """Service de gestion des données utilisateur."""
    
    def __init__(self, client: Client):
        """Initialise avec le client Supabase."""
        self.client = client

    def get_mood_entries(self, user_id: str) -> List[Dict]:
        """
        Récupère les entrées d'humeur de l'utilisateur.
        
        Args:
            user_id: ID de l'utilisateur (validé)
            
        Returns:
            Liste des entrées d'humeur
        """
        try:
            # Validation sécurisée de l'user_id
            if not user_id or not isinstance(user_id, str) or len(user_id) < 10:
                st.error("🔒 Identifiant utilisateur invalide")
                return []
            
            response = self.client.table('mood_entries').select("*").eq(
                'user_id', user_id
            ).order('created_at', desc=True).limit(30).execute()
            
            return response.data or []
            
        except Exception as e:
            # Log sécurisé sans exposition d'informations sensibles
            st.error("🔒 Erreur de récupération des données. Veuillez réessayer.")
            return []

    def add_mood_entry(self, user_id: str, mood: int, energy: int, confidence: int, notes: str) -> Dict:
        """
        Ajoute une nouvelle entrée d'humeur avec validation sécurisée.
        
        Args:
            user_id: ID de l'utilisateur (UUID validé)
            mood: Score d'humeur (1-10)
            energy: Niveau d'énergie (1-10) 
            confidence: Niveau de confiance (1-10)
            notes: Notes optionnelles (sécurisées)
            
        Returns:
            Dictionnaire avec success et data/error
        """
        try:
            # Validation sécurisée de tous les inputs
            if not InputValidator.validate_user_id(user_id):
                return {"success": False, "error": "Identifiant utilisateur invalide"}
            
            mood = InputValidator.validate_mood_score(mood)
            energy = InputValidator.validate_mood_score(energy)
            confidence = InputValidator.validate_mood_score(confidence)
            
            if mood is None or energy is None or confidence is None:
                return {"success": False, "error": "Scores invalides (doivent être entre 1 et 10)"}
            
            # Nettoyage sécurisé des notes (protection XSS)
            safe_notes = InputValidator.sanitize_text(notes, max_length=500)
            
            response = self.client.table('mood_entries').insert({
                "user_id": user_id,
                "mood_score": mood,
                "energy_level": energy,
                "confidence_level": confidence,
                "notes": safe_notes
            }).execute()
            
            return {
                "success": True, 
                "data": response.data[0] if response.data else None
            }
            
        except Exception as e:
            # Log sécurisé sans exposition de données sensibles
            st.error("🔒 Erreur lors de l'enregistrement. Veuillez réessayer.")
            return {"success": False, "error": "Erreur de sauvegarde"}

    def get_user_stats(self, user_id: str) -> Dict:
        """
        Calcule les statistiques utilisateur.
        
        Returns:
            Dictionnaire avec moyennes et tendances
        """
        entries = self.get_mood_entries(user_id)
        
        if not entries:
            return {"total_entries": 0}
        
        mood_scores = [entry['mood_score'] for entry in entries]
        confidence_scores = [entry['confidence_level'] for entry in entries]
        
        return {
            "total_entries": len(entries),
            "avg_mood": round(sum(mood_scores) / len(mood_scores), 1),
            "avg_confidence": round(sum(confidence_scores) / len(confidence_scores), 1),
            "trend": "📈" if len(entries) > 1 and mood_scores[0] > mood_scores[-1] else "➡️"
        }
