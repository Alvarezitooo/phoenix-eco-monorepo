# 🦋 Phoenix Rise - Guide Architecture Complète pour Gemini CLI

> **Mission :** Construire une application Streamlit de coaching IA pour reconversions professionnelles avec architecture professionnelle modulaire.

---

## 📋 **ÉTAPE 0 : PRÉPARATION DE L'ENVIRONNEMENT**

### Structure de Dossiers à Créer

```
phoenix-rise/
├── 📄 rise_app.py                 # Point d'entrée principal
├── 📄 .env                        # Variables d'environnement (secrets)
├── 📄 requirements.txt            # Dépendances Python
├── 📄 README.md                   # Documentation projet
│
├── 📁 models/                     # Modèles de données
│   ├── __init__.py
│   ├── user.py                    # Modèle utilisateur
│   └── journal.py                 # Modèles journal/humeur
│
├── 📁 services/                   # Logique métier
│   ├── __init__.py
│   ├── auth_service.py            # Authentification Supabase
│   ├── db_service.py              # Base de données
│   └── ai_coach_service.py        # Service IA Gemini
│
├── 📁 ui/                         # Composants interface
│   ├── __init__.py
│   ├── journal_ui.py              # Interface saisie humeur
│   ├── dashboard_ui.py            # Tableaux de bord
│   └── coaching_ui.py             # Interface coaching
│
└── 📁 utils/                      # Utilitaires
    ├── __init__.py
    └── constants.py               # Constantes application
```

### Commandes d'Initialisation

```bash
# Créer le projet
mkdir phoenix-rise && cd phoenix-rise

# Créer l'environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate  # Windows

# Créer la structure de dossiers
mkdir models services ui utils
touch models/__init__.py services/__init__.py ui/__init__.py utils/__init__.py
```

---

## 📄 **ÉTAPE 1 : FICHIERS DE CONFIGURATION**

### `requirements.txt`
```txt
streamlit>=1.28.0
python-dotenv>=1.0.0
supabase>=1.0.3
google-generativeai>=0.3.0
plotly>=5.17.0
pandas>=2.1.0
```

### `.env` (À remplir avec tes clés)
```env
# Clés Supabase (depuis ton dashboard Supabase)
SUPABASE_URL=https://YOUR_PROJECT_ID.supabase.co
SUPABASE_KEY=YOUR_PROJECT_ANON_KEY

# Clé Google Gemini (depuis Google AI Studio)
GOOGLE_API_KEY=YOUR_GOOGLE_API_KEY
```

### `README.md`
```markdown
# 🦋 Phoenix Rise - Coach IA Reconversion

Application Streamlit de coaching IA pour accompagner les reconversions professionnelles.

## Setup Rapide
1. Cloner le projet
2. `pip install -r requirements.txt`
3. Configurer `.env` avec tes clés API
4. `streamlit run rise_app.py`

## Stack Technique
- **Frontend:** Streamlit
- **Backend:** Supabase (PostgreSQL + Auth)
- **IA:** Google Gemini 1.5 Flash
- **Déploiement:** Streamlit Cloud

## Architecture
- `models/` : Structures de données
- `services/` : Logique métier et APIs
- `ui/` : Composants interface utilisateur
- `utils/` : Utilitaires et constantes
```

---

## 📊 **ÉTAPE 2 : MODÈLES DE DONNÉES**

### `models/user.py`
```python
"""
Modèle de données utilisateur pour Phoenix Rise.
Représente un utilisateur authentifié via Supabase.
"""

from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    """Modèle utilisateur simplifié."""
    id: str
    email: Optional[str] = None
    user_metadata: Optional[dict] = None
    
    def get_display_name(self) -> str:
        """Retourne le nom d'affichage (partie avant @ de l'email)."""
        if self.email:
            return self.email.split('@')[0]
        return "Utilisateur"
```

