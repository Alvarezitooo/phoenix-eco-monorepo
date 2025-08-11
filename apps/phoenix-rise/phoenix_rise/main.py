import os
import sys
import asyncio
from datetime import datetime, date
import google.generativeai as genai
import streamlit as st

# Configuration de la page
st.set_page_config(
    page_title="🦋 Phoenix Rise - Dojo Mental Kaizen-Zazen",
    page_icon="🦋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Imports des services et UI
from .services.dojo_api_service import DojoApiService, KaizenEntry, ZazenSession
from .services.ai_coach_service import AICoachService
from .services.mock_db_service import MockDBService

# Import iris_core depuis la racine phoenix-rise
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from iris_core.interaction.renaissance_protocol import RenaissanceProtocol, RenaissanceState

# Configuration de l'API Gemini (optionnelle)
api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

# Initialisation des services
@st.cache_resource
def init_services():
    """Initialise tous les services Phoenix Rise"""
    dojo_service = DojoApiService()
    db_service = MockDBService()
    ai_service = AICoachService() if api_key else None
    renaissance = RenaissanceProtocol()
    return dojo_service, db_service, ai_service, renaissance


def render_research_action_banner():
    """🔬 Bannière de sensibilisation à la recherche-action Phoenix"""
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 1.5rem;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        ">
            <p style="margin: 0; font-size: 0.95rem; font-weight: 500;">
                🎓 <strong>Participez à une recherche-action sur l'impact de l'IA dans la reconversion professionnelle.</strong>
            </p>
            <p style="margin: 0.5rem 0 0 0; font-size: 0.85rem; opacity: 0.9; line-height: 1.4;">
                En utilisant Phoenix, vous contribuez anonymement à une étude sur l'IA éthique et la réinvention de soi. 
                Vos données (jamais nominatives) aideront à construire des outils plus justes et plus humains.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_dojo_mental_interface():
    """Interface principale du Dojo Mental Kaizen-Zazen"""
    
    # Header du Dojo Mental
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    ">
        <h1 style="margin: 0; font-size: 2.5rem; font-weight: 300;">🦋 Dojo Mental Phoenix</h1>
        <h3 style="margin: 0.5rem 0 0 0; font-weight: 400; opacity: 0.9;">Kaizen-Zazen • Renaissance Intérieure</h3>
        <p style="margin: 0.8rem 0 0 0; opacity: 0.8; font-style: italic;">
            "Dans la petite action quotidienne et la pleine conscience, naît la transformation"
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialisation des services
    dojo_service, db_service, ai_service, renaissance = init_services()
    
    # Navigation principale
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎯 Kaizen Quotidien", 
        "🧘 Zazen Méditation", 
        "🤖 Coach Iris", 
        "📊 Mon Évolution"
    ])
    
    with tab1:
        render_kaizen_tracker(dojo_service)
    
    with tab2:
        render_zazen_timer(dojo_service)
    
    with tab3:
        render_coach_iris(ai_service, renaissance)
    
    with tab4:
        render_evolution_dashboard(db_service)


