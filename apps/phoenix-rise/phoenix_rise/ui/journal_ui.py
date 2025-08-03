"""
Module UI pour l'affichage de l'interface du journal de bord.

Ce module fournit les fonctions Streamlit pour permettre aux utilisateurs
d'enregistrer et de consulter leurs entrées de journal.
"""

import streamlit as st
from services.mock_db_service import MockDBService


def render_journal_ui(user_id: str, db_service: MockDBService):
    """Affiche l'interface du journal de bord avec un style amélioré."""
    st.header("Mon Journal de Bord")

    st.markdown(
        """
        <style>
            .journal-form-container {
                background: rgba(255, 255, 255, 0.95);
                padding: 2rem;
                border-radius: 10px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
                margin-bottom: 2rem;
            }
            .journal-entry-card {
                background: rgba(255, 255, 255, 0.9);
                padding: 1.5rem;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
                margin-bottom: 1rem;
                border-left: 5px solid #6a11cb; /* Accent color */
            }
            .journal-entry-header {
                font-weight: 600;
                color: #333;
                margin-bottom: 0.5rem;
            }
            .journal-entry-notes {
                color: #555;
                line-height: 1.6;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.container():
        st.markdown("<div class='journal-form-container'>", unsafe_allow_html=True)
        with st.form("journal_form"):
            st.write("Comment vous sentez-vous aujourd'hui ?")
            mood = st.slider("Humeur (1=Bas, 10=Haut)", 1, 10, 5, key="mood_slider")
            confidence = st.slider(
                "Confiance (1=Basse, 10=Haute)", 1, 10, 5, key="confidence_slider"
            )
            notes = st.text_area(
                "Vos pensées, succès et défis du jour...", key="notes_textarea"
            )
            submitted = st.form_submit_button("Enregistrer l'entrée")

            if submitted:
                db_service.add_journal_entry(user_id, mood, confidence, notes)
                st.success("Entrée enregistrée !")
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.subheader("Historique des Entrées")
    entries = db_service.get_journal_entries(user_id)
    if not entries:
        st.info(
            "Aucune entrée pour le moment. Commencez par ajouter une entrée ci-dessus."
        )
    else:
        for entry in entries:
            st.markdown(
                f"""
                <div class='journal-entry-card'>
                    <div class='journal-entry-header'>
                        {entry.created_at.strftime('%d/%m/%Y')} - Humeur: {entry.mood}/10, Confiance: {entry.confidence}/10
                    </div>
                    <div class='journal-entry-notes'>
                        {entry.notes}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