### `models/journal.py`
```python
"""
Modèles de données pour le journal d'humeur et les sessions de coaching.
"""

from dataclasses import dataclass
from typing import List, Dict
from datetime import datetime

@dataclass
class MoodEntry:
    """Entrée d'humeur quotidienne."""
    id: int
    user_id: str
    created_at: str
    mood_score: int          # 1-10
    energy_level: int        # 1-10
    confidence_level: int    # 1-10
    notes: str
    tags: List[str]

@dataclass
class JournalEntry:
    """Entrée de journal avec encouragement IA."""
    id: int
    user_id: str
    created_at: str
    title: str
    content: str
    mood_before: int
    mood_after: int
    ai_encouragement: str

@dataclass
class CoachingSession:
    """Session d'entraînement aux entretiens."""
    id: str
    user_id: str
    created_at: str
    sector: str                    # cybersécurité, développement, etc.
    question: str
    user_response: str
    ai_feedback: Dict
    score: float
```

---

## 🔧 **ÉTAPE 3 : SERVICES (LOGIQUE MÉTIER)**

### `services/auth_service.py`
```python
"""
Service d'authentification utilisant Supabase.
Gère connexion, inscription, déconnexion.
"""

import os
import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
from models.user import User

load_dotenv()

class AuthService:
    """Service d'authentification Supabase."""
    
    def __init__(self):
        """Initialise le client Supabase."""
        url: str = os.environ.get("SUPABASE_URL")
        key: str = os.environ.get("SUPABASE_KEY")
        
        if not url or not key:
            raise ValueError("Variables SUPABASE_URL et SUPABASE_KEY requises dans .env")
        
        self.client: Client = create_client(url, key)

    def sign_in(self, email: str, password: str) -> tuple[bool, str | None]:
        """
        Connecte un utilisateur existant.
        
        Returns:
            (success: bool, error_message: str | None)
        """
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email, 
                "password": password
            })
            
            if response.user:
                st.session_state['user'] = User(
                    id=response.user.id, 
                    email=response.user.email
                )
                return True, None
            else:
                return False, "Échec de connexion"
                
        except Exception as e:
            return False, f"Erreur de connexion : {str(e)}"

    def sign_up(self, email: str, password: str) -> tuple[bool, str | None]:
        """
        Inscrit un nouvel utilisateur.
        
        Returns:
            (success: bool, error_message: str | None)
        """
        try:
            response = self.client.auth.sign_up({
                "email": email, 
                "password": password
            })
            
            if response.user:
                st.session_state['user'] = User(
                    id=response.user.id, 
                    email=response.user.email
                )
                return True, None
            else:
                return False, "Échec d'inscription"
                
        except Exception as e:
            return False, f"Erreur d'inscription : {str(e)}"

    def sign_out(self) -> bool:
        """Déconnecte l'utilisateur actuel."""
        if 'user' in st.session_state:
            del st.session_state['user']
        return True

    def get_current_user(self) -> User | None:
        """Retourne l'utilisateur actuellement connecté."""
        return st.session_state.get('user')
```

### `services/db_service.py`
```python
"""
Service de base de données pour Phoenix Rise.
Gère toutes les interactions avec Supabase PostgreSQL.
"""

import streamlit as st
from supabase import Client
from typing import List, Dict
from datetime import timedelta

class DBService:
    """Service de gestion des données utilisateur."""
    
    def __init__(self, client: Client):
        """Initialise avec le client Supabase."""
        self.client = client

    @st.cache_data(ttl=timedelta(minutes=5))
    def get_mood_entries(_user_id: str) -> List[Dict]:
        """
        Récupère les entrées d'humeur de l'utilisateur (avec cache).
        
        Args:
            _user_id: ID de l'utilisateur
            
        Returns:
            Liste des entrées d'humeur
        """
        try:
            # Récupération via session_state pour éviter les problèmes de cache
            db_client = st.session_state.get('db_client')
            if not db_client:
                return []
            
            response = db_client.table('mood_entries').select("*").eq(
                'user_id', _user_id
            ).order('created_at', desc=True).limit(30).execute()
            
            return response.data or []
            
        except Exception as e:
            st.error(f"Erreur de récupération des données : {e}")
            return []

    def add_mood_entry(self, user_id: str, mood: int, energy: int, confidence: int, notes: str) -> Dict:
        """
        Ajoute une nouvelle entrée d'humeur.
        
        Args:
            user_id: ID de l'utilisateur
            mood: Score d'humeur (1-10)
            energy: Niveau d'énergie (1-10)
            confidence: Niveau de confiance (1-10)
            notes: Notes optionnelles
            
        Returns:
            Dictionnaire avec success et data/error
        """
        try:
            response = self.client.table('mood_entries').insert({
                "user_id": user_id,
                "mood_score": mood,
                "energy_level": energy,
                "confidence_level": confidence,
                "notes": notes or ""
            }).execute()
            
            # Invalidation du cache après écriture
            self.get_mood_entries.clear()
            
            return {
                "success": True, 
                "data": response.data[0] if response.data else None
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_user_stats(self, user_id: str) -> Dict:
        """
        Calcule les statistiques utilisateur.
        
        Returns:
            Dictionnaire avec moyennes et tendances
        """
        entries = self.get_mood_entries(user_id)
        
        if not entries:
            return {"total_entries": 0}
        
        mood_scores = [entry['mood_score'] for entry in entries]
        confidence_scores = [entry['confidence_level'] for entry in entries]
        
        return {
            "total_entries": len(entries),
            "avg_mood": round(sum(mood_scores) / len(mood_scores), 1),
            "avg_confidence": round(sum(confidence_scores) / len(confidence_scores), 1),
            "trend": "📈" if len(entries) > 1 and mood_scores[0] > mood_scores[-1] else "➡️"
        }
```

