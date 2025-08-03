"""
Module UI pour l'affichage de l'interface du coach IA.

Ce module fournit les fonctions Streamlit pour interagir avec le coach IA
et afficher les conseils générés.
"""

import streamlit as st
from services.ai_coach_service import AICoachService
from services.mock_db_service import MockDBService


def render_coaching_ui(
    user_id: str, ai_service: AICoachService, db_service: MockDBService, user_tier: str
):
    """Affiche l'interface du coach IA avec un style amélioré."""
    st.header("Mon Coach IA")

    st.markdown(
        """
        <style>
            .coaching-info-box {
                background: #e6f7ff; /* Light blue */
                border-left: 5px solid #2575fc; /* Vibrant blue accent */
                padding: 1rem;
                border-radius: 8px;
                margin-bottom: 1.5rem;
                color: #333;
            }
            .coaching-advice-box {
                background: rgba(255, 255, 255, 0.95);
                padding: 2rem;
                border-radius: 10px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
                margin-top: 2rem;
            }
            .coaching-advice-box h3 {
                color: #6a11cb; /* Purple accent */
                margin-bottom: 1rem;
            }
            .coaching-advice-box p {
                line-height: 1.8;
                color: #444;
            }
            .coaching-advice-box ul {
                list-style-type: none;
                padding-left: 0;
            }
            .coaching-advice-box li {
                margin-bottom: 0.5rem;
                padding-left: 1.5rem;
                position: relative;
            }
            .coaching-advice-box li::before {
                content: '✨'; /* Sparkle icon */
                position: absolute;
                left: 0;
                color: #2575fc;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        "<div class='coaching-info-box'>Demandez à votre coach IA des conseils personnalisés basés sur votre journal de bord.</div>",
        unsafe_allow_html=True,
    )

    if st.button("Obtenir des Conseils du Coach IA", type="primary"):
        with st.spinner("Votre coach IA analyse vos données..."):
            journal_entries = db_service.get_journal_entries(user_id)
            user_profile = db_service.get_profile(user_id)  # Récupérer le profil

            advice = ai_service.get_coaching_advice(
                journal_entries, user_profile, user_tier
            )

            st.markdown("<div class='coaching-advice-box'>", unsafe_allow_html=True)
            st.markdown("### 💡 Conseils de votre Coach IA")
            st.write(advice)
            st.markdown("</div>", unsafe_allow_html=True)
