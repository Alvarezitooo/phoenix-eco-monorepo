"""
Interface du tableau de bord avec métriques et graphiques.
"""

from typing import Dict, List

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from services.db_service import DBService


def render_dashboard_ui(user_id: str, db_service: DBService):
    """
    Affiche le tableau de bord complet de l'utilisateur.

    Args:
        user_id: ID de l'utilisateur connecté
        db_service: Service de base de données
    """
    st.header("📈 Votre Tableau de Bord")

    with st.spinner("📊 Analyse de votre progression..."):
        mood_entries = db_service.get_mood_entries(user_id)
        stats = db_service.get_user_stats(user_id)

    if not mood_entries:
        st.info("🎯 Votre tableau de bord se remplira après quelques saisies d'humeur.")
        return

    # Métriques principales
    _render_key_metrics(stats)

    st.markdown("---")

    # Graphiques d'évolution
    _render_evolution_charts(mood_entries)


def _render_key_metrics(stats: Dict):
    """Affiche les métriques clés sous forme de cartes."""
    st.markdown("#### 📊 Vue d'overview")

    col1, col2, col3 = st.columns(3)

    with col1:
        avg_mood = stats.get("avg_mood", 0)
        delta_mood = round(avg_mood - 5, 1) if avg_mood > 5 else None

        st.metric(
            label="😊 Humeur Moyenne",
            value=f"{avg_mood}/10",
            delta=f"+{delta_mood}" if delta_mood and delta_mood > 0 else None,
        )

    with col2:
        avg_confidence = stats.get("avg_confidence", 0)
        delta_confidence = round(avg_confidence - 5, 1) if avg_confidence > 5 else None

        st.metric(
            label="💪 Confiance Moyenne",
            value=f"{avg_confidence}/10",
            delta=(
                f"+{delta_confidence}"
                if delta_confidence and delta_confidence > 0
                else None
            ),
        )

    with col3:
        st.metric(
            label="📝 Jours de Suivi",
            value=stats.get("total_entries", 0),
            delta=stats.get("trend", "➡️"),
        )


def _render_evolution_charts(mood_entries: List[Dict]):
    """
    Génère les graphiques d'évolution.
    """
    if len(mood_entries) < 2:
        st.info("📈 Les graphiques d'évolution apparaîtront avec plus de données.")
        return

    try:
        # Préparation des données
        df = pd.DataFrame(mood_entries)
        df["created_at"] = pd.to_datetime(df["created_at"])
        df = df.sort_values("created_at")

        st.markdown("#### 📈 Évolution de votre État d'Esprit")

        # Graphique linéaire principal
        fig = px.line(
            df,
            x="created_at",
            y=["mood_score", "confidence_level"],
            title="Progression de votre Humeur et Confiance",
            labels={
                "value": "Score (sur 10)",
                "created_at": "Date",
                "variable": "Métrique",
            },
            color_discrete_map={"mood_score": "#667eea", "confidence_level": "#764ba2"},
        )

        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#333"),
            hovermode="x unified",
        )

        fig.update_traces(mode="lines+markers", line=dict(width=3), marker=dict(size=8))

        st.plotly_chart(fig, use_container_width=True)

        # Graphique en aires empilées pour une vue d'ensemble
        fig_area = px.area(
            df,
            x="created_at",
            y="mood_score",
            title="Zone de Confort Émotionnel",
            color_discrete_sequence=["#667eea"],
        )

        fig_area.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
        )

        st.plotly_chart(fig_area, use_container_width=True)

    except Exception as e:
        st.error(f"Erreur lors de la génération des graphiques : {e}")
