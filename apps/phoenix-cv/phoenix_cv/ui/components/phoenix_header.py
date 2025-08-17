"""
🎨 Phoenix CV - Header Component Unifié
🏛️ CONSOLIDATION: Délégation vers phoenix-shared-ui

Author: Claude Phoenix DevSecOps Guardian  
Version: 4.1.0 - Reusable UI Components
"""

import streamlit as st
from typing import Dict, Any, Optional


class PhoenixCVHeader:
    """Wrapper vers phoenix-shared-ui pour compatibilité CV"""
    
    @staticmethod
    def render(
        title: str = "Phoenix CV",
        subtitle: str = "Créez des CV qui se démarquent",
        icon: str = "📄",
        show_stats: bool = True,
        custom_gradient: Optional[str] = None
    ):
        """
        Rendu header via service unifié phoenix-shared-ui
        
        Args:
            title: Titre principal
            subtitle: Sous-titre descriptif
            icon: Icône du header
            show_stats: Afficher les stats utilisateur
            custom_gradient: Gradient CSS personnalisé
        """
        
        try:
            # 🏛️ CONSOLIDATION: Utilisation header unifié
            from phoenix_shared_ui.components.header import render_cv_header
            
            # Récupérer stats utilisateur si demandé
            user_stats = None
            if show_stats:
                user_stats = PhoenixCVHeader._get_user_stats()
            
            # Déléguer au header unifié
            render_cv_header(
                title=title,
                subtitle=subtitle,
                show_stats=show_stats,
                user_stats=user_stats,
                custom_gradient=custom_gradient
            )
            
        except ImportError:
            # Fallback si phoenix-shared-ui indisponible
            st.error("❌ Phoenix Shared UI indisponible - header simplifié")
            st.markdown(f"## {icon} {title}")
            st.markdown(f"*{subtitle}*")
    
    @staticmethod
    def _get_user_stats() -> Dict[str, Any]:
        """Récupère les stats utilisateur pour le header unifié"""
        
        user_id = st.session_state.get("user_id", "anonymous")
        
        if user_id == "anonymous":
            return {}
        
        from phoenix_cv.models.phoenix_user import UserTier
        user_tier = st.session_state.get("user_tier", UserTier.FREE)
        remaining = PhoenixCVHeader._get_remaining_generations(user_tier)
        
        return {
            "CV Créés": st.session_state.get("total_cv_generated", 0),
            "Générations": remaining if remaining != -1 else "∞",
            "Score ATS": f"{st.session_state.get('avg_ats_score', 75)}%",
            "Téléchargements": st.session_state.get("total_downloads", 0)
        }
    
    @staticmethod
    def _render_user_stats():
        """Affichage stats utilisateur"""
        
        user_id = st.session_state.get("user_id", "anonymous")
        
        if user_id == "anonymous":
            return
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="💼 CV Créés",
                value=st.session_state.get("total_cv_generated", 0),
                delta=f"+{st.session_state.get('cv_this_month', 0)} ce mois"
            )
        
        with col2:
            from phoenix_cv.models.phoenix_user import UserTier
            user_tier = st.session_state.get("user_tier", UserTier.FREE)
            remaining = PhoenixCVHeader._get_remaining_generations(user_tier)
            
            st.metric(
                label="⚡ Générations restantes",
                value=remaining if remaining != -1 else "∞",
                delta="Premium" if user_tier == UserTier.PREMIUM else "Free"
            )
        
        with col3:
            st.metric(
                label="🎯 Score ATS Moyen",
                value=f"{st.session_state.get('avg_ats_score', 75)}%",
                delta="+5% vs moyenne"
            )
        
        with col4:
            st.metric(
                label="📥 Téléchargements",
                value=st.session_state.get("total_downloads", 0),
                delta="Total"
            )
    
    @staticmethod
    def _get_remaining_generations(user_tier) -> int:
        """Calcule générations restantes"""
        from phoenix_cv.models.phoenix_user import UserTier
        
        if user_tier == UserTier.PREMIUM:
            return -1  # Illimité
        return max(0, 3 - st.session_state.get("cv_generated_this_month", 0))


class PhoenixCVAlert:
    """Composant alertes Phoenix CV"""
    
    @staticmethod
    def success(message: str, title: str = "Succès", icon: str = "✅"):
        """Alerte succès"""
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            padding: 1.5rem;
            border-radius: 1rem;
            margin: 1rem 0;
            color: white;
        ">
            <h4 style="margin: 0 0 0.5rem 0;">{icon} {title}</h4>
            <p style="margin: 0; opacity: 0.9;">{message}</p>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def warning(message: str, title: str = "Attention", icon: str = "⚠️"):
        """Alerte warning"""
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
            padding: 1.5rem;
            border-radius: 1rem;
            margin: 1rem 0;
            color: white;
        ">
            <h4 style="margin: 0 0 0.5rem 0;">{icon} {title}</h4>
            <p style="margin: 0; opacity: 0.9;">{message}</p>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def error(message: str, title: str = "Erreur", icon: str = "❌"):
        """Alerte erreur"""
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
            padding: 1.5rem;
            border-radius: 1rem;
            margin: 1rem 0;
            color: white;
        ">
            <h4 style="margin: 0 0 0.5rem 0;">{icon} {title}</h4>
            <p style="margin: 0; opacity: 0.9;">{message}</p>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def info(message: str, title: str = "Information", icon: str = "ℹ️"):
        """Alerte info"""
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
            padding: 1.5rem;
            border-radius: 1rem;
            margin: 1rem 0;
            color: white;
        ">
            <h4 style="margin: 0 0 0.5rem 0;">{icon} {title}</h4>
            <p style="margin: 0; opacity: 0.9;">{message}</p>
        </div>
        """, unsafe_allow_html=True)


class PhoenixCVCard:
    """Composant cards Phoenix CV"""
    
    @staticmethod
    def render(
        title: str,
        content: str,
        icon: str = "📄",
        button_text: Optional[str] = None,
        button_key: Optional[str] = None,
        selected: bool = False
    ) -> bool:
        """
        Rendu card Phoenix CV
        
        Returns:
            bool: True si le bouton a été cliqué
        """
        
        border_color = "#3b82f6" if selected else "#e5e7eb"
        background = "#eff6ff" if selected else "white"
        
        card_html = f"""
        <div style="
            border: 2px solid {border_color};
            border-radius: 1rem;
            padding: 1.5rem;
            margin: 1rem 0;
            background: {background};
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
        ">
            <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                <span style="font-size: 1.5rem; margin-right: 0.5rem;">{icon}</span>
                <h3 style="margin: 0; color: #1e3a8a; font-weight: 600;">{title}</h3>
            </div>
            <p style="margin: 0; color: #6b7280; line-height: 1.5;">{content}</p>
        </div>
        """
        
        st.markdown(card_html, unsafe_allow_html=True)
        
        # Bouton optionnel
        if button_text and button_key:
            return st.button(button_text, key=button_key, use_container_width=True)
        
        return False