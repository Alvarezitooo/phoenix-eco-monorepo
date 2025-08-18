
# packages/phoenix_shared_ui/components/header.py
# 🎨 PHOENIX SHARED UI - Header unifié pour tout l'écosystème

import streamlit as st
from typing import Optional, Dict, Any

def render_header(app_name: str, app_icon: str):
    """
    Affiche un header standardisé simple pour une application de l'écosystème Phoenix.
    
    Args:
        app_name: Le nom de l'application (ex: "Phoenix Letters").
        app_icon: L'emoji icône de l'application (ex: "✉️").
    """
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        border-left: 6px solid #667eea;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); 
    ">
        <h2 style="margin: 0; color: #2c3e50; font-weight: 600;">
            {app_icon} {app_name}
        </h2>
        <p style="margin: 0.3rem 0 0 0; color: #57647c; font-size: 0.9rem;">
            Fait partie de l'écosystème 🦋 Phoenix
        </p>
    </div>
    """, unsafe_allow_html=True)

class PhoenixHeader:
    """Composant header unifié avancé pour toutes les apps Phoenix"""
    
    # Palettes couleurs par app
    APP_COLORS = {
        "cv": {
            "primary": "#1e3a8a",
            "secondary": "#3b82f6", 
            "gradient": "linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%)"
        },
        "letters": {
            "primary": "#7c2d12",
            "secondary": "#ea580c",
            "gradient": "linear-gradient(135deg, #7c2d12 0%, #ea580c 100%)"
        },
        "rise": {
            "primary": "#166534", 
            "secondary": "#16a34a",
            "gradient": "linear-gradient(135deg, #166534 0%, #16a34a 100%)"
        },
        "default": {
            "primary": "#6b7280",
            "secondary": "#9ca3af", 
            "gradient": "linear-gradient(135deg, #6b7280 0%, #9ca3af 100%)"
        }
    }
    
    @classmethod
    def render_advanced(
        cls,
        title: str = "Phoenix",
        subtitle: str = "Écosystème d'applications IA",
        icon: str = "🦋",
        app_type: str = "default",
        show_stats: bool = False,
        user_stats: Optional[Dict[str, Any]] = None,
        custom_gradient: Optional[str] = None
    ):
        """
        Rendu header avancé unifié pour toutes les apps Phoenix
        
        Args:
            title: Titre principal
            subtitle: Sous-titre descriptif
            icon: Icône du header
            app_type: Type d'app (cv, letters, rise, default)
            show_stats: Afficher les stats utilisateur
            user_stats: Dictionnaire des stats à afficher
            custom_gradient: Gradient CSS personnalisé
        """
        
        # Récupération couleurs app
        colors = cls.APP_COLORS.get(app_type, cls.APP_COLORS["default"])
        gradient = custom_gradient or colors["gradient"]
        
        # Stats HTML si demandé
        stats_html = ""
        if show_stats and user_stats:
            stats_items = []
            for key, value in user_stats.items():
                stats_items.append(f"<span style='margin-right: 1rem;'><strong>{key}:</strong> {value}</span>")
            
            if stats_items:
                stats_html = f"""
                <div style="
                    margin-top: 1rem; 
                    padding-top: 1rem; 
                    border-top: 1px solid rgba(255,255,255,0.3);
                    font-size: 0.9rem;
                    opacity: 0.9;
                ">
                    {''.join(stats_items)}
                </div>
                """
        
        # Header HTML unifié
        header_html = f"""
        <div style="
            background: {gradient};
            padding: 2rem;
            border-radius: 1rem;
            margin-bottom: 2rem;
            color: white;
            text-align: center;
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
            position: relative;
            overflow: hidden;
        ">
            <!-- Effet brillance -->
            <div style="
                position: absolute;
                top: -50%;
                left: -50%;
                width: 200%;
                height: 200%;
                background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 50%);
                pointer-events: none;
            "></div>
            
            <!-- Contenu principal -->
            <div style="position: relative; z-index: 1;">
                <h1 style="
                    margin: 0 0 0.5rem 0;
                    font-size: 2.5rem;
                    font-weight: 700;
                    text-shadow: 0 2px 4px rgba(0,0,0,0.3);
                ">
                    {icon} {title}
                </h1>
                <p style="
                    margin: 0;
                    font-size: 1.1rem;
                    opacity: 0.95;
                    font-weight: 300;
                ">
                    {subtitle}
                </p>
                {stats_html}
            </div>
        </div>
        """
        
        st.markdown(header_html, unsafe_allow_html=True)

# Fonctions de compatibilité app-spécifiques
def render_cv_header(title="Phoenix CV", subtitle="Créez des CV qui se démarquent", **kwargs):
    """Header spécialisé pour Phoenix CV"""
    PhoenixHeader.render_advanced(
        title=title,
        subtitle=subtitle,
        icon="📄",
        app_type="cv",
        **kwargs
    )

def render_letters_header(title="Phoenix Letters", subtitle="Rédigez des lettres percutantes", **kwargs):
    """Header spécialisé pour Phoenix Letters"""
    PhoenixHeader.render_advanced(
        title=title,
        subtitle=subtitle,
        icon="✉️",
        app_type="letters",
        **kwargs
    )

def render_rise_header(title="Phoenix Rise", subtitle="Votre développement personnel", **kwargs):
    """Header spécialisé pour Phoenix Rise"""
    PhoenixHeader.render_advanced(
        title=title,
        subtitle=subtitle,
        icon="🌱",
        app_type="rise",
        **kwargs
    )