### `services/ai_coach_service.py`
```python
"""
Service de coaching IA utilisant Google Gemini.
Génère encouragements et feedback d'entretiens.
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv
from typing import Dict

load_dotenv()

class AICoachService:
    """Service de coaching IA avec Google Gemini."""
    
    def __init__(self):
        """Initialise le modèle Gemini."""
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY requis dans .env")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def generate_encouragement(self, mood: int, confidence: int, notes: str) -> str:
        """
        Génère un encouragement personnalisé basé sur l'état de l'utilisateur.
        
        Args:
            mood: Score d'humeur (1-10)
            confidence: Score de confiance (1-10)
            notes: Notes de l'utilisateur
            
        Returns:
            Message d'encouragement personnalisé
        """
        prompt = f"""
        Tu es Phoenix, un coach IA bienveillant spécialisé dans l'accompagnement 
        des reconversions professionnelles.
        
        Un utilisateur partage son état aujourd'hui :
        - Humeur : {mood}/10
        - Confiance : {confidence}/10
        - Notes : "{notes}"
        
        Génère un encouragement personnalisé (2-3 phrases max) qui :
        - Soit authentiquement bienveillant (pas générique)
        - Prenne en compte son état émotionnel
        - L'encourage dans sa reconversion
        - Reste professionnel mais chaleureux
        
        Commence par un emoji approprié.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            # Fallback intelligent basé sur les scores
            return self._generate_fallback_encouragement(mood, confidence)

    def _generate_fallback_encouragement(self, mood: int, confidence: int) -> str:
        """Fallback d'encouragement si l'IA n'est pas disponible."""
        if mood >= 7 and confidence >= 7:
            return "🌟 Quelle énergie ! Tu rayonnes de confiance. Les recruteurs vont le sentir."
        elif mood >= 5 and confidence >= 5:
            return "💪 Tu progresses bien. Chaque jour te rapproche de ton objectif de reconversion."
        else:
            return "🫂 Les doutes font partie du chemin. Ta persévérance est ta plus grande force."

    def generate_interview_feedback(self, response: str, question_type: str) -> Dict:
        """
        Génère un feedback sur une réponse d'entretien.
        
        Args:
            response: Réponse de l'utilisateur
            question_type: Type de question (reconversion, technique, etc.)
            
        Returns:
            Dictionnaire avec score, point fort et amélioration
        """
        prompt = f"""
        Tu es Phoenix, expert en coaching d'entretiens pour reconversions.
        
        Analyse cette réponse à une question de type "{question_type}" :
        "{response}"
        
        Fournis un feedback structuré :
        1. Score sur 10 (considère structure, clarté, pertinence)
        2. Principal point fort (1 phrase)
        3. Axe d'amélioration prioritaire (1 phrase)
        
        Ton ton doit être encourageant mais constructif.
        """
        
        try:
            gemini_response = self.model.generate_content(prompt)
            # Parse la réponse Gemini (à implémenter selon le format retourné)
            return self._parse_feedback_response(gemini_response.text)
        except Exception as e:
            # Fallback basé sur des heuristiques simples
            return self._generate_fallback_feedback(response)

    def _parse_feedback_response(self, text: str) -> Dict:
        """Parse la réponse de Gemini en feedback structuré."""
        # Implémentation de parsing à faire selon le format Gemini
        return {
            "score": 7.5,
            "strength": "Bonne structure de réponse",
            "improvement": "Ajouter des exemples concrets"
        }

    def _generate_fallback_feedback(self, response: str) -> Dict:
        """Feedback de fallback basé sur des heuristiques."""
        word_count = len(response.split())
        score = min(9.0, max(4.0, word_count / 15 + 5.0))
        
        return {
            "score": round(score, 1),
            "strength": "Réponse bien structurée avec de bons détails.",
            "improvement": "Pensez à quantifier vos résultats avec des chiffres."
        }
```

