"""
🔬 Composant de Consentement Éthique - Recherche-Action Phoenix
Gardien de l'Éthique des Données - Privacy by Design

Author: Claude Phoenix DevSecOps Guardian
Version: 1.0.0 - Éthique First
"""

import streamlit as st
from typing import Optional
from datetime import datetime


class ResearchConsentComponent:
    """Composant de consentement éthique pour la recherche-action Phoenix"""
    
    @staticmethod
    def render_consent_banner() -> None:
        """Bannière d'information sur la recherche-action (non-intrusive)"""
        st.markdown(
            """
            <div style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 1rem;
                border-radius: 10px;
                margin-bottom: 1rem;
                text-align: center;
            ">
                <p style="margin: 0; font-size: 0.9rem;">
                    🎓 <strong>Participez à une recherche-action sur l'impact de l'IA dans la reconversion professionnelle.</strong>
                </p>
                <p style="margin: 0.5rem 0 0 0; font-size: 0.8rem; opacity: 0.9;">
                    En utilisant Phoenix, vous contribuez anonymement à une étude sur l'IA éthique et la réinvention de soi. 
                    Vos données (jamais nominatives) aideront à construire des outils plus justes et plus humains.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    @staticmethod
    def render_detailed_consent_section(current_consent: bool = False) -> Optional[bool]:
        """
        Section détaillée de consentement avec explication complète
        
        Args:
            current_consent: État actuel du consentement utilisateur
            
        Returns:
            bool: Nouvel état du consentement si modifié, None sinon
        """
        st.markdown("---")
        st.markdown("## 🔬 **Contribution à la Recherche**")
        
        # Explication détaillée
        st.markdown(
            """
            ### 🎯 **Notre Mission Recherche-Action**
            
            Phoenix ne se contente pas d'aider les utilisateurs à refaire leur CV ou lettre de motivation. 
            **Nous construisons un projet d'utilité publique** : un outil IA éthique, responsable, et utile à la société.
            
            ### 💡 **En quoi consiste la recherche ?**
            Nous étudions comment l'intelligence artificielle peut :
            - 🎯 Mieux accompagner les personnes en reconversion
            - 💪 Renforcer l'estime de soi et la clarté de parcours  
            - 🤖 Offrir des recommandations personnalisées sans biais ni jugement
            - 🌱 Favoriser un développement personnel authentique
            
            ### 🛡️ **Respect total de votre vie privée**
            - ✅ **Anonymisation complète** : Aucune donnée nominative
            - ✅ **Jamais revendues** : Vos données ne quittent jamais Phoenix
            - ✅ **Usage recherche uniquement** : Amélioration du service et publications scientifiques
            - ✅ **Révocable à tout moment** : Vous pouvez retirer votre consentement quand vous voulez
            
            ### 🚀 **Pourquoi participer ?**
            - 📚 Vous faites progresser la recherche publique sur l'IA éthique
            - 🏗️ Vous contribuez à un projet de terrain, indépendant, et engagé
            - 🌍 Vous devenez acteur d'un futur numérique plus humain
            - 🤝 Vous aidez d'autres personnes en reconversion
            """
        )
        
        # Section consentement avec style éthique
        st.markdown(
            """
            <div style="
                background: #f8f9fa;
                border: 2px solid #28a745;
                border-radius: 10px;
                padding: 1.5rem;
                margin: 1rem 0;
            ">
                <h4 style="color: #28a745; margin-top: 0;">
                    ✋ Consentement Éclairé et Révocable
                </h4>
                <p style="margin-bottom: 1rem; color: #495057;">
                    Votre participation est entièrement <strong>volontaire</strong> et 
                    <strong>révocable</strong> à tout moment. En cochant cette case, 
                    vous autorisez Phoenix à utiliser vos données (anonymisées et agrégées) 
                    pour la recherche sur les dynamiques de reconversion professionnelle.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Checkbox de consentement
        new_consent = st.checkbox(
            "🔬 Je consens à ce que mes données (anonymisées et agrégées) soient utilisées pour la recherche sur les dynamiques de la reconversion professionnelle, afin d'aider la communauté.",
            value=current_consent,
            key="research_consent_checkbox"
        )
        
        # Message de confirmation si changement
        if new_consent != current_consent:
            if new_consent:
                st.success("✅ Merci pour votre contribution à la recherche éthique ! Vos données anonymisées aideront la communauté.")
            else:
                st.info("ℹ️ Votre consentement a été retiré. Aucune de vos données ne sera utilisée pour la recherche.")
            
            return new_consent
        
        # Affichage du statut actuel
        if current_consent:
            st.success("✅ Vous contribuez actuellement à la recherche-action Phoenix. Merci !")
        else:
            st.info("ℹ️ Vous ne participez pas actuellement à la recherche (votre choix est respecté).")
        
        return None
    
    @staticmethod
    def render_compact_consent_toggle(current_consent: bool = False) -> Optional[bool]:
        """
        Version compacte pour intégration dans profiles/settings
        
        Args:
            current_consent: État actuel du consentement
            
        Returns:
            bool: Nouvel état si modifié, None sinon
        """
        
        with st.expander("🔬 Recherche-Action Phoenix", expanded=False):
            st.markdown(
                """
                **Contribuez anonymement à la recherche sur l'IA éthique en reconversion.**
                
                Vos données (anonymisées) aident à améliorer les outils pour la communauté.
                Participation volontaire et révocable à tout moment.
                """
            )
            
            new_consent = st.checkbox(
                "Participer à la recherche (données anonymisées)",
                value=current_consent,
                key="compact_research_consent"
            )
            
            if new_consent != current_consent:
                return new_consent
        
        return None


def get_research_ethics_info() -> dict:
    """Informations sur l'éthique de la recherche Phoenix"""
    return {
        "principle": "Privacy by Design",
        "methodology": "Consentement explicite + Anonymisation robuste",
        "purpose": "Recherche publique sur IA éthique en reconversion",
        "data_retention": "Anonymisées, jamais revendues, usage recherche uniquement",
        "revocable": True,
        "contact": "recherche@phoenix-creator.fr"
    }