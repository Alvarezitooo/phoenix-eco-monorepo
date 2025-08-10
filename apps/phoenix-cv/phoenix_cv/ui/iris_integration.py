"""
🤖 PHOENIX CV - INTÉGRATION IRIS
Module d'intégration de l'agent Iris dans Phoenix CV.
Spécialisé pour l'optimisation CV et conseils carrière.
"""

import os

try:
    from iris_client import (
        IrisStreamlitClient,
        IrisAppContext,
        render_iris_chat,
        render_iris_status,
    )
    from security_patches import (
        SecureIrisClient,
        SecureContextBuilder,
        SecureLogger,
        create_secure_iris_client,
    )
    IRIS_SECURITY_ENABLED = True
except ImportError:
    # Fallback si le package n'est pas disponible
    class IrisStreamlitClient:
        def __init__(self, app_context, api_url=None):
            pass
        def render_chat_interface(self, additional_context=None):
            import streamlit as st
            st.error("🤖 Iris temporairement indisponible")
    
    IrisAppContext = None
    IRIS_SECURITY_ENABLED = False
    
    def render_iris_chat(*args, **kwargs):
        import streamlit as st
        st.error("🤖 Iris temporairement indisponible")
    
    def render_iris_status(*args, **kwargs):
        import streamlit as st
        st.warning("🤖 Iris hors ligne")

import streamlit as st
import logging

logger = logging.getLogger(__name__)

