"""
🔥 Phoenix Letters - Premium Page avec Stripe
Page Premium intégrée avec système de paiement Stripe

Author: Claude Phoenix DevSecOps Guardian
Version: 2.0.0 - Production Ready avec Stripe
"""

from typing import Optional
import streamlit as st
import logging

from core.entities.user import UserTier
from core.services.subscription_service import SubscriptionService
from infrastructure.payment.stripe_service import StripeService
from ui.components.premium_checkout import PremiumCheckout

logger = logging.getLogger(__name__)


class PremiumPage:
    def __init__(
        self, 
        stripe_service: Optional[StripeService] = None,
        subscription_service: Optional[SubscriptionService] = None
    ):
        self.stripe_service = stripe_service
        self.subscription_service = subscription_service
        self.premium_checkout = PremiumCheckout(subscription_service, stripe_service) if all([stripe_service, subscription_service]) else None

    def render(self):
        """Affiche la page Premium avec intégration Stripe."""
        
        # Vérification des services requis
        if not self.premium_checkout:
            st.warning("⚠️ Services de paiement en cours de configuration")
            st.info("💡 **Mode développement actuel** - Les paiements nécessitent la configuration des clés Stripe.")
            
            # Afficher quand même le contenu Premium pour le développement
            st.markdown("---")
            st.info("📋 **Aperçu des fonctionnalités Premium** (interface de développement)")
            
            # Continuer à afficher le reste de l'interface pour les tests
            
        # Gestion des paramètres URL (success/cancel) seulement si services disponibles
        query_params = st.query_params
        
        if self.premium_checkout:
            if "session_id" in query_params:
                self.premium_checkout.render_payment_success(query_params["session_id"])
                return
            elif query_params.get("status") == "cancel":
                st.warning("💔 Paiement annulé - Aucun souci !")
                st.info("Vous pouvez reprendre votre abonnement à tout moment.")

        # Header avec proposition de valeur forte
        st.markdown("""
        <div style="text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 2rem; border-radius: 15px; margin-bottom: 2rem; color: white;">
            <h1 style="margin: 0; font-size: 2.5rem;">🚀 Phoenix Letters Premium</h1>
            <h3 style="margin: 0.5rem 0; opacity: 0.9;">Débloquez votre potentiel de reconversion</h3>
            <p style="font-size: 1.2rem; margin: 0;">Première application française IA spécialisée reconversion</p>
        </div>
        """, unsafe_allow_html=True)

        # Récupération du contexte utilisateur
        current_user_id = st.session_state.get('user_id')
        current_tier = UserTier(st.session_state.get('user_tier', 'free'))
        
        # Bénéfices proposés (en développement)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("✨ Fonctionnalités", "5+", "outils IA avancés")
        with col2:
            st.metric("⚡ Génération", "illimitée", "sans restrictions")
        with col3:
            st.metric("🎯 Application", "nouveau", "en cours de développement")

        st.markdown("---")

        # Interface contextuelle selon l'utilisateur
        if current_user_id and current_tier != UserTier.FREE:
            # Utilisateur Premium : gestion d'abonnement
            st.subheader("🎛️ Gestion de votre abonnement Premium")
            if self.premium_checkout:
                self.premium_checkout.render_subscription_management(current_user_id)
            else:
                st.info("Fonctionnalité de gestion disponible avec les services de paiement configurés.")
            
            st.markdown("---")
            
            # Dashboard d'utilisation
            if self.premium_checkout:
                self.premium_checkout.render_usage_dashboard(current_user_id)
            else:
                self._render_mock_usage_dashboard()
            
        else:
            # Utilisateur gratuit : pricing et checkout
            st.subheader("🎯 Choisissez votre plan")
            
            # Affichage des cartes de pricing
            if self.premium_checkout:
                self.premium_checkout.render_pricing_cards(current_user_id or "guest", current_tier)
            else:
                self._render_mock_pricing_cards()

        st.markdown("---")

        # Témoignages utilisateurs
        self._render_testimonials()

        # Garanties et sécurité
        self._render_guarantees()

        # FAQ rapide
        self._render_faq()

    def _render_testimonials(self):
        """Affiche la vision du produit."""
        st.subheader("🎯 Phoenix Letters Premium - Notre Vision")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            ### 🚀 Innovation IA pour la Reconversion
            
            Phoenix Letters est la **première application française** spécialisée 
            dans la génération de lettres de motivation pour les reconversions professionnelles.
            
            Nous utilisons l'IA Gemini pour créer des lettres ultra-personnalisées 
            qui transforment votre expérience passée en atout pour votre nouvelle carrière.
            """)

        with col2:
            st.markdown("""
            ### 🛠️ Fonctionnalités en Développement
            
            - **Mirror Match** : Adaptation automatique du ton selon l'entreprise
            - **ATS Analyzer** : Optimisation pour les systèmes de recrutement
            - **Smart Coach** : Conseils personnalisés en temps réel
            - **Trajectory Builder** : Planification de parcours professionnel
            
            *Application en phase de développement et d'amélioration continue.*
            """)

    def _render_guarantees(self):
        """Affiche les garanties et sécurité."""
        st.markdown("""
        <div style="text-align: center; margin-top: 2rem; padding: 1rem; background: #f8f9fa; border-radius: 10px;">
            <p><strong>🛡️ Engagement Qualité</strong></p>
            <p>✅ Annulation à tout moment | 🔒 Paiement sécurisé Stripe | 📱 Aucun engagement</p>
            <p><em>Application française spécialisée reconversion professionnelle</em></p>
        </div>
        """, unsafe_allow_html=True)

    def _render_faq(self):
        """Affiche la FAQ."""
        with st.expander("❓ Questions fréquentes"):
            st.markdown("""
            **Q: Puis-je annuler à tout moment ?**  
            R: Oui, annulation en 1 clic depuis votre profil. Aucun engagement.
            
            **Q: Que se passe-t-il si je ne suis pas satisfait ?**  
            R: Vous pouvez annuler à tout moment. Remboursement au cas par cas selon les conditions d'utilisation.
            
            **Q: Mes données sont-elles sécurisées ?**  
            R: 100% RGPD compliant. Données chiffrées et supprimées à la demande.
            
            **Q: Support technique inclus ?**  
            R: Oui, support prioritaire 24/7 par email et chat.
            
            **Q: Comment fonctionne le paiement ?**  
            R: Paiement sécurisé via Stripe. Cartes VISA, Mastercard, American Express acceptées.
            """)

    def _render_mock_pricing_cards(self):
        """Affiche les cartes de pricing en mode développement."""
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div style="border: 2px solid #ddd; border-radius: 10px; padding: 2rem; text-align: center;">
                <h3>✨ Premium Mensuel</h3>
                <h2 style="color: #667eea;">14,90€<small>/mois</small></h2>
                <ul style="text-align: left; list-style: none; padding: 0;">
                    <li>✅ Lettres illimitées</li>
                    <li>✅ Mirror Match AI</li>
                    <li>✅ ATS Optimizer</li>
                    <li>✅ Smart Coach</li>
                    <li>✅ Support prioritaire</li>
                </ul>
                <button style="background: #667eea; color: white; border: none; padding: 1rem 2rem; border-radius: 8px; cursor: pointer;">
                    Configuration paiement requise
                </button>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="border: 2px solid #764ba2; border-radius: 10px; padding: 2rem; text-align: center;">
                <h3>🌟 Premium Annuel</h3>
                <h2 style="color: #764ba2;">149,90€<small>/an</small></h2>
                <p style="color: green;"><strong>Économisez 33% !</strong></p>
                <ul style="text-align: left; list-style: none; padding: 0;">
                    <li>✅ Tout Premium Mensuel</li>
                    <li>✅ Trajectory Builder</li>
                    <li>✅ Analyse de marché</li>
                    <li>✅ Sessions coaching 1-on-1</li>
                    <li>✅ Accès bêta nouvelles features</li>
                </ul>
                <button style="background: #764ba2; color: white; border: none; padding: 1rem 2rem; border-radius: 8px; cursor: pointer;">
                    Configuration paiement requise
                </button>
            </div>
            """, unsafe_allow_html=True)

    def _render_mock_usage_dashboard(self):
        """Affiche un dashboard d'utilisation en mode développement."""
        st.subheader("📊 Tableau de bord d'utilisation (Mode Demo)")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Lettres générées", "47", "+12 ce mois")
        with col2:
            st.metric("Score ATS moyen", "87%", "+5%")
        with col3:
            st.metric("Temps économisé", "23h", "+8h")
        
        st.info("🔧 Dashboard complet disponible avec configuration des services de paiement.")

    def _track_conversion_event(self, event_name: str, properties: Optional[dict] = None):
        """Track conversion events pour analytics."""
        try:
            user_id = st.session_state.get("user_id", "anonymous")
            logger.info(f"Conversion event: {event_name}, user: {user_id}, properties: {properties}")
        except Exception as e:
            logger.warning(f"Analytics tracking failed: {e}")
