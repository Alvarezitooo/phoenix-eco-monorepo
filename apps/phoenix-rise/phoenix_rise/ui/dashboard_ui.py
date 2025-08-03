"""
Module UI pour l'affichage du tableau de bord de l'utilisateur.

Ce module fournit les fonctions Streamlit pour visualiser les données
du journal de bord sous forme de graphiques et de statistiques.
"""

import pandas as pd
import plotly.express as px
import streamlit as st
from services.mock_db_service import MockDBService


def render_dashboard_ui(user_id: str, db_service: MockDBService):
    """Affiche le tableau de bord de l'utilisateur avec un style amélioré."""
    st.header("Mon Tableau de Bord")

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
            .stMetric {
                background: rgba(255, 255, 255, 0.9);
                padding: 1rem;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
                border-left: 5px solid #2575fc; /* Blue accent */
            }
            .stMetric > div:first-child {
                font-size: 0.9rem;
                color: #666;
            }
            .stMetric > div:nth-child(2) {
                font-size: 2rem;
                font-weight: 600;
                color: #333;
            }
            .stMetric > div:nth-child(3) {
                font-size: 0.8rem;
                color: #888;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    entries = db_service.get_journal_entries(user_id)

    if not entries:
        st.info(
            "Aucune donnée de journal pour le moment. Enregistrez des entrées pour voir votre tableau de bord."
        )
        return

    # Convertir les entrées en DataFrame Pandas
    data = [
        {
            "date": entry.created_at.date(),
            "mood": entry.mood,
            "confidence": entry.confidence,
        }
        for entry in entries
    ]
    df = pd.DataFrame(data)
    df = df.sort_values(by="date")

    st.markdown("<div class='dashboard-container'>", unsafe_allow_html=True)

    st.subheader("Évolution de l'Humeur")
    fig_mood = px.line(
        df,
        x="date",
        y="mood",
        title="Humeur au fil du temps",
        color_discrete_sequence=["#6a11cb"],  # Purple
        template="plotly_white",
    )
    fig_mood.update_layout(hovermode="x unified")
    st.plotly_chart(fig_mood, use_container_width=True)

    st.subheader("Évolution de la Confiance")
    fig_confidence = px.line(
        df,
        x="date",
        y="confidence",
        title="Confiance au fil du temps",
        color_discrete_sequence=["#2575fc"],  # Blue
        template="plotly_white",
    )
    fig_confidence.update_layout(hovermode="x unified")
    st.plotly_chart(fig_confidence, use_container_width=True)

    st.subheader("Statistiques Résumé")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Humeur Moyenne", f"{df['mood'].mean():.1f}")
    with col2:
        st.metric("Confiance Moyenne", f"{df['confidence'].mean():.1f}")

    st.markdown("</div>", unsafe_allow_html=True)
