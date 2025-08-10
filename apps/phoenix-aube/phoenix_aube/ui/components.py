"""
🔮 Phoenix Aube - Composants UI Réutilisables
Composants Streamlit modulaires pour interface Phoenix Aube
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime


# =============================================
# COMPOSANTS HERO & BRANDING
# =============================================

def render_hero_section() -> None:
    """Section hero avec présentation concept Phoenix Aube"""
    st.markdown("""
    <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 15px; margin-bottom: 2rem;">
        <h1>🔮 Phoenix Aube</h1>
        <h3>Premier outil européen d'exploration métier + validation IA future-proof</h3>
        <p style="font-size: 1.2rem; margin-top: 1rem;">Transformez la peur de l'IA en superpouvoir professionnel</p>
    </div>
    """, unsafe_allow_html=True)


def render_feature_card(title: str, content: str, icon: str = "✨") -> None:
    """Carte de feature avec style Phoenix Aube"""
    st.markdown(f"""
    <div style="background: white; padding: 1.5rem; border-radius: 12px; border-left: 4px solid #667eea; box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-bottom: 1rem;">
        <h4>{icon} {title}</h4>
        <p>{content}</p>
    </div>
    """, unsafe_allow_html=True)


def render_progress_bar(progress: float, label: str) -> None:
    """Barre de progression personnalisée"""
    progress_html = f"""
    <div style="margin: 1rem 0;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
            <span><strong>{label}</strong></span>
            <span>{progress:.0%}</span>
        </div>
        <div style="background-color: #f0f0f0; border-radius: 10px; overflow: hidden;">
            <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); height: 8px; width: {progress*100}%; transition: width 0.3s;"></div>
        </div>
    </div>
    """
    st.markdown(progress_html, unsafe_allow_html=True)


# =============================================
# COMPOSANTS TEST ANXIÉTÉ
# =============================================

def render_anxiety_test() -> Optional[Dict[str, Any]]:
    """Formulaire de test d'anxiété IA (feature freemium)"""
    
    st.markdown("## 🧠 **Test Anxiété IA - Gratuit**")
    st.markdown("*Découvrez en 2 minutes si votre métier actuel résiste à l'IA*")
    
    with st.form("anxiety_test_form"):
        # Métier actuel
        current_job = st.text_input(
            "Quel est votre métier actuel ?",
            placeholder="Ex: Data Analyst, Coach, Chef de Projet..."
        )
        
        # Expérience
        experience_years = st.slider(
            "Années d'expérience dans ce métier",
            min_value=0, max_value=30, value=5
        )
        
        # Inquiétudes
        concerns = st.multiselect(
            "Vos inquiétudes concernant l'IA (optionnel)",
            [
                "Remplacement par des robots",
                "Obsolescence de mes compétences", 
                "Concurrence IA moins chère",
                "Évolution trop rapide du secteur",
                "Incertitude sur l'avenir"
            ]
        )
        
        # Niveau d'exposition actuelle à l'IA
        ai_exposure = st.select_slider(
            "Votre niveau d'exposition actuel à l'IA dans votre travail",
            options=["Aucune", "Faible", "Modérée", "Importante", "Très importante"],
            value="Modérée"
        )
        
        submitted = st.form_submit_button("🔍 **Analyser Mon Anxiété IA**", type="primary")
        
        if submitted and current_job:
            return {
                "current_job": current_job,
                "experience_years": experience_years,
                "concerns": concerns,
                "ai_exposure": ai_exposure
            }
    
    return None


def render_anxiety_results(anxiety_result: Dict[str, Any], job_title: str) -> None:
    """Affichage des résultats du test d'anxiété"""
    
    st.markdown("---")
    st.markdown("## 🎯 **Résultats de Votre Test**")
    
    # Gauge chart principal
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        score = anxiety_result.get("score_anxiété", 0.5)
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = score * 100,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Score Anxiété IA"},
            delta = {'reference': 50},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 30], 'color': "lightgreen"},
                    {'range': [30, 70], 'color': "yellow"},
                    {'range': [70, 100], 'color': "red"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 80
                }
            }
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    # Message personnalisé
    render_anxiety_message(anxiety_result, score)


