import base64
import hashlib
import json
import secrets
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import plotly.graph_objects as go
import streamlit as st

# ==============================================================================
# 1. ARCHITECTURE & CONFIGURATION
# ==============================================================================

st.set_page_config(
    page_title="Phoenix Rise - Coach IA Reconversion",
    page_icon="🦋",
    layout="wide",
    initial_sidebar_state="expanded",
)


def load_css():
    """Charge le CSS professionnel pour une interface soignée."""
    st.markdown(
        """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
    }
    .main {
        background: #f0f2f6; /* Fond clair et professionnel */
    }
    .phoenix-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 12px;
        margin-bottom: 2rem;
    }
    .phoenix-title {
        font-size: 2.8rem;
        font-weight: 700;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .phoenix-subtitle {
        font-size: 1.3rem;
        font-weight: 300;
        opacity: 0.9;
    }
    .stButton > button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
        border: 1px solid #667eea;
        background-color: #667eea;
        color: white;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4) !important;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-top: 4px solid #764ba2;
        text-align: center;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )


# ==============================================================================
# 2. MODÈLES DE DONNÉES (MODELS)
# ==============================================================================


@dataclass
class MoodEntry:
    date: str
    mood_score: int
    energy_level: int
    confidence_level: int
    notes: str
    tags: List[str]


@dataclass
class JournalEntry:
    date: str
    timestamp: str
    title: str
    content: str
    mood_before: int
    mood_after: int
    ai_encouragement: str


@dataclass
class CoachingSession:
    session_id: str
    date: str
    sector: str
    difficulty_level: str
    questions_asked: List[Dict]
    user_responses: List[str]
    ai_feedback: List[Dict]
    overall_score: float


# ==============================================================================
# 3. SERVICES (LOGIQUE MÉTIER)
# ==============================================================================


class SessionStateStorage:
    """
    Remplacement sécurisé de SecureLocalStorage.
    Utilise st.session_state, la méthode officielle de Streamlit pour la persistance
    des données au sein d'une session utilisateur. C'est sécurisé et scalable.
    """

    def __init__(self, user_id: str):
        self.user_key_prefix = (
            f"phoenix_rise_{hashlib.sha256(user_id.encode()).hexdigest()[:10]}"
        )

    def _get_key(self, data_type: str) -> str:
        return f"{self.user_key_prefix}_{data_type}"

    def save_data(self, data_type: str, data: Any):
        key = self._get_key(data_type)
        serializable_data = (
            [asdict(item) for item in data]
            if isinstance(data, list) and data and hasattr(data[0], "__dict__")
            else data
        )
        st.session_state[key] = serializable_data

    def load_data(self, data_type: str, default_value: Any = None) -> Any:
        key = self._get_key(data_type)
        return st.session_state.get(
            key, default_value if default_value is not None else []
        )


class CoachingService:
    """
    Service gérant la logique d'IA.
    Préparé pour des appels réels à l'API Gemini.
    """

    @staticmethod
    def generate_ai_encouragement(
        mood_score: int, confidence_score: int, notes: str
    ) -> str:
        # PRÊT POUR L'IA : Ce prompt est conçu pour l'API Gemini
        prompt = f"""
        Tu es Phoenix, un coach IA bienveillant. Un utilisateur en reconversion partage son état :
        - Humeur : {mood_score}/10, Confiance : {confidence_score}/10
        - Notes : "{notes}"
        Génère une phrase d'encouragement personnalisée, positive et inspirante.
        """
        # --- Simulation d'appel API Gemini ---
        if mood_score >= 7:
            return "🌟 Quelle énergie ! Tu es sur une voie royale. Ta confiance est palpable et va convaincre les recruteurs."
        elif mood_score >= 4:
            return "💪 Chaque pas, même les plus petits, te rapproche de ton but. C'est normal d'avoir des doutes, mais ta persévérance est ta plus grande force."
        else:
            return "🫂 C'est dans les moments de doute que l'on puise sa force de demain. Accroche-toi, tu es en train de construire une histoire de résilience incroyable."

    @staticmethod
    def generate_interview_feedback(
        response: str, question_type: str
    ) -> Dict[str, Any]:
        # PRÊT POUR L'IA : Ce prompt est conçu pour l'API Gemini
        prompt = f"""
        Analyse cette réponse à une question d'entretien de type '{question_type}' : "{response}".
        Évalue la structure, la clarté et la pertinence. Fournis un score sur 10,
        un point fort principal et un axe d'amélioration prioritaire.
        Format de réponse JSON: {{"score": X, "strength": "...", "improvement": "..."}}
        """
        # --- Simulation d'appel API Gemini ---
        score = round(min(10, len(response.split()) / 5 + secrets.randint(1, 3)), 1)
        return {
            "score": score,
            "strength": "Excellente structure dans ta réponse, tu as bien mis en avant une compétence clé.",
            "improvement": "Pour encore plus d'impact, essaie d'ajouter un résultat chiffré pour illustrer ton succès.",
        }


class QuestionBank:
    """Conserve la banque de questions pour les entretiens."""

    QUESTIONS = {
        "cybersécurité": [
            {
                "question": "Comment votre expérience en EHPAD vous a-t-elle préparé à la gestion de crise en cybersécurité ?",
                "type": "reconversion",
            }
        ],
        "développement": [
            {
                "question": "Décrivez un projet où vous avez dû apprendre rapidement une nouvelle compétence, comme vous le faites pour le code.",
                "type": "apprentissage",
            }
        ],
        "marketing": [
            {
                "question": "Comment votre capacité d'empathie, développée en tant qu'aide-soignant, peut-elle être un atout pour comprendre les besoins d'un client ?",
                "type": "reconversion",
            }
        ],
    }

    @classmethod
    def get_random_question(cls, sector: str) -> Dict:
        return secrets.choice(cls.QUESTIONS.get(sector, cls.QUESTIONS["cybersécurité"]))


class MoodJournalManager:
    """Gère toute la logique du journal et des métriques d'humeur."""

    def __init__(self, storage: SessionStateStorage, coach_service: CoachingService):
        self.storage = storage
        self.coach_service = coach_service

    def add_mood_entry(
        self, mood_score: int, energy_level: int, confidence_level: int, notes: str
    ) -> str:
        entry = MoodEntry(
            date=datetime.now().strftime("%Y-%m-%d"),
            mood_score=mood_score,
            energy_level=energy_level,
            confidence_level=confidence_level,
            notes=notes,
            tags=[],
        )
        mood_entries = self.storage.load_data("mood_entries", [])
        mood_entries.append(entry)
        self.storage.save_data("mood_entries", mood_entries)
        return self.coach_service.generate_ai_encouragement(
            mood_score, confidence_level, notes
        )

    def get_mood_analytics(self) -> Optional[Dict]:
        mood_entries_raw = self.storage.load_data("mood_entries", [])
        if not mood_entries_raw:
            return None

        mood_entries = [MoodEntry(**e) for e in mood_entries_raw]
        avg_mood = sum(e.mood_score for e in mood_entries) / len(mood_entries)
        avg_confidence = sum(e.confidence_level for e in mood_entries) / len(
            mood_entries
        )

        return {
            "avg_mood": round(avg_mood, 1),
            "avg_confidence": round(avg_confidence, 1),
            "trend": (
                "📈"
                if len(mood_entries) > 1
                and mood_entries[-1].mood_score > mood_entries[0].mood_score
                else "➡️"
            ),
        }


# ==============================================================================
# 4. INTERFACE UTILISATEUR (COMPOSANTS UI)
# ==============================================================================


def render_header():
    st.markdown(
        """
    <div class="phoenix-header">
        <div class="phoenix-title">🦋 Phoenix Rise</div>
        <div class="phoenix-subtitle">Votre coach IA personnel pour réussir votre reconversion</div>
    </div>
    """,
        unsafe_allow_html=True,
    )


def render_mood_tracker(journal_manager: MoodJournalManager):
    st.subheader("📊 Comment vous sentez-vous aujourd'hui ?")
    with st.container(border=True):
        col1, col2, col3 = st.columns(3)
        mood = col1.slider("😊 Humeur", 1, 10, 5)
        energy = col2.slider("⚡ Énergie", 1, 10, 5)
        confidence = col3.slider("💪 Confiance", 1, 10, 5)
        notes = st.text_area(
            "💭 Notes (ex: 'J'ai postulé à 3 offres', 'Entretien demain')", height=100
        )

        if st.button("Enregistrer et recevoir mon encouragement"):
            encouragement = journal_manager.add_mood_entry(
                mood, energy, confidence, notes
            )
            st.toast(f"✅ Enregistré ! L'IA vous dit :", icon="🦋")
            st.success(f"**Phoenix dit :** {encouragement}")


def render_dashboard(journal_manager: MoodJournalManager):
    st.subheader("📈 Votre Tableau de Bord")
    analytics = journal_manager.get_mood_analytics()

    if not analytics:
        st.info("Enregistrez votre humeur pour voir apparaître votre tableau de bord.")
        return

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f"<div class='metric-card'><h4>Humeur Moyenne</h4><h2>{analytics['avg_mood']}/10</h2></div>",
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"<div class='metric-card'><h4>Confiance Moyenne</h4><h2>{analytics['avg_confidence']}/10</h2></div>",
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"<div class='metric-card'><h4>Tendance</h4><h2>{analytics['trend']}</h2></div>",
            unsafe_allow_html=True,
        )