---

## 🎨 **ÉTAPE 4 : COMPOSANTS UI**

### `utils/constants.py`
```python
"""
Constantes et données statiques de Phoenix Rise.
"""

# Banque de questions d'entretien par secteur
QUESTION_BANK = {
    "cybersécurité": [
        "Comment votre expérience passée vous a-t-elle préparé à la rigueur exigée en cybersécurité ?",
        "Décrivez une situation complexe que vous avez gérée et vos étapes de résolution.",
        "Quelle est la plus grande menace cyber actuelle et comment restez-vous informé ?",
        "Comment expliqueriez-vous l'importance de la cybersécurité à un dirigeant non-technique ?"
    ],
    "développement": [
        "Qu'est-ce qui vous a poussé à devenir développeur ?",
        "Parlez-moi d'un projet qui vous a particulièrement appris quelque chose.",
        "Comment abordez-vous un problème de code jamais rencontré ?",
        "Comment gérez-vous les critiques de code et les demandes de modification ?"
    ],
    "marketing": [
        "Comment votre empathie peut-elle comprendre les besoins clients ?",
        "Quelle campagne récente avez-vous trouvée efficace et pourquoi ?",
        "Comment mesurez-vous le succès de vos actions marketing ?",
        "Comment adaptez-vous votre message selon les différents canaux ?"
    ]
}

# Thèmes de couleur Phoenix
PHOENIX_COLORS = {
    "primary": "#667eea",
    "secondary": "#764ba2",
    "success": "#10b981",
    "warning": "#f59e0b",
    "error": "#ef4444",
    "background": "#f8fafc"
}
```

### `ui/journal_ui.py`
```python
"""
Interface de saisie du journal d'humeur quotidien.
"""

import streamlit as st
import pandas as pd
from services.db_service import DBService
from services.ai_coach_service import AICoachService
from typing import List, Dict

def render_journal_ui(user_id: str, db_service: DBService, ai_service: AICoachService):
    """
    Interface complète du journal : saisie + historique.
    
    Args:
        user_id: ID de l'utilisateur connecté
        db_service: Service de base de données
        ai_service: Service de coaching IA
    """
    st.header("🖋️ Mon Suivi Quotidien")

    # Section de saisie
    _render_mood_input_section(user_id, db_service, ai_service)
    
    st.markdown("---")
    
    # Section historique
    _render_mood_history_section(user_id, db_service)

def _render_mood_input_section(user_id: str, db_service: DBService, ai_service: AICoachService):
    """Section de saisie de l'humeur du jour."""
    st.subheader("📊 Comment vous sentez-vous aujourd'hui ?")
    
    with st.container(border=True):
        # Sliders d'évaluation
        col1, col2 = st.columns(2)
        
        with col1:
            mood = st.slider(
                "😊 Humeur générale", 
                min_value=1, max_value=10, value=7,
                help="1 = Très difficile, 10 = Excellent moral"
            )
            
        with col2:
            confidence = st.slider(
                "💪 Confiance en ma reconversion", 
                min_value=1, max_value=10, value=7,
                help="1 = Plein de doutes, 10 = Très confiant"
            )
        
        # Zone de notes
        notes = st.text_area(
            "💭 Notes du jour (optionnel)",
            placeholder="Ex: J'ai postulé à 3 offres, entretien prévu demain, cours terminé...",
            height=100
        )
        
        # Bouton d'enregistrement
        if st.button("✨ Enregistrer et recevoir mon encouragement IA", type="primary"):
            with st.spinner("Phoenix analyse votre journée..."):
                # Sauvegarde en base
                result = db_service.add_mood_entry(user_id, mood, 0, confidence, notes)
                
                if result.get("success"):
                    # Génération de l'encouragement IA
                    encouragement = ai_service.generate_encouragement(mood, confidence, notes)
                    
                    st.success("✅ Journée enregistrée avec succès !")
                    st.info(f"**🦋 Phoenix vous dit :** {encouragement}")
                else:
                    st.error(f"❌ Erreur lors de la sauvegarde : {result.get('error')}")

def _render_mood_history_section(user_id: str, db_service: DBService):
    """Section d'affichage de l'historique."""
    st.subheader("📖 Votre Historique")
    
    mood_entries = db_service.get_mood_entries(user_id)
    
    if not mood_entries:
        st.info("📝 Votre historique apparaîtra ici après votre première saisie.")
        return
    
    # Affichage des entrées récentes
    for entry in mood_entries[:10]:  # Limite à 10 entrées récentes
        entry_date = pd.to_datetime(entry['created_at']).strftime('%d %B %Y à %H:%M')
        
        with st.expander(
            f"**{entry_date}** - Humeur: {entry['mood_score']}/10, Confiance: {entry['confidence_level']}/10"
        ):
            if entry.get('notes'):
                st.write(f"**Notes :** {entry['notes']}")
            else:
                st.write("*Aucune note pour cette journée*")
```

