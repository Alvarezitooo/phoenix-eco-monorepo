"""
🎨 Phoenix Letters UI Components
Interface utilisateur modulaire et réutilisable
"""

import os
import streamlit as st
from typing import Optional, Dict, Any
from core.entities.user import UserTier


class PhoenixUIComponents:
    """Composants UI centralisés pour Phoenix Letters"""

    @staticmethod
    def render_app_header(current_user: Dict[str, Any]) -> None:
        """Affiche l'en-tête principal de l'application"""
        tier_status = (
            "Premium"
            if current_user.get("user_tier") == UserTier.PREMIUM
            else "Gratuite"
        )
        tier_emoji = "💎" if current_user.get("user_tier") == UserTier.PREMIUM else "🌟"

        st.markdown(
            f"""
        <div style="
            background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
            padding: 2rem;
            border-radius: 20px;
            color: white;
            margin-bottom: 2rem;
            box-shadow: 0 10px 30px rgba(249, 115, 22, 0.3);
        ">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h1 style="margin: 0; font-size: 2.5rem; font-weight: 700;">🔥 Phoenix Letters</h1>
                    <p style="margin: 0.5rem 0 0 0; opacity: 0.9; font-size: 1.1rem;">
                        Votre copilote bienveillant pour des lettres d'exception
                    </p>
                </div>
                <div style="text-align: right;">
                    <div style="background: rgba(255,255,255,0.2); padding: 0.8rem 1.5rem; border-radius: 15px; margin-bottom: 0.5rem;">
                        <span style="font-weight: 600; font-size: 1.1rem;">{tier_emoji} {tier_status}</span>
                    </div>
                    <p style="margin: 0; opacity: 0.8; font-size: 0.9rem;">
                        {current_user.get('email', 'Utilisateur')}
                    </p>
                </div>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    @staticmethod
    def render_login_form_header() -> None:
        """Affiche l'en-tête du formulaire de connexion"""
        st.markdown(
            """
        <div style="text-align: center; margin: 2rem 0;">
            <h1 style="
                background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                font-size: 3rem;
                font-weight: 700;
                margin-bottom: 0.5rem;
            ">🔥 Phoenix Letters</h1>
            <p style="color: #6b7280; font-size: 1.1rem; margin-bottom: 2rem;">
                Votre copilote bienveillant pour des lettres d'exception
            </p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    @staticmethod
    def render_premium_teaser(
        feature_name: str, description: str, button_key: str
    ) -> bool:
        """Affiche un teaser pour une fonctionnalité Premium"""
        st.markdown(
            f"""
        <div style="background: linear-gradient(135deg, #fef3e2 0%, #fde8cc 100%); 
                   padding: 1.5rem; border-radius: 15px; border-left: 4px solid #8b5cf6; margin-bottom: 1rem;">
            <h4 style="color: #7c3aed; margin: 0 0 0.5rem 0;">🎯 {feature_name}</h4>
            <p style="color: #9a3412; margin: 0; font-size: 0.9rem;">
                {description}
            </p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        if st.button(
            f"🔓 Débloquer {feature_name}", key=button_key, use_container_width=True
        ):
            st.balloons()
            st.info(f"🎉 Passez à Premium pour débloquer {feature_name} !")
            return True
        return False

    @staticmethod
    def render_free_upgrade_banner() -> None:
        """Affiche la bannière d'upgrade pour les utilisateurs Free"""
        st.markdown(
            """
        <div style="background: linear-gradient(135deg, #f0f0f0 0%, #e0e0e0 100%); padding: 0.8rem; border-radius: 8px; margin-bottom: 1.5rem; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <p style="margin: 0; font-size: 0.95rem; font-weight: 500; color: #333;">
                Vous utilisez la version gratuite. Libérez toute la puissance de Phoenix.
            </p>
            <div style="margin-top: 0.5rem;">
                <a href="/premium" target="_self" style="text-decoration: none;">
                    <button style="background: #f97316; color: white; border: none; padding: 0.4rem 1rem; border-radius: 5px; cursor: pointer; font-weight: bold; font-size: 0.85rem;">
                        Voir les offres
                    </button>
                </a>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    @staticmethod
    def render_security_footer() -> None:
        """Affiche le pied de page sécurité RGPD"""
        st.markdown(
            """
        <div style="text-align: center; margin: 3rem 0; padding: 1rem; 
                   background: #f1f5f9; border-radius: 10px; border: 1px solid #e2e8f0;">
            <p style="margin: 0; color: #475569; font-size: 0.9rem;">
                🔒 <strong>Sécurité Phoenix :</strong> Vos données sont chiffrées et protégées selon les standards RGPD. 
                Nous respectons votre vie privée et ne partageons jamais vos informations.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    @staticmethod
    def render_inspirational_footer() -> None:
        """Affiche le pied de page inspirant"""
        st.markdown(
            """
        <div style="text-align: center; padding: 1rem; opacity: 0.7;">
            <p style="margin: 0; font-style: italic; color: #64748b;">
                "Chaque lettre est une opportunité de briller. Phoenix vous accompagne avec bienveillance vers votre réussite."
            </p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    @staticmethod
    def load_css_styles() -> None:
        """Charge les styles CSS du Design System Phoenix"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        style_path = os.path.join(
            current_dir, "../packages/phoenix_shared_ui/phoenix_shared_ui/style.css"
        )

        try:
            if os.path.exists(style_path):
                with open(style_path) as f:
                    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
            else:
                # Fallback pour Streamlit Cloud
                alt_style_path = os.path.join(
                    current_dir,
                    "../../packages/phoenix_shared_ui/phoenix_shared_ui/style.css",
                )
                if os.path.exists(alt_style_path):
                    with open(alt_style_path) as f:
                        st.markdown(
                            f"<style>{f.read()}</style>", unsafe_allow_html=True
                        )
        except Exception:
            # Gestion silencieuse pour ne pas casser l'app
            pass

    @staticmethod
    def render_quick_letter_generator() -> Optional[str]:
        """Affiche le générateur de lettres gratuit et retourne le contenu généré"""
        st.markdown("### 🆓 Générateur Gratuit - Testez Phoenix Letters")

        with st.form("quick_letter_generator"):
            st.write("**Générez votre première lettre gratuitement :**")

            col_input1, col_input2 = st.columns(2)
            with col_input1:
                company_name = st.text_input(
                    "🏢 Nom de l'entreprise", placeholder="Ex: Google, Microsoft..."
                )
                position = st.text_input(
                    "💼 Poste visé", placeholder="Ex: Développeur, Manager..."
                )

            with col_input2:
                your_name = st.text_input(
                    "👤 Votre nom", placeholder="Votre nom complet"
                )
                experience = st.selectbox(
                    "📈 Votre expérience",
                    [
                        "Débutant (0-2 ans)",
                        "Intermédiaire (2-5 ans)",
                        "Senior (5+ ans)",
                    ],
                )

            motivation = st.text_area(
                "✨ Pourquoi cette entreprise vous intéresse ?",
                placeholder="Expliquez en quelques lignes pourquoi vous voulez rejoindre cette entreprise...",
                height=100,
            )

            generate_button = st.form_submit_button(
                "🚀 Générer ma lettre gratuite",
                use_container_width=True,
                type="primary",
            )

        if generate_button:
            if company_name and position and your_name and motivation:
                with st.spinner("✨ Génération de votre lettre personnalisée..."):
                    # Génération simple et immédiate
                    generated_letter = f"""Objet : Candidature pour le poste de {position}

Madame, Monsieur,

Je me permets de vous adresser ma candidature pour le poste de {position} au sein de {company_name}.

{motivation}

Fort(e) de mon expérience en tant que profil {experience.lower()}, je suis convaincu(e) que mes compétences et ma motivation seront des atouts précieux pour votre équipe.

Je serais ravi(e) de vous rencontrer pour discuter de cette opportunité et vous démontrer ma motivation.

Je vous prie d'agréer, Madame, Monsieur, l'expression de mes salutations distinguées.

{your_name}"""

                    st.success("✅ Lettre générée avec succès !")
                    st.markdown("### 📄 Votre lettre de motivation :")
                    st.text_area(
                        "",
                        value=generated_letter,
                        height=300,
                        key="generated_letter_display",
                    )

                    col_action1, col_action2, col_action3 = st.columns(3)
                    with col_action1:
                        st.download_button(
                            "📥 Télécharger",
                            data=generated_letter,
                            file_name=f"lettre_{company_name.lower().replace(' ', '_')}.txt",
                            mime="text/plain",
                        )
                    with col_action2:
                        if st.button("🔄 Regénérer"):
                            if "generated_letter" in st.session_state:
                                del st.session_state["generated_letter"]
                            st.rerun()
                    with col_action3:
                        st.info("💎 Upgrader pour plus de personnalisation")

                    return generated_letter
            else:
                st.error("❌ Veuillez remplir tous les champs obligatoires")

        return None
