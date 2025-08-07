"""
🤖 PHOENIX CV - PAGE IRIS
Page dédiée à l'agent Iris pour Phoenix CV.
Interface complète d'accompagnement CV et carrière.
"""

import streamlit as st
from phoenix_cv.ui.iris_integration import (
    render_cv_iris_chat,
    render_ats_iris_assistant, 
    render_template_iris_assistant,
    render_career_iris_chat
)

def render_iris_page():
    """Page principale d'Iris pour Phoenix CV"""
    
    st.title("🤖 Iris CV - Votre Expert Carrière IA")
    
    # Vérification de l'authentification
    if not st.session_state.get('authenticated_user'):
        st.warning("🔒 Connectez-vous pour accéder à Iris CV")
        st.info("Iris CV vous accompagne dans l'optimisation de votre CV et votre stratégie carrière.")
        
        with st.expander("💡 Découvrez les capacités d'Iris CV"):
            st.markdown("""
            **🎯 Optimisation CV & ATS**
            - Analyse de votre CV et suggestions d'amélioration
            - Optimisation pour les systèmes ATS (Applicant Tracking Systems)
            - Adaptation aux mots-clés des offres d'emploi
            
            **🎨 Conseils Templates & Design**
            - Recommandations de templates selon votre profil
            - Conseils de mise en forme et structure
            - Adaptation au secteur d'activité cible
            
            **🚀 Stratégie Carrière**
            - Planification de trajectoire professionnelle
            - Conseils pour la reconversion
            - Analyse des compétences à développer
            
            **📊 Analyse Personnalisée**
            - Évaluation de vos forces et points d'amélioration
            - Suggestions de formations complémentaires
            - Conseils sectoriels spécialisés
            """)
        return
    
    # Tabs pour organiser les différents assistants
    tab1, tab2, tab3, tab4 = st.tabs([
        "💬 Chat Général", 
        "🎯 Optimisation ATS", 
        "🎨 Templates & Design", 
        "🚀 Trajectoire Carrière"
    ])
    
    with tab1:
        st.markdown("### 💬 Assistance Générale CV")
        st.info("Posez toutes vos questions sur l'optimisation CV, la recherche d'emploi et votre carrière.")
        
        # Récupération des données CV si disponibles
        cv_data = st.session_state.get('current_cv_data')
        template_type = st.session_state.get('selected_template')
        
        render_cv_iris_chat(cv_data=cv_data, template_type=template_type)
    
    with tab2:
        st.markdown("### 🎯 Optimisation ATS")
        st.info("Optimisez votre CV pour les systèmes de tri automatique des candidatures.")
        
        # Section pour coller une offre d'emploi
        with st.expander("📋 Analysez une offre d'emploi"):
            job_offer_text = st.text_area(
                "Collez ici le texte de l'offre d'emploi :",
                height=150,
                placeholder="Copiez-collez l'annonce d'emploi pour une analyse personnalisée..."
            )
            
            if job_offer_text:
                job_offer = {
                    'title': 'Offre analysée',
                    'description': job_offer_text,
                    'requirements': job_offer_text
                }
                st.success("✅ Offre d'emploi prise en compte pour l'analyse")
            else:
                job_offer = None
        
        render_ats_iris_assistant(job_offer=job_offer)
    
    with tab3:
        st.markdown("### 🎨 Templates & Design")
        st.info("Choisissez le template parfait et optimisez la présentation de votre CV.")
        
        # Simulation des templates disponibles
        available_templates = [
            "Moderne", "Classique", "Créatif", "Minimaliste", 
            "Professionnel", "Tech", "Commercial", "International"
        ]
        
        selected_template = st.selectbox(
            "Template actuellement sélectionné :",
            ["Aucun"] + available_templates,
            index=0
        )
        
        if selected_template != "Aucun":
            st.success(f"🎨 Template {selected_template} sélectionné")
            templates_context = available_templates
        else:
            templates_context = available_templates
        
        render_template_iris_assistant(templates=templates_context)
    
    with tab4:
        st.markdown("### 🚀 Trajectoire Carrière")
        st.info("Planifiez votre évolution professionnelle et votre reconversion.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            current_role = st.text_input(
                "Votre poste actuel :",
                placeholder="Ex: Comptable, Développeur, Commercial..."
            )
        
        with col2:
            target_role = st.text_input(
                "Poste visé :",
                placeholder="Ex: Data Analyst, Chef de projet, Consultant..."
            )
        
        if current_role or target_role:
            if current_role and target_role:
                st.success(f"🎯 Transition planifiée : {current_role} → {target_role}")
            elif current_role:
                st.info(f"📍 Poste actuel : {current_role}")
            elif target_role:
                st.info(f"🎯 Objectif : {target_role}")
        
        render_career_iris_chat(current=current_role, target=target_role)
    
    # Section conseils rapides
    st.markdown("---")
    st.markdown("### 💡 Conseils Rapides")
    
    tips_cols = st.columns(3)
    
    with tips_cols[0]:
        if st.button("🔍 Analyse express de mon CV"):
            st.session_state['iris_quick_question'] = "Peux-tu analyser rapidement mon CV et me donner 3 conseils d'amélioration prioritaires ?"
            st.rerun()
    
    with tips_cols[1]:
        if st.button("📈 Mots-clés tendance 2025"):
            st.session_state['iris_quick_question'] = "Quels sont les mots-clés et compétences les plus recherchés en 2025 pour mon secteur ?"
            st.rerun()
    
    with tips_cols[2]:
        if st.button("🎯 Optimisation ATS rapide"):
            st.session_state['iris_quick_question'] = "Comment optimiser rapidement mon CV pour passer les filtres ATS ?"
            st.rerun()
    
    # Métriques d'utilisation d'Iris (si disponibles)
    with st.sidebar:
        st.markdown("### 📊 Utilisation Iris CV")
        
        user_tier = st.session_state.get('user_tier', 'FREE')
        if user_tier == 'FREE':
            messages_used = st.session_state.get('iris_messages_today', 0)
            st.metric("Messages aujourd'hui", f"{messages_used}/5")
            
            if messages_used >= 4:
                st.warning("⚠️ Bientôt à la limite quotidienne")
            
            st.markdown("[🚀 Passer à PREMIUM](/pricing)")
        else:
            st.success("💎 Accès illimité à Iris")