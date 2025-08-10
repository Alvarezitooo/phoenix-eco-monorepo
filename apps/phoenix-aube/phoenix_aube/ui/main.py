"""
Phoenix Aube - Interface Streamlit Trust by Design
UX d'exploration métier avec transparence radicale
"""

import streamlit as st
import asyncio
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, List, Any, Optional
import json
from datetime import datetime

# Imports services Phoenix Aube
from ..services.ia_validator import IAFutureValidator
from ..core import TransparencyEngine, PhoenixAubeEventStore, PhoenixAubeOrchestrator
from ..utils.mock_providers import MockEventStore, MockResearchProvider, MockRecommendationEngine
from .components import (
    render_hero_section,
    render_anxiety_test,
    render_career_exploration,
    render_ia_validation,
    render_ecosystem_transition,
    render_anxiety_results,
    render_ia_analysis_results,
    render_analytics_dashboard
)

# Configuration Streamlit
st.set_page_config(
    page_title="Phoenix Aube - Exploration Métier IA-proof",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS custom
st.markdown("""
<style>
.main-header {
    text-align: center;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 2rem;
    border-radius: 15px;
    margin-bottom: 2rem;
    box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
}

.feature-card {
    background: white;
    padding: 1.5rem;
    border-radius: 12px;
    border-left: 4px solid #667eea;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    margin-bottom: 1rem;
}

.metric-card {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    color: white;
    padding: 1rem;
    border-radius: 10px;
    text-align: center;
    margin: 0.5rem 0;
}

.success-message {
    background: #d4edda;
    border: 1px solid #c3e6cb;
    color: #155724;
    padding: 1rem;
    border-radius: 8px;
    margin: 1rem 0;
}

.warning-message {
    background: #fff3cd;
    border: 1px solid #ffeaa7;
    color: #856404;
    padding: 1rem;
    border-radius: 8px;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

# Initialisation service global
@st.cache_resource
def get_ia_validator():
    """Initialise le service de validation IA"""
    event_store = MockEventStore()
    research_provider = MockResearchProvider()
    return IAFutureValidator(event_store, research_provider)

def main():
    """Point d'entrée principal de l'interface Phoenix Aube"""
    
    # Choix du mode d'interface
    interface_choice = st.sidebar.selectbox(
        "Mode d'interface:",
        ["Trust by Design (Recommandé)", "Mode Basique"]
    )
    
    if interface_choice == "Trust by Design (Recommandé)":
        # Utiliser la nouvelle interface Trust by Design
        from .trust_by_design_app import main as trust_main
        trust_main()
    else:
        # Interface basique originale
        render_basic_interface()

def render_basic_interface():
    """Interface basique Phoenix Aube"""
    
    # Header principal
    st.markdown("""
    <div class="main-header">
        <h1>🔮 Phoenix Aube</h1>
        <h3>Premier outil européen d'exploration métier + validation IA future-proof</h3>
        <p>Transformez la peur de l'IA en superpouvoir professionnel</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar navigation
    with st.sidebar:
        st.title("🔮 Navigation")
        
        page = st.radio(
            "Choisissez votre parcours :",
            [
                "🏠 Accueil",
                "🧠 Test Anxiété IA (Gratuit)",
                "🔍 Exploration Métier",
                "🤖 Validation IA",
                "🔗 Écosystème Phoenix",
                "📊 Métriques & Analytics"
            ]
        )
        
        st.markdown("---")
        st.markdown("### 🎯 Votre Progression")
        
        # Mock progression
        progress = st.progress(0.3)
        st.write("30% - Test anxiété complété")
        
        st.markdown("---")
        st.markdown("### ℹ️ À propos")
        st.info("""
        **Phoenix Aube** résout la "double anxiété" :
        
        1. **Identitaire** : "Quel métier me correspond ?"
        2. **Pérennité** : "Va-t-il survivre à l'IA ?"
        
        🇪🇺 **Conçu en Europe, pour les Européens**
        """)
    
    # Routing des pages
    if page == "🏠 Accueil":
        render_home_page()
    elif page == "🧠 Test Anxiété IA (Gratuit)":
        render_anxiety_test_page()
    elif page == "🔍 Exploration Métier":
        render_exploration_page()
    elif page == "🤖 Validation IA":
        render_validation_page()
    elif page == "🔗 Écosystème Phoenix":
        render_ecosystem_page()
    elif page == "📊 Métriques & Analytics":
        render_analytics_page()

def render_home_page():
    """Page d'accueil avec présentation du concept"""
    
    # Hero section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ## 🎯 **Concept Révolutionnaire en 3 Temps**
        
        ### **TEMPS 1 - Exploration Métier Approfondie** (70% effort)
        - 🧠 Tests psychométriques scientifiques (Big Five + RIASEC)
        - 🎯 Cartographie compétences transférables cachées
        - 🤝 Algorithme matching multidimensionnel
        - 🏆 Top 5 métiers recommandés avec justifications transparentes
        
        ### **TEMPS 2 - Validation IA Future-Proof** (20% effort)
        - 🔮 Prédiction impact IA personnalisée par métier
        - 📊 Score résistance automatisation (0-1)
        - ⏰ Timeline évolution secteurs (5-10 ans)
        - 🚀 Plan maîtrise compétences IA pour exceller
        
        ### **TEMPS 3 - Intégration Écosystème** (10% effort)
        - 🔗 Transition automatique vers Phoenix CV/Letters/Rise
        - 📝 Event store central pour données cross-apps
        """)
        
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h4>🇪🇺 Innovation Européenne</h4>
            <p><strong>Trust by Design</strong><br>
            IA explicable vs boîtes noires US</p>
        </div>
        
        <div class="feature-card">
            <h4>🔬 Validation Scientifique</h4>
            <p><strong>Partenariat 3IA</strong><br>
            Légitimité académique française</p>
        </div>
        
        <div class="feature-card">
            <h4>🛡️ RGPD by Design</h4>
            <p><strong>Compliance AI Act</strong><br>
            Protection données natives</p>
        </div>
        """, unsafe_allow_html=True)
    
    # CTA principal
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 **Commencer Mon Exploration Gratuite**", type="primary"):
            st.session_state['page'] = "🧠 Test Anxiété IA (Gratuit)"
            st.rerun()
        
        st.markdown("*Commencez par le test d'anxiété IA gratuit - 2 minutes seulement*")
    
    # Témoignages et social proof
    st.markdown("---")
    st.markdown("## 💬 **Témoignages Utilisateurs**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <p><em>"Enfin un outil qui explique pourquoi ! J'ai compris que mon métier de Coach était IA-résistant."</em></p>
            <strong>- Marie, 42 ans, Reconversion</strong>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <p><em>"L'approche européenne fait la différence. Transparence totale vs algorithmes opaques."</em></p>
            <strong>- Thomas, 38 ans, Data Analyst</strong>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <p><em>"Ma reconversion vers Data Scientist validée scientifiquement. Confiance retrouvée !"</em></p>
            <strong>- Amélie, 35 ans, Ex-Marketing</strong>
        </div>
        """, unsafe_allow_html=True)

def render_anxiety_test_page():
    """Page de test d'anxiété IA (feature freemium)"""
    
    st.markdown("## 🧠 **Test Anxiété IA - Gratuit**")
    st.markdown("*Découvrez en 2 minutes si votre métier actuel résiste à l'IA*")
    
    with st.form("anxiety_test_form"):
        st.markdown("### 📝 **Votre Métier Actuel**")
        
        current_job = st.text_input(
            "Quel est votre métier actuel ?",
            placeholder="Ex: Data Analyst, Coach, Chef de Projet..."
        )
        
        experience_years = st.slider(
            "Années d'expérience dans ce métier",
            min_value=0, max_value=30, value=5
        )
        
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
        
        submitted = st.form_submit_button("🔍 **Analyser Mon Anxiété IA**", type="primary")
        
        if submitted and current_job:
            with st.spinner("🤖 Analyse de votre métier face à l'IA..."):
                # Simulation async call
                import time
                time.sleep(2)  # Simulation processing
                
                # Mock results
                validator = get_ia_validator()
                
                # Simuler appel async de manière synchrone pour MVP
                try:
                    # En production: anxiety_result = asyncio.run(validator.calculer_score_anxiété_ia(current_job))
                    anxiety_result = {
                        "métier": current_job,
                        "score_anxiété": 0.35,
                        "niveau_anxiété": "faible",
                        "message_court": f"Votre métier {current_job} évolue avec l'IA. Opportunité d'amélioration ! 🚀",
                        "recommandation_action": "Explorez comment l'IA peut augmenter votre productivité"
                    }
                    
                    render_anxiety_results(anxiety_result, current_job)
                    
                except Exception as e:
                    st.error(f"Erreur lors de l'analyse : {str(e)}")

def render_anxiety_results(anxiety_result: Dict[str, Any], job_title: str):
    """Affiche les résultats du test d'anxiété"""
    
    st.markdown("---")
    st.markdown("## 🎯 **Résultats de Votre Test**")
    
    # Score principal
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        score = anxiety_result["score_anxiété"]
        
        # Gauge chart avec Plotly
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
    if score < 0.3:
        st.markdown(f"""
        <div class="success-message">
            <h4>✅ Excellente Nouvelle !</h4>
            <p>{anxiety_result['message_court']}</p>
            <p><strong>Recommandation :</strong> {anxiety_result['recommandation_action']}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="warning-message">
            <h4>⚠️ Attention à Anticiper</h4>
            <p>{anxiety_result['message_court']}</p>
            <p><strong>Recommandation :</strong> {anxiety_result['recommandation_action']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # CTA vers exploration complète
    st.markdown("---")
    st.markdown("### 🚀 **Aller Plus Loin**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔍 **Exploration Métier Complète**", type="primary"):
            st.session_state['current_job_context'] = job_title
            st.info("🔄 Redirection vers l'exploration complète...")
            
    with col2:
        if st.button("🤖 **Analyse IA Détaillée**"):
            st.session_state['job_to_analyze'] = job_title
            st.info("🔄 Redirection vers l'analyse IA...")

def render_exploration_page():
    """Page d'exploration métier complète (TEMPS 1)"""
    
    st.markdown("## 🔍 **Exploration Métier Approfondie**")
    st.markdown("*Découvrez les métiers qui vous correspondent vraiment*")
    
    # Étapes du processus
    tabs = st.tabs([
        "1️⃣ Profil Personnel",
        "2️⃣ Tests Psychométriques", 
        "3️⃣ Compétences",
        "4️⃣ Recommandations"
    ])
    
    with tabs[0]:
        render_personal_profile_step()
    
    with tabs[1]:
        render_psychometric_tests_step()
    
    with tabs[2]:
        render_skills_assessment_step()
    
    with tabs[3]:
        render_career_recommendations_step()

def render_personal_profile_step():
    """Étape 1 : Profil personnel"""
    
    st.markdown("### 👤 **Votre Profil Personnel**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.selectbox("Tranche d'âge", ["25-35", "35-45", "45-55", "55+"])
        st.text_input("Secteur actuel", placeholder="Ex: Tech, Finance, Santé...")
        st.text_input("Poste actuel", placeholder="Ex: Data Analyst, Manager...")
    
    with col2:
        st.slider("Années d'expérience", 0, 30, 8)
        st.text_input("Contraintes géographiques", placeholder="Ex: Région parisienne uniquement")
        st.text_input("Contraintes salariales", placeholder="Ex: Minimum 45k€/an")
    
    st.multiselect(
        "Motivations principales de reconversion",
        [
            "Recherche de sens", "Équilibre vie pro/perso", "Évolution salariale",
            "Nouvelles compétences", "Secteur en croissance", "Passion personnelle",
            "Éviter obsolescence IA", "Entrepreneuriat"
        ]
    )
    
    if st.button("➡️ Continuer vers les tests", type="primary"):
        st.success("✅ Profil enregistré ! Passons aux tests psychométriques.")

def render_psychometric_tests_step():
    """Étape 2 : Tests psychométriques"""
    
    st.markdown("### 🧠 **Tests Psychométriques Scientifiques**")
    st.info("Tests basés sur Big Five et RIASEC - Standards scientifiques internationaux")
    
    # Mock test Big Five
    st.markdown("#### 📊 **Test Big Five**")
    
    questions_big_five = [
        "Je suis quelqu'un qui aime essayer de nouvelles choses",
        "Je suis quelqu'un qui fait les choses de manière systématique", 
        "Je suis quelqu'un qui aime être entouré de monde",
        "Je suis quelqu'un qui fait confiance aux autres",
        "Je suis quelqu'un qui reste calme en situation de stress"
    ]
    
    big_five_responses = {}
    for i, question in enumerate(questions_big_five):
        big_five_responses[f"q{i}"] = st.slider(
            question,
            min_value=1, max_value=7, value=4,
            help="1 = Pas du tout d'accord, 7 = Tout à fait d'accord"
        )
    
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
        with st.spinner("Calcul de votre profil..."):
            import time
            time.sleep(2)
            
            # Mock results
            st.success("✅ Profil psychométrique calculé !")
            
            # Afficher résultats mock
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Big Five Profile:**")
                mock_scores = {"Ouverture": 0.7, "Conscience": 0.8, "Extraversion": 0.6, "Agréabilité": 0.9, "Névrosisme": 0.3}
                df = pd.DataFrame(list(mock_scores.items()), columns=["Trait", "Score"])
                fig = px.bar(df, x="Trait", y="Score", title="Votre Profil Big Five")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("**RIASEC Profile:**")
                riasec_scores = {"Social": 0.85, "Investigative": 0.7, "Enterprising": 0.6}
                df2 = pd.DataFrame(list(riasec_scores.items()), columns=["Type", "Score"])
                fig2 = px.pie(df2, values="Score", names="Type", title="Vos Intérêts Dominants")
                st.plotly_chart(fig2, use_container_width=True)

def render_skills_assessment_step():
    """Étape 3 : Évaluation compétences"""
    st.markdown("### 🛠️ **Cartographie de Vos Compétences**")
    st.info("Identifiez vos compétences transférables et talents cachés")
    
    # TODO: Implémenter évaluation compétences
    st.markdown("*🚧 Fonctionnalité en développement*")

def render_career_recommendations_step():
    """Étape 4 : Recommandations métiers"""
    st.markdown("### 🎯 **Vos Recommandations Métiers**")
    
    # Mock recommendations
    recommendations = [
        {
            "title": "Coach en Reconversion",
            "compatibility": 0.92,
            "sector": "Services",
            "justification": "Parfaite compatibilité avec votre profil Social et votre expérience",
            "ia_resistance": 0.88
        },
        {
            "title": "Data Scientist",
            "compatibility": 0.78,
            "sector": "Tech",
            "justification": "Vos compétences analytiques et votre profil Investigative",
            "ia_resistance": 0.65
        }
    ]
    
    for i, rec in enumerate(recommendations):
        with st.expander(f"🏆 **#{i+1} - {rec['title']}** (Compatibilité: {rec['compatibility']:.0%})"):
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Compatibilité Globale", f"{rec['compatibility']:.0%}")
                st.metric("Résistance IA", f"{rec['ia_resistance']:.0%}")
            
            with col2:
                st.write(f"**Secteur:** {rec['sector']}")
                st.write(f"**Justification:** {rec['justification']}")
            
            if st.button(f"🤖 Valider ce métier avec l'IA", key=f"validate_{i}"):
                st.session_state['job_to_analyze'] = rec['title']
                st.info(f"🔄 Analyse IA pour {rec['title']} en cours...")

def render_validation_page():
    """Page de validation IA (TEMPS 2)"""
    
    st.markdown("## 🤖 **Validation IA Future-Proof**")
    st.markdown("*Analyse de la résistance de vos métiers recommandés face à l'IA*")
    
    # Input métier à analyser
    job_to_analyze = st.text_input(
        "Métier à analyser",
        value=st.session_state.get('job_to_analyze', ''),
        placeholder="Ex: Data Scientist, Coach, Chef de Projet..."
    )
    
    if st.button("🔍 **Analyser la Résistance IA**", type="primary") and job_to_analyze:
        
        with st.spinner("🤖 Analyse approfondie en cours..."):
            validator = get_ia_validator()
            
            # Mock analysis pour MVP
            try:
                # En production: analysis = asyncio.run(validator.évaluer_résistance_métier(job_to_analyze))
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
                    "message_futur_positif": f"Excellente nouvelle ! Le métier de {job_to_analyze} évolue positivement avec l'IA.",
                    "niveau_confiance": "élevé"
                }
                
                render_ia_analysis_results(mock_analysis)
                
            except Exception as e:
                st.error(f"Erreur lors de l'analyse : {str(e)}")

def render_ia_analysis_results(analysis: Dict[str, Any]):
    """Affiche les résultats de l'analyse IA"""
    
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
    <div class="success-message">
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

def render_ecosystem_page():
    """Page de transition vers l'écosystème Phoenix"""
    
    st.markdown("## 🔗 **Écosystème Phoenix**")
    st.markdown("*Continuez votre parcours avec les autres applications Phoenix*")
    
    # Applications disponibles
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h4>📄 Phoenix CV</h4>
            <p>Créez un CV optimisé pour votre nouveau métier IA-resistant</p>
            <ul>
                <li>Template adapté au secteur</li>
                <li>Compétences IA intégrées</li>
                <li>ATS-friendly</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("➡️ Aller sur Phoenix CV"):
            st.info("🔄 Redirection vers Phoenix CV...")
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h4>✉️ Phoenix Letters</h4>
            <p>Lettres de motivation personnalisées pour votre reconversion</p>
            <ul>
                <li>Narrative de reconversion</li>
                <li>Adaptation IA storyline</li>
                <li>Ultra-personnalisées</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("➡️ Aller sur Phoenix Letters"):
            st.info("🔄 Redirection vers Phoenix Letters...")
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h4>🦋 Phoenix Rise</h4>
            <p>Coaching IA pour accompagner votre transformation</p>
            <ul>
                <li>Suivi personnalisé</li>
                <li>Confiance en soi</li>
                <li>Plan d'action 90j</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("➡️ Aller sur Phoenix Rise"):
            st.info("🔄 Redirection vers Phoenix Rise...")

def render_analytics_page():
    """Page d'analytics et métriques"""
    render_analytics_dashboard()

if __name__ == "__main__":
    main()