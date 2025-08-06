"""
🤖 IRIS STREAMLIT CLIENT - Client Iris optimisé pour Streamlit
Interface Streamlit pour l'agent Iris avec gestion d'état et UI sécurisée.
"""

import logging
from typing import Optional, Dict, Any, List

import streamlit as st

from .base_client import IrisBaseClient, IrisAppContext, IrisMessage

logger = logging.getLogger(__name__)

class IrisStreamlitClient:
    """
    Client Iris optimisé pour Streamlit avec gestion d'état intégrée.
    """
    
    def __init__(self, app_context: IrisAppContext, api_url: str = "http://localhost:8003/api/v1/chat"):
        self.app_context = app_context
        self.base_client = IrisBaseClient(api_url=api_url, app_context=app_context)
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        """Initialise l'état de session Streamlit pour Iris"""
        session_key = f"iris_messages_{self.app_context.value}"
        if session_key not in st.session_state:
            st.session_state[session_key] = []
    
    def _get_messages(self) -> List[IrisMessage]:
        """Récupère les messages de la session"""
        session_key = f"iris_messages_{self.app_context.value}"
        return st.session_state[session_key]
    
    def _add_message(self, role: str, content: str):
        """Ajoute un message à l'historique"""
        session_key = f"iris_messages_{self.app_context.value}"
        message = IrisMessage(
            role=role, 
            content=content, 
            app_context=self.app_context
        )
        st.session_state[session_key].append(message)
    
    def get_user_auth_token(self) -> Optional[str]:
        """Récupère le token d'authentification de l'utilisateur Phoenix"""
        if 'authenticated_user' not in st.session_state:
            return None
        return st.session_state.get('access_token')
    
    def is_user_authenticated(self) -> bool:
        """Vérifie si l'utilisateur est authentifié"""
        return self.get_user_auth_token() is not None
    
    def get_user_tier(self) -> str:
        """Récupère le tier de l'utilisateur"""
        return st.session_state.get('user_tier', 'FREE')
    
    def render_authentication_prompt(self):
        """Affiche l'invite de connexion contextuelle à l'app"""
        app_contexts = {
            IrisAppContext.LETTERS: {
                "icon": "✍️",
                "title": "Iris Lettres",
                "description": "Optimisez vos lettres de motivation avec l'IA"
            },
            IrisAppContext.CV: {
                "icon": "📋", 
                "title": "Iris CV",
                "description": "Améliorez votre CV et maximisez vos chances"
            },
            IrisAppContext.RISE: {
                "icon": "🌱",
                "title": "Iris Coach", 
                "description": "Accompagnement personnalisé de votre reconversion"
            },
            IrisAppContext.WEBSITE: {
                "icon": "🚀",
                "title": "Iris Phoenix",
                "description": "Découvrez l'écosystème Phoenix avec votre guide IA"
            }
        }
        
        context = app_contexts.get(self.app_context, app_contexts[IrisAppContext.LETTERS])
        
        st.warning(f"🔒 Connectez-vous pour accéder à {context['title']}")
        st.info(f"{context['icon']} {context['description']}")
        
        # Suggestions sans authentification
        with st.expander("💡 Aperçu des capacités d'Iris"):
            suggestions = self.base_client.get_app_specific_suggestions()
            for suggestion in suggestions[:3]:  # Limite à 3 suggestions
                st.write(f"• {suggestion}")
    
    def render_tier_info(self):
        """Affiche les informations du tier utilisateur"""
        user_tier = self.get_user_tier()
        
        if user_tier == 'FREE':
            st.info("🎆 Version FREE : 5 messages/jour | 🚀 [Passer à PREMIUM](/premium)")
        elif user_tier == 'PREMIUM':
            st.success("🎆 Version PREMIUM : Accès illimité à Iris")
        elif user_tier == 'ENTERPRISE':
            st.success("🎆 Version ENTERPRISE : Accès illimité + fonctionnalités avancées")
    
    def render_chat_interface(self, additional_context: Optional[Dict[str, Any]] = None):
        """
        Rend l'interface de chat Iris complète.
        
        Args:
            additional_context: Contexte additionnel spécifique à l'app
        """
        # Vérification authentification
        if not self.is_user_authenticated():
            self.render_authentication_prompt()
            return
        
        # Titre contextuel
        app_titles = {
            IrisAppContext.LETTERS: "🤖 Iris Lettres - Expert Lettres de Motivation",
            IrisAppContext.CV: "🤖 Iris CV - Optimisation CV & Carrière", 
            IrisAppContext.RISE: "🤖 Iris Coach - Accompagnement Reconversion",
            IrisAppContext.WEBSITE: "🤖 Iris Phoenix - Guide Écosystème"
        }
        
        st.subheader(app_titles.get(self.app_context, "🤖 Iris - Assistant IA"))
        
        # Info tier utilisateur
        self.render_tier_info()
        
        # Historique des messages
        messages = self._get_messages()
        for message in messages:
            with st.chat_message(message.role):
                st.markdown(message.content)
        
        # Input utilisateur
        if prompt := st.chat_input(f"Posez votre question à Iris..."):
            # Ajouter message utilisateur
            self._add_message("user", prompt)
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Générer réponse IA
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                with st.spinner("Iris réfléchit..."):
                    auth_token = self.get_user_auth_token()
                    response = self.base_client.send_message_sync(
                        prompt, 
                        auth_token, 
                        additional_context
                    )
                    
                    # Gestion des différents statuts
                    if response.status == "auth_error":
                        st.error("🔒 Session expirée. Reconnectez-vous pour continuer.")
                        # Clear session to force re-auth
                        if 'access_token' in st.session_state:
                            del st.session_state['access_token']
                        st.rerun()
                        return
                    elif response.status == "quota_exceeded":
                        st.error("📊 Limite quotidienne atteinte.")
                        st.info("Passez à PREMIUM pour un accès illimité à Iris.")
                    elif response.status == "rate_limited":
                        st.warning("⏳ Trop de requêtes. Patientez quelques instants.")
                    elif response.status == "access_denied":
                        st.error("💫 Accès refusé. Vérifiez votre email ou contactez le support.")
                    elif response.status == "service_unavailable":
                        st.error("😢 Iris est temporairement indisponible.")
                    
                    message_placeholder.markdown(response.reply)
                    
                    # Ajouter réponse à l'historique
                    self._add_message("assistant", response.reply)
        
        # Suggestions contextuelles
        self._render_suggestions()
    
    def _render_suggestions(self):
        """Affiche les suggestions contextuelles"""
        suggestions = self.base_client.get_app_specific_suggestions()
        
        if suggestions:
            st.markdown("---")
            st.markdown("💡 **Suggestions de questions :**")
            
            # Afficher 2 suggestions aléatoires en colonnes
            import random
            selected_suggestions = random.sample(suggestions, min(2, len(suggestions)))
            
            col1, col2 = st.columns(2)
            for i, suggestion in enumerate(selected_suggestions):
                col = col1 if i % 2 == 0 else col2
                with col:
                    if st.button(suggestion, key=f"suggestion_{i}_{self.app_context.value}"):
                        # Simuler l'envoi du message
                        st.rerun()
    
    def render_sidebar_status(self):
        """Affiche le statut Iris dans la sidebar"""
        with st.sidebar:
            st.markdown("### 🤖 Iris - Statut")
            
            if self.is_user_authenticated():
                st.success("✅ Connecté à Iris")
                user_tier = self.get_user_tier()
                
                if user_tier == 'FREE':
                    st.info("🎆 Plan FREE\n5 messages/jour")
                    st.markdown("[Passer à PREMIUM 🚀](/premium)")
                elif user_tier == 'PREMIUM':
                    st.success("🎆 Plan PREMIUM\nAccès illimité")
                
                # Conseils contextuels
                app_tips = {
                    IrisAppContext.LETTERS: "Partagez l'offre d'emploi pour des conseils personnalisés",
                    IrisAppContext.CV: "Mentionnez votre secteur cible pour de meilleurs conseils",
                    IrisAppContext.RISE: "Soyez honnête sur vos émotions pour un accompagnement adapté",
                    IrisAppContext.WEBSITE: "Explorez toutes les applications Phoenix"
                }
                
                tip = app_tips.get(self.app_context, "Soyez spécifique dans vos questions")
                st.info(f"💡 **Conseil :** {tip}")
            else:
                st.warning("⚠️ Non connecté")
                st.info("Connectez-vous pour accéder à Iris")

# Fonctions utilitaires pour compatibilité avec l'existant
def render_iris_chat(
    app_context: IrisAppContext,
    additional_context: Optional[Dict[str, Any]] = None,
    api_url: str = "http://localhost:8003/api/v1/chat"
):
    """
    Fonction utilitaire pour rendre rapidement un chat Iris.
    Compatible avec l'interface existante de phoenix-letters.
    """
    client = IrisStreamlitClient(app_context, api_url)
    client.render_chat_interface(additional_context)

def render_iris_status(
    app_context: IrisAppContext,
    api_url: str = "http://localhost:8003/api/v1/chat"
):
    """
    Fonction utilitaire pour rendre le statut Iris dans la sidebar.
    """
    client = IrisStreamlitClient(app_context, api_url)
    client.render_sidebar_status()