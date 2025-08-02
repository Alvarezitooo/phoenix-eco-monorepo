"""
🔥 Phoenix Letters - Premium Barriers Component
Système de barrières élégant pour fonctionnalités Premium avec Stripe

Author: Claude Phoenix DevSecOps Guardian
Version: 2.0.0 - Production Ready avec Stripe
"""

from typing import Any, Callable, Optional
from functools import wraps
from datetime import datetime
import logging

import streamlit as st
from core.entities.user import UserTier
from core.services.subscription_service import SubscriptionService

logger = logging.getLogger(__name__)


class PremiumBarrier:
    """
    Composant de barrière Premium avec intégration Stripe.
    Bloque l'accès aux fonctionnalités Premium avec UX optimisée.
    """
    
    def __init__(self, subscription_service: Optional[SubscriptionService] = None):
        self.subscription_service = subscription_service

    def require_tier(self, required_tier: UserTier, feature_name: str = "cette fonctionnalité"):
        """
        Décorateur pour protéger une fonction avec une barrière de tier.
        
        Args:
            required_tier: Tier minimum requis
            feature_name: Nom de la fonctionnalité (pour l'affichage)
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                current_user_id = st.session_state.get('user_id')
                if not current_user_id:
                    self.render_login_barrier(feature_name)
                    return None
                    
                user_subscription = self._get_user_subscription(current_user_id)
                current_tier = user_subscription.current_tier if user_subscription else UserTier.FREE
                
                if self._tier_allows_access(current_tier, required_tier):
                    return func(*args, **kwargs)
                else:
                    self.render_tier_barrier(current_tier, required_tier, feature_name)
                    return None
                    
            return wrapper
        return decorator

    @staticmethod
    def require_premium(feature_name: str, description: str = ""):
        """Décorateur legacy pour compatibilité."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                user_tier = UserTier(st.session_state.get("user_tier", "free"))

                if user_tier == UserTier.FREE:
                    PremiumBarrier.show_feature_lock_modern(feature_name, description)
                    return None

                return func(*args, **kwargs)
            return wrapper
        return decorator

    @staticmethod
    def show_feature_lock(feature_name: str, description: str = "") -> None:
        """Affiche verrou Premium pour fonctionnalité (legacy)."""
        PremiumBarrier.show_feature_lock_modern(feature_name, description)

    @staticmethod
    def show_feature_lock_modern(feature_name: str, description: str = "") -> None:
        """Affiche verrou Premium moderne avec Stripe."""
        
        # CSS moderne
        st.markdown("""
        <style>
        .premium-barrier-modern {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 20px;
            padding: 2.5rem;
            text-align: center;
            color: white;
            margin: 2rem 0;
            box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
            border: 1px solid rgba(255,255,255,0.2);
            position: relative;
            overflow: hidden;
        }
        
        .premium-barrier-modern:before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0) 70%);
            animation: shimmer 3s ease-in-out infinite;
        }
        
        @keyframes shimmer {
            0%, 100% { transform: rotate(0deg); }
            50% { transform: rotate(45deg); }
        }
        
        .premium-icon-modern {
            font-size: 4rem;
            margin-bottom: 1rem;
            filter: drop-shadow(0 0 20px rgba(255,255,255,0.5));
        }
        
        .premium-benefits-modern {
            background: rgba(255,255,255,0.15);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 1.5rem;
            margin: 1.5rem 0;
            text-align: left;
        }
        
        .premium-benefits-modern li {
            margin: 0.8rem 0;
            list-style: none;
            position: relative;
            padding-left: 2rem;
        }
        
        .premium-benefits-modern li:before {
            content: "✨";
            position: absolute;
            left: 0;
            font-size: 1.2rem;
        }
        
        .premium-price-modern {
            font-size: 2.5rem;
            font-weight: bold;
            margin: 1rem 0;
            text-shadow: 0 0 10px rgba(255,255,255,0.5);
        }
        </style>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="premium-barrier-modern">
            <div class="premium-icon-modern">⭐</div>
            <h3 style="margin-bottom: 1rem; font-size: 1.8rem; text-shadow: 0 0 10px rgba(255,255,255,0.5);">
                🔒 {feature_name} - Fonctionnalité Premium
            </h3>
            <p style="margin: 1rem 0; opacity: 0.9; font-size: 1.1rem;">{description}</p>
            
            <div class="premium-benefits-modern">
                <p style="font-weight: bold; margin-bottom: 1rem; font-size: 1.2rem;">✨ Débloquez maintenant :</p>
                <li>{feature_name} + toutes les fonctionnalités Premium</li>
                <li>50 lettres par mois (au lieu de 3)</li>
                <li>Analyses ATS avancées</li>
                <li>Mirror Match précis</li>
                <li>Smart Coach personnalisé</li>
                <li>Support prioritaire 24/7</li>
            </div>
            
            <div class="premium-price-modern">
                <span style="text-decoration: line-through; opacity: 0.6; font-size: 1.5rem;">29€</span> 
                9.99€<small style="font-size: 1rem;">/mois</small>
            </div>
            <p style="color: #ffd700; font-size: 1rem; margin: 0;">🎉 Offre de lancement limitée</p>
        </div>
        """, unsafe_allow_html=True)

        # Boutons d'action avec analytics
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button(
                f"🚀 Passer à Premium",
                use_container_width=True,
                type="primary",
                key=f"upgrade_premium_{feature_name.lower().replace(' ', '_')}",
            ):
                # Track conversion attempt
                PremiumBarrier._track_upgrade_attempt(feature_name)
                st.session_state.page = "premium"
                st.rerun()
                
            if st.button(
                "📖 En savoir plus sur Premium",
                use_container_width=True,
                type="secondary",
                key=f"learn_more_{feature_name.lower().replace(' ', '_')}",
            ):
                PremiumBarrier._show_premium_details()

    # Méthodes utilitaires pour le système moderne

    def render_login_barrier(self, feature_name: str):
        """Affiche une barrière de connexion requise."""
        st.markdown("""
        <div class="premium-barrier-modern" style="background: linear-gradient(135deg, #3742fa 0%, #2f3542 100%);">
            <div class="premium-icon-modern">🔐</div>
            <h3>Connexion requise</h3>
            <p>Connectez-vous pour accéder à <strong>{feature_name}</strong> et sauvegarder votre travail.</p>
        </div>
        """.format(feature_name=feature_name), unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔑 Se connecter", type="primary", key="login_from_barrier"):
                st.session_state.auth_flow_choice = "login"
                st.rerun()

    def render_tier_barrier(self, current_tier: UserTier, required_tier: UserTier, feature_name: str):
        """Affiche une barrière élégante pour upgrade de tier."""
        if required_tier == UserTier.PREMIUM:
            icon = "⭐"
            tier_name = "Premium"
            benefits = [
                "50 lettres par mois",
                "Analyses ATS avancées", 
                "Mirror Match précis",
                "Smart Coach personnalisé",
                "Templates exclusifs"
            ]
        else:  # PREMIUM_PLUS
            icon = "💎"
            tier_name = "Premium Plus"
            benefits = [
                "Lettres illimitées",
                "Trajectory Builder complet",
                "Analyses sectorielles",
                "API access",
                "Support VIP 24/7"
            ]
        
        st.markdown(f"""
        <div class="premium-barrier-modern">
            <div class="premium-icon-modern">{icon}</div>
            <h3>Fonctionnalité {tier_name} Requise</h3>
            <p><strong>{feature_name}</strong> nécessite un abonnement {tier_name}.</p>
            <div class="premium-benefits-modern">
                <p><strong>Avec {tier_name}, débloquez :</strong></p>
                {''.join([f'<li>{benefit}</li>' for benefit in benefits])}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button(f"🚀 Upgrader vers {tier_name}", type="primary", key=f"upgrade_{required_tier.value}"):
                st.session_state.page = "premium"
                st.rerun()

    def _get_user_subscription(self, user_id: str):
        """Récupère l'abonnement utilisateur avec cache."""
        if self.subscription_service:
            try:
                return self.subscription_service.get_user_subscription(user_id)
            except Exception as e:
                logger.error(f"Erreur récupération abonnement: {e}")
        return None

    def _tier_allows_access(self, current_tier: UserTier, required_tier: UserTier) -> bool:
        """Vérifie si le tier actuel permet l'accès."""
        tier_hierarchy = {
            UserTier.FREE: 0,
            UserTier.PREMIUM: 1,
            UserTier.PREMIUM_PLUS: 2
        }
        return tier_hierarchy.get(current_tier, 0) >= tier_hierarchy.get(required_tier, 0)

    @staticmethod
    def _track_upgrade_attempt(feature_name: str):
        """Track les tentatives d'upgrade pour analytics."""
        try:
            user_id = st.session_state.get('user_id', 'anonymous')
            # TODO: Intégrer avec service analytics
            logger.info(f"Upgrade attempt tracked: user={user_id}, feature={feature_name}")
        except Exception as e:
            logger.error(f"Erreur tracking upgrade: {e}")

    @staticmethod
    def _show_premium_details():
        """Affiche les détails Premium dans un expander."""
        with st.expander("📋 Détails Premium Phoenix Letters", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                **⭐ Premium (9.99€/mois)**
                - 50 lettres par mois
                - Analyses ATS avancées
                - Mirror Match précis
                - Smart Coach personnalisé
                - Templates exclusifs
                - Export PDF premium
                """)
                
            with col2:
                st.markdown("""
                - Lettres ILLIMITÉES
                - Trajectory Builder complet
                - Analyses sectorielles
                - API access
                - Coaching personnalisé
                - Support VIP 24/7
                """)


class SmartUpgradePrompts:
    """Prompts intelligents pour upgrade Premium."""

    @staticmethod
    def show_usage_milestone(letters_count: int) -> None:
        """Affiche prompt basé sur utilisation."""

        if letters_count == 1:
            st.info(
                """
            🎯 **Première lettre réussie !** Avec Premium, elle aurait été optimisée avec :
            • **Mirror Match** - Analyse culture entreprise  
            • **ATS Analyzer** - Passage filtres automatiques garantis
            """
            )

        elif letters_count == 2:
            st.warning(
                """
            ⚠️ **Dernière lettre gratuite !** Pour continuer votre reconversion :
            • **Lettres illimitées** dès maintenant
            • **Tous les outils Premium** pour maximiser vos chances
            """
            )

            if st.button("🚀 Continuer en illimité", key="milestone_upgrade"):
                st.switch_page("Offres Premium")

    @staticmethod
    def show_competitive_advantage() -> None:
        """Montre avantage concurrentiel Premium."""

        with st.expander("💡 Pourquoi Phoenix Letters Premium ?"):
            col1, col2 = st.columns(2)

            with col1:
                st.markdown(
                    """
                **🆚 Autres solutions :**
                • Generic - Pas spécialisé reconversion
                • Cher - 50€+ pour moins de fonctionnalités  
                • Complexe - Interface difficile
                • Limité - Peu d'outils IA
                """
                )

            with col2:
                st.markdown(
                    """
                **✅ Phoenix Letters Premium :**
                • **Spécialisé reconversion** 100%
                • **19€/mois** - Prix imbattable
                • **Interface intuitive** Streamlit
                • **4 outils IA avancés** inclus
                """
                )

    @staticmethod
    def show_time_sensitive_offer() -> None:
        """Affiche offre limitée dans le temps."""

        import datetime

        end_date = datetime.date.today() + datetime.timedelta(days=7)

        st.markdown(
            f"""
        <div style="background: linear-gradient(45deg, #ff6b35, #ffd700); 
                    color: white; padding: 1rem; border-radius: 10px; text-align: center;">
            <h4>⏰ OFFRE LIMITÉE - Se termine le {end_date.strftime('%d/%m')}</h4>
            <p>-33% sur Phoenix Letters Premium</p>
            <p><strong>Seulement 19€/mois au lieu de 29€</strong></p>
        </div>
        """,
            unsafe_allow_html=True,
        )


class ConversionOptimizer:
    """Optimiseur de conversion avec A/B testing."""

    @staticmethod
    def get_cta_variant() -> dict:
        """Retourne variant CTA pour A/B test."""
        import random

        variants = [
            {"text": "🚀 Passer Premium", "color": "primary", "style": "standard"},
            {"text": "✨ Débloquer Maintenant", "color": "primary", "style": "urgent"},
            {"text": "🎯 Commencer Premium", "color": "primary", "style": "action"},
        ]

        # Sélection basée sur user_id pour cohérence
        user_id = st.session_state.get("user_id", "default")
        variant_index = hash(user_id) % len(variants)

        return variants[variant_index]

    @staticmethod
    def track_cta_performance(variant: dict, clicked: bool) -> None:
        """Track performance CTA pour optimisation."""
        try:
            from core.services.analytics_service import AnalyticsService

            analytics = AnalyticsService()
            user_id = st.session_state.get("user_id", "anonymous")

            analytics.track_event(
                event_name="cta_ab_test",
                user_id=user_id,
                user_tier=st.session_state.get("user_tier", "free"),
                properties={
                    "variant_text": variant["text"],
                    "variant_style": variant["style"],
                    "clicked": clicked,
                },
            )
        except Exception:
            pass  # Fail silently pour ne pas casser l'UX
