# packages/phoenix_shared_ui/components/common.py
# 🧩 PHOENIX SHARED UI COMMON - Composants communs unifiés

import streamlit as st
from typing import Optional, Dict, Any

class PhoenixPremiumBarrier:
    """Barrière premium unifiée pour toutes les apps Phoenix"""
    
    @staticmethod
    def render(feature_name: str, description: str, app_name: str = "Phoenix", 
               app_color: str = "#3b82f6") -> None:
        """Affiche une barrière premium avec design unifié"""
        
        with st.container():
            st.markdown(f"""
            <div style="
                border: 2px dashed {app_color}40;
                border-radius: 10px;
                padding: 20px;
                text-align: center;
                background: linear-gradient(135deg, {app_color}10, {app_color}05);
                margin: 20px 0;
            ">
                <h3 style="color: {app_color}; margin-bottom: 10px;">
                    🔒 {feature_name} - Fonctionnalité Premium
                </h3>
                <p style="color: #666; margin-bottom: 15px;">
                    {description}
                </p>
                <p style="color: #888; font-size: 0.9em;">
                    Upgrade vers {app_name} Premium pour débloquer cette fonctionnalité
                </p>
            </div>
            """, unsafe_allow_html=True)

class PhoenixProgressBar:
    """Barres de progression unifiées pour toutes les apps Phoenix"""
    
    @staticmethod
    def render_static(progress: int, message: str, app_color: str = "#3b82f6") -> None:
        """Barre de progression statique"""
        st.progress(progress / 100, text=message)
    
    @staticmethod
    def render_animated(progress: int, message: str, app_color: str = "#3b82f6") -> None:
        """Barre de progression avec animation"""
        progress_placeholder = st.empty()
        with progress_placeholder.container():
            st.markdown(f"""
            <div style="margin: 20px 0;">
                <p style="margin-bottom: 10px; color: {app_color};">{message}</p>
                <div style="
                    width: 100%; 
                    height: 20px; 
                    background-color: #f0f0f0;
                    border-radius: 10px;
                    overflow: hidden;
                ">
                    <div style="
                        width: {progress}%; 
                        height: 100%; 
                        background: linear-gradient(90deg, {app_color}, {app_color}80);
                        transition: width 0.3s ease;
                        border-radius: 10px;
                    "></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    @staticmethod
    def render_multi_stage(stages: list, current_stage: int, app_color: str = "#3b82f6") -> None:
        """Barre de progression multi-étapes"""
        total_stages = len(stages)
        progress = (current_stage / total_stages) * 100
        
        st.markdown(f"""
        <div style="margin: 20px 0;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                {"".join([
                    f'<span style="color: {app_color if i < current_stage else "#ccc"}; font-size: 0.9em;">{stage}</span>'
                    for i, stage in enumerate(stages)
                ])}
            </div>
            <div style="
                width: 100%; 
                height: 8px; 
                background-color: #f0f0f0;
                border-radius: 4px;
                overflow: hidden;
            ">
                <div style="
                    width: {progress}%; 
                    height: 100%; 
                    background: {app_color};
                    transition: width 0.5s ease;
                    border-radius: 4px;
                "></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Fonctions de compatibilité app-spécifiques
def render_cv_premium_barrier(feature_name: str, description: str) -> None:
    """Compatibilité CV - barrière premium"""
    PhoenixPremiumBarrier.render(feature_name, description, "Phoenix CV", "#3b82f6")

def render_letters_premium_barrier(feature_name: str, description: str) -> None:
    """Compatibilité Letters - barrière premium"""
    PhoenixPremiumBarrier.render(feature_name, description, "Phoenix Letters", "#7c3aed")

def render_cv_progress(progress: int, message: str) -> None:
    """Compatibilité CV - progress bar"""
    PhoenixProgressBar.render_static(progress, message, "#3b82f6")

def render_letters_progress(progress: int, message: str) -> None:
    """Compatibilité Letters - progress bar"""
    PhoenixProgressBar.render_static(progress, message, "#7c3aed")