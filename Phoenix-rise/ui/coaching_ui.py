
Interface de coaching d'entretien avec IA.


import streamlit as st
import secrets
from services.ai_coach_service import AICoachService
from utils.constants import QUESTION_BANK

def render_coaching_ui(ai_service: AICoachService):
    """
    Interface complète de coaching d'entretien.
    
    Args:
        ai_service: Service de coaching IA
    """
    st.header("🎯 Coach d'Entretien IA")

    with st.container(border=True):
        st.info("💡 Entraînez-vous aux questions d'entretien et recevez un feedback IA personnalisé.")

        # Gestion de l'état de session
        if 'coaching_session_active' not in st.session_state:
            st.session_state.coaching_session_active = False

        if not st.session_state.coaching_session_active:
            _render_session_setup()
        else:
            _render_active_session(ai_service)

def _render_session_setup():
    """Interface de configuration d'une nouvelle session."""
    st.subheader("🚀 Nouvelle Session de Coaching")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        sector = st.selectbox(
            "Choisissez votre secteur d'entretien :",
            list(QUESTION_BANK.keys()),
            format_func=lambda x: x.title(),
            help="Sélectionnez le domaine pour des questions ciblées"
        )
    
    with col2:
        if st.button("🎯 Commencer", type="primary", use_container_width=True):
            # Initialisation de la session
            st.session_state.coaching_session_active = True
            st.session_state.coaching_sector = sector
            st.session_state.current_question = secrets.choice(QUESTION_BANK[sector])
            st.session_state.question_count = 1
            st.rerun()

def _render_active_session(ai_service: AICoachService):
    """Interface de session active."""
    sector = st.session_state.get('coaching_sector', 'cybersécurité')
    question = st.session_state.get('current_question', 'Question non définie')
    question_count = st.session_state.get('question_count', 1)
    
    # En-tête de session
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader(f"🎯 Session {sector.title()} - Question #{question_count}")
    with col2:
        if st.button("⏹️ Terminer", type="secondary"):
            _reset_coaching_session()
            st.success("🎉 Session terminée ! Excellent travail.")
            st.rerun()
    
    # Affichage de la question
    st.markdown("#### 💭 Question de l'IA :")
    st.info(f"*{question}*")
    
    # Formulaire de réponse
    with st.form("coaching_response_form", clear_on_submit=False):
        response = st.text_area(
            "✍️ Votre réponse :",
            height=200,
            placeholder="Prenez le temps de structurer votre réponse comme en entretien réel...",
            help="Conseil : Utilisez la méthode STAR (Situation, Tâche, Action, Résultat)"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("🔍 Analyser ma réponse", type="primary")
        with col2:
            next_question = st.form_submit_button("🔄 Question suivante")

        # Traitement des actions
        if submitted and response.strip():
            _process_response_feedback(response, sector, ai_service)
        
        if next_question:
            _load_next_question(sector)

def _process_response_feedback(response: str, sector: str, ai_service: AICoachService):
    """Traite la réponse et affiche le feedback IA."""
    with st.spinner("🧠 Phoenix analyse votre réponse..."):
        feedback = ai_service.generate_interview_feedback(
            cv_summary="Candidat en reconversion", 
            job_context=f"Poste en {sector}", 
            question=st.session_state.get('current_question', ''), 
            user_response=response
        )
        
        st.markdown("#### 📊 Feedback de Phoenix")
        
        # Affichage du score avec barre de progression
        col1, col2 = st.columns([1, 3])
        with col1:
            st.metric("Score", f"{feedback['score']}/10")
        with col2:
            st.progress(feedback['score'] / 10)
        
        # Points forts et améliorations
        col1, col2 = st.columns(2)
        with col1:
            st.success(f"✅ **Point Fort**\n{feedback['strength']}")
        with col2:
            st.warning(f"💡 **À Améliorer**\n{feedback['improvement']}")

def _load_next_question(sector: str):
    """Charge une nouvelle question aléatoire."""
    st.session_state.current_question = secrets.choice(QUESTION_BANK[sector])
    st.session_state.question_count = st.session_state.get('question_count', 1) + 1
    st.rerun()

def _reset_coaching_session():
    """Réinitialise l'état de la session de coaching."""
    keys_to_reset = [
        'coaching_session_active', 
        'current_question', 
        'coaching_sector', 
        'question_count'
    ]
    for key in keys_to_reset:
        if key in st.session_state:
            del st.session_state[key]

