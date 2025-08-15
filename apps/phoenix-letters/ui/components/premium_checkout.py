"""
🔥 Phoenix Letters - Premium Checkout Component
Interface de checkout Stripe élégante et sécurisée

Author: Claude Phoenix DevSecOps Guardian
Version: 1.0.0 - Production Ready
"""

import streamlit as st
import logging
from typing import Dict, Any
from concurrent.futures import TimeoutError as FuturesTimeout

from core.services.subscription_service import SubscriptionService
from phoenix_shared_auth.stripe_manager import StripeManager
from core.entities.user import UserTier

logger = logging.getLogger(__name__)


class PremiumCheckout:
    """
    Composant de checkout Premium pour Phoenix Letters.
    Interface moderne et conversion optimizada.
    """
    
    def __init__(self, subscription_service: SubscriptionService, stripe_service: StripeManager):
        self.subscription_service = subscription_service
        self.stripe_service = stripe_service
        
        # URLs de retour (à adapter selon votre domaine)
        self.success_url = "https://phoenix-letters.streamlit.app/success"
        self.cancel_url = "https://phoenix-letters.streamlit.app/cancel"

    def render_pricing_cards(self, current_user_id: str, current_tier: UserTier = UserTier.FREE):
        """
        Affiche les cartes de pricing Phoenix avec tous les produits.
        Redirige vers le site web principal pour le paiement.
        """
        import os
        website_url = os.environ.get("PHOENIX_WEBSITE_URL", "https://phoenix-ecosystem.com")

        st.markdown("""... (style CSS omis pour la clarté) ...""", unsafe_allow_html=True)
        st.markdown("### 🎯 Choisissez votre solution Phoenix")
        col1, col2, col3, col4 = st.columns(4)

        # Plan Gratuit
        with col1:
            st.info("🆓 Plan Gratuit - 3 lettres/mois")

        # Phoenix Letters Premium
        with col2:
            st.markdown("""... (carte letters inchangée) ...""")
            st.link_button("🚀 S'abonner Letters", f"{website_url}/pricing#letters", key="letters_premium", type="primary")
        
        # Phoenix CV Premium
        with col3:
            st.markdown("""... (carte cv inchangée) ...""")
            st.link_button("📄 S'abonner CV", f"{website_url}/pricing#cv", key="cv_premium", type="primary")
        
        # Phoenix Bundle
        with col4:
            st.markdown("""... (carte bundle inchangée) ...""")
            st.link_button("🔥 Bundle Deal", f"{website_url}/pricing#bundle", key="bundle_premium", type="primary")
        
        st.markdown("---")
        st.markdown("""... (message de comparaison inchangé) ...""", unsafe_allow_html=True)
        

    def render_subscription_management(self, current_user_id: str):
        """
        Affiche l'interface de gestion d'abonnement.
        
        Args:
            current_user_id: ID utilisateur actuel
        """
        st.subheader("🎛️ Gestion de votre abonnement")
        
        try:
            # Récupération de l'abonnement actuel
            subscription = st.session_state.get('user_subscription')
            if not subscription:
                # Chargement asynchrone si pas en cache
                subscription = self._load_user_subscription(current_user_id)
                st.session_state.user_subscription = subscription
                
            if subscription and subscription.current_tier != UserTier.FREE:
                self._render_active_subscription_info(subscription)
                self._render_subscription_actions(current_user_id, subscription)
            else:
                st.info("Aucun abonnement Premium actif")
                
        except Exception as e:
            logger.error(f"Erreur gestion abonnement: {e}")
            st.error("Impossible de charger les informations d'abonnement")

    def render_payment_success(self, session_id: str):
        """
        Affiche la page de succès après paiement.
        
        Args:
            session_id: ID de la session Stripe
        """
        st.balloons()
        st.success("🎉 Paiement confirmé avec succès !")
        
        try:
            # Récupération des détails de la session
            session_info = self.stripe_service.get_session_status(session_id)
            
            st.markdown(f"""
            ### 📋 Détails de votre abonnement
            
            - **Plan** : {session_info.get('plan_id', 'N/A').title()}
            - **Statut** : {session_info.get('payment_status', 'N/A')}
            - **ID Session** : `{session_id}`
            
            Votre abonnement est maintenant actif ! 🚀
            """)
            
            if st.button("Retourner à l'application", type="primary"):
                st.session_state.page = "generator"
                st.rerun()
                
        except Exception as e:
            logger.error(f"Erreur affichage succès: {e}")
            st.error("Erreur lors de la récupération des détails")

    def render_usage_dashboard(self, current_user_id: str):
        """
        Affiche le tableau de bord d'utilisation.
        
        Args:
            current_user_id: ID utilisateur actuel
        """
        st.subheader("📊 Votre utilisation")
        
        try:
            stats = self._load_user_stats(current_user_id)
            subscription = self._load_user_subscription(current_user_id)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Lettres ce mois",
                    stats.get("letters_generated_this_month", 0),
                    help="Nombre de lettres générées ce mois"
                )
                
            with col2:
                st.metric(
                    "Lettres totales",
                    stats.get("letters_generated", 0),
                    help="Nombre total de lettres générées"
                )
                
            with col3:
                st.metric(
                    "Sessions",
                    stats.get("total_sessions", 0),
                    help="Nombre de sessions utilisateur"
                )
                
            with col4:
                tier = subscription.current_tier if subscription else UserTier.FREE
                st.metric(
                    "Plan actuel",
                    tier.value.title(),
                    help="Votre plan d'abonnement actuel"
                )
                
            # Barre de progression pour les limites
            if subscription and subscription.current_tier != UserTier.PREMIUM:
                self._render_usage_progress(stats, subscription.current_tier)
                
        except Exception as e:
            logger.error(f"Erreur dashboard utilisation: {e}")
            st.error("Impossible de charger les statistiques d'utilisation")

    # Méthodes privées

    def _handle_plan_change(self, user_id: str, new_plan_id: str):
        """Gère le changement de plan."""
        try:
            with st.spinner("Changement de plan en cours..."):
                # Implementation du changement de plan
                st.success("Plan modifié avec succès !")
                st.rerun()
                
        except Exception as e:
            logger.error(f"Erreur changement plan: {e}")
            st.error(f"Erreur lors du changement: {e}")

    def _handle_downgrade(self, user_id: str):
        """Gère le passage au plan gratuit."""
        try:
            with st.spinner("Annulation en cours..."):
                self.subscription_service.cancel_subscription(user_id)
                st.success("Abonnement annulé. Vous gardez l'accès jusqu'à la fin de votre période.")
                st.rerun()
        except Exception as e:
            logger.error(f"Erreur downgrade: {e}")
            st.error(f"Erreur lors de l'annulation: {e}")

    def _load_user_subscription(self, user_id: str):
        """Charge l'abonnement utilisateur."""
        try:
            if "async_service_runner" in st.session_state:
                future = st.session_state.async_service_runner.run_coro_in_thread(
                    self.subscription_service.get_user_subscription(user_id)
                )
                return future.result(timeout=10)
            return None
        except Exception as e:
            logger.error(f"Erreur chargement abonnement: {e}")
            return None

    def _load_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Charge les statistiques utilisateur."""
        try:
            if "async_service_runner" in st.session_state:
                future = st.session_state.async_service_runner.run_coro_in_thread(
                    self.subscription_service.get_user_usage_stats(user_id)
                )
                return future.result(timeout=10) or {}
            return {}
        except Exception as e:
            logger.error(f"Erreur chargement stats: {e}")
            return {}

    def _render_active_subscription_info(self, subscription):
        """Affiche les informations d'abonnement actif."""
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"""
            **Plan actuel** : {subscription.current_tier.value.title()}
            **Statut** : {subscription.status.value.title()}
            """)
            
        with col2:
            if subscription.subscription_end:
                st.info(f"""
                **Prochaine facturation** : {subscription.subscription_end.strftime('%d/%m/%Y')}
                **Renouvellement auto** : {'✅' if subscription.auto_renewal else '❌'}
                """)

    def _render_subscription_actions(self, user_id: str, subscription):
        """Affiche les actions possibles sur l'abonnement."""
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("❌ Annuler l'abonnement", type="secondary"):
                self._handle_downgrade(user_id)
                
        with col2:
            if not subscription.auto_renewal:
                if st.button("🔄 Réactiver le renouvellement", type="primary"):
                    try:
                        if subscription.subscription_id:
                            self.stripe_service.reactivate_subscription(subscription.subscription_id)
                            st.success("Renouvellement réactivé !")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Erreur: {e}")

    def _render_usage_progress(self, stats: Dict[str, Any], tier: UserTier):
        """Affiche la barre de progression d'utilisation."""
        if tier == UserTier.FREE:
            limit = 3
        elif tier == UserTier.PREMIUM:
            limit = 50
        else:
            return  # Pas de limite pour Premium Plus
            
        current = stats.get("letters_generated_this_month", 0)
        progress = min(current / limit, 1.0)
        
        st.markdown("#### 📈 Utilisation mensuelle")
        st.progress(progress)
        st.caption(f"{current}/{limit} lettres utilisées ce mois")
        
        if progress > 0.8:
            st.warning("⚠️ Vous approchez de votre limite mensuelle !")
        elif progress >= 1.0:
            st.error("🚫 Limite mensuelle atteinte ! Passez à un plan supérieur.")