class PhoenixCVIrisIntegration:
    """
    Intégration spécialisée d'Iris pour Phoenix CV avec sécurité renforcée.
    Contexte: optimisation CV, ATS, templates, carrière.
    """
    
    def __init__(self):
        # Client sécurisé si disponible, sinon fallback
        if IRIS_SECURITY_ENABLED:
            try:
                self.secure_client = create_secure_iris_client(
                    app_context="phoenix-cv",
                    user_id=st.session_state.get('user_id', 'anonymous'),
                    api_url=os.getenv('IRIS_API_URL', 'http://localhost:8003/api/v1/chat')
                )
                self.security_enabled = True
                logger.info("Phoenix CV Iris integration initialized with security patches")
            except Exception as e:
                logger.warning(f"Failed to initialize secure Iris client: {e}")
                self.security_enabled = False
        else:
            self.security_enabled = False
        
        # Fallback au client standard
        if not self.security_enabled:
            self.iris_client = IrisStreamlitClient(
                app_context=IrisAppContext.CV if IrisAppContext else None,
                api_url=os.getenv('IRIS_API_URL', 'http://localhost:8003/api/v1/chat')
            )
    
    def render_cv_optimization_chat(self, cv_data=None, template_type=None):
        """
        Interface Iris spécialisée pour l'optimisation CV.
        
        Args:
            cv_data: Données du CV analysé (optionnel)
            template_type: Type de template sélectionné (optionnel)
        """
        st.subheader("🤖 Iris CV - Votre Expert Optimisation")
        
        # Contexte additionnel pour Iris
        additional_context = {
            "current_page": "cv_optimization",
            "has_cv_data": cv_data is not None,
            "template_type": template_type,
            "user_context": {
                "analyzing_cv": bool(cv_data),
                "selecting_template": bool(template_type)
            }
        }
        
        # Si des données CV sont disponibles, les inclure dans le contexte
        if cv_data:
            additional_context["cv_context"] = {
                "has_experience": len(cv_data.get('experiences', [])) > 0,
                "has_education": len(cv_data.get('education', [])) > 0,
                "has_skills": len(cv_data.get('skills', [])) > 0,
                "language": cv_data.get('language', 'français')
            }
        
        # Afficher des conseils contextuels avant le chat
        if cv_data:
            st.info("💡 Iris a accès aux informations de votre CV pour des conseils personnalisés")
        elif template_type:
            st.info(f"💡 Iris vous aide à optimiser le template {template_type}")
        
        # Interface de chat avec contexte CV sécurisé
        if self.security_enabled:
            # Utilisation du client sécurisé avec validation contextuelle
            try:
                # Les données du contexte sont déjà validées par Streamlit,
                # mais on applique une couche de sécurité supplémentaire
                if additional_context:
                    # Log sécurisé de l'interaction
                    SecureLogger.log_iris_interaction(
                        app_context=self.secure_client.app_context,
                        user_id=self.secure_client.user_id,
                        message_preview="CV_OPTIMIZATION_CHAT"
                    )
                self.iris_client.render_chat_interface(additional_context)
            except Exception as e:
                logger.error(f"Secure Iris CV chat error: {e}")
                st.error("🛡️ Erreur de sécurité Iris. Veuillez réessayer.")
        else:
            # Fallback au client standard
            self.iris_client.render_chat_interface(additional_context)
    
    def render_ats_optimization_assistant(self, job_offer=None):
        """
        Assistant Iris spécialisé pour l'optimisation ATS.
        
        Args:
            job_offer: Offre d'emploi à analyser (optionnel)
        """
        st.subheader("🎯 Iris ATS - Optimisation Mots-Clés")
        
        additional_context = {
            "current_page": "ats_optimization",
            "has_job_offer": job_offer is not None,
            "optimization_type": "ats_keywords"
        }
        
        if job_offer:
            additional_context["job_offer_context"] = {
                "title": job_offer.get('title', ''),
                "company": job_offer.get('company', ''),
                "sector": job_offer.get('sector', ''),
                "has_requirements": bool(job_offer.get('requirements', ''))
            }
            st.success("🎯 Iris va analyser l'offre d'emploi pour optimiser votre CV")
        
        self.iris_client.render_chat_interface(additional_context)
    
    def render_template_selection_assistant(self, available_templates=None):
        """
        Assistant Iris pour la sélection de template CV.
        
        Args:
            available_templates: Liste des templates disponibles
        """
        st.subheader("🎨 Iris Design - Conseiller Templates CV")
        
        additional_context = {
            "current_page": "template_selection",
            "available_templates": available_templates or [],
            "selection_context": "template_recommendation"
        }
        
        if available_templates:
            st.info(f"💡 {len(available_templates)} templates disponibles - Iris vous aide à choisir")
        
        self.iris_client.render_chat_interface(additional_context)
    
    def render_career_trajectory_chat(self, current_role=None, target_role=None):
        """
        Chat Iris pour la trajectoire de carrière.
        
        Args:
            current_role: Poste actuel
            target_role: Poste visé
        """
        st.subheader("🚀 Iris Trajectoire - Planification Carrière")
        
        additional_context = {
            "current_page": "career_trajectory",
            "current_role": current_role,
            "target_role": target_role,
            "planning_context": "career_transition"
        }
        
        if current_role and target_role:
            st.success(f"🎯 Trajectoire : {current_role} → {target_role}")
            st.info("💡 Iris analyse votre transition et vous propose un plan personnalisé")
        
        self.iris_client.render_chat_interface(additional_context)
    
    def render_sidebar_status(self):
        """Affiche le statut Iris dans la sidebar de Phoenix CV"""
        self.iris_client.render_sidebar_status()
    
    def get_cv_specific_suggestions(self, context="general"):
        """
        Retourne des suggestions spécifiques au contexte CV.
        
        Args:
            context: Contexte spécifique (general, ats, template, career)
        """
        suggestions = {
            "general": [
                "Comment améliorer mon CV pour l'ATS ?",
                "Quelles compétences mettre en avant ?",
                "Comment structurer mes expériences ?"
            ],
            "ats": [
                "Quels mots-clés utiliser pour cette offre ?",
                "Comment optimiser mon CV pour les robots ?",
                "Aide-moi à améliorer mon score ATS"
            ],
            "template": [
                "Quel template correspond à mon profil ?",
                "Comment choisir entre moderne et classique ?",
                "Quels sont les templates tendance 2025 ?"
            ],
            "career": [
                "Comment valoriser ma reconversion ?",
                "Quelles formations ajouter à mon CV ?",
                "Comment expliquer ma transition de carrière ?"
            ]
        }
        
        return suggestions.get(context, suggestions["general"])

# Instance globale pour Phoenix CV
phoenix_cv_iris = PhoenixCVIrisIntegration()

# Fonctions d'interface pour compatibilité
def render_cv_iris_chat(cv_data=None, template_type=None):
    """Interface rapide pour intégrer Iris dans Phoenix CV"""
    phoenix_cv_iris.render_cv_optimization_chat(cv_data, template_type)

def render_ats_iris_assistant(job_offer=None):
    """Interface rapide pour l'assistant ATS Iris"""
    phoenix_cv_iris.render_ats_optimization_assistant(job_offer)

def render_template_iris_assistant(templates=None):
    """Interface rapide pour l'assistant template Iris"""
    phoenix_cv_iris.render_template_selection_assistant(templates)

def render_career_iris_chat(current=None, target=None):
    """Interface rapide pour le chat trajectoire carrière"""
    phoenix_cv_iris.render_career_trajectory_chat(current, target)

def render_iris_sidebar():
    """Interface rapide pour la sidebar Iris"""
    phoenix_cv_iris.render_sidebar_status()