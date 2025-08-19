"""
💼 Phoenix CV - Application de Création de CV IA
Architecture Clean Code et Monorepo - Compatible Docker/Render
"""

import os
import sys
import logging
from pathlib import Path

import streamlit as st

# === Configuration Monorepo Path ===
current_dir = Path(__file__).resolve().parent
monorepo_root = current_dir.parent.parent
packages_dir = monorepo_root / "packages"

# Ajout des packages au path
if str(packages_dir) not in sys.path:
    sys.path.insert(0, str(packages_dir))

# === Imports Phoenix CV ===
from ui_components import PhoenixCVUIComponents
from services import PhoenixCVServiceManager, EnvironmentValidator, CVServiceContainer
from auth_manager import PhoenixCVAuthManager

# === Configuration Logging ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class PhoenixCVApp:
    """Application Phoenix CV - Clean Architecture"""
    
    def __init__(self):
        self.auth_manager = PhoenixCVAuthManager()
        self.service_manager = PhoenixCVServiceManager()
        self.services: CVServiceContainer = None
        self.ui_components = PhoenixCVUIComponents
        
    def run(self) -> None:
        """Point d'entrée principal de l'application"""
        
        # Configuration Streamlit
        st.set_page_config(
            page_title="💼 Phoenix CV - Créateur IA",
            page_icon="💼",
            layout="wide",
            initial_sidebar_state="expanded",
        )
        
        # Chargement des styles CSS
        self.ui_components.load_css_styles()
        
        # Validation environnement
        self._validate_environment()
        
        # Initialisation services
        self._initialize_services()
        
        # Gestion authentication
        if not self.auth_manager.is_authenticated():
            self._handle_unauthenticated_flow()
            return
            
        # Application principale
        self._render_authenticated_app()
    
    def _validate_environment(self) -> None:
        """Valide la configuration environnement"""
        validation = EnvironmentValidator.validate_environment()
        
        if not validation["valid"]:
            st.error("❌ Configuration Phoenix CV manquante")
            st.write(EnvironmentValidator.get_validation_summary())
            st.info("""
            **Variables requises pour Phoenix CV :**
            - `GOOGLE_API_KEY` : Pour l'IA Gemini
            
            **Variables optionnelles :**
            - `STRIPE_SECRET_KEY` : Pour les paiements Premium
            - `SUPABASE_URL` + `SUPABASE_ANON_KEY` : Pour l'authentification
            """)
            st.stop()
    
    def _initialize_services(self) -> None:
        """Initialise tous les services Phoenix CV"""
        try:
            self.services = self.service_manager.initialize_all_services()
            
            if self.services.error:
                st.warning(f"⚠️ Services partiellement disponibles: {self.services.error}")
            else:
                logger.info("✅ Services Phoenix CV initialisés avec succès")
                
        except Exception as e:
            logger.error(f"Erreur initialisation services: {e}")
            st.error(f"❌ Impossible d'initialiser Phoenix CV: {e}")
            st.stop()
    
    def _handle_unauthenticated_flow(self) -> None:
        """Gère le flux pour utilisateurs non authentifiés"""
        
        # En-tête application
        self.ui_components.render_login_form_header()
        
        # Teaser gratuit pour inciter à l'inscription
        st.markdown("---")
        generated_cv = self.ui_components.render_quick_cv_generator()
        
        if generated_cv:
            st.markdown("---")
            st.info("💎 **Créez un compte pour des CV plus professionnels !**")
        
        st.markdown("---")
        
        # Page de connexion/inscription
        self.auth_manager.render_login_page()
        
        # Footer sécurisé
        self.ui_components.render_security_footer()
    
    def _render_authenticated_app(self) -> None:
        """Rendu application pour utilisateurs authentifiés"""
        
        current_user = self.auth_manager.get_current_user()
        
        # En-tête principal
        self.ui_components.render_app_header()
        
        # Sidebar navigation
        self._render_sidebar(current_user)
        
        # Contenu principal selon navigation
        selected_page = st.session_state.get("cv_selected_page", "creator")
        
        if selected_page == "creator":
            self._render_cv_creator_page(current_user)
        elif selected_page == "templates":
            self._render_templates_page(current_user)
        elif selected_page == "history":
            self._render_history_page(current_user)
        elif selected_page == "settings":
            self._render_settings_page(current_user)
        else:
            self._render_dashboard_page(current_user)
            
        # Footer inspirant
        self.ui_components.render_inspirational_footer()
    
    def _render_sidebar(self, current_user) -> None:
        """Rendu sidebar navigation"""
        
        with st.sidebar:
            st.markdown(f"### 👋 Bonjour {current_user.email.split('@')[0]} !")
            
            # Statut utilisateur
            if current_user.user_tier == "PREMIUM":
                st.success("💎 Compte Premium")
            else:
                st.info("🆓 Compte Gratuit")
                if st.button("🔓 Passer à Premium"):
                    st.balloons()
                    st.info("Fonctionnalité bientôt disponible !")
            
            st.markdown("---")
            
            # Navigation
            st.markdown("### 📂 Navigation")
            
            pages = {
                "dashboard": "📊 Tableau de Bord",
                "creator": "✨ Créateur de CV", 
                "templates": "📋 Templates",
                "history": "📚 Historique",
                "settings": "⚙️ Paramètres"
            }
            
            for page_key, page_name in pages.items():
                if st.button(page_name, key=f"nav_{page_key}"):
                    st.session_state.cv_selected_page = page_key
                    st.rerun()
            
            st.markdown("---")
            
            # Déconnexion
            if st.button("🚪 Se déconnecter"):
                self.auth_manager.logout()
    
    def _render_dashboard_page(self, current_user) -> None:
        """Page tableau de bord"""
        st.markdown("## 📊 Tableau de Bord Phoenix CV")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("CV Créés", "0", "Nouveau compte")
        
        with col2:
            st.metric("Templates Utilisés", "0", "Découvrez nos modèles")
        
        with col3:
            st.metric("Optimisations ATS", "0", "Boostez vos candidatures")
        
        st.markdown("### 🚀 Actions Rapides")
        
        col_action1, col_action2 = st.columns(2)
        
        with col_action1:
            if st.button("✨ Créer un nouveau CV", use_container_width=True):
                st.session_state.cv_selected_page = "creator"
                st.rerun()
        
        with col_action2:
            if st.button("📋 Parcourir les templates", use_container_width=True):
                st.session_state.cv_selected_page = "templates"
                st.rerun()
    
    def _render_cv_creator_page(self, current_user) -> None:
        """Page créateur de CV"""
        st.markdown("## ✨ Créateur de CV Phoenix")
        
        if current_user.user_tier != "PREMIUM":
            self.ui_components.render_free_upgrade_banner()
        
        # Formulaire création CV
        with st.form("cv_creator_form"):
            st.markdown("### 👤 Informations Personnelles")
            
            col1, col2 = st.columns(2)
            
            with col1:
                full_name = st.text_input("Nom complet", placeholder="Jean Dupont")
                job_title = st.text_input("Titre du poste", placeholder="Développeur Senior")
                email = st.text_input("Email", placeholder="jean.dupont@email.com")
            
            with col2:
                phone = st.text_input("Téléphone", placeholder="06 12 34 56 78")
                location = st.text_input("Localisation", placeholder="Paris, France")
                linkedin = st.text_input("LinkedIn", placeholder="linkedin.com/in/jean-dupont")
            
            st.markdown("### 💼 Expérience Professionnelle")
            experience = st.text_area(
                "Décrivez votre expérience",
                placeholder="Ex: 5 ans en développement Python...",
                height=150
            )
            
            st.markdown("### 🛠️ Compétences")
            skills = st.text_area(
                "Listez vos compétences",
                placeholder="Python, React, Docker, AWS...",
                height=100
            )
            
            st.markdown("### 🎓 Formation")
            education = st.text_area(
                "Votre parcours éducatif",
                placeholder="Master en Informatique - Université...",
                height=100
            )
            
            # Bouton génération
            generate_cv = st.form_submit_button(
                "🚀 Générer mon CV Phoenix",
                type="primary",
                use_container_width=True
            )
        
        if generate_cv:
            if full_name and job_title and experience and skills:
                with st.spinner("✨ Génération de votre CV professionnel..."):
                    # Génération CV
                    cv_content = self._generate_professional_cv(
                        full_name, job_title, email, phone, location, linkedin,
                        experience, skills, education
                    )
                    
                    st.success("✅ CV généré avec succès !")
                    st.markdown("### 📄 Votre CV Professionnel Phoenix")
                    
                    st.text_area(
                        "",
                        value=cv_content,
                        height=500,
                        key="generated_professional_cv"
                    )
                    
                    # Actions
                    col_dl, col_edit, col_share = st.columns(3)
                    
                    with col_dl:
                        st.download_button(
                            "📥 Télécharger",
                            data=cv_content,
                            file_name=f"cv_{full_name.lower().replace(' ', '_')}_phoenix.txt",
                            mime="text/plain"
                        )
                    
                    with col_edit:
                        if current_user.user_tier == "PREMIUM":
                            st.button("✏️ Éditer", disabled=True, help="Bientôt disponible")
                        else:
                            self.ui_components.render_premium_teaser(
                                "Éditeur Avancé",
                                "Personnalisez votre CV avec notre éditeur intelligent",
                                "premium_editor"
                            )
                    
                    with col_share:
                        if current_user.user_tier == "PREMIUM":
                            st.button("🔗 Partager", disabled=True, help="Bientôt disponible")
                        else:
                            self.ui_components.render_premium_teaser(
                                "Partage Pro",
                                "Partagez votre CV avec un lien professionnel",
                                "premium_share"
                            )
            else:
                st.error("❌ Veuillez remplir au moins le nom, poste, expérience et compétences")
    
    def _generate_professional_cv(
        self, full_name: str, job_title: str, email: str, phone: str,
        location: str, linkedin: str, experience: str, skills: str, education: str
    ) -> str:
        """Génère un CV professionnel formaté"""
        
        return f"""
# {full_name}
## {job_title}

### 📧 Contact
- Email: {email}
- Téléphone: {phone if phone else 'N/A'}
- Localisation: {location if location else 'N/A'}
- LinkedIn: {linkedin if linkedin else 'N/A'}

---

### 💼 Expérience Professionnelle
{experience}

### 🛠️ Compétences Techniques
{skills}

### 🎓 Formation
{education if education else 'À compléter...'}

### 🎯 Profil Professionnel
{job_title} expérimenté(e) passionné(e) par l'innovation et l'excellence technique. 
Fort d'une solide expérience dans le domaine, je m'engage à apporter 
une valeur ajoutée significative aux projets et équipes.

### 🌟 Objectifs de Carrière
Contribuer au succès d'une entreprise innovante en mettant à profit 
mes compétences en {job_title.lower()} et ma passion pour les défis techniques.

---
*CV généré par Phoenix CV - Votre partenaire pour une carrière réussie*
*Optimisé pour les systèmes ATS (Applicant Tracking System)*
        """
    
    def _render_templates_page(self, current_user) -> None:
        """Page des templates"""
        st.markdown("## 📋 Templates Phoenix CV")
        
        templates = [
            {"name": "Moderne", "description": "Design épuré et professionnel", "premium": False},
            {"name": "Créatif", "description": "Pour les profils artistiques", "premium": True},
            {"name": "Tech", "description": "Optimisé pour les développeurs", "premium": True},
            {"name": "Executive", "description": "Pour les postes de direction", "premium": True},
        ]
        
        cols = st.columns(2)
        
        for i, template in enumerate(templates):
            with cols[i % 2]:
                if template["premium"] and current_user.user_tier != "PREMIUM":
                    # Template premium pour utilisateur gratuit
                    st.markdown(f"""
                    <div style="border: 2px dashed #fbbf24; padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
                        <h4>🔒 {template['name']} (Premium)</h4>
                        <p>{template['description']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"🔓 Débloquer {template['name']}", key=f"template_{i}"):
                        st.info("💎 Passez à Premium pour accéder à ce template !")
                else:
                    # Template gratuit ou utilisateur premium
                    st.markdown(f"""
                    <div style="border: 2px solid #10b981; padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
                        <h4>✅ {template['name']}</h4>
                        <p>{template['description']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"📋 Utiliser {template['name']}", key=f"use_template_{i}"):
                        st.success(f"Template {template['name']} sélectionné ! Fonctionnalité bientôt disponible.")
    
    def _render_history_page(self, current_user) -> None:
        """Page historique"""
        st.markdown("## 📚 Historique de vos CV")
        
        st.info("🔄 Fonctionnalité en développement")
        st.markdown("""
        Bientôt disponible :
        - 📋 Liste de tous vos CV créés
        - 📊 Statistiques de performance
        - 🔄 Versions et révisions
        - 📤 Historique des candidatures
        """)
    
    def _render_settings_page(self, current_user) -> None:
        """Page paramètres"""
        st.markdown("## ⚙️ Paramètres du Compte")
        
        st.markdown("### 👤 Informations du Compte")
        st.text_input("Email", value=current_user.email, disabled=True)
        st.text_input("Statut", value=current_user.user_tier, disabled=True)
        
        st.markdown("### 🔧 Préférences")
        st.checkbox("Notifications par email", value=True)
        st.checkbox("Sauvegardes automatiques", value=True)
        st.selectbox("Langue", ["Français", "English"], index=0)
        
        st.markdown("### 🔒 Sécurité")
        if st.button("🔐 Changer le mot de passe"):
            st.info("Fonctionnalité bientôt disponible")
        
        if st.button("📤 Exporter mes données"):
            st.info("Export RGPD bientôt disponible")


def main() -> None:
    """Point d'entrée principal"""
    try:
        app = PhoenixCVApp()
        app.run()
    except Exception as e:
        logger.error(f"Erreur critique Phoenix CV: {e}")
        st.error(f"❌ Erreur Phoenix CV: {e}")
        st.info("🔄 Rechargez la page ou contactez le support")


if __name__ == "__main__":
    main()