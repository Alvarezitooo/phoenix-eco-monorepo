"""
🎨 Phoenix CV UI Components
Interface utilisateur modulaire et réutilisable pour Phoenix CV
"""

import os
import streamlit as st
from typing import Optional, Dict, Any


class PhoenixCVUIComponents:
    """Composants UI centralisés pour Phoenix CV"""
    
    @staticmethod
    def render_app_header() -> None:
        """Affiche l'en-tête principal de l'application CV"""
        st.markdown(
            f"""
        <div style="
            background: linear-gradient(135deg, #3b82f6 0%, #1e40af 100%);
            padding: 2rem;
            border-radius: 20px;
            color: white;
            margin-bottom: 2rem;
            box-shadow: 0 10px 30px rgba(59, 130, 246, 0.3);
        ">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h1 style="margin: 0; font-size: 2.5rem; font-weight: 700;">💼 Phoenix CV</h1>
                    <p style="margin: 0.5rem 0 0 0; opacity: 0.9; font-size: 1.1rem;">
                        Votre CV professionnel optimisé par l'IA
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
                background: linear-gradient(135deg, #3b82f6 0%, #1e40af 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                font-size: 3rem;
                font-weight: 700;
                margin-bottom: 0.5rem;
            ">💼 Phoenix CV</h1>
            <p style="color: #6b7280; font-size: 1.1rem; margin-bottom: 2rem;">
                Créez un CV professionnel optimisé par l'IA
            </p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    @staticmethod
    def render_premium_teaser(
        feature_name: str, description: str, button_key: str
    ) -> bool:
        """Affiche un teaser pour une fonctionnalité Premium CV"""
        st.markdown(
            f"""
        <div style="background: linear-gradient(135deg, #fef3e2 0%, #fde8cc 100%); 
                   padding: 1.5rem; border-radius: 15px; border-left: 4px solid #3b82f6; margin-bottom: 1rem;">
            <h4 style="color: #1e40af; margin: 0 0 0.5rem 0;">💼 {feature_name}</h4>
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
        <div style="background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%); padding: 0.8rem; border-radius: 8px; margin-bottom: 1.5rem; text-align: center; box-shadow: 0 2px 8px rgba(59, 130, 246, 0.1);">
            <p style="margin: 0; font-size: 0.95rem; font-weight: 500; color: #1e40af;">
                Version gratuite Phoenix CV. Upgradez pour plus de fonctionnalités.
            </p>
            <div style="margin-top: 0.5rem;">
                <a href="/premium" target="_self" style="text-decoration: none;">
                    <button style="background: #3b82f6; color: white; border: none; padding: 0.4rem 1rem; border-radius: 5px; cursor: pointer; font-weight: bold; font-size: 0.85rem;">
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
                🔒 <strong>Sécurité Phoenix :</strong> Vos CV sont chiffrés et protégés selon les standards RGPD. 
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
                "Votre CV est votre première impression. Phoenix vous aide à la rendre inoubliable."
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
                # Fallback pour déploiement 
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
    def render_quick_cv_generator() -> Optional[str]:
        """Affiche le générateur de CV gratuit et retourne le contenu généré"""
        st.markdown("### 🆓 Générateur CV Gratuit - Testez Phoenix CV")

        with st.form("quick_cv_generator"):
            st.write("**Créez votre CV professionnel gratuitement :**")

            col_input1, col_input2 = st.columns(2)
            with col_input1:
                full_name = st.text_input(
                    "👤 Nom complet", placeholder="Ex: Jean Dupont"
                )
                job_title = st.text_input(
                    "💼 Titre du poste", placeholder="Ex: Développeur Senior"
                )

            with col_input2:
                email = st.text_input(
                    "📧 Email", placeholder="jean.dupont@email.com"
                )
                phone = st.text_input(
                    "📱 Téléphone", placeholder="06 12 34 56 78"
                )

            skills = st.text_area(
                "🛠️ Compétences clés",
                placeholder="Ex: Python, React, Management...",
                height=100,
            )

            experience = st.text_area(
                "💼 Expérience professionnelle",
                placeholder="Décrivez brièvement votre expérience principale...",
                height=120,
            )

            generate_button = st.form_submit_button(
                "🚀 Générer mon CV gratuit",
                use_container_width=True,
                type="primary",
            )

        if generate_button:
            if full_name and job_title and email and skills:
                with st.spinner("✨ Génération de votre CV professionnel..."):
                    # Génération simple et immédiate
                    generated_cv = f"""
# {full_name}
## {job_title}

📧 {email} | 📱 {phone if phone else 'N/A'}

---

## 🛠️ Compétences
{skills}

## 💼 Expérience Professionnelle
{experience if experience else 'À compléter...'}

## 🎯 Profil Professionnel
Professionnel expérimenté en {job_title.lower()}, passionné par l'innovation et l'excellence.

---
*CV généré par Phoenix CV - Votre partenaire pour une carrière réussie*
                    """

                    st.success("✅ CV généré avec succès !")
                    st.markdown("### 📄 Votre CV professionnel :")
                    st.text_area(
                        "",
                        value=generated_cv,
                        height=400,
                        key="generated_cv_display",
                    )

                    col_action1, col_action2, col_action3 = st.columns(3)
                    with col_action1:
                        st.download_button(
                            "📥 Télécharger",
                            data=generated_cv,
                            file_name=f"cv_{full_name.lower().replace(' ', '_')}.txt",
                            mime="text/plain",
                        )
                    with col_action2:
                        if st.button("🔄 Regénérer"):
                            if "generated_cv" in st.session_state:
                                del st.session_state["generated_cv"]
                            st.rerun()
                    with col_action3:
                        st.info("💎 Upgrader pour CV professionnel")

                    return generated_cv
            else:
                st.error("❌ Veuillez remplir au moins le nom, poste, email et compétences")

        return None