def render_anxiety_message(anxiety_result: Dict[str, Any], score: float) -> None:
    """Message personnalisé selon score anxiété"""
    
    if score < 0.3:
        st.markdown(f"""
        <div style="background: #d4edda; border: 1px solid #c3e6cb; color: #155724; padding: 1rem; border-radius: 8px; margin: 1rem 0;">
            <h4>✅ Excellente Nouvelle !</h4>
            <p>{anxiety_result.get('message_court', 'Votre métier évolue positivement avec l\'IA')}</p>
            <p><strong>Recommandation :</strong> {anxiety_result.get('recommandation_action', 'Explorez les opportunités')}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background: #fff3cd; border: 1px solid #ffeaa7; color: #856404; padding: 1rem; border-radius: 8px; margin: 1rem 0;">
            <h4>⚠️ Attention à Anticiper</h4>
            <p>{anxiety_result.get('message_court', 'Votre métier nécessite une adaptation proactive')}</p>
            <p><strong>Recommandation :</strong> {anxiety_result.get('recommandation_action', 'Développez des compétences complémentaires')}</p>
        </div>
        """, unsafe_allow_html=True)


# =============================================
# COMPOSANTS EXPLORATION MÉTIER
# =============================================

def render_career_exploration() -> Optional[Dict[str, Any]]:
    """Interface d'exploration métier complète"""
    
    st.markdown("## 🔍 **Exploration Métier Approfondie**")
    
    # Tabs pour les étapes
    tabs = st.tabs([
        "1️⃣ Profil Personnel",
        "2️⃣ Tests Psychométriques", 
        "3️⃣ Compétences",
        "4️⃣ Recommandations"
    ])
    
    exploration_data = {}
    
    with tabs[0]:
        profile_data = render_personal_profile_step()
        if profile_data:
            exploration_data.update(profile_data)
    
    with tabs[1]:
        psycho_data = render_psychometric_tests_step()
        if psycho_data:
            exploration_data.update(psycho_data)
    
    with tabs[2]:
        skills_data = render_skills_assessment_step()
        if skills_data:
            exploration_data.update(skills_data)
    
    with tabs[3]:
        recommendations_data = render_career_recommendations_step()
        if recommendations_data:
            exploration_data.update(recommendations_data)
    
    return exploration_data if exploration_data else None


