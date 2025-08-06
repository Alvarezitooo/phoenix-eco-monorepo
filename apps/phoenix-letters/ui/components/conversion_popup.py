"""Composant popup de conversion Free → Premium."""

from typing import Optional

import streamlit as st


class ConversionPopup:
    """Popup optimisé pour conversion Premium."""

    def __init__(self):
        self.session_key_shown = "conversion_popup_shown"

    def show_limit_reached_popup(self) -> bool:
        """
        Affiche message bienveillant quand limite Free atteinte.
        Returns: True si CTA cliqué, False sinon
        """

        # Éviter spam - montrer max 1 fois par session
        if st.session_state.get(self.session_key_shown, False):
            return False

        # Message bienveillant non-bloquant
        st.success("🎉 **Félicitations !** Vous avez découvert le potentiel de Phoenix Letters")
        
        st.markdown(
            """
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        padding: 2rem; border-radius: 15px; color: white; text-align: center; margin: 1rem 0;">
                <h3 style="margin: 0 0 1rem 0;">✨ Continuez votre réussite avec Premium</h3>
                <p style="font-size: 1.1rem; opacity: 0.9; margin-bottom: 1.5rem;">
                    Vous avez utilisé vos <strong>2 lettres d'essai</strong> ce mois. 
                    C'est le moment parfait pour débloquer tout le potentiel !
                </p>
                <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px;">
                    <div style="margin-bottom: 0.5rem;">🚀 <strong>Lettres illimitées</strong></div>
                    <div style="margin-bottom: 0.5rem;">🎯 <strong>Analyses avancées</strong></div>
                    <div style="margin-bottom: 0.5rem;">🧠 <strong>Coach IA personnalisé</strong></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            # CTA principal bienveillant
            if st.button(
                "✨ Découvrir Premium (9,99€/mois)",
                use_container_width=True,
                type="primary",
                key="popup_cta_premium",
            ):
                st.session_state[self.session_key_shown] = True
                self._track_event("popup_conversion_clicked")
                return True

            # Option alternative respectueuse
            if st.button(
                "📅 Me rappeler le mois prochain",
                use_container_width=True,
                key="popup_remind_later",
            ):
                st.session_state[self.session_key_shown] = True
                self._track_event("popup_remind_later")
                st.info("💙 Parfait ! Nous respectons votre rythme. À bientôt sur Phoenix Letters !")
                return False

        return False

    def show_feature_locked_popup(self, feature_name: str) -> bool:
        """
        Information transparente quand utilisateur Free découvre fonctionnalité Premium.

        Args:
            feature_name: Nom de la fonctionnalité (ex: "Mirror Match")
        Returns: True si conversion déclenchée
        """

        st.info(f"✨ **{feature_name}** fait partie de l'offre Premium")

        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown(
                f"""
            ### 🎯 Avec {feature_name} Premium:
            - Analyses IA approfondies
            - Personnalisation avancée  
            - Résultats détaillés
            - Support prioritaire
            """
            )

        with col2:
            st.markdown(
                """
            ### 💰 Tarif Transparent
            <div style="text-align: center; padding: 1rem; background: #f8f9fa; border-radius: 10px;">
                <div style="color: #28a745; font-size: 2rem; font-weight: bold;">9,99€/mois</div>
                <div style="color: #6c757d; margin-top: 0.5rem;">Phoenix Letters Premium</div>
                <div style="color: #6c757d; font-size: 0.9rem;">Sans engagement</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        if st.button(
            f"🚀 Débloquer {feature_name} + Toutes les fonctionnalités",
            use_container_width=True,
            type="primary",
            key=f"unlock_{feature_name.lower().replace(' ', '_')}",
        ):
            self._track_event("feature_unlock_clicked", {"feature": feature_name})
            st.balloons()
            st.success("🎉 Redirection vers Premium...")
            return True

        return False

    def show_success_upsell(self, letter_count: int) -> bool:
        """
        Upsell subtil après génération réussie.

        Args:
            letter_count: Nombre de lettres générées par l'utilisateur
        Returns: True si intérêt Premium exprimé
        """

        if letter_count == 1:  # Première lettre
            st.success("🎉 **Première lettre générée avec succès !**")

            with st.expander("💡 Conseil Pro - Maximisez vos chances"):
                st.markdown(
                    """
                **Votre lettre est bonne, mais elle pourrait être PARFAITE !**
                
                Avec **Premium**, cette même lettre aurait bénéficié de :
                - 🎯 **Mirror Match** : Adaptation parfaite à la culture d'entreprise
                - 🤖 **ATS Analyzer** : Optimisation pour les filtres automatiques  
                - 🧠 **Smart Coach** : Feedback détaillé pour amélioration
                
                **Résultat** : +89% de taux de réponse vs lettres standard
                """
                )

                if st.button("🚀 Voir Premium (9,99€/mois)", key="success_upsell_1"):
                    self._track_event(
                        "success_upsell_clicked", {"letter_count": letter_count}
                    )
                    return True

        elif letter_count == 2:  # Dernière lettre gratuite
            st.warning("⚠️ **Dernière lettre gratuite utilisée !**")

            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown(
                    """
                🎯 **Vous maîtrisez Phoenix Letters !** 
                
                Pour continuer votre reconversion avec succès :
                - **Lettres illimitées** pour postuler sans limite
                - **Outils Premium** pour maximiser vos chances
                - **Support 24/7** pour vous accompagner
                """
                )

            with col2:
                if st.button(
                    "🚀 Continuer en Premium", type="primary", key="success_upsell_2"
                ):
                    self._track_event(
                        "success_upsell_clicked", {"letter_count": letter_count}
                    )
                    return True

        return False

    def _track_event(self, event: str, properties: Optional[dict] = None):
        """Track conversion events."""
        try:
            from core.services.analytics_service import AnalyticsService
            import logging

            analytics = AnalyticsService()
            user_id = st.session_state.get("user_id", "anonymous")
            user_tier = st.session_state.get("user_tier", "free")

            analytics.track_conversion_funnel(
                step=event,
                user_id=user_id,
                user_tier=user_tier,
                source="popup",
                properties=properties,
            )
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.warning(f"Analytics tracking failed: {e}")
