"""
Module UI hybride pour le tableau de bord Phoenix Rise.
Compatible avec MockDBService ET SupabaseReadService pour transition progressive.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime, date, timedelta
from typing import Dict, Any, List

from services.hybrid_db_service import HybridDBService
from services.supabase_read_service import SupabaseReadService


def render_hybrid_dashboard_ui(user_id: str, hybrid_service: HybridDBService):
    """
    Affiche le tableau de bord hybride utilisant Mock + Supabase.
    
    Args:
        user_id: ID utilisateur
        hybrid_service: Service hybride (Mock + Events)
    """
    
    # Initialisation du service de lecture Supabase
    supabase_service = SupabaseReadService()
    
    st.header("🚀 Mon Tableau de Bord Phoenix Rise")
    
    # Styles améliorés
    st.markdown(
        """
        <style>
            .dashboard-container {
                background: rgba(255, 255, 255, 0.95);
                padding: 2rem;
                border-radius: 10px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
                margin-bottom: 2rem;
            }
            .hybrid-badge {
                background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 0.5rem 1rem;
                border-radius: 20px;
                font-size: 0.8rem;
                font-weight: bold;
                margin-bottom: 1rem;
                text-align: center;
            }
            .status-indicator {
                display: inline-block;
                width: 10px;
                height: 10px;
                border-radius: 50%;
                margin-right: 8px;
            }
            .status-active { background-color: #28a745; }
            .status-fallback { background-color: #ffc107; }
            .stMetric {
                background: rgba(255, 255, 255, 0.9);
                padding: 1rem;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
                border-left: 5px solid #667eea;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Indicateur de status du système
    _render_system_status(hybrid_service, supabase_service)
    
    # Sélection de la source de données
    data_source = _select_data_source(supabase_service)
    
    # Récupération des données selon la source
    if data_source == "supabase":
        metrics = supabase_service.get_dashboard_metrics(user_id)
        journal_entries = supabase_service.get_journal_entries(user_id)
        journal_stats = supabase_service.get_journal_stats(user_id)
        objectives = supabase_service.get_objectives(user_id)
    else:
        # Fallback vers Mock
        metrics = _get_mock_dashboard_metrics(user_id, hybrid_service)
        journal_entries = hybrid_service.get_journal_entries(user_id)
        journal_stats = hybrid_service.get_journal_stats(user_id)
        objectives = hybrid_service.get_objectives(user_id)
    
    # Affichage des métriques principales
    _render_main_metrics(metrics, journal_stats)
    
    # Graphiques et visualisations
    if journal_entries:
        _render_mood_confidence_charts(journal_entries, data_source)
        _render_trend_analysis(journal_entries, data_source)
    else:
        st.info("📝 Commencez par ajouter des entrées à votre journal pour voir vos statistiques ici.")
    
    # Section objectifs
    if objectives:
        _render_objectives_section(objectives, data_source)
    
    # Event status pour debug
    if st.checkbox("🔧 Afficher status technique"):
        _render_technical_status(hybrid_service, supabase_service)


def _render_system_status(hybrid_service: HybridDBService, supabase_service: SupabaseReadService):
    """Affiche le status du système hybride."""
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        event_status = hybrid_service.get_event_status()
        
        if event_status["event_bridge_available"] and supabase_service.is_available:
            status_html = '<span class="status-indicator status-active"></span>Mode Hybride Actif'
            st.markdown(f'<div class="hybrid-badge">{status_html}</div>', unsafe_allow_html=True)
        else:
            status_html = '<span class="status-indicator status-fallback"></span>Mode Fallback Actif'
            st.markdown(f'<div class="hybrid-badge">{status_html}</div>', unsafe_allow_html=True)


def _select_data_source(supabase_service: SupabaseReadService) -> str:
    """Permet à l'utilisateur de choisir la source des données."""
    
    if supabase_service.is_available:
        with st.sidebar:
            st.subheader("🔄 Source des Données")
            data_source = st.radio(
                "Choisir la source:",
                ["supabase", "mock"],
                format_func=lambda x: "📊 Supabase (Production)" if x == "supabase" else "🧪 Mock (Local)",
                index=0
            )
            
            if data_source == "supabase":
                st.success("✅ Données depuis la pipeline Event Sourcing")
            else:
                st.warning("⚠️ Données locales (session)")
                
            return data_source
    else:
        st.sidebar.warning("📊 Supabase indisponible - utilisation données locales")
        return "mock"


def _render_main_metrics(metrics: Dict[str, Any], journal_stats: Dict[str, Any]):
    """Affiche les métriques principales."""
    
    st.subheader("📊 Vue d'ensemble")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Entrées Journal",
            metrics.get("journal_entries_count", journal_stats.get("total_entries", 0)),
            help="Nombre total d'entrées dans votre journal"
        )
    
    with col2:
        avg_mood = metrics.get("avg_mood", journal_stats.get("avg_mood", 0))
        st.metric(
            "Humeur Moyenne",
            f"{avg_mood:.1f}/10",
            help="Votre humeur moyenne sur toutes les entrées"
        )
    
    with col3:
        avg_confidence = metrics.get("avg_confidence", journal_stats.get("avg_confidence", 0))
        st.metric(
            "Confiance Moyenne", 
            f"{avg_confidence:.1f}/10",
            help="Votre niveau de confiance moyen"
        )
    
    with col4:
        active_objectives = metrics.get("active_objectives", 0)
        st.metric(
            "Objectifs Actifs",
            active_objectives,
            help="Nombre d'objectifs en cours"
        )


def _render_mood_confidence_charts(journal_entries: List, data_source: str):
    """Affiche les graphiques d'humeur et confiance."""
    
    st.subheader("📈 Évolution de votre bien-être")
    
    # Préparation des données
    if data_source == "supabase":
        # Données depuis Supabase
        df_data = []
        for entry in journal_entries:
            df_data.append({
                "Date": entry.created_at.date() if hasattr(entry.created_at, 'date') else entry.created_at,
                "Humeur": entry.mood,
                "Confiance": entry.confidence
            })
        df = pd.DataFrame(df_data)
    else:
        # Données depuis Mock
        df_data = []
        for entry in journal_entries:
            df_data.append({
                "Date": entry.created_at.date() if hasattr(entry.created_at, 'date') else entry.created_at,
                "Humeur": entry.mood,
                "Confiance": entry.confidence
            })
        df = pd.DataFrame(df_data)
    
    if not df.empty:
        # Graphique en ligne
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df["Date"],
            y=df["Humeur"],
            mode='lines+markers',
            name='Humeur',
            line=dict(color='#667eea', width=3),
            marker=dict(size=8)
        ))
        
        fig.add_trace(go.Scatter(
            x=df["Date"],
            y=df["Confiance"],
            mode='lines+markers',
            name='Confiance',
            line=dict(color='#764ba2', width=3),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title="Évolution de l'Humeur et de la Confiance",
            xaxis_title="Date",
            yaxis_title="Score (1-10)",
            yaxis=dict(range=[0, 11]),
            hovermode='x unified',
            template='plotly_white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Graphique en barres pour comparaison
        col1, col2 = st.columns(2)
        
        with col1:
            fig_mood = px.histogram(
                df, 
                x="Humeur", 
                title="Distribution de l'Humeur",
                color_discrete_sequence=['#667eea']
            )
            fig_mood.update_layout(template='plotly_white')
            st.plotly_chart(fig_mood, use_container_width=True)
        
        with col2:
            fig_confidence = px.histogram(
                df, 
                x="Confiance", 
                title="Distribution de la Confiance",
                color_discrete_sequence=['#764ba2']
            )
            fig_confidence.update_layout(template='plotly_white')
            st.plotly_chart(fig_confidence, use_container_width=True)


def _render_trend_analysis(journal_entries: List, data_source: str):
    """Affiche l'analyse des tendances."""
    
    if len(journal_entries) < 2:
        return
        
    st.subheader("📊 Analyse des Tendances")
    
    # Calcul des tendances récentes (7 derniers jours)
    recent_entries = journal_entries[:7]  # Déjà triées par date desc
    
    if len(recent_entries) >= 2:
        recent_moods = [entry.mood for entry in recent_entries]
        recent_confidence = [entry.confidence for entry in recent_entries]
        
        mood_trend = "🔼" if recent_moods[0] > recent_moods[-1] else "🔽" if recent_moods[0] < recent_moods[-1] else "➡️"
        confidence_trend = "🔼" if recent_confidence[0] > recent_confidence[-1] else "🔽" if recent_confidence[0] < recent_confidence[-1] else "➡️"
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                "Tendance Humeur (7j)",
                f"{mood_trend} {recent_moods[0]}/10",
                f"{recent_moods[0] - recent_moods[-1]:+.1f}"
            )
        
        with col2:
            st.metric(
                "Tendance Confiance (7j)",
                f"{confidence_trend} {recent_confidence[0]}/10",
                f"{recent_confidence[0] - recent_confidence[-1]:+.1f}"
            )


def _render_objectives_section(objectives: List[Dict[str, Any]], data_source: str):
    """Affiche la section des objectifs."""
    
    st.subheader("🎯 Mes Objectifs")
    
    if objectives:
        active_objectives = [obj for obj in objectives if obj.get("status") == "active"]
        completed_objectives = [obj for obj in objectives if obj.get("status") == "completed"]
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            for obj in active_objectives[:5]:  # Limite à 5 objectifs
                st.write(f"🎯 **{obj['title']}**")
                if obj.get("description"):
                    st.write(f"   📝 {obj['description']}")
                
                if obj.get("target_date"):
                    st.write(f"   📅 Échéance: {obj['target_date']}")
                st.write("---")
        
        with col2:
            if completed_objectives:
                st.success(f"✅ {len(completed_objectives)} objectifs complétés")
            
            if active_objectives:
                st.info(f"🎯 {len(active_objectives)} objectifs actifs")
    else:
        st.info("🎯 Aucun objectif défini. Créez votre premier objectif dans la section correspondante.")


def _render_technical_status(hybrid_service: HybridDBService, supabase_service: SupabaseReadService):
    """Affiche le status technique pour debug."""
    
    st.subheader("🔧 Status Technique")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.json(hybrid_service.get_event_status())
    
    with col2:
        st.json(supabase_service.health_check())


def _get_mock_dashboard_metrics(user_id: str, hybrid_service: HybridDBService) -> Dict[str, Any]:
    """Récupère les métriques depuis le service Mock."""
    
    journal_stats = hybrid_service.get_journal_stats(user_id)
    objectives = hybrid_service.get_objectives(user_id)
    
    active_objectives = len([obj for obj in objectives if obj.get("status") != "completed"])
    completed_objectives = len([obj for obj in objectives if obj.get("status") == "completed"])
    
    return {
        "journal_entries_count": journal_stats.get("total_entries", 0),
        "avg_mood": journal_stats.get("avg_mood", 0),
        "avg_confidence": journal_stats.get("avg_confidence", 0),
        "total_objectives": len(objectives),
        "active_objectives": active_objectives,
        "completed_objectives": completed_objectives,
        "total_coaching_sessions": 0,  # Mock ne track pas encore les sessions
        "recent_coaching_sessions": 0
    }