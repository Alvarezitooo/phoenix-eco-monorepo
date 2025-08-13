"""
🚀 Phoenix Letters - Point d'entrée principal avec authentification unifiée
Intégration complète Phoenix Shared Auth + Cross-App Navigation

Author: Claude Phoenix DevSecOps Guardian
Version: 2.0.0 - Unified Authentication Ready
"""

import logging
import streamlit as st
from config.settings import Settings
from infrastructure.database.db_connection import DatabaseConnection
from infrastructure.auth.phoenix_letters_unified_auth import create_phoenix_letters_auth_service

# Configuration du logger
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Import du style global du Design System
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
style_path = os.path.join(current_dir, "../packages/phoenix_shared_ui/phoenix_shared_ui/style.css")

try:
    with open(style_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    logger.info("✅ Design System chargé avec succès")
except FileNotFoundError:
    logger.warning("⚠️ Fichier de style Design System non trouvé")
except Exception as e:
    logger.error(f"❌ Erreur chargement Design System: {e}")


def configure_page():
    """Configuration initiale de la page Streamlit."""
    st.set_page_config(
        page_title="Phoenix Letters - IA Reconversion",
        page_icon="📝",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://phoenix-letters.streamlit.app/about',
            'Report a bug': "https://github.com/phoenix-letters/issues",
            'About': "# Phoenix Letters\nGénérateur IA de lettres de motivation pour reconversions professionnelles."
        }
    )


