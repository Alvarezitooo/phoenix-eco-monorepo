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
    _step_header(1, "Trouvons d’abord une direction", "2 minutes pour cadrer votre reconversion, simplement.")

    with st.container():
        cols = st.columns(2)
        with cols[0]:
            st.radio("En ce moment, je me sens…", ["Plutôt serein(e)", "Partagé(e)", "Perdu(e)"], index=1, key="anx_q1")
            st.radio("Je cherche…", ["Un nouveau métier", "Des pistes à explorer", "Je ne sais pas encore"], index=0, key="anx_q2")
        with cols[1]:
            st.radio("Mes contraintes principales…", ["Temps", "Budget", "Formation", "Aucune"], index=0, key="anx_q3")
            st.radio("Je préfère avancer…", ["Pas à pas", "Avec un plan", "Avec accompagnement"], index=0, key="anx_q4")

    if st.button("Voir mes pistes métiers"):
        st.session_state["pa_step"] = "exploration"


def _screen_exploration() -> None:
    _step_header(2, "Vos pistes de métiers", "Choisissez celle qui vous parle le plus maintenant.")

    with st.container():
        left, right = st.columns([2, 1])
        with left:
            st.markdown("**Suggestions**")
            options = ["Data Analyst", "UX Researcher", "Chef(fe) de projet digital"]
            st.session_state["pa_selected_job"] = st.radio(
                "Je me projette le plus dans…",
                options,
                index=0,
                key="pa_choice",
            )
        with right:
            with st.expander("Pourquoi ces pistes ?"):
                st.markdown("Basé sur vos réponses et votre expérience. Vous pourrez ajuster ensuite.")

    selected = st.session_state.get("pa_selected_job")
    if st.button(f"Continuer avec {selected}"):
        st.session_state["pa_step"] = "validation_ia"


def _screen_validation() -> None:
    job = st.session_state.get("pa_selected_job", "ce métier")
    _step_header(3, "Confirmer mon choix", f"Voyons si {job} correspond bien à vos forces et envies.")

    with st.container():
        cols = st.columns(2)
        with cols[0]:
            st.markdown("**Alignement avec vos valeurs**: Fort")
            st.markdown("**Compétences transférables**: Élevé")
            with st.expander("Détails de l’alignement"):
                st.markdown("Vos compétences actuelles sont proches de ce rôle.")
        with cols[1]:
            with st.expander("Impact de l’IA (optionnel)"):
                st.markdown("**Résistance estimée**: 78%\n\nPoints d’attention et pistes de spécialisation.")

    if st.button("Obtenir mon plan personnalisé"):
        st.session_state["pa_step"] = "choix"


def _screen_choice() -> None:
    job = st.session_state.get("pa_selected_job", "votre nouvelle piste")
    _step_header(4, "Votre prochaine étape concrète", f"Plan simple pour démarrer {job} dès cette semaine.")

    with st.container():
        with st.expander("Votre plan (6 semaines)"):
            st.markdown(
                """
1. Semaine 1: Découverte métier et vocabulaire
2. Semaine 2: Première compétence clé
3. Semaine 3: Mise en pratique guidée
4. Semaine 4: Projet simple à montrer
5. Semaine 5: Consolidation + feedback
6. Semaine 6: Simulation entretien et prochaines étapes
"""
            )

    if st.button("Commencer aujourd’hui"):
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


