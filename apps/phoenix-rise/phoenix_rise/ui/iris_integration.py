"""
🤖 PHOENIX RISE - INTÉGRATION IRIS
Module d'intégration de l'agent Iris dans Phoenix Rise.
Spécialisé pour l'accompagnement développement personnel et reconversion.
"""

import os

try:
    from iris_client import (
        IrisStreamlitClient,
        IrisAppContext,
        render_iris_chat,
        render_iris_status,
    )
except ImportError:
    # Fallback si le package n'est pas disponible
    class IrisStreamlitClient:
        def __init__(self, app_context, api_url=None):
            self.app_context = app_context
            self.api_url = api_url
        def render_chat_interface(self, additional_context=None):
            import streamlit as st
            st.error("🤖 Iris temporairement indisponible")
    
    IrisAppContext = None
    
    def render_iris_chat(*args, **kwargs):
        import streamlit as st
        st.error("🤖 Iris temporairement indisponible")
    
    def render_iris_status(*args, **kwargs):
        import streamlit as st
        st.warning("🤖 Iris hors ligne")

import streamlit as st
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class PhoenixRiseIrisIntegration:
    """
    Intégration spécialisée d'Iris pour Phoenix Rise.
    Contexte: développement personnel, reconversion, coaching, journal.
    """
    
    def __init__(self):
        self.iris_client = IrisStreamlitClient(
            app_context=IrisAppContext.RISE,
            api_url=os.getenv('IRIS_API_URL', 'http://localhost:8003/api/v1/chat')
        )
    
    def render_personal_coaching_chat(self, journal_entries=None, mood_data=None):
        """
        Interface Iris spécialisée pour le coaching personnel.
        
        Args:
            journal_entries: Entrées récentes du journal (optionnel)
            mood_data: Données d'humeur/émotions (optionnel)
        """
        st.subheader("🤖 Iris Coach - Accompagnement Personnel")
        
        # Contexte additionnel pour Iris
        additional_context = {
            "current_page": "personal_coaching",
            "has_journal_entries": journal_entries is not None,
            "has_mood_data": mood_data is not None,
            "coaching_type": "personal_development",
            "user_context": {
                "journaling_active": bool(journal_entries),
                "mood_tracking": bool(mood_data)
            }
        }
        
        # Si des entrées de journal sont disponibles
        if journal_entries:
            recent_entries_count = len(journal_entries)
            additional_context["journal_context"] = {
                "recent_entries_count": recent_entries_count,
                "last_entry_date": journal_entries[0].get('created_at') if journal_entries else None,
                "journaling_frequency": "regular" if recent_entries_count > 3 else "occasional"
            }
            st.info(f"💡 Iris a accès à vos {recent_entries_count} dernières entrées de journal pour un coaching personnalisé")
        
        # Si des données d'humeur sont disponibles
        if mood_data:
            additional_context["mood_context"] = {
                "current_mood": mood_data.get('current_mood'),
                "energy_level": mood_data.get('energy_level'),
                "stress_level": mood_data.get('stress_level')
            }
        
        # Interface de chat avec contexte coaching
        self.iris_client.render_chat_interface(additional_context)
    
    def render_reconversion_assistant(self, career_goals=None, progress_data=None):
        """
        Assistant Iris spécialisé pour l'accompagnement reconversion.
        
        Args:
            career_goals: Objectifs de reconversion
            progress_data: Données de progression
        """
        st.subheader("🚀 Iris Reconversion - Stratégie & Progression")
        
        additional_context = {
            "current_page": "reconversion_planning",
            "has_career_goals": career_goals is not None,
            "has_progress_data": progress_data is not None,
            "coaching_type": "career_transition"
        }
        
        if career_goals:
            additional_context["career_context"] = {
                "current_field": career_goals.get('current_field', ''),
                "target_field": career_goals.get('target_field', ''),
                "timeline": career_goals.get('timeline', ''),
                "key_challenges": career_goals.get('challenges', [])
            }
            st.success("🎯 Iris adapte ses conseils à votre projet de reconversion")
        
        if progress_data:
            additional_context["progress_context"] = {
                "completed_steps": progress_data.get('completed_steps', 0),
                "current_phase": progress_data.get('current_phase', ''),
                "success_rate": progress_data.get('success_rate', 0)
            }
        
        self.iris_client.render_chat_interface(additional_context)
    
    def render_emotional_support_chat(self, recent_mood=None, challenges=None):
        """
        Chat Iris pour le soutien émotionnel et gestion du stress.
        
        Args:
            recent_mood: Humeur récente
            challenges: Défis actuels
        """
        st.subheader("💖 Iris Bien-être - Soutien Émotionnel")
        
        additional_context = {
            "current_page": "emotional_support",
            "recent_mood": recent_mood,
            "current_challenges": challenges,
            "support_type": "emotional_wellness"
        }
        
        if recent_mood:
            mood_emoji = {
                "excellent": "😄", "good": "😊", "neutral": "😐", 
                "stressed": "😰", "overwhelmed": "😵", "sad": "😢"
            }
            mood_display = mood_emoji.get(recent_mood, "😐")
            st.info(f"💡 Humeur actuelle : {mood_display} {recent_mood.title()}")
        
        if challenges:
            st.info("💡 Iris vous accompagne face à vos défis actuels")
        
        self.iris_client.render_chat_interface(additional_context)
    
    def render_goal_setting_assistant(self, current_goals=None, achievements=None):
        """
        Assistant Iris pour la définition et suivi d'objectifs.
        
        Args:
            current_goals: Objectifs actuels
            achievements: Réalisations récentes
        """
        st.subheader("🎯 Iris Objectifs - Planification & Suivi")
        
        additional_context = {
            "current_page": "goal_setting",
            "has_current_goals": current_goals is not None,
            "has_achievements": achievements is not None,
            "planning_type": "goal_management"
        }
        
        if current_goals:
            additional_context["goals_context"] = {
                "active_goals_count": len(current_goals),
                "goal_categories": [goal.get('category') for goal in current_goals],
                "progress_overview": "in_progress"
            }
            st.success(f"🎯 {len(current_goals)} objectifs actifs suivis par Iris")
        
        if achievements:
            st.success(f"🏆 {len(achievements)} réalisations récentes à célébrer !")
        
        self.iris_client.render_chat_interface(additional_context)
    
    def render_daily_reflection_chat(self, today_entry=None):
        """
        Chat Iris pour la réflexion quotidienne et l'introspection.
        
        Args:
            today_entry: Entrée du jour dans le journal
        """
        st.subheader("🌅 Iris Réflexion - Introspection Quotidienne")
        
        additional_context = {
            "current_page": "daily_reflection",
            "has_today_entry": today_entry is not None,
            "reflection_type": "daily_introspection",
            "date": datetime.now().strftime("%Y-%m-%d")
        }
        
        if today_entry:
            additional_context["reflection_context"] = {
                "entry_length": len(today_entry.get('content', '')),
                "mood_logged": today_entry.get('mood') is not None,
                "goals_mentioned": 'objectif' in today_entry.get('content', '').lower()
            }
            st.info("💡 Iris vous aide à approfondir votre réflexion du jour")
        else:
            st.info("💡 Iris vous guide dans votre introspection quotidienne")
        
        self.iris_client.render_chat_interface(additional_context)
    
    def render_sidebar_status(self):
        """Affiche le statut Iris dans la sidebar de Phoenix Rise"""
        self.iris_client.render_sidebar_status()
    
    def get_rise_specific_suggestions(self, context="general"):
        """
        Retourne des suggestions spécifiques au contexte Rise.
        
        Args:
            context: Contexte spécifique (general, emotional, career, goals, reflection)
        """
        suggestions = {
            "general": [
                "Comment progresser dans ma reconversion ?",
                "Quels objectifs me fixer cette semaine ?",
                "Comment gérer mes émotions ?"
            ],
            "emotional": [
                "Comment gérer mon stress de reconversion ?",
                "Aide-moi à retrouver confiance en moi",
                "Comment surmonter mes peurs ?"
            ],
            "career": [
                "Quelle stratégie pour ma transition ?",
                "Comment identifier mes compétences transférables ?",
                "Aide-moi à définir mon projet professionnel"
            ],
            "goals": [
                "Comment définir des objectifs SMART ?",
                "Aide-moi à prioriser mes actions",
                "Comment mesurer mes progrès ?"
            ],
            "reflection": [
                "Que retenir de ma journée ?",
                "Comment analyser mes réussites ?",
                "Quelles leçons tirer de mes difficultés ?"
            ]
        }
        
        return suggestions.get(context, suggestions["general"])

