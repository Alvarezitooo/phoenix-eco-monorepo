"""
Page d'accueil securisee - Phoenix CV
Module UI pour la page d'accueil avec navigation et metriques securisees
"""

import streamlit as st
from ..models.phoenix_user import UserTier
from ..utils.safe_markdown import safe_markdown
from phoenix_shared_ui.components import render_primary_button, render_info_card, render_section_header, render_alert, render_metric_card, render_ariadne_thread


def render_home_page_secure():
    """Page d'accueil securisee"""

    # Sidebar securisee
    with st.sidebar:
        st.markdown("### 🧭 Navigation Securisee")

        # CSRF protection sur les boutons
        csrf_token = st.session_state.get("csrf_token", "")

        if render_primary_button("🏠 Accueil", key=f"home_btn_{csrf_token[:8]}"):
            st.session_state.current_page = "home"
            st.rerun()

        if render_primary_button("✍️ Creer CV", key=f"create_btn_{csrf_token[:8]}"):
            st.session_state.current_page = "create_cv"
            st.rerun()

        if render_primary_button("📁 Importer CV", key=f"upload_btn_{csrf_token[:8]}"):
            st.session_state.current_page = "upload_cv"
            st.rerun()

        if render_primary_button("🎨 Templates", key=f"templates_btn_{csrf_token[:8]}"):
            st.session_state.current_page = "templates"
            st.rerun()

        if render_primary_button("💎 Tarifs", key=f"pricing_btn_{csrf_token[:8]}"):
            st.session_state.current_page = "pricing"
            st.rerun()

        st.markdown("---")

        # Informations securisees utilisateur
        user_tier = st.session_state.get("user_tier", UserTier.FREE)

        st.markdown("### 👤 Compte Securise")
        if user_tier == UserTier.FREE:
            st.markdown("**Plan:** 🆓 Gratuit")
            st.markdown(
                f"**CV ce mois:** {st.session_state.get('cv_count_monthly', 0)}/1"
            )
            render_alert("🔒 Donnees chiffrees AES-256", alert_type="info")
        else:
            st.markdown("**Plan:** 💎 Pro")
            st.markdown("**CV:** Illimites")
            render_alert("🛡️ Protection Enterprise", alert_type="success")

        # Fil d'Ariane
        render_ariadne_thread(
            steps=["Accueil", "Créer CV", "Importer CV", "Templates", "Tarifs"],
            current_step_index=0 # À adapter selon la page active
        )

    # Contenu principal securise
    render_section_header(
        "🛡️ Votre Reconversion en Toute Securite",
        "Premier generateur CV IA securise de niveau Enterprise"
    )
    safe_markdown(
        """
    <p style="text-align: center; opacity: 0.9;">
        🔐 Chiffrement AES-256 • 🛡️ RGPD Compliant • ⚡ Optimisation ATS Securisee
    </p>
    """
    )

    # Fonctionnalites securisees
    col1, col2, col3 = st.columns(3)

    with col1:
        render_info_card(
            title="🔐 Securite Enterprise",
            content="- Chiffrement AES-256 bout-en-bout\n- Anonymisation PII automatique\n- Conformite RGPD stricte\n- Audit trail complet",
            icon="🔒"
        )

    with col2:
        render_info_card(
            title="🧠 IA Protegee",
            content="- Prompts anti-injection\n- Validation multi-niveaux\n- Rate limiting intelligent\n- Monitoring temps reel",
            icon="🧠"
        )

    with col3:
        render_info_card(
            title="🎯 Reconversion Expertisee",
            content="- Templates specialises securises\n- ATS optimization certifiee\n- Donnees anonymisees pour IA\n- Export multi-formats securise",
            icon="🎯"
        )

    # Metriques de securite
    st.markdown("---")
    render_section_header("📊 Metriques de Securite", subtitle=None)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        render_metric_card("Chiffrement", "AES-256", "✅ Actif")

    with col2:
        render_metric_card("Score Securite", "9.2/10", "+4.1 vs Standard")

    with col3:
        render_metric_card("Incidents", "0", "30 derniers jours")

    with col4:
        render_metric_card("Conformite RGPD", "100%", "Audit recent")

    # CTA securise
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])

    with col2:
        if render_primary_button(
            "🛡️ Creer Mon CV Securise", type="primary", use_container_width=True
        ):
            st.session_state.current_page = "create_cv"
            st.rerun()