def render_coaching_interface(coach_service: CoachingService):
    st.subheader("🎯 Coach d'Entretien IA")
    with st.container(border=True):
        sector = st.selectbox(
            "Choisissez le secteur de l'entretien :",
            ["cybersécurité", "développement", "marketing"],
        )

        if st.button("🎙️ Démarrer une session de coaching"):
            st.session_state.current_question = QuestionBank.get_random_question(sector)

        if "current_question" in st.session_state:
            question_data = st.session_state.current_question
            st.info(f"**Question :** {question_data['question']}")

            with st.form("response_form"):
                response = st.text_area("Votre réponse :", height=150)
                submitted = st.form_submit_button("Obtenir le feedback de l'IA")

                if submitted and response:
                    feedback = coach_service.generate_interview_feedback(
                        response, question_data["type"]
                    )
                    st.markdown("---")
                    st.success(f"**Point Fort :** {feedback['strength']}")
                    st.warning(f"**Axe d'amélioration :** {feedback['improvement']}")
                    st.progress(
                        feedback["score"] / 10,
                        text=f"Score de la réponse : {feedback['score']}/10",
                    )

                    if st.button("Question suivante"):
                        del st.session_state.current_question
                        st.rerun()


# ==============================================================================
# 5. APPLICATION PRINCIPALE (MAIN)
# ==============================================================================


