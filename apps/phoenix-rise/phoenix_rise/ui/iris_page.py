"""
🤖 PHOENIX RISE - PAGE IRIS
Page dédiée à l'agent Iris pour Phoenix Rise.
Interface complète d'accompagnement développement personnel et reconversion.
"""

import streamlit as st
from .iris_integration import (
    render_coaching_iris_chat,
    render_reconversion_iris_assistant,
    render_emotional_iris_chat,
    render_goals_iris_assistant,
    render_reflection_iris_chat
)

def render_iris_page():
    """Page principale d'Iris pour Phoenix Rise"""
    
    st.title("🤖 Iris Coach - Votre Accompagnateur Reconversion")
    
    # Vérification de l'authentification
    if not st.session_state.get('authenticated_user'):
        st.warning("🔒 Connectez-vous pour accéder à Iris Coach")
        st.info("Iris Coach vous accompagne dans votre développement personnel et votre reconversion professionnelle.")
        
        with st.expander("💡 Découvrez les capacités d'Iris Coach"):
            st.markdown("""
            **🌱 Accompagnement Personnel**
            - Coaching personnalisé basé sur votre journal
            - Analyse de vos émotions et humeurs
            - Conseils pour le développement personnel
            
            **🚀 Stratégie Reconversion**
            - Planification de votre transition professionnelle
            - Identification de vos compétences transférables
            - Définition d'objectifs et plan d'action
            
            **💖 Soutien Émotionnel**
            - Gestion du stress et des émotions
            - Techniques de bien-être et relaxation
            - Soutien dans les moments difficiles
            
            **🎯 Définition d'Objectifs**
            - Aide à la formulation d'objectifs SMART
            - Suivi de progression et motivation
            - Ajustement de stratégies selon les résultats
            
            **🌅 Réflexion Quotidienne**
            - Guide pour l'introspection et l'auto-évaluation
            - Questions de développement personnel
            - Analyse des patterns et tendances
            """)
        return
    
    # Métriques personnelles en en-tête
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        journal_entries_count = len(st.session_state.get('journal_entries', []))
        st.metric("Entrées Journal", journal_entries_count)
    
    with col2:
        current_goals_count = len(st.session_state.get('current_goals', []))
        st.metric("Objectifs Actifs", current_goals_count)
    
    with col3:
        mood_streak = st.session_state.get('mood_tracking_streak', 0)
        st.metric("Suivi Humeur", f"{mood_streak} jours")
    
    with col4:
        achievements_count = len(st.session_state.get('achievements', []))
        st.metric("Réalisations", achievements_count)
    
    st.markdown("---")
    
    # Tabs pour organiser les différents assistants
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "💬 Coach Personnel", 
        "🚀 Reconversion", 
        "💖 Soutien Émotionnel", 
        "🎯 Objectifs",
        "🌅 Réflexion"
    ])
    
    with tab1:
        st.markdown("### 💬 Coaching Personnel")
        st.info("Bénéficiez d'un accompagnement personnalisé basé sur votre parcours et vos écrits.")
        
        # Récupération des données du journal
        journal_entries = st.session_state.get('recent_journal_entries', [])
        mood_data = st.session_state.get('current_mood_data')
        
        if journal_entries:
            st.success(f"📖 {len(journal_entries)} entrées récentes analysées")
        
        render_coaching_iris_chat(journal_entries=journal_entries, mood_data=mood_data)
    
    with tab2:
        st.markdown("### 🚀 Stratégie Reconversion")
        st.info("Planifiez et optimisez votre transition professionnelle.")
        
        # Section pour définir les objectifs de reconversion
        with st.expander("🎯 Définir mes objectifs de reconversion"):
            col1, col2 = st.columns(2)
            
            with col1:
                current_field = st.text_input(
                    "Domaine actuel :",
                    value=st.session_state.get('current_field', ''),
                    placeholder="Ex: Finance, Marketing, Enseignement..."
                )
            
            with col2:
                target_field = st.text_input(
                    "Domaine visé :",
                    value=st.session_state.get('target_field', ''),
                    placeholder="Ex: Data Science, UX Design, Coaching..."
                )
            
            timeline = st.selectbox(
                "Échéance souhaitée :",
                ["3 mois", "6 mois", "1 an", "2 ans", "Plus de 2 ans"]
            )
            
            challenges = st.multiselect(
                "Principaux défis :",
                [
                    "Manque de compétences techniques",
                    "Peur de l'échec", 
                    "Contraintes financières",
                    "Manque de réseau",
                    "Incertitude sur le choix",
                    "Manque de temps",
                    "Opposition familiale"
                ]
            )
            
            if current_field or target_field:
                career_goals = {
                    'current_field': current_field,
                    'target_field': target_field,
                    'timeline': timeline,
                    'challenges': challenges
                }
                # Sauvegarder en session
                st.session_state['career_goals'] = career_goals
                st.success("✅ Objectifs de reconversion enregistrés")
            else:
                career_goals = st.session_state.get('career_goals')
        
        progress_data = st.session_state.get('reconversion_progress')
        
        render_reconversion_iris_assistant(career_goals=career_goals, progress_data=progress_data)
    
    with tab3:
        st.markdown("### 💖 Soutien Émotionnel")
        st.info("Gérez vos émotions et trouvez l'équilibre dans votre parcours.")
        
        # Sélecteur d'humeur rapide
        col1, col2 = st.columns(2)
        
        with col1:
            current_mood = st.selectbox(
                "Comment vous sentez-vous maintenant ?",
                ["", "excellent", "good", "neutral", "stressed", "overwhelmed", "sad"],
                format_func=lambda x: {
                    "": "Sélectionnez...",
                    "excellent": "😄 Excellent",
                    "good": "😊 Bien", 
                    "neutral": "😐 Neutre",
                    "stressed": "😰 Stressé(e)",
                    "overwhelmed": "😵 Débordé(e)", 
                    "sad": "😢 Triste"
                }.get(x, x)
            )
        
        with col2:
            current_challenges = st.multiselect(
                "Défis actuels :",
                [
                    "Doutes sur mon avenir",
                    "Stress financier",
                    "Isolement social", 
                    "Fatigue/épuisement",
                    "Conflits familiaux",
                    "Procrastination",
                    "Perfectionnisme"
                ]
            )
        
        if current_mood or current_challenges:
            st.info("💡 Iris adapte son soutien à votre état émotionnel actuel")
        
        render_emotional_iris_chat(recent_mood=current_mood, challenges=current_challenges)
    
    with tab4:
        st.markdown("### 🎯 Définition d'Objectifs")
        st.info("Créez, suivez et atteignez vos objectifs avec l'aide d'Iris.")
        
        # Gestion des objectifs
        current_goals = st.session_state.get('current_goals', [])
        achievements = st.session_state.get('achievements', [])
        
        # Mini-interface de gestion d'objectifs
        with st.expander("➕ Ajouter un nouvel objectif"):
            new_goal_title = st.text_input("Titre de l'objectif :")
            new_goal_category = st.selectbox(
                "Catégorie :",
                ["Professionnel", "Formation", "Personnel", "Santé", "Finance", "Relation"]
            )
            new_goal_deadline = st.date_input("Échéance :")
            
            if st.button("Ajouter l'objectif") and new_goal_title:
                if 'current_goals' not in st.session_state:
                    st.session_state['current_goals'] = []
                
                st.session_state['current_goals'].append({
                    'title': new_goal_title,
                    'category': new_goal_category,
                    'deadline': new_goal_deadline.isoformat(),
                    'status': 'active'
                })
                st.success(f"✅ Objectif '{new_goal_title}' ajouté !")
                st.rerun()
        
        if current_goals:
            st.markdown("**Vos objectifs actuels :**")
            for i, goal in enumerate(current_goals):
                st.write(f"{i+1}. {goal['title']} ({goal['category']})")
        
        render_goals_iris_assistant(current_goals=current_goals, achievements=achievements)
    
    with tab5:
        st.markdown("### 🌅 Réflexion Quotidienne")
        st.info("Prenez du recul et analysez votre parcours avec bienveillance.")
        
        # Entrée du jour
        today_entry = st.session_state.get('today_journal_entry')
        
        if not today_entry:
            st.info("💭 Vous n'avez pas encore écrit dans votre journal aujourd'hui")
            
            # Option pour écrire rapidement
            if st.button("✍️ Écrire une entrée rapide"):
                st.session_state['show_quick_journal'] = True
                st.rerun()
        else:
            st.success("📖 Entrée du jour disponible pour analyse")
        
        # Interface d'écriture rapide
        if st.session_state.get('show_quick_journal'):
            with st.expander("✍️ Écriture rapide", expanded=True):
                quick_entry = st.text_area(
                    "Comment s'est passée votre journée ?",
                    height=100,
                    placeholder="Décrivez vos ressentis, réalisations, défis..."
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 Sauvegarder") and quick_entry:
                        st.session_state['today_journal_entry'] = {
                            'content': quick_entry,
                            'date': st.session_state.get('current_date'),
                            'mood': None
                        }
                        st.session_state['show_quick_journal'] = False
                        st.success("✅ Entrée sauvegardée !")
                        st.rerun()
                
                with col2:
                    if st.button("❌ Annuler"):
                        st.session_state['show_quick_journal'] = False
                        st.rerun()
        
        render_reflection_iris_chat(today_entry=today_entry)
    
    # Section conseils rapides
    st.markdown("---")
    st.markdown("### 🚀 Actions Rapides")
    
    action_cols = st.columns(4)
    
    with action_cols[0]:
        if st.button("💪 Boost de motivation"):
            st.session_state['iris_quick_question'] = "J'ai besoin d'un boost de motivation pour continuer ma reconversion. Peux-tu me remotiver ?"
            st.rerun()
    
    with action_cols[1]:
        if st.button("🧘 Exercice de relaxation"):
            st.session_state['iris_quick_question'] = "Guide-moi dans un exercice de relaxation rapide pour gérer mon stress"
            st.rerun()
    
    with action_cols[2]:
        if st.button("🎯 Objectif de la semaine"):
            st.session_state['iris_quick_question'] = "Aide-moi à définir un objectif réalisable pour cette semaine"
            st.rerun()
    
    with action_cols[3]:
        if st.button("📊 Bilan de progression"):
            st.session_state['iris_quick_question'] = "Fais un bilan de ma progression dans ma reconversion et donne-moi des conseils"
            st.rerun()