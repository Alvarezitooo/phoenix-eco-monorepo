"""
🎨 Phoenix CV - Composant Header Sécurisé
Header réutilisable conforme Contrat d'Exécution V5

Author: Claude Phoenix DevSecOps Guardian  
Version: 4.1.0 - Monorepo Architecture
"""

import streamlit as st
from typing import Optional


class PhoenixCVHeader:
    """Composant header Phoenix CV sécurisé et réutilisable"""
    
    @staticmethod
    def render(
        title: str = "Phoenix CV", 
        subtitle: str = "Créez des CV qui se démarquent", 
        icon: str = "📄",
        show_stats: bool = True,
        custom_gradient: Optional[str] = None
    ):
        """
        Rendu header Phoenix CV avec style moderne
        
        Args:
            title: Titre principal (sanitisé)
            subtitle: Sous-titre (sanitisé)
            icon: Icône d'en-tête
            show_stats: Afficher les statistiques
            custom_gradient: Gradient CSS personnalisé
        """
        
        # 🛡️ SÉCURITÉ: Sanitisation des entrées utilisateur
        title = str(title).replace('<', '&lt;').replace('>', '&gt;')[:100]
        subtitle = str(subtitle).replace('<', '&lt;').replace('>', '&gt;')[:200]
        
        # Gradient par défaut Phoenix CV (bleu)
        gradient = custom_gradient or "linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%)"
        
        header_html = f"""
        <div style="
            background: {gradient};
            padding: 2rem;
            border-radius: 1rem;
            text-align: center;
            color: white;
            margin-bottom: 2rem;
            box-shadow: 0 8px 25px rgba(30, 58, 138, 0.3);
        ">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">{icon}</div>
            <h1 style="margin: 0 0 0.5rem 0; font-size: 2rem; font-weight: 700;">{title}</h1>
            <p style="margin: 0; opacity: 0.9; font-size: 1.1rem;">{subtitle}</p>
        </div>
        """
        
        st.markdown(header_html, unsafe_allow_html=True)
        
        # Statistiques conditionnelles
        if show_stats:
            PhoenixCVHeader._render_stats()
    
    @staticmethod
    def _render_stats():
        """Affichage des statistiques utilisateur"""
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("📄 CV Créés", value=st.session_state.get("total_cv_generated", 0))
        
        with col2:
            st.metric("🎯 Score ATS", value=f"{st.session_state.get('avg_ats_score', 75)}%")
        
        with col3:
            st.metric("📥 Downloads", value=st.session_state.get("total_downloads", 0))
    
    @staticmethod
    def render_compact(title: str = "Phoenix CV", icon: str = "📄"):
        """Version compacte du header pour les sous-pages"""
        
        # 🛡️ SÉCURITÉ: Sanitisation
        title = str(title).replace('<', '&lt;').replace('>', '&gt;')[:100]
        
        compact_html = f"""
        <div style="
            background: linear-gradient(90deg, #0ea5e9, #22d3ee);
            -webkit-background-clip: text;
            color: transparent;
            padding: 12px 0;
        ">
            <h1 style="margin: 0; font-size: 1.8rem; font-weight: 700;">{icon} {title}</h1>
        </div>
        """
        
        st.markdown(compact_html, unsafe_allow_html=True)