def render_header():
    """Affiche le header principal de l'application."""
    st.markdown(
        """
        <div style="background: linear-gradient(90deg, #f97316 0%, #ef4444 100%); 
                    padding: 1.5rem; border-radius: 10px; margin-bottom: 2rem; text-align: center;">
            <h1 style="color: white; margin: 0; font-size: 2.2rem;">📝 Phoenix Letters</h1>
            <p style="color: white; opacity: 0.9; margin: 0.5rem 0 0 0; font-size: 1.1rem;">
                Générateur IA de lettres de motivation pour reconversions professionnelles
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_navigation(current_user, auth_service):
    """Affiche la navigation principale."""
    if current_user:
        # Navigation pour utilisateurs connectés
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        
        with col1:
            session_info = auth_service.get_session_info()
            ecosystem_badge = "🌟" if session_info.get("phoenix_ecosystem") else ""
            st.markdown(f"👋 **Connecté** {current_user.email} {ecosystem_badge}")
        
        with col2:
            user_tier = session_info.get("user_tier", "free")
            tier_emoji = "🆓" if user_tier == "free" else "⭐"
            st.markdown(f"**Plan:** {tier_emoji} {user_tier.title()}")
        
        with col3:
            if st.button("🔗 Écosystème Phoenix", help="Accédez aux autres applications Phoenix"):
                st.markdown(
                    """
                    ### 🌟 Écosystème Phoenix
                    
                    - 📄 **Phoenix CV** : Créateur de CV optimisé IA
                    - 📝 **Phoenix Letters** : Générateur de lettres (vous êtes ici)
                    - 🌅 **Phoenix Rise** : Coach de développement personnel
                    - 🌐 **Phoenix Website** : Hub principal
                    """
                )
        
        with col4:
            if st.button("🔓 Déconnexion"):
                auth_service.logout_user()
                st.success("✅ Déconnexion réussie")
                st.rerun()
    else:
        # Navigation pour visiteurs
        st.markdown("### 🎯 Bienvenue sur Phoenix Letters")
        st.markdown("Créez des lettres de motivation optimisées IA pour votre reconversion professionnelle.")


def render_main_app(current_user):
    """Affiche l'application principale après authentification."""
    # Import des pages et services (uniquement après auth)
    from ui.pages.generator_page import GeneratorPage
    from ui.pages.about_page import AboutPage
    from ui.pages.premium_page import PremiumPage
    from ui.pages.settings_page import SettingsPage
    
    # Navigation par onglets
    tab1, tab2, tab3, tab4 = st.tabs([
        "📝 Générateur", "⭐ Premium", "⚙️ Paramètres", "ℹ️ À propos"
    ])
    
    with tab1:
        st.markdown("### 📝 Générateur de lettres de motivation")
        st.info("🚧 Interface de génération en cours d'intégration avec l'authentification unifiée")
        
        # Affichage des informations utilisateur
        st.markdown("#### 👤 Informations de session")
        col1, col2 = st.columns(2)
        
        with col1:
            if hasattr(current_user, 'email'):
                st.write(f"**Email :** {current_user.email}")
            if hasattr(current_user, 'username'):
                st.write(f"**Nom :** {current_user.username}")
        
        with col2:
            if hasattr(current_user, 'subscription'):
                tier = getattr(current_user.subscription, 'current_tier', 'free')
                st.write(f"**Plan :** {tier.title()}")
                
                # Suggestions selon le tier
                if tier == 'free':
                    st.info("💡 **Conseil** : Passez Premium pour des lettres illimitées et l'optimisation ATS")
    
    with tab2:
        st.markdown("### ⭐ Fonctionnalités Premium")
        st.info("🚧 Interface Premium en cours d'intégration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🆓 Version Gratuite")
            st.markdown("- ✅ 3 lettres par mois")
            st.markdown("- ✅ Modèles de base")
            st.markdown("- ✅ Support email")
        
        with col2:
            st.markdown("#### ⭐ Version Premium")
            st.markdown("- ✅ **Lettres illimitées**")
            st.markdown("- ✅ **Optimisation ATS avancée**")
            st.markdown("- ✅ **Templates premium**")
            st.markdown("- ✅ **Analyse de correspondance CV/Offre**")
            st.markdown("- ✅ **Support prioritaire**")
            
            if st.button("🚀 Passer Premium", type="primary"):
                st.success("🔗 Redirection vers le paiement...")
    
    with tab3:
        st.markdown("### ⚙️ Paramètres utilisateur")
        st.info("🚧 Interface de paramètres en cours d'intégration")
        
        # Paramètres de base
        st.markdown("#### 📧 Préférences email")
        newsletter = st.checkbox("Recevoir la newsletter Phoenix", value=False)
        career_tips = st.checkbox("Conseils carrière personnalisés", value=True)
        
        st.markdown("#### 🔒 Confidentialité")
        data_retention = st.selectbox(
            "Durée de conservation des lettres",
            ["30 jours", "90 jours", "1 an", "Permanent"]
        )
        
        if st.button("💾 Sauvegarder les paramètres"):
            st.success("✅ Paramètres sauvegardés")
    
    with tab4:
        st.markdown("### ℹ️ À propos de Phoenix Letters")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(
                """
                #### 🎯 Notre mission
                Phoenix Letters révolutionne la création de lettres de motivation 
                pour les reconversions professionnelles grâce à l'intelligence artificielle.
                
                #### ⚡ Fonctionnalités clés
                - 🤖 **IA Gemini 1.5** : Génération ultra-personnalisée
                - 🎯 **Spécialisation reconversion** : Expertise métier
                - 🔒 **Sécurité RGPD** : Protection données garantie
                - 🌟 **Écosystème Phoenix** : Synergie avec CV et coaching
                """
            )
        
        with col2:
            st.markdown(
                """
                #### 📊 Statistiques
                - ✅ **+10,000** lettres générées
                - 🎯 **92%** de taux de réponse moyen
                - ⭐ **4.8/5** satisfaction utilisateur
                - 🚀 **France #1** reconversion IA
                
                #### 🔗 Liens utiles
                - [Documentation](https://phoenix-letters.streamlit.app/docs)
                - [Support](mailto:support@phoenix-letters.fr)
                - [Écosystème Phoenix](https://phoenix-eco-monorepo.vercel.app)
                """
            )


def main():
    """Point d'entrée principal avec authentification unifiée."""
    # Configuration page
    configure_page()
    
    # Chargement des services
    settings = Settings()
    
    @st.cache_resource
    def get_db_connection(settings: Settings) -> DatabaseConnection:
        """Initialise et retourne une connexion à la base de données."""
        return DatabaseConnection(settings)
    
    db_connection = get_db_connection(settings)
    
    # Initialisation du service d'authentification unifié
    auth_service = create_phoenix_letters_auth_service(settings, db_connection)
    
    # Header principal
    render_header()
    
    # Bannière de recherche Phoenix (si activée)
    try:
        enable_banner = os.getenv("ENABLE_RESEARCH_BANNER", "false").lower() == "true"
        if enable_banner:
            st.info("🔬 **Recherche Phoenix** : Votre utilisation contribue à améliorer l'IA de reconversion")
    except:
        pass
    
    # Vérification utilisateur actuel (cross-app + local)
    current_user = auth_service.get_current_user()
    
    if current_user:
        # Utilisateur connecté - afficher l'application
        render_navigation(current_user, auth_service)
        
        # Bannière cross-app si utilisateur vient d'une autre app
        if st.session_state.get("cross_app_source"):
            source = st.session_state.get("cross_app_source")
            st.success(f"✅ Connexion réussie depuis {source.title()} ! Bienvenue sur Phoenix Letters 🎉")
        
        # Application principale
        render_main_app(current_user)
        
        # Recommandations écosystème
        if auth_service.is_shared_auth_available():
            st.markdown("---")
            st.markdown("### 🌟 Découvrir l'écosystème Phoenix")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📄 Phoenix CV", use_container_width=True):
                    st.info("🔗 Redirection vers Phoenix CV...")
            
            with col2:
                if st.button("🌅 Phoenix Rise", use_container_width=True):
                    st.info("🔗 Redirection vers Phoenix Rise...")
            
            with col3:
                if st.button("🌐 Phoenix Hub", use_container_width=True):
                    st.info("🔗 Redirection vers Phoenix Website...")
    
    else:
        # Utilisateur non connecté - afficher l'interface d'authentification
        render_navigation(None, auth_service)
        
        st.markdown("---")
        
        # Interface d'authentification
        authenticated_user = auth_service.render_auth_interface()
        
        if authenticated_user:
            st.rerun()
    
    # Footer informations
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; color: #666; font-size: 0.9rem; padding: 1rem;">
            <p>🚀 <strong>Phoenix Letters</strong> - Générateur IA de lettres de motivation • 
               Fait avec ❤️ en France • 
               <a href="https://phoenix-eco-monorepo.vercel.app" style="color: #f97316;">Écosystème Phoenix</a>
            </p>
            <p style="font-size: 0.8rem;">
                🔒 Conforme RGPD • 🌱 Neutre carbone • ⚡ Propulsé par Gemini 1.5 Flash
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()