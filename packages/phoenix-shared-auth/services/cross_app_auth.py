"""
🌉 Phoenix Cross-App Authentication Service
Service d'authentification unifié pour navigation entre applications Phoenix
"""

import base64
import json
import logging
import streamlit as st
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from urllib.parse import parse_qs, urlparse

from .phoenix_auth_service import PhoenixAuthService
from ..entities.phoenix_user import PhoenixUser, PhoenixApp

logger = logging.getLogger(__name__)


class CrossAppAuthService:
    """
    Service d'authentification cross-app pour l'écosystème Phoenix
    Gère les tokens de navigation entre website, letters, cv, rise
    """
    
    def __init__(self, auth_service: PhoenixAuthService):
        self.auth_service = auth_service
        self.secret_key = st.secrets.get("PHOENIX_SECRET", "phoenix-secret-key")
    
    def handle_cross_app_login(self) -> Optional[PhoenixUser]:
        """
        Gère la connexion cross-app depuis une autre application Phoenix
        Vérifie les paramètres URL pour token d'authentification
        """
        try:
            # Vérifier paramètres URL
            query_params = st.query_params
            phoenix_token = query_params.get("phoenix_token")
            source = query_params.get("source")
            user_data = query_params.get("user_data")
            
            if not phoenix_token:
                return None
                
            # Décoder et valider token
            user = self._validate_cross_app_token(phoenix_token)
            if not user:
                return None
                
            # Créer session Streamlit
            self._create_streamlit_session(user, source, user_data)
            
            # Nettoyer URL
            self._clean_url_params()
            
            logger.info(f"Cross-app login successful for user {user.email} from {source}")
            return user
            
        except Exception as e:
            logger.error(f"Cross-app login error: {e}")
            return None
    
    def _validate_cross_app_token(self, token: str) -> Optional[PhoenixUser]:
        """Valide et décode le token cross-app"""
        try:
            # Décoder token base64
            decoded = base64.b64decode(token).decode('utf-8')
            token_data = json.loads(decoded)
            
            # Vérifier structure token
            required_fields = ['userId', 'email', 'targetApp', 'timestamp', 'signature']
            if not all(field in token_data for field in required_fields):
                logger.warning("Invalid token structure")
                return None
            
            # Vérifier expiration (5 minutes)
            token_time = datetime.fromtimestamp(token_data['timestamp'] / 1000)
            if datetime.now() - token_time > timedelta(minutes=5):
                logger.warning("Token expired")
                return None
            
            # Vérifier signature
            expected_signature = self._generate_signature(
                token_data['userId'], 
                token_data['targetApp']
            )
            if token_data['signature'] != expected_signature:
                logger.warning("Invalid token signature")
                return None
            
            # Récupérer utilisateur depuis DB
            user = self.auth_service.get_user_by_id(token_data['userId'])
            return user
            
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            return None
    
    def _generate_signature(self, user_id: str, target_app: str) -> str:
        """Génère signature pour validation token"""
        signature_data = f"{user_id}-{target_app}-{self.secret_key}"
        return base64.b64encode(signature_data.encode()).decode()
    
    def _create_streamlit_session(self, user: PhoenixUser, source: str, user_data: str):
        """Crée session Streamlit avec données utilisateur"""
        # Session auth
        st.session_state['authenticated'] = True
        st.session_state['user_id'] = str(user.id)
        st.session_state['user_email'] = user.email
        st.session_state['user_tier'] = user.subscription.tier.value
        st.session_state['full_name'] = user.full_name
        
        # Métadonnées cross-app
        st.session_state['cross_app_source'] = source
        st.session_state['login_method'] = 'cross_app'
        st.session_state['login_timestamp'] = datetime.now().isoformat()
        
        # Données utilisateur additionnelles
        if user_data:
            try:
                additional_data = json.loads(user_data)
                st.session_state['cross_app_data'] = additional_data
            except:
                pass
        
        # Préférences utilisateur
        if hasattr(user, 'preferences'):
            st.session_state['user_preferences'] = user.preferences
    
    def _clean_url_params(self):
        """Nettoie les paramètres URL après authentification"""
        try:
            # Recharger page sans paramètres
            st.rerun()
        except:
            pass
    
    def create_cross_app_redirect_url(self, target_app: PhoenixApp, user_data: Dict[str, Any] = None) -> str:
        """
        Crée URL de redirection vers autre app avec token auth
        """
        try:
            # Vérifier session active
            if not st.session_state.get('authenticated'):
                raise ValueError("No active session")
            
            user_id = st.session_state.get('user_id')
            user_email = st.session_state.get('user_email')
            
            # Générer token cross-app
            token_data = {
                'userId': user_id,
                'email': user_email,
                'targetApp': target_app.value,
                'timestamp': int(datetime.now().timestamp() * 1000),
                'signature': self._generate_signature(user_id, target_app.value)
            }
            
            # Encoder token
            token = base64.b64encode(json.dumps(token_data).encode()).decode()
            
            # URLs des applications
            app_urls = {
                PhoenixApp.LETTERS: st.secrets.get("PHOENIX_LETTERS_URL", "https://phoenix-letters.streamlit.app"),
                PhoenixApp.CV: st.secrets.get("PHOENIX_CV_URL", "https://phoenix-cv.streamlit.app"),
                PhoenixApp.RISE: st.secrets.get("PHOENIX_RISE_URL", "https://phoenix-rise.streamlit.app"),
                PhoenixApp.WEBSITE: st.secrets.get("PHOENIX_WEBSITE_URL", "https://phoenix-eco-monorepo.vercel.app")
            }
            
            base_url = app_urls.get(target_app)
            if not base_url:
                raise ValueError(f"Unknown target app: {target_app}")
            
            # Construire URL avec paramètres
            params = {
                'phoenix_token': token,
                'source': st.session_state.get('current_app', 'unknown')
            }
            
            if user_data:
                params['user_data'] = json.dumps(user_data)
            
            query_string = "&".join([f"{k}={v}" for k, v in params.items()])
            return f"{base_url}?{query_string}"
            
        except Exception as e:
            logger.error(f"Create redirect URL error: {e}")
            raise
    
    def init_streamlit_auth_check(self):
        """
        Initialise vérification auth au démarrage Streamlit
        À appeler au début de chaque app Streamlit
        """
        # Vérifier cross-app login d'abord
        cross_app_user = self.handle_cross_app_login()
        if cross_app_user:
            return cross_app_user
        
        # Vérifier session existante
        if st.session_state.get('authenticated'):
            user_id = st.session_state.get('user_id')
            if user_id:
                return self.auth_service.get_user_by_id(user_id)
        
        return None
    
    def logout_all_apps(self):
        """Déconnexion de toutes les applications Phoenix"""
        # Nettoyer session Streamlit
        for key in list(st.session_state.keys()):
            if key.startswith(('user_', 'authenticated', 'cross_app_')):
                del st.session_state[key]
        
        # Rediriger vers website
        website_url = st.secrets.get("PHOENIX_WEBSITE_URL", "https://phoenix-eco-monorepo.vercel.app")
        st.markdown(f'<meta http-equiv="refresh" content="0; url={website_url}">', unsafe_allow_html=True)
        st.stop()


# Instance singleton pour import facile
cross_app_auth = None

def get_cross_app_auth_service(auth_service: PhoenixAuthService = None) -> CrossAppAuthService:
    """Factory function pour service cross-app auth"""
    global cross_app_auth
    if cross_app_auth is None and auth_service:
        cross_app_auth = CrossAppAuthService(auth_service)
    return cross_app_auth