### `ui/dashboard_ui.py`
```python
"""
Interface du tableau de bord avec métriques et graphiques.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from services.db_service import DBService
from typing import List, Dict

def render_dashboard_ui(user_id: str, db_service: DBService):
    """
    Affiche le tableau de bord complet de l'utilisateur.
    
    Args:
        user_id: ID de l'utilisateur connecté
        db_service: Service de base de données
    """
    st.header("📈 Votre Tableau de Bord")
    
    with st.spinner("📊 Analyse de votre progression..."):
        mood_entries = db_service.get_mood_entries(user_id)
        stats = db_service.get_user_stats(user_id)

    if not mood_entries:
        st.info("🎯 Votre tableau de bord se remplira après quelques saisies d'humeur.")
        return

    # Métriques principales
    _render_key_metrics(stats)
    
    st.markdown("---")
    
    # Graphiques d'évolution
    _render_evolution_charts(mood_entries)

def _render_key_metrics(stats: Dict):
    """Affiche les métriques clés sous forme de cartes."""
    st.markdown("#### 📊 Vue d'ensemble")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        avg_mood = stats.get('avg_mood', 0)
        delta_mood = round(avg_mood - 5, 1) if avg_mood > 5 else None
        
        st.metric(
            label="😊 Humeur Moyenne",
            value=f"{avg_mood}/10",
            delta=f"+{delta_mood}" if delta_mood and delta_mood > 0 else None
        )
    
    with col2:
        avg_confidence = stats.get('avg_confidence', 0)
        delta_confidence = round(avg_confidence - 5, 1) if avg_confidence > 5 else None
        
        st.metric(
            label="💪 Confiance Moyenne",
            value=f"{avg_confidence}/10",
            delta=f"+{delta_confidence}" if delta_confidence and delta_confidence > 0 else None
        )
    
    with col3:
        st.metric(
            label="📝 Jours de Suivi",
            value=stats.get('total_entries', 0),
            delta=stats.get('trend', '➡️')
        )

def _render_evolution_charts(mood_entries: List[Dict]):
    """Génère les graphiques d'évolution."""
    if len(mood_entries) < 2:
        st.info("📈 Les graphiques d'évolution apparaîtront avec plus de données.")
        return
    
    try:
        # Préparation des données
        df = pd.DataFrame(mood_entries)
        df['created_at'] = pd.to_datetime(df['created_at'])
        df = df.sort_values('created_at')
        
        st.markdown("#### 📈 Évolution de votre État d'Esprit")
        
        # Graphique linéaire principal
        fig = px.line(
            df,
            x='created_at',
            y=['mood_score', 'confidence_level'],
            title="Progression de votre Humeur et Confiance",
            labels={
                'value': 'Score (sur 10)',
                'created_at': 'Date',
                'variable': 'Métrique'
            },
            color_discrete_map={
                'mood_score': '#667eea',
                'confidence_level': '#764ba2'
            }
        )
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color="#333"),
            hovermode='x unified'
        )
        
        fig.update_traces(mode='lines+markers', line=dict(width=3), marker=dict(size=8))
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Graphique en aires empilées pour une vue d'ensemble
        fig_area = px.area(
            df,
            x='created_at',
            y='mood_score',
            title="Zone de Confort Émotionnel",
            color_discrete_sequence=['#667eea']
        )
        
        fig_area.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False
        )
        
        st.plotly_chart(fig_area, use_container_width=True)
        
    except Exception as e:
        st.error(f"Erreur lors de la génération des graphiques : {e}")
```