def main():
    load_css()
    render_header()

    # --- Simulation de Connexion Utilisateur ---
    st.sidebar.title("Connexion")
    user_id = st.sidebar.text_input(
        "Entrez votre email pour commencer", "matthieu.alvarez@example.com"
    )

    if not user_id:
        st.warning("Veuillez entrer un identifiant pour utiliser l'application.")
        st.stop()

    st.sidebar.success(f"Connecté en tant que **{user_id}**")

    # --- Initialisation des Services avec l'ID utilisateur ---
    # C'est ici que la magie opère : chaque service est lié à la session de l'utilisateur.
    storage = SessionStateStorage(user_id)
    coach_service = CoachingService()
    journal_manager = MoodJournalManager(storage, coach_service)

    # --- Navigation par Onglets ---
    tab1, tab2, tab3 = st.tabs(
        [
            "**📊 Mon Suivi Quotidien**",
            "**🎯 Coaching Entretien**",
            "**📖 Mon Journal**",
        ]
    )

    with tab1:
        render_mood_tracker(journal_manager)
        st.markdown("---")
        render_dashboard(journal_manager)

    with tab2:
        render_coaching_interface(coach_service)

    with tab3:
        st.info("Le module de journal détaillé est en cours de développement.")
        st.image(
            "https://img.freepik.com/free-vector/man-thinking-with-light-bulb-cartoon-icon-illustration_138676-2794.jpg",
            caption="Bientôt disponible !",
        )


if __name__ == "__main__":
    main()
