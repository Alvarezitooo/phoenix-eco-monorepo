#!/usr/bin/env python3
"""
🌅 Phoenix Aube - Interface Streamlit Principale
Point d'entrée unique pour l'application Streamlit
"""

import sys
import os
import streamlit as st

# Ajouter le chemin vers la racine du monorepo pour Streamlit Cloud
monorepo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if monorepo_root not in sys.path:
    sys.path.insert(0, monorepo_root)

from phoenix_event_bridge import PhoenixEventBridge, PhoenixEventData, PhoenixEventType

# Initialiser Event Bridge global
event_bridge = PhoenixEventBridge()

# Ajouter le répertoire au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configuration Streamlit
st.set_page_config(
    page_title="Phoenix Aube - Exploration Carrière IA-proof",
    page_icon="🌅",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Interface principale Phoenix Aube"""
    
    # Header principal
    st.markdown("""
    <div style="text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem; border-radius: 15px; margin-bottom: 2rem;">
        <h1>🌅 Phoenix Aube</h1>
        <h3>Premier outil européen d'exploration métier + validation IA future-proof</h3>
        <p>Transformez la peur de l'IA en superpouvoir professionnel</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation principale
    with st.sidebar:
        st.title("🌅 Navigation")
        # Choix du mode d'interface (parcours guidé vs mode classique)
        mode = st.selectbox(
            "Mode d'interface",
            ["Parcours Guidé (Recommandé)", "Mode Classique"],
            index=0,
        )
        if mode == "Parcours Guidé (Recommandé)":
            from phoenix_aube.ui.guided_flow import main as guided_main
            guided_main()
            return
        
        page = st.radio(
            "Choisissez votre parcours :",
            [
                "🏠 Accueil",
                "🧠 Test Anxiété IA (Gratuit)",
                "🔍 Exploration Métier",
                "🤖 Validation IA",
                "🔗 Écosystème Phoenix"
            ]
        )
        
        st.markdown("---")
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
        render_anxiety_test()
    elif page == "🔍 Exploration Métier":
        render_career_exploration()
    elif page == "🤖 Validation IA":
        render_ia_validation()
    elif page == "🔗 Écosystème Phoenix":
        render_ecosystem_links()

def render_home_page():
    """Page d'accueil"""
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
        <div style="background: white; padding: 1.5rem; border-radius: 12px; border-left: 4px solid #667eea; box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-bottom: 1rem;">
            <h4>🇪🇺 Innovation Européenne</h4>
            <p><strong>Trust by Design</strong><br>
            IA explicable vs boîtes noires US</p>
        </div>
        """, unsafe_allow_html=True)
    
    # CTA principal
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 **Commencer Mon Exploration Gratuite**", type="primary"):
            st.success("✅ Redirection vers le test d'anxiété IA...")

def render_anxiety_test():
    """Test d'anxiété IA gratuit"""
    st.markdown("## 🧠 **Test Anxiété IA - Gratuit**")
    st.markdown("*Découvrez en 2 minutes si votre métier actuel résiste à l'IA*")
    
    with st.form("anxiety_test_form"):
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
            # Mock analysis
            import random
            score = random.uniform(0.2, 0.7)
            
            st.markdown("---")
            st.markdown("## 🎯 **Résultats de Votre Test**")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                # Gauge chart simple
                import plotly.graph_objects as go
                fig = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = score * 100,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "Score Anxiété IA"},
                    gauge = {
                        'axis': {'range': [None, 100]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [0, 30], 'color': "lightgreen"},
                            {'range': [30, 70], 'color': "yellow"},
                            {'range': [70, 100], 'color': "red"}
                        ],
                    }
                ))
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
            
            if score < 0.3:
                st.success(f"✅ Excellente nouvelle ! Votre métier **{current_job}** évolue positivement avec l'IA.")
            else:
                st.warning(f"⚠️ Attention - Votre métier **{current_job}** nécessite une adaptation IA.")

def render_career_exploration():
    """Exploration métier complète"""
    st.markdown("## 🔍 **Exploration Métier Approfondie**")
    st.info("🚧 **Fonctionnalité en développement** - Tests psychométriques et algorithme de matching")
    
    st.markdown("""
    ### 🎯 **Prochaines étapes à implémenter :**
    - Tests Big Five et RIASEC
    - Cartographie des compétences
    - Algorithme de matching métiers
    - Recommandations personnalisées
    """)

def render_ia_validation():
    """Validation IA des métiers"""
    st.markdown("## 🤖 **Validation IA Future-Proof**")
    
    job_to_analyze = st.text_input(
        "Métier à analyser",
        placeholder="Ex: Data Scientist, Coach, Chef de Projet..."
    )
    
    if st.button("🔍 **Analyser la Résistance IA**", type="primary") and job_to_analyze:
        # Mock analysis
        import random
        resistance_score = random.uniform(0.5, 0.9)
        
        st.markdown("---")
        st.markdown(f"## 🎯 **Analyse IA : {job_to_analyze}**")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Résistance IA", f"{resistance_score:.0%}")
        with col2:
            st.metric("Évolution", "Enhanced")
        with col3:
            st.metric("Timeline", "5-10 ans")
        
        st.success(f"💡 Excellente nouvelle ! Le métier de **{job_to_analyze}** évolue positivement avec l'IA.")
        
        # 🔥 PUBLIER ÉVÉNEMENT DANS DATA PIPELINE
        try:
            import asyncio
            from datetime import datetime
            
            # Obtenir user_id depuis session state ou générer un ID temporaire
            user_id = st.session_state.get('user_id', f"anonymous_{hash(st.session_state.get('session_id', 'default'))}")
            
            event_data = PhoenixEventData(
                event_type=PhoenixEventType.JOB_OFFER_ANALYZED,
                user_id=user_id,
                app_source="phoenix-aube",
                payload={
                    "job_title": job_to_analyze,
                    "resistance_score": resistance_score,
                    "evolution_type": "enhanced",
                    "timeline": "5-10 ans",
                    "analysis_time": datetime.now().isoformat(),
                    "recommendation": "positive"
                },
                metadata={
                    "analysis_method": "mock_validation",
                    "confidence": resistance_score,
                    "source_app": "phoenix-aube-streamlit"
                }
            )
            
            # Publier l'événement en mode non-bloquant
            try:
                asyncio.run(event_bridge.publish_event(event_data))
                st.info("✅ Analyse sauvegardée dans votre profil Phoenix")
            except Exception:
                pass  # Mode dégradé silencieux
                
        except Exception:
            pass  # Event publishing ne doit pas faire crasher l'interface

def render_ecosystem_links():
    """Liens vers l'écosystème Phoenix"""
    st.markdown("## 🔗 **Écosystème Phoenix**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 📄 Phoenix CV
        Créez un CV optimisé pour votre nouveau métier IA-resistant
        """)
        st.button("➡️ Phoenix CV", disabled=True)
    
    with col2:
        st.markdown("""
        ### ✉️ Phoenix Letters  
        Lettres de motivation personnalisées pour reconversion
        """)
        st.button("➡️ Phoenix Letters", disabled=True)
    
    with col3:
        st.markdown("""
        ### 🦋 Phoenix Rise
        Coaching IA pour accompagner votre transformation
        """)
        st.button("➡️ Phoenix Rise", disabled=True)

if __name__ == "__main__":
    main()