def render_kaizen_tracker(dojo_service):
    """🎯 Interface Kaizen - Actions quotidiennes micro-progressives"""
    
    st.markdown("### 🎯 **Kaizen Quotidien - L'Art du Micro-Progrès**")
    st.markdown("*Une action infiniment petite aujourd'hui = une transformation infinie demain*")
    
    # Formulaire Kaizen
    with st.expander("✨ **Créer une nouvelle action Kaizen**", expanded=True):
        with st.form("kaizen_form"):
            st.markdown("**Quelle micro-action veux-tu accomplir aujourd'hui ?**")
            
            action_input = st.text_area(
                "Action Kaizen",
                placeholder="Ex: Lire 2 pages d'un livre, faire 5 pompes, écrire 1 ligne dans mon journal...",
                height=80,
                help="Plus c'est petit, plus c'est puissant ! L'idée est de créer une habitude durable."
            )
            
            col1, col2 = st.columns([3, 1])
            with col1:
                kaizen_date = st.date_input(
                    "Date", 
                    value=date.today(),
                    help="Pour quelle date planifies-tu cette action ?"
                )
            with col2:
                completed = st.checkbox("✅ Déjà accomplie ?")
            
            submitted = st.form_submit_button("🚀 **Ajouter au Dojo**", type="primary")
            
            if submitted and action_input.strip():
                # Création de l'entrée Kaizen
                user_id = st.session_state.get('user_id', 'demo_user_kaizen')
                kaizen = KaizenEntry(
                    user_id=user_id,
                    action=action_input.strip(),
                    date=kaizen_date,
                    completed=completed
                )
                
                # Simulation de l'ajout (en vrai ça irait vers l'API Dojo)
                with st.spinner("✨ Ajout au Dojo Mental..."):
                    try:
                        # Simulation réussie
                        st.success("🎉 **Action Kaizen ajoutée avec succès !**")
                        st.balloons()
                        
                        if not completed:
                            st.info("💡 **Rappel** : Même 1% d'effort est infiniment plus puissant que 0% !")
                        else:
                            st.success("🏆 **Bravo !** Tu viens de nourrir ta spirale de croissance !")
                            
                    except Exception as e:
                        st.error(f"❌ Erreur lors de l'ajout : {e}")
    
    # Liste des Kaizen récents (simulation)
    st.markdown("---")
    st.markdown("### 📋 **Mes Actions Kaizen Récentes**")
    
    # Simulation de données Kaizen
    kaizen_demo = [
        {"action": "5 minutes de lecture", "date": "Aujourd'hui", "completed": True},
        {"action": "Écrire 3 lignes dans mon journal", "date": "Hier", "completed": True},
        {"action": "1 verre d'eau au réveil", "date": "Avant-hier", "completed": False},
    ]
    
    for i, kaizen in enumerate(kaizen_demo):
        status = "✅" if kaizen["completed"] else "⏳"
        color = "#e8f5e8" if kaizen["completed"] else "#fff5e6"
        
        st.markdown(f"""
        <div style="
            background: {color};
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid {'#28a745' if kaizen['completed'] else '#ffc107'};
            margin-bottom: 0.5rem;
        ">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-weight: 500;">{status} {kaizen['action']}</span>
                <small style="color: #666;">{kaizen['date']}</small>
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_zazen_timer(dojo_service):
    """🧘 Interface Zazen - Sessions de méditation pleine conscience"""
    
    st.markdown("### 🧘 **Zazen - La Méditation de l'Instant Présent**")
    st.markdown("*Dans l'immobilité du corps, l'esprit trouve sa clarté*")
    
    # Configuration de la session
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### ⏱️ **Configuration de ta Session**")
        
        duration = st.selectbox(
            "Durée de méditation",
            [1, 3, 5, 10, 15, 20, 25, 30],
            index=2,
            help="Commence petit, même 1 minute compte !"
        )
        
        session_type = st.selectbox(
            "Type de session",
            [
                "🌬️ Respiration consciente",
                "🎯 Attention focalisée", 
                "❤️ Méditation compassion",
                "🌊 Pleine conscience libre"
            ]
        )
        
    with col2:
        st.markdown("#### 🎨 **Ambiance**")
        
        st.markdown("""
        <div style="
            background: linear-gradient(45deg, #f093fb 0%, #f5576c 100%);
            height: 120px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 2rem;
            margin-bottom: 1rem;
        ">
            🕯️ 🧘‍♀️ 🌸
        </div>
        """, unsafe_allow_html=True)
    
    # Timer principal
    st.markdown("---")
    
    if 'zazen_active' not in st.session_state:
        st.session_state.zazen_active = False
        st.session_state.zazen_start_time = None
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if not st.session_state.zazen_active:
            if st.button(f"🧘 **Commencer {duration} min de Zazen**", type="primary", use_container_width=True):
                st.session_state.zazen_active = True
                st.session_state.zazen_start_time = datetime.now()
                st.session_state.zazen_duration = duration
                st.rerun()
        else:
            # Calcul du temps écoulé
            elapsed = (datetime.now() - st.session_state.zazen_start_time).total_seconds()
            remaining = max(0, (st.session_state.zazen_duration * 60) - elapsed)
            
            if remaining > 0:
                minutes_remaining = int(remaining // 60)
                seconds_remaining = int(remaining % 60)
                
                st.markdown(f"""
                <div style="
                    text-align: center;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 2rem;
                    border-radius: 15px;
                    margin: 1rem 0;
                ">
                    <h2 style="margin: 0; font-size: 3rem; font-weight: 300;">
                        {minutes_remaining:02d}:{seconds_remaining:02d}
                    </h2>
                    <p style="margin: 0.5rem 0 0 0; opacity: 0.8;">
                        Respire... Tu es dans l'instant présent
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("⏸️ **Terminer la session**", use_container_width=True):
                    st.session_state.zazen_active = False
                    st.success("🙏 **Session Zazen terminée !** Tu as nourri ta présence.")
                    st.rerun()
                    
                # Auto-refresh pour le timer
                import time
                time.sleep(1)
                st.rerun()
                
            else:
                # Session terminée
                st.session_state.zazen_active = False
                st.success("🎉 **Session Zazen complétée !** Félicitations pour ce moment de présence.")
                st.balloons()
                
                # Enregistrement de la session
                user_id = st.session_state.get('user_id', 'demo_user_zazen')
                session = ZazenSession(
                    user_id=user_id,
                    timestamp=st.session_state.zazen_start_time,
                    duration=duration,
                    triggered_by="manual_start"
                )
                
                st.info("✨ Session enregistrée dans ton parcours Dojo Mental")


def render_coach_iris(ai_service, renaissance):
    """🤖 Coach IA Iris - Protocole Renaissance"""
    
    st.markdown("### 🤖 **Coach Iris - Protocole Renaissance**")
    st.markdown("*Votre compagnon IA pour la transformation intérieure*")
    
    if ai_service is None:
        st.warning("⚠️ **API Gemini non configurée** - Mode démonstration activé")
        st.markdown("*Pour activer le coaching IA, configurez votre clé API Gemini dans les variables d'environnement.*")
    
    # État du protocole Renaissance
    if 'renaissance_state' not in st.session_state:
        st.session_state.renaissance_state = RenaissanceState.ECOUTE_ACTIVE
        st.session_state.conversation_history = []
    
    # Interface de conversation
    st.markdown("#### 💬 **Conversation avec Iris**")
    
    # Affichage de l'historique
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.conversation_history:
            if message["role"] == "user":
                st.markdown(f"""
                <div style="
                    background: #e3f2fd;
                    padding: 1rem;
                    border-radius: 10px;
                    margin: 0.5rem 0;
                    margin-left: 2rem;
                    border-left: 4px solid #2196f3;
                ">
                    <strong>Vous :</strong> {message['content']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="
                    background: #f3e5f5;
                    padding: 1rem;
                    border-radius: 10px;
                    margin: 0.5rem 0;
                    margin-right: 2rem;
                    border-left: 4px solid #9c27b0;
                ">
                    <strong>🤖 Iris :</strong> {message['content']}
                </div>
                """, unsafe_allow_html=True)
    
    # Message initial d'Iris
    if not st.session_state.conversation_history:
        mock_eev = {"burnout_risk_score": 0.3, "mood_average_7d": 0.6, "confidence_trend": 0.1}
        iris_greeting = renaissance.process_interaction("", mock_eev)
        
        st.session_state.conversation_history.append({
            "role": "iris",
            "content": iris_greeting
        })
        st.rerun()
    
    # Input utilisateur
    user_input = st.text_input(
        "Votre message à Iris",
        placeholder="Partagez ce que vous ressentez...",
        key="iris_input"
    )
    
    if st.button("💌 **Envoyer à Iris**", type="primary") and user_input.strip():
        # Ajouter message utilisateur
        st.session_state.conversation_history.append({
            "role": "user", 
            "content": user_input.strip()
        })
        
        # Générer réponse Iris (simulation)
        mock_eev = {"burnout_risk_score": 0.4, "mood_average_7d": 0.5}
        iris_response = renaissance.process_interaction(user_input, mock_eev)
        
        st.session_state.conversation_history.append({
            "role": "iris",
            "content": iris_response
        })
        
        st.rerun()


def render_evolution_dashboard(db_service):
    """📊 Dashboard de progression et évolution"""
    
    st.markdown("### 📊 **Mon Évolution - Tableau de Bord Personnel**")
    st.markdown("*Visualisation de votre transformation jour après jour*")
    
    # Métriques clés
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "🎯 Actions Kaizen",
            "12",
            delta="3 cette semaine",
            help="Nombre total d'actions micro-progressives accomplies"
        )
    
    with col2:
        st.metric(
            "🧘 Sessions Zazen",
            "8",
            delta="2 cette semaine",
            help="Nombre de sessions de méditation complétées"
        )
    
    with col3:
        st.metric(
            "💪 Série Actuelle",
            "5 jours",
            delta="Record personnel !",
            help="Jours consécutifs avec au moins une action"
        )
    
    with col4:
        st.metric(
            "📈 Score Renaissance",
            "73%",
            delta="12% ce mois",
            help="Indice global de progression dans votre transformation"
        )
    
    # Graphique de progression (simulation)
    st.markdown("---")
    st.markdown("#### 📈 **Évolution de Votre Renaissance**")
    
    try:
        import plotly.graph_objects as go
        from datetime import datetime, timedelta
        
        # Données de simulation
        dates = [(datetime.now() - timedelta(days=x)).strftime("%d/%m") for x in range(14, 0, -1)]
        kaizen_data = [0, 1, 1, 2, 1, 3, 2, 4, 3, 2, 4, 5, 3, 6]
        zazen_data = [0, 0, 1, 1, 1, 2, 1, 2, 2, 1, 2, 3, 2, 2]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=kaizen_data,
            mode='lines+markers',
            name='🎯 Actions Kaizen',
            line=dict(color='#667eea', width=3),
            marker=dict(size=8)
        ))
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=zazen_data,
            mode='lines+markers', 
            name='🧘 Sessions Zazen',
            line=dict(color='#764ba2', width=3),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title="Progression des 14 derniers jours",
            xaxis_title="Date",
            yaxis_title="Nombre d'actions",
            hovermode='x unified',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except ImportError:
        st.info("📊 Graphique de progression disponible avec Plotly installé")
    
    # Insights personnalisés
    st.markdown("---")
    st.markdown("#### 💡 **Insights Personnalisés**")
    
    insights = [
        "🔥 **Excellent !** Votre régularité Kaizen s'améliore chaque semaine",
        "🧘 **Suggestion :** Essayez d'associer une session Zazen après chaque action Kaizen importante",
        "⭐ **Célébration :** Vous avez maintenu votre pratique 5 jours consécutifs - c'est remarquable !",
        "🎯 **Défi :** Prêt(e) pour passer à 2 actions Kaizen par jour cette semaine ?"
    ]
    
    for insight in insights:
        st.success(insight)


def main():
    """Point d'entrée principal - Dojo Mental Phoenix Rise"""
    
    # 🔬 BANNIÈRE RECHERCHE-ACTION PHOENIX
    render_research_action_banner()
    
    # Interface principale du Dojo Mental
    render_dojo_mental_interface()
    
    # Footer Phoenix
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 1rem; background: #f8f9fa; border-radius: 10px; margin-top: 2rem;">
        <p style="margin: 0; color: #666; font-size: 0.9rem;">
            🦋 **Phoenix Rise - Dojo Mental Kaizen-Zazen** | 
            💻 **Développé par Claude Phoenix DevSecOps Guardian** | 
            🔒 **Sécurité & RGPD by design**
        </p>
        <p style="margin: 0.5rem 0 0 0; color: #999; font-size: 0.8rem; font-style: italic;">
            "La transformation commence par un souffle conscient et une action infinitesimale"
        </p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()