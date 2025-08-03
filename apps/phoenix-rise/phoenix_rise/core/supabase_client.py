"""
Module pour l'initialisation du client Supabase.

Ce module gère la configuration et la création d'une instance du client Supabase
en utilisant les variables d'environnement.
"""

import os

from dotenv import load_dotenv
from supabase import Client, create_client

# Charger les variables d'environnement du fichier .env
load_dotenv()


def get_supabase_client() -> Client:
    """
    Initialise et retourne le client Supabase en lisant les variables d'environnement.
    Lève une exception si les variables ne sont pas configurées.
    """
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        raise ValueError(
            "Les variables d'environnement SUPABASE_URL et SUPABASE_KEY sont requises."
        )

    return create_client(supabase_url, supabase_key)


# Instance globale du client pour être réutilisée dans l'application
supabase_client = get_supabase_client()
