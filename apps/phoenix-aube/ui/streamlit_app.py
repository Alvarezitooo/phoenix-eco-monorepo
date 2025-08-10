import os
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import httpx
import streamlit as st


def get_setting(key: str, default: Optional[str] = None) -> Optional[str]:
    if key in st.secrets:
        value = st.secrets[key]
        if isinstance(value, str):
            return value
    return os.getenv(key, default)


API_BASE_URL = get_setting("AUBE_API_BASE_URL", "http://localhost:8000")
AUTH_TOKEN = get_setting("AUTH_TOKEN", None)

CV_APP_URL = get_setting("CV_APP_URL", None)
LETTERS_APP_URL = get_setting("LETTERS_APP_URL", None)
RISE_APP_URL = get_setting("RISE_APP_URL", None)


@st.cache_data(ttl=300)
def fetch_json(path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    url = f"{API_BASE_URL}{path}"
    headers: Dict[str, str] = {"Accept": "application/json"}
    if AUTH_TOKEN:
        headers["Authorization"] = f"Bearer {AUTH_TOKEN}"
    with httpx.Client(timeout=30.0) as client:
        response = client.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()


def main() -> None:
    st.set_page_config(page_title="Phoenix Aube", page_icon="🌅", layout="wide")

    st.title("Phoenix Aube – Orientation IA-assistée, transparente et humaine")
    st.caption(
        "Version informative non-prescriptive. Disclaimers et sources publiques (INSEE/APEC) inclus."
    )

    with st.expander("Confiance & Transparence (AI Act)", expanded=False):
        st.markdown(
            "- Données publiques référencées.\n"
            "- IA explicable, human-in-the-loop.\n"
            "- Résultats indicatifs, à valider avec un conseiller."
        )

    st.sidebar.header("Navigation")
    section = st.sidebar.radio("Choisissez une section", [
        "Données métier enrichies",
        "Analyse de marché par secteur",
    ])

    st.sidebar.divider()
    st.sidebar.subheader("Écosystème Phoenix")
    st.sidebar.caption("Passage naturel vers CV / Letters / Rise")

    # Context minimal que l'on peut transmettre via query params
    shared_context: Dict[str, Any] = {}

    if section == "Données métier enrichies":
        st.header("Données métier enrichies")
        job_title = st.text_input("Métier (ex: Data Analyst, Développeur)", value="Data Analyst")
        if st.button("Analyser le métier"):
            try:
                data = fetch_json(f"/api/v1/data/enriched-job/{job_title}")
                st.subheader("Résultat")
                st.json(data)
                shared_context["metier"] = job_title
            except Exception as exc:  # noqa: BLE001
                st.error(f"Erreur lors de l'appel API: {exc}")

    elif section == "Analyse de marché par secteur":
        st.header("Analyse de marché par secteur")
        secteurs = ["Tech/IT", "Santé", "Éducation", "Commerce", "Services", "Industrie"]
        sector = st.selectbox("Secteur", options=secteurs, index=0)
        if st.button("Générer l'analyse"):
            try:
                data = fetch_json(f"/api/v1/data/market-analysis/{sector}")
                st.subheader("Résultat")
                st.json(data)
                shared_context["secteur"] = sector
            except Exception as exc:  # noqa: BLE001
                st.error(f"Erreur lors de l'appel API: {exc}")

    st.divider()
    st.subheader("Poursuivre dans l'écosystème Phoenix")
    query = urlencode(shared_context)

    cols = st.columns(3)
    with cols[0]:
        if CV_APP_URL:
            st.link_button("Aller vers Phoenix CV", f"{CV_APP_URL}?{query}" if query else CV_APP_URL)
        else:
            st.caption("Configurer CV_APP_URL dans les secrets Streamlit pour activer le lien")
    with cols[1]:
        if LETTERS_APP_URL:
            st.link_button(
                "Aller vers Phoenix Letters",
                f"{LETTERS_APP_URL}?{query}" if query else LETTERS_APP_URL,
            )
        else:
            st.caption("Configurer LETTERS_APP_URL dans les secrets Streamlit pour activer le lien")
    with cols[2]:
        if RISE_APP_URL:
            st.link_button("Aller vers Phoenix Rise", f"{RISE_APP_URL}?{query}" if query else RISE_APP_URL)
        else:
            st.caption("Configurer RISE_APP_URL dans les secrets Streamlit pour activer le lien")

    st.caption(
        "En beta publique: freemium actif. Étapes premium accessibles avec un conseiller."
    )


if __name__ == "__main__":
    main()