# Instance globale pour Phoenix Rise
phoenix_rise_iris = PhoenixRiseIrisIntegration()

# Fonctions d'interface pour compatibilité
def render_coaching_iris_chat(journal_entries=None, mood_data=None):
    """Interface rapide pour le coaching personnel"""
    phoenix_rise_iris.render_personal_coaching_chat(journal_entries, mood_data)

def render_reconversion_iris_assistant(career_goals=None, progress_data=None):
    """Interface rapide pour l'assistant reconversion"""
    phoenix_rise_iris.render_reconversion_assistant(career_goals, progress_data)

def render_emotional_iris_chat(recent_mood=None, challenges=None):
    """Interface rapide pour le soutien émotionnel"""
    phoenix_rise_iris.render_emotional_support_chat(recent_mood, challenges)

def render_goals_iris_assistant(current_goals=None, achievements=None):
    """Interface rapide pour l'assistant objectifs"""
    phoenix_rise_iris.render_goal_setting_assistant(current_goals, achievements)

def render_reflection_iris_chat(today_entry=None):
    """Interface rapide pour la réflexion quotidienne"""
    phoenix_rise_iris.render_daily_reflection_chat(today_entry)

def render_iris_sidebar():
    """Interface rapide pour la sidebar Iris"""
    phoenix_rise_iris.render_sidebar_status()