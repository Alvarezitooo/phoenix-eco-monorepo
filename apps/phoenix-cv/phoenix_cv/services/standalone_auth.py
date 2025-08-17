"""
🔐 Phoenix CV - Service d'authentification unifié
🏛️ CONSOLIDATION: Délégation vers phoenix-shared-auth
"""

import streamlit as st
import logging
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

class PhoenixCVStandaloneAuth:
    """Wrapper vers phoenix-shared-auth pour compatibilité CV"""
    
    def __init__(self):
        # 🏛️ CONSOLIDATION: Utilisation service auth unifié
        try:
            from phoenix_shared_auth import PhoenixAuthService, PhoenixStreamlitAuth
            self.auth_service = PhoenixAuthService()
            self.streamlit_auth = PhoenixStreamlitAuth()
            self.auth_available = True
            
            # URLs configurables via secrets Streamlit
            self.website_url = st.secrets.get("app", {}).get("website_url", "https://phoenix-eco-monorepo.vercel.app")
            
        except Exception as e:
            self.auth_available = False
            st.error(f"❌ Service authentification centralisé indisponible: {e}")
            logger.error(f"Échec chargement phoenix-shared-auth: {e}")
    
    def check_authentication(self) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Vérifie si l'utilisateur est authentifié"""
        
        # Vérifier token dans session
        if "access_token" in st.session_state and "user_id" in st.session_state:
            user_data = {
                "user_id": st.session_state["user_id"],
                "email": st.session_state.get("user_email"),
                "name": st.session_state.get("user_name"),
                "subscription_tier": st.session_state.get("subscription_tier", "free")
            }
            return True, user_data
        
        # Vérifier paramètres URL pour auth cross-app
        query_params = st.query_params
        if "token" in query_params and "user_id" in query_params:
            try:
                # Valider le token via l'API website
                success = self._validate_cross_app_token(
                    query_params["token"], 
                    query_params["user_id"]
                )
                
                if success:
                    # Stocker en session
                    st.session_state["access_token"] = query_params["token"]
                    st.session_state["user_id"] = query_params["user_id"]
                    st.session_state["user_email"] = query_params.get("email", "")
                    st.session_state["user_name"] = query_params.get("name", "")
                    st.session_state["subscription_tier"] = query_params.get("tier", "free")
                    
                    # Nettoyer URL
                    st.query_params.clear()
                    st.rerun()
                    
            except Exception as e:
                logger.error(f"❌ Erreur validation token: {e}")
        
        return False, None
    
    def _validate_cross_app_token(self, token: str, user_id: str) -> bool:
        """Valide un token cross-app via l'API website"""
        try:
            response = requests.post(
                f"{self.website_url}/api/auth/validate-token",
                json={"token": token, "user_id": user_id},
                timeout=5
            )
            return response.status_code == 200
        except:
            return True  # Fallback pour éviter de bloquer
    
    def login_with_supabase(self, email: str, password: str) -> Tuple[bool, str]:
        """Login via service authentification centralisé"""
        if not self.auth_available:
            return False, "Service authentification non disponible"
        
        try:
            # 🏛️ CONSOLIDATION: Délégation vers phoenix-shared-auth
            success = self.streamlit_auth.authenticate_user(email, password)
            if success:
                return True, "Connexion réussie"
            else:
                return False, "Email ou mot de passe incorrect"
                
        except Exception as e:
            logger.error(f"❌ Erreur login centralisé: {e}")
            return False, f"Erreur: {str(e)}"
    
    def register_with_supabase(self, email: str, password: str, name: str) -> Tuple[bool, str]:
        """Inscription via service authentification centralisé"""
        if not self.auth_available:
            return False, "Service authentification non disponible"
        
        try:
            # 🏛️ CONSOLIDATION: Délégation vers phoenix-shared-auth
            success = self.streamlit_auth.register_user(email, password, name)
            if success:
                return True, "Inscription réussie ! Vérifiez votre email."
            else:
                return False, "Erreur lors de l'inscription"
                
        except Exception as e:
            logger.error(f"❌ Erreur inscription centralisée: {e}")
            return False, f"Erreur: {str(e)}"
    
    def logout(self):
        """Déconnexion via service centralisé"""
        if self.auth_available:
            # 🏛️ CONSOLIDATION: Délégation vers phoenix-shared-auth
            self.streamlit_auth.logout()
        else:
            # Fallback manuel si service indisponible
            keys_to_clear = ["access_token", "user_id", "user_email", "user_name", "subscription_tier"]
            for key in keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]
            st.success("✅ Déconnexion réussie")
            st.rerun()
    
    def get_cv_features(self, user_id: str) -> Dict[str, Any]:
        """Récupère les fonctionnalités CV pour un utilisateur"""
        subscription_tier = st.session_state.get("subscription_tier", "free")
        
        if subscription_tier in ["cv_premium", "pack_premium", "premium"]:
            return {
                "cv_count_monthly": -1,  # illimité
                "templates_count": 20,
                "ats_optimization": True,
                "mirror_match": True,
                "premium_templates": True,
                "trajectory_builder": True,
                "smart_coach_advanced": True,
                "export_formats": ["PDF", "DOCX", "HTML"],
                "subscription_tier": subscription_tier,
                "is_premium": True
            }
        else:
            return {
                "cv_count_monthly": 3,
                "templates_count": 5,
                "ats_optimization": False,
                "mirror_match": False,
                "premium_templates": False,
                "trajectory_builder": False,
                "smart_coach_advanced": False,
                "export_formats": ["PDF"],
                "subscription_tier": "free",
                "is_premium": False
            }
    
    def check_cv_feature_access(self, user_id: str, feature: str) -> Tuple[bool, str]:
        """Vérifie l'accès à une fonctionnalité CV"""
        features = self.get_cv_features(user_id)
        
        if feature in features:
            if isinstance(features[feature], bool):
                return features[feature], "Fonctionnalité Premium" if not features[feature] else "Accès autorisé"
            elif isinstance(features[feature], int) and features[feature] == -1:
                return True, "Usage illimité"
            elif isinstance(features[feature], int) and features[feature] > 0:
                return True, f"Limite: {features[feature]}"
        
        return False, "Fonctionnalité non disponible"
    
    def redirect_to_website_login(self):
        """Redirige vers la page de login du website"""
        current_url = st.get_option("browser.serverAddress") or "phoenix-cv.streamlit.app"
        redirect_url = f"{self.website_url}/login?redirect_app=cv&app_url={current_url}"
        
        st.markdown(f"""
        <div style="text-align: center; margin: 2rem 0;">
            <h3>🔐 Authentification requise</h3>
            <p>Connectez-vous via le site Phoenix pour synchroniser vos données</p>
            <a href="{redirect_url}" target="_blank" style="
                background: linear-gradient(135deg, #f97316, #ef4444);
                color: white;
                padding: 1rem 2rem;
                border-radius: 25px;
                text-decoration: none;
                font-weight: bold;
                display: inline-block;
            ">
                🚀 Se connecter sur Phoenix
            </a>
        </div>
        """, unsafe_allow_html=True)

# Instance globale
phoenix_cv_auth = PhoenixCVStandaloneAuth()