"""
Service d'authentification utilisant Supabase.
Gère connexion, inscription, déconnexion.
"""

import os

import streamlit as st
from dotenv import load_dotenv
from models.user import User
from supabase import Client, create_client

load_dotenv()


class AuthService:
    """Service d'authentification Supabase."""

    def __init__(self):
        """Initialise le client Supabase."""
        url: str = os.environ.get("SUPABASE_URL")
        key: str = os.environ.get("SUPABASE_KEY")

        if not url or not key:
            raise ValueError(
                "Variables SUPABASE_URL et SUPABASE_KEY requises dans .env"
            )

        self.client: Client = create_client(url, key)

    def sign_in(self, email: str, password: str) -> tuple[bool, str | None]:
        """
        Connecte un utilisateur existant.

        Returns:
            (success: bool, error_message: str | None)
        """
        try:
            response = self.client.auth.sign_in_with_password(
                {"email": email, "password": password}
            )

            if response.user:
                st.session_state["user"] = User(
                    id=response.user.id, email=response.user.email
                )
                return True, None
            else:
                return False, "Échec de connexion"

        except Exception as e:
            return False, f"Erreur de connexion : {str(e)}"

    def sign_up(self, email: str, password: str) -> tuple[bool, str | None]:
        """
        Inscrit un nouvel utilisateur.

        Returns:
            (success: bool, error_message: str | None)
        """
        try:
            response = self.client.auth.sign_up({"email": email, "password": password})

            if response.user:
                st.session_state["user"] = User(
                    id=response.user.id, email=response.user.email
                )
                return True, None
            else:
                return False, "Échec d'inscription"

        except Exception as e:
            return False, f"Erreur d'inscription : {str(e)}"

    def sign_out(self) -> bool:
        """Déconnecte l'utilisateur actuel."""
        if "user" in st.session_state:
            del st.session_state["user"]
        return True

    def get_current_user(self) -> User | None:
        """Retourne l'utilisateur actuellement connecté."""
        return st.session_state.get("user")
