"""
🎨 Phoenix CV - Composants Premium Réutilisables
Composants premium barriers et upgrade flows style Phoenix Letters

Author: Claude Phoenix DevSecOps Guardian  
Version: 4.1.0 - Premium Components
"""

import streamlit as st
from typing import Dict, Any, Optional, List
from phoenix_cv.models.phoenix_user import UserTier


class PhoenixCVPremiumBarrier:
    """Composant barrier premium Phoenix CV"""
    
    @staticmethod
    def render(
        feature_name: str,
        description: str,
        benefits: Optional[List[str]] = None,
        cta_text: str = "🔥 Passer Premium - 9,99€/mois",
        show_comparison: bool = False
    ):
        """
        Rendu barrier premium avec style Phoenix Letters
        
        Args:
            feature_name: Nom de la fonctionnalité
            description: Description de la fonctionnalité  
            benefits: Liste des bénéfices (optionnel)
            cta_text: Texte du bouton CTA
            show_comparison: Afficher tableau comparatif
        """
        
        # Header premium
        premium_html = f"""
        <div style="
            background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
            padding: 2rem;
            border-radius: 1rem;
            text-align: center;
            color: white;
            margin: 1rem 0;
            box-shadow: 0 8px 25px rgba(245, 158, 11, 0.3);
        ">
            <h3 style="margin: 0 0 0.5rem 0; font-size: 1.5rem;">🔐 {feature_name}</h3>
            <p style="margin: 0 0 1rem 0; opacity: 0.9; font-size: 1.1rem;">{description}</p>
            
            <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 0.5rem; margin: 1rem 0;">
                <p style="margin: 0; font-weight: 600; font-size: 1rem;">✨ Inclus dans Phoenix Premium</p>
            </div>
        </div>
        """
        
        st.markdown(premium_html, unsafe_allow_html=True)
        
        # Bénéfices si fournis
        if benefits:
            PhoenixCVPremiumBarrier._render_benefits(benefits)
        
        # Tableau comparatif si demandé
        if show_comparison:
            PhoenixCVPremiumBarrier._render_comparison_table()
        
        # CTA Button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button(cta_text, type="primary", use_container_width=True):
                PhoenixCVPremiumBarrier._handle_premium_upgrade()
    
    @staticmethod
    def _render_benefits(benefits: List[str]):
        """Affichage des bénéfices"""
        
        st.markdown("#### 🎯 Ce que vous débloquez :")
        
        for benefit in benefits:
            st.markdown(f"""
            <div style="
                background: #f0f9ff;
                border-left: 4px solid #3b82f6;
                padding: 1rem;
                margin: 0.5rem 0;
                border-radius: 0.5rem;
            ">
                <p style="margin: 0; color: #1e3a8a; font-weight: 500;">✅ {benefit}</p>
            </div>
            """, unsafe_allow_html=True)
    
    @staticmethod
    def _render_comparison_table():
        """Tableau comparatif Free vs Premium"""
        
        st.markdown("#### 📊 Comparaison des offres")
        
        comparison_data = {
            "Fonctionnalité": [
                "📄 Générations CV/mois",
                "🎨 Templates disponibles", 
                "🎯 Optimisation ATS",
                "🔍 Mirror Match",
                "🚀 Smart Coach",
                "📥 Formats export",
                "💬 Support"
            ],
            "🆓 Gratuit": [
                "3",
                "5 basiques",
                "❌",
                "❌", 
                "❌",
                "PDF",
                "Email"
            ],
            "⭐ Premium": [
                "Illimité",
                "20+ premium",
                "✅ Avancée",
                "✅ Complet",
                "✅ IA personnalisée", 
                "PDF + DOCX + HTML",
                "Prioritaire"
            ]
        }
        
        # Tableau stylé
        st.markdown("""
        <style>
        .comparison-table {
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
            background: white;
            border-radius: 1rem;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .comparison-table th {
            background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
            color: white;
            padding: 1rem;
            text-align: left;
            font-weight: 600;
        }
        .comparison-table td {
            padding: 1rem;
            border-bottom: 1px solid #e5e7eb;
        }
        .comparison-table tr:hover {
            background: #f9fafb;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Créer le tableau
        df = st.dataframe(comparison_data, use_container_width=True)
    
    @staticmethod
    def _handle_premium_upgrade():
        """Gestion upgrade premium"""
        # Integration future avec Stripe
        st.info("🔥 Redirection vers la page de paiement Stripe...")
        st.session_state.show_premium_checkout = True


class PhoenixCVProgressBar:
    """Composant progress bar Phoenix CV"""
    
    @staticmethod
    def render_animated(
        stages: List[tuple],
        current_stage: int = 0,
        speed: float = 0.5
    ):
        """
        Progress bar animée style Phoenix Letters
        
        Args:
            stages: Liste de tuples (progress, message)
            current_stage: Étape actuelle
            speed: Vitesse d'animation en secondes
        """
        
        import time
        
        progress_container = st.container()
        
        with progress_container:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, (progress, message) in enumerate(stages):
                if i <= current_stage:
                    progress_bar.progress(progress / 100)
                    status_text.text(message)
                    time.sleep(speed)
            
            # Animation finale
            if current_stage >= len(stages) - 1:
                st.balloons()
    
    @staticmethod
    def render_static(progress: int, message: str, color: str = "#3b82f6"):
        """Progress bar statique avec style custom"""
        
        progress_html = f"""
        <div style="
            background: #f3f4f6;
            border-radius: 1rem;
            padding: 1rem;
            margin: 1rem 0;
        ">
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                <span style="font-weight: 600; color: #374151;">{message}</span>
                <span style="font-weight: 600; color: {color};">{progress}%</span>
            </div>
            <div style="
                background: #e5e7eb;
                border-radius: 0.5rem;
                height: 8px;
                overflow: hidden;
            ">
                <div style="
                    background: {color};
                    height: 100%;
                    width: {progress}%;
                    border-radius: 0.5rem;
                    transition: width 0.3s ease;
                "></div>
            </div>
        </div>
        """
        
        st.markdown(progress_html, unsafe_allow_html=True)


class PhoenixCVMetrics:
    """Composant métriques Phoenix CV"""
    
    @staticmethod
    def render_dashboard():
        """Dashboard métriques utilisateur"""
        
        user_id = st.session_state.get("user_id", "anonymous")
        
        if user_id == "anonymous":
            PhoenixCVMetrics._render_anonymous_metrics()
        else:
            PhoenixCVMetrics._render_user_metrics()
    
    @staticmethod
    def _render_anonymous_metrics():
        """Métriques pour utilisateurs anonymes"""
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            PhoenixCVMetrics._render_metric_card(
                "🚀", "Commencez", "Créez votre compte", "#3b82f6"
            )
        
        with col2:
            PhoenixCVMetrics._render_metric_card(
                "📄", "Templates", "5 gratuits", "#10b981"
            )
        
        with col3:
            PhoenixCVMetrics._render_metric_card(
                "⚡", "Génération", "3 gratuits", "#f59e0b"
            )
    
    @staticmethod
    def _render_user_metrics():
        """Métriques utilisateur connecté"""
        
        col1, col2, col3, col4 = st.columns(4)
        
        metrics = [
            ("💼", "CV Créés", st.session_state.get("total_cv_generated", 0), "#3b82f6"),
            ("📊", "Score ATS", f"{st.session_state.get('avg_ats_score', 75)}%", "#10b981"),
            ("📥", "Downloads", st.session_state.get("total_downloads", 0), "#f59e0b"),
            ("🎯", "Optimisations", st.session_state.get("total_optimizations", 0), "#ef4444")
        ]
        
        for i, (icon, label, value, color) in enumerate(metrics):
            with [col1, col2, col3, col4][i]:
                PhoenixCVMetrics._render_metric_card(icon, label, str(value), color)
    
    @staticmethod
    def _render_metric_card(icon: str, label: str, value: str, color: str):
        """Card métrique individuelle"""
        
        card_html = f"""
        <div style="
            background: white;
            border: 2px solid {color};
            border-radius: 1rem;
            padding: 1.5rem;
            text-align: center;
            margin: 0.5rem 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        ">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
            <div style="color: {color}; font-size: 1.5rem; font-weight: 700; margin-bottom: 0.25rem;">{value}</div>
            <div style="color: #6b7280; font-size: 0.9rem; font-weight: 500;">{label}</div>
        </div>
        """
        
        st.markdown(card_html, unsafe_allow_html=True)


class PhoenixCVTooltip:
    """Composant tooltip Phoenix CV"""
    
    @staticmethod
    def render(text: str, tooltip: str, icon: str = "ℹ️"):
        """Tooltip interactif"""
        
        tooltip_html = f"""
        <div style="position: relative; display: inline-block;">
            <span style="cursor: help;" title="{tooltip}">{text} {icon}</span>
        </div>
        """
        
        st.markdown(tooltip_html, unsafe_allow_html=True)