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
from phoenix_shared_auth.stripe_manager import StripeManager
from ui.components.premium_checkout import PremiumCheckout

logger = logging.getLogger(__name__)


class PremiumPage:
    def __init__(
        self, 
        stripe_service: Optional[StripeManager] = None,
        subscription_service: Optional[SubscriptionService] = None
    ):
        self.stripe_service = stripe_service
        self.subscription_service = subscription_service
        self.premium_checkout = PremiumCheckout(subscription_service, stripe_service) if all([stripe_service, subscription_service]) else None

    def render(self):
        """Affiche la page Premium avec intégration Stripe."""
        
        # Vérification des services requis
        if not self.premium_checkout:
            st.error("⚠️ Services de paiement non disponibles temporairement")
            st.info("Veuillez réessayer plus tard ou contacter le support.")
            return
            
        # Gestion des paramètres URL (success/cancel)
        query_params = st.query_params
        
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
            <p style="font-size: 1.2rem; margin: 0;">La seule plateforme IA spécialisée reconversion professionnelle</p>
        </div>
        """, unsafe_allow_html=True)

        # Récupération du contexte utilisateur
        current_user_id = st.session_state.get('user_id')
        current_tier = UserTier(st.session_state.get('user_tier', 'free'))
        
        # Bénéfices quantifiés avec social proof
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("✨ Taux de réussite", "89%", "+23% vs lettres manuelles")
        with col2:
            st.metric("⚡ Temps économisé", "4h", "par lettre générée")
        with col3:
            st.metric("🎯 Utilisateurs actifs", "2,847", "+156 cette semaine")

        st.markdown("---")

        # Interface contextuelle selon l'utilisateur
        if current_user_id and current_tier != UserTier.FREE:
            # Utilisateur Premium : gestion d'abonnement
            st.subheader("🎛️ Gestion de votre abonnement Premium")
            self.premium_checkout.render_subscription_management(current_user_id)
            
            st.markdown("---")
            
            # Dashboard d'utilisation
            self.premium_checkout.render_usage_dashboard(current_user_id)
            
        else:
            # Utilisateur gratuit : pricing et checkout
            st.subheader("🎯 Choisissez votre plan")
            
            # Affichage des cartes de pricing
            self.premium_checkout.render_pricing_cards(current_user_id or "guest", current_tier)

        st.markdown("---")

        # Témoignages utilisateurs
        self._render_testimonials()

        # Garanties et sécurité
        self._render_guarantees()

        # FAQ rapide
        self._render_faq()

    def _render_testimonials(self):
        """Affiche les témoignages utilisateurs."""
        st.subheader("💬 Ce que disent nos utilisateurs Premium")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            > *"Grâce à Phoenix Letters Premium, j'ai décroché 3 entretiens en 2 semaines ! 
            > Le Mirror Match m'a aidé à adapter parfaitement mon ton à chaque entreprise."*
            > 
            > **Sarah M.** - Transition Marketing → Tech
            """)

        with col2:
            st.markdown("""
            > *"L'ATS Analyzer est un game-changer. Mes lettres passent maintenant 
            > tous les filtres automatiques. ROI immédiat !"*
            > 
            > **Thomas R.** - Reconversion Finance → Startup
            """)

    def _render_guarantees(self):
        """Affiche les garanties et sécurité."""
        st.markdown("""
        <div style="text-align: center; margin-top: 2rem; padding: 1rem; background: #f8f9fa; border-radius: 10px;">
            <p><strong>🛡️ Garanties Premium</strong></p>
            <p>✅ Satisfait ou remboursé 30 jours | 🔒 Paiement sécurisé Stripe | 📱 Annulation en 1 clic</p>
            <p><em>Rejoignez 2,847+ professionnels qui ont déjà transformé leur reconversion</em></p>
        </div>
        """, unsafe_allow_html=True)

    def _render_faq(self):
        """Affiche la FAQ."""
        with st.expander("❓ Questions fréquentes"):
            st.markdown("""
            **Q: Puis-je annuler à tout moment ?**  
            R: Oui, annulation en 1 clic depuis votre profil. Aucun engagement.
            
            **Q: Que se passe-t-il si je ne suis pas satisfait ?**  
            R: Garantie remboursement intégral sous 30 jours, sans questions.
            
            **Q: Mes données sont-elles sécurisées ?**  
            R: 100% RGPD compliant. Données chiffrées et supprimées à la demande.
            
            **Q: Support technique inclus ?**  
            R: Oui, support prioritaire 24/7 par email et chat.
            
            **Q: Comment fonctionne le paiement ?**  
            R: Paiement sécurisé via Stripe. Cartes VISA, Mastercard, American Express acceptées.
            """)

    def _track_conversion_event(self, event_name: str, properties: Optional[dict] = None):
        """Track conversion events pour analytics."""
        try:
            user_id = st.session_state.get("user_id", "anonymous")
            logger.info(f"Conversion event: {event_name}, user: {user_id}, properties: {properties}")
        except Exception as e:
            logger.warning(f"Analytics tracking failed: {e}")
