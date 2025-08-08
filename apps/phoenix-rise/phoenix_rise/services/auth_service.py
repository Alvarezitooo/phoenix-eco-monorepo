"""
Service d'authentification pour Phoenix Rise.

Ce module gère les opérations d'authentification des utilisateurs
avec Supabase, y compris l'inscription, la connexion et la déconnexion.
"""

from supabase import Client
from phoenix_shared_ui.adapters import session_manager



class AuthService:
    """Service pour gérer l'authentification avec Supabase."""

    def __init__(self, client: Client):
        self.client = client

    def sign_up(self, email, password):
        """Inscrit un nouvel utilisateur."""
        try:
            auth_response = self.client.auth.sign_up({"email": email, "password": password})
            if auth_response.user:
                session_manager.set("user", auth_response.user)
                return True, None
            return False, "Erreur lors de la création de l'utilisateur."
        except Exception as e:
            # Log error instead of using st.error
            import logging
            logging.error(f"Erreur d'inscription: {e}")
            return False, "Une erreur inattendue est survenue lors de l'inscription."

    def sign_in(self, email, password):
        """Connecte un utilisateur existant."""
        try:
            auth_response = self.client.auth.sign_in_with_password(
                {"email": email, "password": password}
            )
            if auth_response.user:
                session_manager.set("user", auth_response.user)
                return True, None
            return False, "Email ou mot de passe incorrect."
        except Exception as e:
            # Log error instead of using st.error
            import logging
            logging.error(f"Erreur de connexion: {e}")
            return False, "Une erreur inattendue est survenue lors de la connexion."

    def sign_out(self):
        """Déconnecte l'utilisateur."""
        if session_manager.contains("user"):
            session_manager.delete("user")
        return self.client.auth.sign_out()

    def is_logged_in(self):
        """Vérifie si un utilisateur est connecté."""
        return session_manager.contains("user")
