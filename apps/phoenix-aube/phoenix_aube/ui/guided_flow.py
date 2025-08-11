"""
Phoenix Aube – Parcours guidé apaisant (UX minimaliste)

Objectif: réduire l'anxiété et guider l'utilisateur pas à pas.
Uniquement composants Streamlit natifs: st.container, st.columns, st.expander, st.button, st.radio, etc.
"""
from __future__ import annotations

import streamlit as st


TOTAL_STEPS = 4


def _step_header(current: int, title: str, subtitle: str = "") -> None:
    with st.container():
        cols = st.columns([1, 6])
        with cols[0]:
            st.markdown(f"**Étape {current}/{TOTAL_STEPS}**")
        with cols[1]:
            st.markdown(f"### {title}")
            if subtitle:
                st.markdown(subtitle)

    with st.expander("Pourquoi cette étape ?"):
        st.markdown(
            "Cette étape vous aide à avancer sereinement, sans engagement. Vos données restent privées (RGPD)."
        )


def _screen_anxiety() -> None:
    _step_header(1, "Calmons le jeu", "2 minutes pour prendre la mesure, sans jugement.")

    with st.container():
        cols = st.columns(2)
        with cols[0]:
            st.radio("Face à l’IA, je me sens…", ["Calme", "Partagé", "Inquiet"], index=1, key="anx_q1")
            st.radio("L’IA menace mon métier…", ["Peu", "Moyennement", "Beaucoup"], index=1, key="anx_q2")
        with cols[1]:
            st.radio("J’ai envie d’agir…", ["Oui", "Je ne sais pas", "Pas maintenant"], index=0, key="anx_q3")
            st.radio("Je préfère avancer…", ["Pas à pas", "Avec un plan", "Avec accompagnement"], index=0, key="anx_q4")

    if st.button("Voir mes résultats"):
        st.session_state["pa_step"] = "exploration"


def _screen_exploration() -> None:
    _step_header(2, "Vos pistes sereines", "Nous croisons vos forces et vos valeurs.")

    with st.container():
        left, right = st.columns([2, 1])
        with left:
            st.markdown("**Pistes proposées**")
            # Placeholder simple (les vraies données pourront être injectées ici)
            st.markdown("- Data Analyst\n- UX Researcher\n- Chef(fe) de projet digital")
        with right:
            with st.expander("Pourquoi ces pistes ?"):
                st.markdown("Basé sur vos réponses et votre expérience.")

    if st.button("Valider cette piste"):
        st.session_state["pa_step"] = "validation_ia"


def _screen_validation() -> None:
    _step_header(3, "Valider l’avenir de votre choix", "Résistance à l’IA et points d’attention.")

    with st.container():
        cols = st.columns(2)
        with cols[0]:
            st.markdown("**Résistance à l’IA**: 78%")
            with st.expander("Détails"):
                st.markdown("Tâches créatives/humaines protégées, automatisation partielle.")
        with cols[1]:
            st.markdown("**Compétences clés**: SQL, Python, Storytelling")
            with st.expander("Plan des risques"):
                st.markdown("Surveillance trimestrielle du marché, veille IA.")

    if st.button("Obtenir mon plan IA"):
        st.session_state["pa_step"] = "choix"


def _screen_choice() -> None:
    _step_header(4, "Votre prochaine étape concrète", "Un plan simple, actionnable cette semaine.")

    with st.container():
        with st.expander("Votre plan IA (6 semaines)"):
            st.markdown(
                """
1. Semaine 1: Bases Python (3h)
2. Semaine 2: SQL appliqué (3h)
3. Semaine 3: Data Viz (2h)
4. Semaine 4: Projet guidé (3h)
5. Semaine 5: Portfolio (2h)
6. Semaine 6: Simulation entretien (1h)
"""
            )

    if st.button("Commencer maintenant"):
        st.session_state["pa_step"] = "done"


def main() -> None:
    """Point d'entrée du parcours guidé."""
    if "pa_step" not in st.session_state:
        st.session_state["pa_step"] = "anxiete"

    step = st.session_state["pa_step"]
    if step == "anxiete":
        _screen_anxiety()
    elif step == "exploration":
        _screen_exploration()
    elif step == "validation_ia":
        _screen_validation()
    elif step == "choix":
        _screen_choice()
    else:
        with st.container():
            st.markdown("Merci. Vous pouvez revenir à tout moment.")


