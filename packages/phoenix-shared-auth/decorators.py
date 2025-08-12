from functools import wraps
import streamlit as st
from packages.phoenix_shared_ui.components.upgrade_prompt import render_upgrade_prompt
from .entities.phoenix_user import UserTier

def premium_feature(feature_name: str):
    """
    Décorateur pour protéger une fonctionnalité et la réserver aux utilisateurs Premium.
    Affiche un message d'incitation si l'utilisateur n'a pas le bon niveau.

    Args:
        feature_name: Le nom de la fonctionnalité qui sera affiché à l'utilisateur.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Vérifier si l'utilisateur est connecté et si son tier est premium
            user = st.session_state.get('phoenix_user')
            is_premium = user and user.subscription.current_tier == UserTier.PREMIUM

            if is_premium:
                # Si l'utilisateur est premium, exécuter la fonctionnalité
                return func(*args, **kwargs)
            else:
                # Sinon, afficher le message pour passer au premium
                render_upgrade_prompt(feature_name)
                return None
        return wrapper
    return decorator