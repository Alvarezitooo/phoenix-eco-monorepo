"""
🤖 Widget flottant Iris pour Phoenix Letters
Composant d'assistant IA intégré en bas à droite de l'interface
"""

import streamlit as st
import requests
import json
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class IrisFloatingWidget:
    """Widget flottant pour l'assistant Iris spécialisé lettres de motivation."""
    
    def __init__(self, api_url: Optional[str] = None):
        """
        Initialise le widget Iris.
        
        Args:
            api_url: URL de l'API Iris (optionnel, utilise une valeur par défaut)
        """
        # URL de l'API Iris (sera configurée via variables d'environnement en prod)
        self.api_url = api_url or st.secrets.get("IRIS_API_URL", "")
        self.is_available = bool(self.api_url)
        
        # État du widget
        if "iris_chat_history" not in st.session_state:
            st.session_state.iris_chat_history = []
        if "iris_widget_open" not in st.session_state:
            st.session_state.iris_widget_open = False
    
    def _inject_floating_css(self):
        """Injecte le CSS pour créer le widget flottant."""
        st.markdown("""
        <style>
        /* Widget flottant Iris */
        .iris-floating-widget {
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 9999;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        /* Bouton d'ouverture/fermeture */
        .iris-toggle-btn {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
            border: none;
            cursor: pointer;
            box-shadow: 0 4px 20px rgba(79, 70, 229, 0.4);
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
            color: white;
            font-size: 24px;
        }
        
        .iris-toggle-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 25px rgba(79, 70, 229, 0.6);
        }
        
        /* Fenêtre de chat */
        .iris-chat-window {
            position: absolute;
            bottom: 80px;
            right: 0;
            width: 350px;
            height: 450px;
            background: white;
            border-radius: 16px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
            border: 1px solid #e5e7eb;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        /* Header du chat */
        .iris-chat-header {
            background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
            color: white;
            padding: 16px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        /* Zone de messages */
        .iris-chat-messages {
            flex: 1;
            padding: 16px;
            overflow-y: auto;
            background: #f8fafc;
        }
        
        /* Message bulle */
        .iris-message {
            margin-bottom: 12px;
            max-width: 80%;
        }
        
        .iris-message.user {
            margin-left: auto;
        }
        
        .iris-message.assistant {
            margin-right: auto;
        }
        
        .iris-message-bubble {
            padding: 10px 14px;
            border-radius: 12px;
            font-size: 14px;
            line-height: 1.4;
        }
        
        .iris-message.user .iris-message-bubble {
            background: #4f46e5;
            color: white;
            border-bottom-right-radius: 4px;
        }
        
        .iris-message.assistant .iris-message-bubble {
            background: white;
            border: 1px solid #e5e7eb;
            border-bottom-left-radius: 4px;
        }
        
        /* Zone de saisie */
        .iris-input-area {
            padding: 16px;
            border-top: 1px solid #e5e7eb;
            background: white;
        }
        
        .iris-status-offline {
            background: #ef4444;
            color: white;
            padding: 8px;
            text-align: center;
            font-size: 12px;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def _call_iris_api(self, message: str, context: Dict[str, Any] = None) -> str:
        """
        Appelle l'API Iris pour obtenir une réponse.
        
        Args:
            message: Message de l'utilisateur
            context: Contexte de la conversation (CV, offre, etc.)
            
        Returns:
            str: Réponse d'Iris
        """
        if not self.is_available:
            return "🤖 Désolé, je ne suis pas disponible pour le moment. Veuillez réessayer plus tard."
        
        try:
            payload = {
                "message": message,
                "context": {
                    "app": "phoenix_letters",
                    "user_context": context or {},
                    "specialization": "lettres_motivation"
                }
            }
            
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=10,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("response", "Je n'ai pas pu traiter votre demande.")
            else:
                logger.error(f"API Iris error: {response.status_code}")
                return "🤖 J'ai rencontré un problème technique. Pouvez-vous reformuler votre question ?"
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Iris API call failed: {e}")
            return "🤖 Je ne suis pas disponible actuellement. Veuillez réessayer plus tard."
    
    def _get_context(self) -> Dict[str, Any]:
        """Récupère le contexte actuel de Phoenix Letters."""
        context = {}
        
        # Ajouter le contexte CV si disponible
        if hasattr(st.session_state, 'cv_content') and st.session_state.cv_content:
            context["has_cv"] = True
        
        # Ajouter le contexte offre d'emploi si disponible
        if hasattr(st.session_state, 'job_offer_content') and st.session_state.job_offer_content:
            context["has_job_offer"] = True
            
        # Ajouter le contexte lettre générée si disponible
        if hasattr(st.session_state, 'generated_letter') and st.session_state.generated_letter:
            context["has_generated_letter"] = True
            
        return context
    
    def render(self):
        """Rend le widget flottant Iris."""
        # Injecter le CSS
        self._inject_floating_css()
        
        # Container flottant
        st.markdown("""
        <div class="iris-floating-widget">
        </div>
        """, unsafe_allow_html=True)
        
        # Logique du widget avec Streamlit
        with st.container():
            # Créer des colonnes pour positionner le widget
            cols = st.columns([1, 1, 1, 1])
            
            with cols[-1]:  # Dernière colonne (droite)
                st.write("")  # Espace pour pousser vers le bas
                
                # Bouton toggle
                if st.button("🤖" if not st.session_state.iris_widget_open else "✕", 
                           key="iris_toggle",
                           help="Assistant Iris - Spécialiste lettres de motivation"):
                    st.session_state.iris_widget_open = not st.session_state.iris_widget_open
                
                # Fenêtre de chat si ouverte
                if st.session_state.iris_widget_open:
                    with st.container():
                        # Header
                        st.markdown("**🤖 Iris - Assistant Lettres**")
                        
                        if not self.is_available:
                            st.error("🔴 Iris hors ligne")
                            st.info("💡 Iris vous aide à optimiser vos lettres de motivation, analyser des offres d'emploi, et vous conseiller pour votre reconversion.")
                        else:
                            # Zone de messages
                            messages_container = st.container()
                            with messages_container:
                                for msg in st.session_state.iris_chat_history[-5:]:  # Afficher les 5 derniers messages
                                    if msg["role"] == "user":
                                        st.markdown(f"**Vous:** {msg['content']}")
                                    else:
                                        st.markdown(f"**🤖 Iris:** {msg['content']}")
                            
                            # Zone de saisie
                            with st.form("iris_chat_form", clear_on_submit=True):
                                user_input = st.text_input(
                                    "Posez votre question à Iris...",
                                    placeholder="Ex: Comment améliorer ma lettre ?",
                                    label_visibility="collapsed"
                                )
                                
                                col1, col2 = st.columns([3, 1])
                                with col2:
                                    send_button = st.form_submit_button("📤")
                                
                                if send_button and user_input.strip():
                                    # Ajouter le message utilisateur
                                    st.session_state.iris_chat_history.append({
                                        "role": "user",
                                        "content": user_input.strip()
                                    })
                                    
                                    # Appeler Iris
                                    context = self._get_context()
                                    with st.spinner("🤖 Iris réfléchit..."):
                                        response = self._call_iris_api(user_input.strip(), context)
                                    
                                    # Ajouter la réponse d'Iris
                                    st.session_state.iris_chat_history.append({
                                        "role": "assistant", 
                                        "content": response
                                    })
                                    
                                    # Rerun pour afficher la nouvelle conversation
                                    st.rerun()
                            
                            # Boutons d'actions rapides
                            st.markdown("**Actions rapides:**")
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                if st.button("💡 Conseils", key="iris_tips"):
                                    # Auto-poser une question
                                    tips_msg = "Donne-moi 3 conseils pour améliorer ma lettre de motivation"
                                    st.session_state.iris_chat_history.append({"role": "user", "content": tips_msg})
                                    response = self._call_iris_api(tips_msg, self._get_context())
                                    st.session_state.iris_chat_history.append({"role": "assistant", "content": response})
                                    st.rerun()
                            
                            with col2:
                                if st.button("🔍 Analyser", key="iris_analyze"):
                                    analyze_msg = "Analyse le contexte actuel et donne-moi des recommandations"
                                    st.session_state.iris_chat_history.append({"role": "user", "content": analyze_msg})
                                    response = self._call_iris_api(analyze_msg, self._get_context())
                                    st.session_state.iris_chat_history.append({"role": "assistant", "content": response})
                                    st.rerun()

def render_iris_floating_widget():
    """Fonction helper pour rendre le widget Iris flottant."""
    widget = IrisFloatingWidget()
    widget.render()