def render_personal_profile_step() -> Optional[Dict[str, Any]]:
    """Étape profil personnel"""
    
    st.markdown("### 👤 **Votre Profil Personnel**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        age_range = st.selectbox("Tranche d'âge", ["25-35", "35-45", "45-55", "55+"])
        current_sector = st.text_input("Secteur actuel", placeholder="Ex: Tech, Finance, Santé...")
        current_position = st.text_input("Poste actuel", placeholder="Ex: Data Analyst, Manager...")
    
    with col2:
        experience_years = st.slider("Années d'expérience", 0, 30, 8)
        geographic_constraints = st.text_input(
            "Contraintes géographiques", 
            placeholder="Ex: Région parisienne uniquement"
        )
        salary_constraints = st.text_input(
            "Contraintes salariales", 
            placeholder="Ex: Minimum 45k€/an"
        )
    
    # Motivations
    motivations = st.multiselect(
        "Motivations principales de reconversion",
        [
            "Recherche de sens", "Équilibre vie pro/perso", "Évolution salariale",
            "Nouvelles compétences", "Secteur en croissance", "Passion personnelle",
            "Éviter obsolescence IA", "Entrepreneuriat"
        ]
    )
    
    if st.button("➡️ Continuer vers les tests", type="primary"):
        return {
            "profile": {
                "age_range": age_range,
                "current_sector": current_sector,
                "current_position": current_position,
                "experience_years": experience_years,
                "geographic_constraints": geographic_constraints,
                "salary_constraints": salary_constraints,
                "motivations": motivations
            }
        }
    
    return None


def render_psychometric_tests_step() -> Optional[Dict[str, Any]]:
    """Étape tests psychométriques"""
    
    st.markdown("### 🧠 **Tests Psychométriques Scientifiques**")
    st.info("Tests basés sur Big Five et RIASEC - Standards scientifiques internationaux")
    
    # Test Big Five simplifié
    st.markdown("#### 📊 **Test Big Five**")
    
    big_five_questions = [
        "Je suis quelqu'un qui aime essayer de nouvelles choses",
        "Je suis quelqu'un qui fait les choses de manière systématique", 
        "Je suis quelqu'un qui aime être entouré de monde",
        "Je suis quelqu'un qui fait confiance aux autres",
        "Je suis quelqu'un qui reste calme en situation de stress"
    ]
    
    big_five_responses = {}
    for i, question in enumerate(big_five_questions):
        big_five_responses[f"q{i}"] = st.slider(
            question,
            min_value=1, max_value=7, value=4,
            help="1 = Pas du tout d'accord, 7 = Tout à fait d'accord"
        )
    
    # Test RIASEC
    st.markdown("#### 🎯 **Test RIASEC (Intérêts Professionnels)**")
    
    interests = st.multiselect(
        "Quelles activités vous intéressent le plus ?",
        [
            "Réparer/Construire des objets (Realistic)",
            "Analyser/Rechercher (Investigative)", 
            "Créer/Dessiner (Artistic)",
            "Aider/Former les autres (Social)",
            "Diriger/Vendre (Enterprising)",
            "Organiser/Administrer (Conventional)"
        ]
    )
    
    if st.button("🔄 Calculer Mon Profil Psychométrique", type="primary"):
        
        # Simulation calcul profil
        with st.spinner("Calcul de votre profil..."):
            import time
            time.sleep(2)
            
            # Générer résultats mock
            render_psychometric_results(big_five_responses, interests)
            
            return {
                "psychometric": {
                    "big_five": big_five_responses,
                    "riasec_interests": interests
                }
            }
    
    return None


def render_psychometric_results(big_five_responses: Dict, interests: List[str]) -> None:
    """Affichage résultats tests psychométriques"""
    
    st.success("✅ Profil psychométrique calculé !")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Big Five Profile:**")
        mock_scores = {
            "Ouverture": 0.7, 
            "Conscience": 0.8, 
            "Extraversion": 0.6, 
            "Agréabilité": 0.9, 
            "Névrosisme": 0.3
        }
        df = pd.DataFrame(list(mock_scores.items()), columns=["Trait", "Score"])
        fig = px.bar(df, x="Trait", y="Score", title="Votre Profil Big Five")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("**RIASEC Profile:**")
        riasec_scores = {"Social": 0.85, "Investigative": 0.7, "Enterprising": 0.6}
        df2 = pd.DataFrame(list(riasec_scores.items()), columns=["Type", "Score"])
        fig2 = px.pie(df2, values="Score", names="Type", title="Vos Intérêts Dominants")
        st.plotly_chart(fig2, use_container_width=True)


def render_skills_assessment_step() -> Optional[Dict[str, Any]]:
    """Étape évaluation compétences"""
    
    st.markdown("### 🛠️ **Cartographie de Vos Compétences**")
    st.info("Identifiez vos compétences transférables et talents cachés")
    
    # Simulation d'évaluation compétences
    competence_categories = {
        "Techniques": ["Python", "Excel", "SQL", "Design", "Marketing Digital"],
        "Managériales": ["Leadership", "Gestion projet", "Négociation", "Coaching"],
        "Interpersonnelles": ["Communication", "Empathie", "Travail équipe", "Présentation"],
        "Cognitives": ["Analyse", "Résolution problème", "Créativité", "Apprentissage"]
    }
    
    skills_assessment = {}
    
    for category, skills in competence_categories.items():
        st.markdown(f"#### {category}")
        
        selected_skills = st.multiselect(
            f"Compétences {category.lower()} que vous possédez:",
            skills,
            key=f"skills_{category}"
        )
        
        if selected_skills:
            skills_levels = {}
            for skill in selected_skills:
                level = st.slider(
                    f"Niveau en {skill}",
                    min_value=1, max_value=10, value=6,
                    key=f"level_{skill}"
                )
                skills_levels[skill] = level
            
            skills_assessment[category] = skills_levels
    
    if st.button("📊 Analyser Mes Compétences", type="primary"):
        if skills_assessment:
            render_skills_analysis(skills_assessment)
            return {"skills_assessment": skills_assessment}
    
    return None


def render_skills_analysis(skills_assessment: Dict[str, Dict[str, int]]) -> None:
    """Analyse et visualisation des compétences"""
    
    st.markdown("#### 🎯 **Analyse de Vos Compétences**")
    
    # Créer DataFrame pour visualisation
    all_skills = []
    for category, skills in skills_assessment.items():
        for skill, level in skills.items():
            all_skills.append({"Compétence": skill, "Niveau": level, "Catégorie": category})
    
    if all_skills:
        df = pd.DataFrame(all_skills)
        
        # Graphique radar
        fig = px.bar(
            df, 
            x="Compétence", 
            y="Niveau", 
            color="Catégorie",
            title="Profil de Compétences"
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
        
        # Top compétences
        top_skills = df.nlargest(5, "Niveau")
        st.markdown("**🏆 Vos Top 5 Compétences:**")
        for _, skill in top_skills.iterrows():
            st.write(f"• **{skill['Compétence']}** ({skill['Catégorie']}) - Niveau {skill['Niveau']}/10")


def render_career_recommendations_step() -> Optional[Dict[str, Any]]:
    """Étape recommandations métiers"""
    
    st.markdown("### 🎯 **Vos Recommandations Métiers**")
    
    # Mock recommendations (en production, utiliserait RecommendationEngine)
    recommendations = [
        {
            "title": "Coach en Reconversion",
            "compatibility": 0.92,
            "sector": "Services",
            "justification": "Parfaite compatibilité avec votre profil Social et votre expérience",
            "ia_resistance": 0.88,
            "salary_range": "35-55k€",
            "required_skills": ["Écoute active", "Empathie", "Méthodes coaching"]
        },
        {
            "title": "Data Scientist",
            "compatibility": 0.78,
            "sector": "Tech",
            "justification": "Vos compétences analytiques et votre profil Investigative",
            "ia_resistance": 0.65,
            "salary_range": "45-70k€", 
            "required_skills": ["Python", "ML", "Statistiques", "Communication"]
        },
        {
            "title": "Designer UX",
            "compatibility": 0.75,
            "sector": "Créatif",
            "justification": "Créativité et compréhension utilisateur excellent",
            "ia_resistance": 0.70,
            "salary_range": "40-60k€",
            "required_skills": ["Design thinking", "Prototypage", "User research"]
        }
    ]
    
    for i, rec in enumerate(recommendations):
        with st.expander(f"🏆 **#{i+1} - {rec['title']}** (Compatibilité: {rec['compatibility']:.0%})"):
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Compatibilité", f"{rec['compatibility']:.0%}")
                st.metric("Résistance IA", f"{rec['ia_resistance']:.0%}")
            
            with col2:
                st.write(f"**Secteur:** {rec['sector']}")
                st.write(f"**Salaire:** {rec['salary_range']}")
            
            with col3:
                st.write("**Compétences requises:**")
                for skill in rec['required_skills']:
                    st.write(f"• {skill}")
            
            st.write(f"**Justification:** {rec['justification']}")
            
            if st.button(f"🤖 Valider ce métier avec l'IA", key=f"validate_{i}"):
                st.session_state[f'job_to_analyze'] = rec['title']
                st.info(f"🔄 Analyse IA pour {rec['title']} préparée...")
    
    return {"recommendations": recommendations}


# =============================================
# COMPOSANTS VALIDATION IA
# =============================================

def render_ia_validation() -> None:
    """Interface de validation IA"""
    
    st.markdown("## 🤖 **Validation IA Future-Proof**")
    st.markdown("*Analyse de la résistance de vos métiers face à l'IA*")
    
    job_to_analyze = st.text_input(
        "Métier à analyser",
        value=st.session_state.get('job_to_analyze', ''),
        placeholder="Ex: Data Scientist, Coach, Chef de Projet..."
    )
    
    if st.button("🔍 **Analyser la Résistance IA**", type="primary") and job_to_analyze:
        
        with st.spinner("🤖 Analyse approfondie en cours..."):
            # Simulation analyse (en production utiliserait IAFutureValidator)
            import time
            time.sleep(2)
            
            # Mock analysis
            mock_analysis = {
                "métier_titre": job_to_analyze,
                "score_résistance_ia": 0.72,
                "niveau_menace": "faible",
                "type_évolution": "enhanced",
                "timeline_impact": "5-10 ans",
                "tâches_automatisables": [
                    "Collecte de données (80%)",
                    "Rapports standardisés (70%)"
                ],
                "tâches_humaines_critiques": [
                    "Interprétation business (95%)",
                    "Communication insights (90%)",
                    "Prise de décision stratégique (85%)"
                ],
                "opportunités_ia_collaboration": [
                    "IA augmente capacité d'analyse",
                    "Automatisation tâches répétitives",
                    "Focus sur stratégique"
                ],
                "compétences_ia_à_développer": [
                    "Prompt engineering",
                    "Interprétation modèles ML",
                    "Éthique IA"
                ],
                "message_futur_positif": f"Excellente nouvelle ! Le métier de {job_to_analyze} évolue positivement avec l'IA."
            }
            
            render_ia_analysis_results(mock_analysis)


def render_ia_analysis_results(analysis: Dict[str, Any]) -> None:
    """Affichage des résultats d'analyse IA"""
    
    st.markdown("---")
    st.markdown(f"## 🎯 **Analyse IA : {analysis['métier_titre']}**")
    
    # Métriques principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Résistance IA", f"{analysis['score_résistance_ia']:.0%}")
    
    with col2:
        st.metric("Niveau Menace", analysis['niveau_menace'].title())
    
    with col3:
        st.metric("Évolution", analysis['type_évolution'].title())
    
    with col4:
        st.metric("Timeline", analysis['timeline_impact'])
    
    # Message rassurant
    st.markdown(f"""
    <div style="background: #d4edda; border: 1px solid #c3e6cb; color: #155724; padding: 1rem; border-radius: 8px; margin: 1rem 0;">
        <h4>💡 Vision Future-Proof</h4>
        <p>{analysis['message_futur_positif']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Détails par onglets
    tabs = st.tabs(["🤖 Automatisation", "👨‍💼 Valeur Humaine", "🚀 Opportunités", "📚 Compétences"])
    
    with tabs[0]:
        st.markdown("### 🤖 **Tâches Automatisables**")
        for task in analysis['tâches_automatisables']:
            st.write(f"• {task}")
    
    with tabs[1]:
        st.markdown("### 👨‍💼 **Valeur Humaine Critique**")
        for task in analysis['tâches_humaines_critiques']:
            st.write(f"• {task}")
    
    with tabs[2]:
        st.markdown("### 🚀 **Opportunités avec l'IA**")
        for opp in analysis['opportunités_ia_collaboration']:
            st.write(f"• {opp}")
    
    with tabs[3]:
        st.markdown("### 📚 **Compétences IA à Développer**")
        for skill in analysis['compétences_ia_à_développer']:
            st.write(f"• {skill}")


# =============================================
# COMPOSANTS ÉCOSYSTÈME
# =============================================

def render_ecosystem_transition() -> None:
    """Interface transition écosystème Phoenix"""
    
    st.markdown("## 🔗 **Écosystème Phoenix**")
    st.markdown("*Continuez votre parcours avec les autres applications Phoenix*")
    
    # Applications Phoenix disponibles
    phoenix_apps = [
        {
            "name": "Phoenix CV",
            "icon": "📄",
            "description": "Créez un CV optimisé pour votre nouveau métier IA-resistant",
            "features": ["Template adapté au secteur", "Compétences IA intégrées", "ATS-friendly"],
            "url": "https://phoenix-cv.streamlit.app/",
            "context_type": "cv_creation"
        },
        {
            "name": "Phoenix Letters",
            "icon": "✉️",
            "description": "Lettres de motivation personnalisées pour votre reconversion",
            "features": ["Narrative de reconversion", "Adaptation IA storyline", "Ultra-personnalisées"],
            "url": "https://phoenix-letters.streamlit.app/",
            "context_type": "cover_letter"
        },
        {
            "name": "Phoenix Rise",
            "icon": "🦋",
            "description": "Coaching IA pour accompagner votre transformation",
            "features": ["Suivi personnalisé", "Confiance en soi", "Plan d'action 90j"],
            "url": "https://phoenix-rise.streamlit.app/",
            "context_type": "coaching"
        }
    ]
    
    cols = st.columns(len(phoenix_apps))
    
    for i, app in enumerate(phoenix_apps):
        with cols[i]:
            render_feature_card(
                f"{app['icon']} {app['name']}",
                app['description']
            )
            
            st.markdown("**Fonctionnalités:**")
            for feature in app['features']:
                st.write(f"• {feature}")
            
            if st.button(f"➡️ Aller sur {app['name']}", key=f"goto_{app['name']}"):
                st.session_state[f'transition_to_{app["context_type"]}'] = True
                st.info(f"🔄 Préparation transition vers {app['name']}...")


# =============================================
# COMPOSANTS ANALYTICS
# =============================================

def render_analytics_dashboard() -> None:
    """Dashboard analytics Phoenix Aube"""
    
    st.markdown("## 📊 **Analytics Phoenix Aube**")
    
    # Métriques principales
    col1, col2, col3, col4 = st.columns(4)
    
    metrics = [
        {"title": "Analyses IA Aujourd'hui", "value": "142", "icon": "🔍"},
        {"title": "Explorations Démarrées", "value": "89", "icon": "🚀"},
        {"title": "Métiers Choisis", "value": "34", "icon": "🎯"},
        {"title": "Satisfaction Moyenne", "value": "4.7/5", "icon": "⭐"}
    ]
    
    for i, metric in enumerate(metrics):
        with [col1, col2, col3, col4][i]:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 1rem; border-radius: 10px; text-align: center; margin: 0.5rem 0;">
                <h3>{metric['value']}</h3>
                <p>{metric['title']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Graphiques
    col1, col2 = st.columns(2)
    
    with col1:
        render_top_analyzed_jobs_chart()
    
    with col2:
        render_resistance_scores_chart()


def render_top_analyzed_jobs_chart() -> None:
    """Graphique top métiers analysés"""
    
    st.markdown("### 🔝 Top Métiers Analysés")
    
    mock_data = {
        "Métier": ["Data Scientist", "Coach", "Chef de Projet", "Designer UX", "Consultant"],
        "Analyses": [45, 38, 32, 28, 24]
    }
    
    df = pd.DataFrame(mock_data)
    fig = px.bar(df, x="Analyses", y="Métier", orientation="h")
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)


def render_resistance_scores_chart() -> None:
    """Graphique scores résistance IA par secteur"""
    
    st.markdown("### 📈 Scores Résistance IA Moyens")
    
    mock_resistance = {
        "Secteur": ["Services", "Créatif", "Tech", "Finance", "Industrie"],
        "Score": [0.82, 0.75, 0.68, 0.45, 0.38]
    }
    
    df = pd.DataFrame(mock_resistance)
    fig = px.pie(df, values="Score", names="Secteur")
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)