### `ui/coaching_ui.py`
```python
"""
Interface de coaching d'entretien avec IA.
"""

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
        feedback = ai_service.generate_interview_feedback(response, "reconversion")
        
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
```

---

## 🚀 **ÉTAPE 5 : APPLICATION PRINCIPALE**

### `rise_app.py`
```python
"""
Point d'entrée principal de Phoenix Rise.
Assemble tous les composants dans une application cohérente.
"""

import streamlit as st
from services.auth_service import AuthService
from services.db_service import DBService
from services.ai_coach_service import AICoachService
from ui.journal_ui import render_journal_ui
from ui.dashboard_ui import render_dashboard_ui
from ui.coaching_ui import render_coaching_ui

# Configuration de la page
st.set_page_config(
    page_title="Phoenix Rise - Coach IA Reconversion",
    page_icon="🦋",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_custom_css():
    """Charge le CSS personnalisé pour l'identité Phoenix."""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .main {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
    }
    
    .phoenix-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.2);
    }
    
    .phoenix-title {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    .phoenix-subtitle {
        font-size: 1.2rem;
        font-weight: 300;
        opacity: 0.9;
    }
    
    .stButton > button {
        border-radius: 12px !important;
        font-weight: 600 !important;
        border: none !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3) !important;
    }
    
    /* Sidebar personnalisée */
    .css-1d391kg {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    .css-1d391kg .css-1v0mbdj {
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_resource
def get_auth_service():
    """Service d'authentification avec cache."""
    return AuthService()

@st.cache_resource  
def get_ai_service():
    """Service IA avec cache."""
    return AICoachService()

def get_db_service(auth_client):
    """Service de BDD (pas de cache car dépend de l'utilisateur)."""
    return DBService(auth_client)

def render_auth_interface(auth_service: AuthService):
    """Interface de connexion/inscription."""
    st.markdown("""
    <div class="phoenix-header">
        <div class="phoenix-title">🦋 Phoenix Rise</div>
        <div class="phoenix-subtitle">
            Votre coach IA personnel pour réussir votre reconversion professionnelle
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Onglets pour connexion/inscription
    tab1, tab2 = st.tabs(["🔑 Se Connecter", "📝 S'Inscrire"])
    
    with tab1:
        _render_signin_form(auth_service)
    
    with tab2:
        _render_signup_form(auth_service)

def _render_signin_form(auth_service: AuthService):
    """Formulaire de connexion."""
    st.subheader("Bienvenue ! Connectez-vous à votre compte")
    
    with st.form("signin_form"):
        email = st.text_input("📧 Email", placeholder="votre@email.com")
        password = st.text_input("🔐 Mot de passe", type="password")
        
        if st.form_submit_button("Se Connecter", type="primary", use_container_width=True):
            if email and password:
                success, error = auth_service.sign_in(email, password)
                if success:
                    st.success("🎉 Connexion réussie !")
                    st.rerun()
                else:
                    st.error(f"❌ {error}")
            else:
                st.warning("⚠️ Veuillez remplir tous les champs")

def _render_signup_form(auth_service: AuthService):
    """Formulaire d'inscription."""
    st.subheader("Créez votre compte Phoenix Rise")
    
    with st.form("signup_form"):
        email = st.text_input("📧 Email", placeholder="votre@email.com")
        password = st.text_input("🔐 Mot de passe", type="password", help="Minimum 6 caractères")
        password_confirm = st.text_input("🔐 Confirmer le mot de passe", type="password")
        
        terms = st.checkbox("J'accepte les conditions d'utilisation et la politique de confidentialité")
        
        if st.form_submit_button("Créer mon Compte", type="primary", use_container_width=True):
            if not all([email, password, password_confirm]):
                st.warning("⚠️ Veuillez remplir tous les champs")
            elif password != password_confirm:
                st.error("❌ Les mots de passe ne correspondent pas")
            elif len(password) < 6:
                st.error("❌ Le mot de passe doit contenir au moins 6 caractères")
            elif not terms:
                st.warning("⚠️ Veuillez accepter les conditions d'utilisation")
            else:
                success, error = auth_service.sign_up(email, password)
                if success:
                    st.success("🎉 Compte créé avec succès !")
                    st.info("📧 Vérifiez votre email pour confirmer votre compte")
                    st.rerun()
                else:
                    st.error(f"❌ {error}")

def render_main_app(user, auth_service: AuthService):
    """Application principale pour utilisateur connecté."""
    # Stockage du client DB pour le cache
    st.session_state.db_client = auth_service.client
    
    # Initialisation des services
    db_service = get_db_service(auth_service.client)
    ai_service = get_ai_service()

    # Sidebar utilisateur
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem; background: rgba(255,255,255,0.1); border-radius: 12px; margin-bottom: 1rem;">
            <h3>👋 Salut, {user.get_display_name()}</h3>
            <p style="opacity: 0.8; font-size: 0.9rem;">{user.email}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Statistiques rapides
        stats = db_service.get_user_stats(user.id)
        if stats.get('total_entries', 0) > 0:
            st.markdown("#### 📊 Vos Stats")
            st.metric("Jours suivis", stats['total_entries'])
            st.metric("Humeur moy.", f"{stats.get('avg_mood', 0)}/10")
            st.metric("Confiance moy.", f"{stats.get('avg_confidence', 0)}/10")
        
        st.markdown("---")
        
        # Bouton de déconnexion
        if st.button("🚪 Se Déconnecter", type="secondary", use_container_width=True):
            auth_service.sign_out()
            st.cache_data.clear()  # Nettoyage des caches
            if 'db_client' in st.session_state:
                del st.session_state.db_client
            st.success("👋 À bientôt !")
            st.rerun()

    # Header principal
    st.markdown("""
    <div class="phoenix-header">
        <div class="phoenix-title">🦋 Phoenix Rise</div>
        <div class="phoenix-subtitle">Transformez vos doutes en confiance authentique</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation principale par onglets
    tab1, tab2, tab3 = st.tabs([
        "**🖋️ Mon Journal**", 
        "**📈 Mon Dashboard**", 
        "**🎯 Coaching Entretien**"
    ])

    with tab1:
        render_journal_ui(user.id, db_service, ai_service)
    
    with tab2:
        render_dashboard_ui(user.id, db_service)
    
    with tab3:
        render_coaching_ui(ai_service)

def main():
    """Fonction principale de l'application."""
    # Chargement du CSS
    load_custom_css()
    
    # Initialisation des services
    auth_service = get_auth_service()
    
    # Routage selon l'état d'authentification
    current_user = auth_service.get_current_user()
    
    if not current_user:
        render_auth_interface(auth_service)
    else:
        render_main_app(current_user, auth_service)

if __name__ == "__main__":
    main()
```

