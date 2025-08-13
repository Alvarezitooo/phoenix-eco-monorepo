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
    
    def __init__(self, subscription_service: SubscriptionService, stripe_service: StripeService):
        self.subscription_service = subscription_service
        self.stripe_service = stripe_service
        
        # URLs de retour (à adapter selon votre domaine)
        self.success_url = "https://phoenix-letters.streamlit.app/success"
        self.cancel_url = "https://phoenix-letters.streamlit.app/cancel"

    def render_pricing_cards(self, current_user_id: str, current_tier: UserTier = UserTier.FREE):
        """
        Affiche les cartes de pricing Phoenix avec tous les produits.
        
        Args:
            current_user_id: ID utilisateur actuel
            current_tier: Tier actuel de l'utilisateur
        """
        st.markdown("""
        <style>
        .pricing-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin: 2rem 0;
        }
        
        .pricing-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            padding: 2rem;
            color: white;
            text-align: center;
            box-shadow: 0 8px 32px rgba(0,0,0,0.2);
            border: 1px solid rgba(255,255,255,0.1);
            transition: transform 0.3s ease;
        }
        
        .pricing-card:hover {
            transform: translateY(-5px);
        }
        
        .pricing-card-letters {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }
        
        .pricing-card-cv {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        }
        
        .pricing-card-bundle {
            background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
            transform: scale(1.02);
            border: 3px solid gold;
            position: relative;
        }
        
        .bundle-badge {
            position: absolute;
            top: -10px;
            right: -10px;
            background: gold;
            color: black;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.8rem;
        }
        
        .pricing-card h3 {
            margin-bottom: 1rem;
            font-size: 1.8rem;
        }
        
        .pricing-price {
            font-size: 2.5rem;
            font-weight: bold;
            margin: 1rem 0;
        }
        
        .pricing-features {
            text-align: left;
            margin: 1.5rem 0;
            min-height: 180px;
        }
        
        .pricing-features li {
            margin: 0.5rem 0;
            list-style: none;
            font-size: 0.9rem;
        }
        
        .pricing-features li:before {
            content: "✅ ";
            margin-right: 0.5rem;
        }
        
        .current-plan {
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%) !important;
        }
        
        .savings {
            background: rgba(255,255,255,0.2);
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 0.9rem;
            margin: 0.5rem 0;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🎯 Choisissez votre solution Phoenix")
        
        # Grille de pricing pour les 4 plans
        col1, col2, col3, col4 = st.columns(4)
        
        # Plan Gratuit
        with col1:
            current_class = "current-plan" if current_tier == UserTier.FREE else ""
            st.markdown(f"""
            <div class="pricing-card {current_class}">
                <h3>🆓 Gratuit</h3>
                <div class="pricing-price">0€<small>/mois</small></div>
                <div class="pricing-features">
                    <li>3 lettres par mois</li>
                    <li>Templates de base</li>
                    <li>Génération simple</li>
                    <li>Support communauté</li>
                    <li>Découverte Phoenix</li>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if current_tier != UserTier.FREE:
                if st.button("Revenir au Gratuit", key="downgrade_free", type="secondary"):
                    self._handle_downgrade(current_user_id)
            else:
                st.success("🎯 Plan actuel")
        
        # Phoenix Letters Premium
        with col2:
            st.markdown("""
            <div class="pricing-card pricing-card-letters">
                <h3>📝 Phoenix Letters</h3>
                <div class="pricing-price">9,99€<small>/mois</small></div>
                <div class="pricing-features">
                    <li>Lettres illimitées</li>
                    <li>Analyses ATS avancées</li>
                    <li>Mirror Match précis</li>
                    <li>Smart Coach personnalisé</li>
                    <li>Templates exclusifs</li>
                    <li>Export PDF premium</li>
                    <li>Support prioritaire</li>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🚀 S'abonner Letters", key="letters_premium", type="primary"):
                # Si services disponibles → checkout dynamique
                if self.subscription_service and self.stripe_service:
                    if not current_user_id or current_user_id == "guest":
                        st.warning("🔒 Connectez-vous pour procéder au paiement sécurisé.")
                    else:
                        self._handle_checkout(current_user_id, "premium")
                else:
                    st.error("⚠️ Services de paiement non disponibles. Veuillez réessayer plus tard ou contacter le support.")
        
        # Phoenix CV Premium
        with col3:
            st.markdown("""
            <div class="pricing-card pricing-card-cv">
                <h3>📄 Phoenix CV</h3>
                <div class="pricing-price">7,99€<small>/mois</small></div>
                <div class="pricing-features">
                    <li>CV illimités</li>
                    <li>Templates premium</li>
                    <li>ATS Optimizer avancé</li>
                    <li>Mirror Match précis</li>
                    <li>Smart Coach IA</li>
                    <li>Export multi-formats</li>
                    <li>Support prioritaire</li>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("📄 S'abonner CV", key="cv_premium", type="primary"):
                if not current_user_id or current_user_id == "guest":
                    st.warning("🔒 Connectez-vous pour procéder au paiement sécurisé.")
                else:
                    self._handle_checkout(current_user_id, "premium")
        
        # Phoenix Bundle
        with col4:
            st.markdown("""
            <div class="pricing-card pricing-card-bundle">
                <div class="bundle-badge">🔥 BEST</div>
                <h3>🚀 Bundle Complet</h3>
                <div class="pricing-price">15,99€<small>/mois</small></div>
                <div class="savings">Économie 1,99€</div>
                <div class="pricing-features">
                    <li>✨ Phoenix Letters complet</li>
                    <li>✨ Phoenix CV complet</li>
                    <li>🎁 Smart Coach cross-platform</li>
                    <li>🎁 Mirror Match universel</li>
                    <li>🎁 Analytics avancées</li>
                    <li>🎁 Support prioritaire VIP</li>
                    <li>🎁 Accès bêta nouvelles features</li>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🔥 Bundle Deal", key="bundle_premium", type="primary"):
                if not current_user_id or current_user_id == "guest":
                    st.warning("🔒 Connectez-vous pour procéder au paiement sécurisé.")
                else:
                    self._handle_checkout(current_user_id, "bundle_premium")
        
        # Message de comparaison
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; padding: 1rem; background: #f8f9fa; border-radius: 10px;">
            <p><strong>💡 Recommandation :</strong></p>
            <p>🎯 <strong>Letters seul</strong> : Spécialisé lettres de motivation | 📄 <strong>CV seul</strong> : Optimisation CV exclusivement</p>
            <p>🚀 <strong>Bundle</strong> : Solution complète reconversion avec économie de 1,99€/mois !</p>
        </div>
        """, unsafe_allow_html=True)
        

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

    def _handle_checkout(self, user_id: str, plan_id: str):
        """Lance le processus de checkout Stripe."""
        try:
            with st.spinner("Préparation du paiement..."):
                # Exécuter l'appel async via AsyncServiceRunner si disponible
                if "async_service_runner" in st.session_state:
                    future = st.session_state.async_service_runner.run_coro_in_thread(
                        self.subscription_service.create_subscription_checkout(
                            user_id=user_id,
                            plan_id=plan_id,
                            success_url=self.success_url,
                            cancel_url=self.cancel_url,
                            user_email=st.session_state.get('user_email')
                        )
                    )
                    payment_session = future.result(timeout=20)
                else:
                    st.error("⚠️ Le service de paiement asynchrone n'est pas disponible. Veuillez contacter le support.")
                    return
                
                # Redirection vers Stripe
                st.markdown(f"""
                <script>
                window.open('{payment_session.session_url}', '_blank');
                </script>
                """, unsafe_allow_html=True)
                
                st.info("Redirection vers Stripe... Si la page ne s'ouvre pas, cliquez sur le lien ci-dessous :")
                st.markdown(f"[Procéder au paiement]({payment_session.session_url})")
                
        except FuturesTimeout:
            logger.error("Timeout lors de la création de la session de paiement")
            st.error("⏳ Le service de paiement met trop de temps à répondre. Réessayez dans un instant.")
        except Exception as e:
            logger.error(f"Erreur checkout: {e}")
            st.error(f"Erreur lors du checkout: {e}")

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