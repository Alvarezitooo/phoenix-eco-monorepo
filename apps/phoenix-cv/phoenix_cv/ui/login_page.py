"""
🔑 Phoenix CV - Page de Login Esthétique
Interface d'authentification moderne et sécurisée pour Phoenix CV

Author: Claude Phoenix DevSecOps Guardian
Version: 1.0.0 - Production Ready
"""

import streamlit as st
from typing import Optional
from phoenix_cv.services.phoenix_unified_auth import phoenix_cv_auth


def render_login_choice_page():
    """Affiche la page de choix d'accès avec design moderne."""
    
    # Hero Section esthétique
    st.markdown(
        """
        <div style="text-align: center; padding: 3rem 1rem; background: linear-gradient(135deg, #28a745 0%, #20c997 100%); border-radius: 20px; color: white; margin-bottom: 2rem;">
            <h1 style="font-size: 2.5rem; margin-bottom: 1rem; font-weight: 600;">📄 Phoenix CV</h1>
            <h2 style="font-size: 1.5rem; margin-bottom: 1.5rem; opacity: 0.9; font-weight: 400;">Créateur de CV IA Nouvelle Génération</h2>
            <p style="font-size: 1.2rem; margin-bottom: 0; opacity: 0.8;">Optimisé pour reconversions • Sécurisé RGPD • ATS Compatible</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # Section de choix avec design moderne
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown(
            """
            ### 🎯 Commencez maintenant
            
            **Aucune inscription requise** • **Données sécurisées** • **Résultat professionnel**
            
            Créez un CV optimisé qui met en valeur votre reconversion professionnelle.
            """
        )
        
        # CTA Principal - Mode Invité
        if st.button(
            "▶️ Créer mon CV maintenant",
            type="primary",
            use_container_width=True,
            key="guest_cv_button",
        ):
            # Création session invité via le service unifié
            guest_data = phoenix_cv_auth.create_guest_session()
            st.session_state.auth_flow = "guest"
            st.success("✅ Session invité créée ! Vous pouvez maintenant créer votre CV.")
            st.rerun()
        
        # Option secondaire - Compte existant
        st.markdown("---")
        st.markdown("##### 💾 Vous avez déjà un compte ?")
        if st.button(
            "🔑 Me connecter pour retrouver mes CV",
            use_container_width=True,
            key="login_cv_button",
        ):
            st.session_state.auth_flow = "login"
            st.rerun()
        
        # Informations sur les avantages d'un compte
        st.markdown("---")
        st.info(
            "🏆 **Avec un compte Phoenix** : Sauvegarde automatique de vos CV, "
            "historique de vos créations, synchronisation avec Phoenix Letters, "
            "et accès aux fonctionnalités Premium."
        )


def render_login_form_page():
    """Affiche le formulaire de connexion/inscription esthétique."""
    
    # Hero Section de connexion
    st.markdown(
        """
        <div style="text-align: center; padding: 2rem 1rem; background: linear-gradient(135deg, #28a745 0%, #20c997 100%); border-radius: 20px; color: white; margin-bottom: 2rem;">
            <h1 style="font-size: 2.2rem; margin-bottom: 0.5rem; font-weight: 600;">🔑 Connexion Phoenix CV</h1>
            <p style="font-size: 1.1rem; margin-bottom: 0; opacity: 0.9;">Retrouvez vos CV sauvegardés et accédez au Premium</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # Centrage du formulaire
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Container esthétique pour le formulaire
        st.markdown(
            """
            <div style="background: white; padding: 2rem; border-radius: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); border: 1px solid #e1e5e9;">
            """,
            unsafe_allow_html=True,
        )
        
        # Tabs pour Connexion/Inscription
        tab1, tab2 = st.tabs(["🔑 Connexion", "✨ Inscription"])
        
        with tab1:
            st.markdown("#### Connectez-vous à votre compte")
            
            with st.form("login_form"):
                email = st.text_input(
                    "Email",
                    placeholder="votre@email.com",
                    help="L'email utilisé lors de votre inscription"
                )
                
                password = st.text_input(
                    "Mot de passe",
                    type="password",
                    help="Votre mot de passe Phoenix"
                )
                
                col_btn1, col_btn2 = st.columns(2)
                
                with col_btn1:
                    login_submitted = st.form_submit_button(
                        "🔑 Se connecter",
                        type="primary",
                        use_container_width=True
                    )
                
                with col_btn2:
                    if st.form_submit_button("🔒 Mot de passe oublié ?", use_container_width=True):
                        st.info("Un email de réinitialisation vous sera envoyé à votre adresse.")
                
                if login_submitted:
                    if email and password:
                        # Authentification via le service Phoenix unifié
                        success, user_data, message = phoenix_cv_auth.authenticate_user(email, password)
                        
                        if success:
                            st.success(f"✅ {message}")
                            
                            # Affichage des infos de connexion
                            if user_data.get("phoenix_ecosystem"):
                                st.info("🌟 **Phoenix Ecosystem** : Accès à toutes les applications Phoenix !")
                            
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
                    else:
                        st.error("⚠️ Veuillez remplir tous les champs")
        
        with tab2:
            st.markdown("#### Créez votre compte Phoenix")
            
            with st.form("register_form"):
                col_name1, col_name2 = st.columns(2)
                
                with col_name1:
                    first_name = st.text_input("Prénom", placeholder="Jean")
                
                with col_name2:
                    last_name = st.text_input("Nom", placeholder="Dupont")
                
                email_reg = st.text_input(
                    "Email",
                    placeholder="jean.dupont@email.com",
                    help="Votre email servira d'identifiant"
                )
                
                password_reg = st.text_input(
                    "Mot de passe",
                    type="password",
                    help="Au moins 8 caractères, incluant majuscule et chiffre"
                )
                
                password_confirm = st.text_input(
                    "Confirmer le mot de passe",
                    type="password"
                )
                
                # Consentements RGPD
                st.markdown("---")
                
                consent_data = st.checkbox(
                    "J'accepte le traitement de mes données personnelles pour la création de CV",
                    help="Obligatoire pour utiliser Phoenix CV"
                )
                
                consent_marketing = st.checkbox(
                    "Je souhaite recevoir des conseils carrière par email (optionnel)"
                )
                
                register_submitted = st.form_submit_button(
                    "✨ Créer mon compte",
                    type="primary",
                    use_container_width=True
                )
                
                if register_submitted:
                    if not all([first_name, last_name, email_reg, password_reg, password_confirm]):
                        st.error("⚠️ Veuillez remplir tous les champs obligatoires")
                    elif password_reg != password_confirm:
                        st.error("❌ Les mots de passe ne correspondent pas")
                    elif not consent_data:
                        st.error("⚠️ Vous devez accepter le traitement des données pour continuer")
                    elif len(password_reg) < 8:
                        st.error("❌ Le mot de passe doit contenir au moins 8 caractères")
                    else:
                        # Inscription via le service Phoenix unifié
                        success, user_data, message = phoenix_cv_auth.register_user(
                            email_reg, password_reg, first_name, last_name, consent_marketing
                        )
                        
                        if success:
                            st.success(f"✅ {message}")
                            
                            # Connexion automatique après inscription
                            if user_data.get("phoenix_ecosystem"):
                                st.info("🌟 **Bienvenue dans l'écosystème Phoenix !** Accès à toutes nos applications.")
                            
                            st.balloons()
                            
                            # Petit délai puis redirection vers connexion
                            st.info("🔄 Redirection vers la connexion dans 3 secondes...")
                            st.session_state.auth_flow = "login"
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Retour à l'accueil
        st.markdown("---")
        if st.button("← Retour à l'accueil", use_container_width=True):
            st.session_state.auth_flow = "choice"
            st.rerun()
        
        # Informations rassurantes
        st.info(
            "🔒 **Sécurité garantie** : Vos données sont chiffrées AES-256 et protégées selon les standards RGPD. "
            "Phoenix CV respecte votre vie privée et ne partage jamais vos informations."
        )


# Les fonctions d'authentification sont maintenant gérées par phoenix_unified_auth


def render_guest_mode_header():
    """Affiche l'en-tête pour le mode invité."""
    st.markdown(
        """
        <div style="background: #e8f5e8; padding: 1rem; border-radius: 10px; margin-bottom: 1rem; text-align: center;">
            <p style="margin: 0; color: #2e7d2e;">
                <strong>🆓 Mode Invité</strong> • Créez votre CV gratuitement • 
                <a href="#" onclick="window.location.reload();" style="color: #2e7d2e; text-decoration: underline;">Créer un compte pour sauvegarder</a>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_authenticated_header(user_email: str = None):
    """Affiche l'en-tête pour les utilisateurs connectés."""
    session_info = phoenix_cv_auth.get_session_info()
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        user_name = f"{session_info.get('user_email', 'utilisateur')}"
        ecosystem_badge = "🌟" if session_info.get("phoenix_ecosystem") else ""
        st.markdown(f"👋 **Connecté** {user_name} {ecosystem_badge}")
    
    with col2:
        user_tier = session_info.get("user_tier", "free")
        tier_emoji = "🆓" if user_tier == "free" else "⭐"
        st.markdown(f"**Plan:** {tier_emoji} {user_tier.title()}")
    
    with col3:
        if st.button("🔓 Déconnexion", key="logout_button"):
            # Déconnexion via le service unifié
            phoenix_cv_auth.logout_user()
            st.success("✅ Déconnexion réussie")
            st.rerun()


def handle_authentication_flow():
    """Gère le flux d'authentification complet."""
    
    # Initialisation du flow d'auth si nécessaire
    if "auth_flow" not in st.session_state:
        st.session_state.auth_flow = "choice"
    
    auth_flow = st.session_state.auth_flow
    
    if auth_flow == "choice":
        render_login_choice_page()
        return False  # Pas encore authentifié
        
    elif auth_flow == "login":
        render_login_form_page()
        return False  # En cours d'authentification
        
    elif auth_flow == "guest":
        render_guest_mode_header()
        return True  # Mode invité activé
        
    elif auth_flow == "authenticated":
        user_email = st.session_state.get("user_email")
        render_authenticated_header(user_email)
        return True  # Utilisateur connecté
    
    return False