---

## 🗄️ **ÉTAPE 6 : CONFIGURATION SUPABASE**

### Structure de Base de Données

```sql
-- Table des entrées d'humeur
CREATE TABLE mood_entries (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    mood_score INTEGER CHECK (mood_score >= 1 AND mood_score <= 10),
    energy_level INTEGER CHECK (energy_level >= 1 AND energy_level <= 10),
    confidence_level INTEGER CHECK (confidence_level >= 1 AND confidence_level <= 10),
    notes TEXT,
    tags TEXT[]
);

-- Table des sessions de coaching (optionnelle pour v1)
CREATE TABLE coaching_sessions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    sector TEXT NOT NULL,
    question TEXT NOT NULL,
    user_response TEXT NOT NULL,
    ai_feedback JSONB,
    score DECIMAL(3,1)
);

-- Index pour les performances
CREATE INDEX idx_mood_entries_user_date ON mood_entries(user_id, created_at DESC);
CREATE INDEX idx_coaching_sessions_user_date ON coaching_sessions(user_id, created_at DESC);

-- Politique de sécurité RLS (Row Level Security)
ALTER TABLE mood_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE coaching_sessions ENABLE ROW LEVEL SECURITY;

-- Politique : utilisateurs peuvent seulement voir leurs propres données
CREATE POLICY "Users can view own mood entries" ON mood_entries
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own mood entries" ON mood_entries
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can view own coaching sessions" ON coaching_sessions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own coaching sessions" ON coaching_sessions
    FOR INSERT WITH CHECK (auth.uid() = user_id);
```

---

## 🚀 **ÉTAPE 7 : DÉPLOIEMENT ET TESTS**

### Commandes de Test Local

```bash
# Installation des dépendances
pip install -r requirements.txt

# Variables d'environnement
cp .env.example .env
# Éditer .env avec tes vraies clés

# Test de l'application
streamlit run rise_app.py

# Test des imports
python -c "from services.auth_service import AuthService; print('✅ Services OK')"
python -c "from ui.journal_ui import render_journal_ui; print('✅ UI OK')"
```

### Checklist de Validation

**✅ Tests Techniques :**
- [ ] Application démarre sans erreur
- [ ] Connexion/Inscription fonctionnelle  
- [ ] Saisie d'humeur sauvegardée
- [ ] Dashboard affiche les données
- [ ] Coaching génère des questions
- [ ] IA retourne des encouragements

**✅ Tests UX :**
- [ ] Interface responsive mobile
- [ ] Messages d'erreur clairs
- [ ] Feedback utilisateur immédiat
- [ ] Navigation intuitive
- [ ] Design cohérent Phoenix

**✅ Tests Sécurité :**
- [ ] Données utilisateur isolées (RLS)
- [ ] Variables d'environnement protégées
- [ ] Validation des inputs
- [ ] Gestion d'erreurs sans exposition

---

## 🎯 **ÉTAPES SUIVANTES D'ÉVOLUTION**

### Phase 1 - MVP (Semaines 1-2)
- ✅ Architecture complète fonctionnelle
- ✅ Auth + BDD + IA intégrées
- ✅ 3 modules UI principaux
- 🎯 **Objectif :** Application utilisable par early adopters

### Phase 2 - Optimisation (Semaines 3-4)  
- 📊 Analytics utilisateur (respectueuses)
- 🎨 Améliorations UI/UX basées sur feedback
- 🤖 Prompts IA plus sophistiqués
- 📱 PWA (Progressive Web App)

### Phase 3 - Scale (Mois 2-3)
- 💳 Intégration système de paiement
- 📈 Dashboard admin/métriques business
- 🔄 API pour intégrations externes
- 🌍 Multi-langue (français/anglais)

---

## 💡 **CONSEILS POUR GEMINI CLI**

### Ordre de Construction Recommandé

1. **Commencer par les modèles** (`models/`) - Structure de données claire
2. **Ensuite les services** (`services/`) - Logique métier robuste  
3. **Puis les UI** (`ui/`) - Interface utilisateur progressive
4. **Finir par l'assemblage** (`rise_app.py`) - Intégration finale

### Points d'Attention Critiques

- **Cache Supabase :** Tester le cache `@st.cache_data` avec de vraies données
- **Gestion d'erreurs IA :** Prévoir des fallbacks intelligents si Gemini est indisponible
- **Performance mobile :** Tester sur mobile dès le début, pas en fin de projet
- **Sécurité RLS :** Valider que chaque utilisateur ne voit QUE ses données

### Debug et Monitoring

```python
# Ajout dans rise_app.py pour debugging
if st.secrets.get("DEBUG_MODE", False):
    st.sidebar.markdown("### 🐛 Debug Info")
    st.sidebar.json(st.session_state)
    st.sidebar.write("User:", st.session_state.get('user'))
```

---

**🎯 Mission :** Cette architecture modulaire te donne une base solide et scalable pour Phoenix Rise. Chaque module est indépendant, testable et évolutif.

**🚀 Prêt à bâtir ?** Commence par créer la structure de dossiers, puis construis module par module. L'architecture Phoenix Rise est prête à t'accompagner vers le succès ! 🦋