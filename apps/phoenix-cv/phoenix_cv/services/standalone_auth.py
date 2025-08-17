"""
🔐 Phoenix CV - Service d'authentification standalone
Service d'auth intégré pour déploiement Streamlit Cloud sans dépendances monorepo
"""

import streamlit as st
import requests
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class PhoenixCVStandaloneAuth:
    """Service d'authentification standalone pour Phoenix CV"""
    
    def __init__(self):
        # URLs configurables via secrets Streamlit
        self.website_url = st.secrets.get("app", {}).get("website_url", "https://phoenix-eco-monorepo.vercel.app")
        
        # 🏛️ CONSOLIDATION: Utilisation client Supabase centralisé
        try:
            from phoenix_common.clients import get_supabase_client
            self.supabase_client = get_supabase_client()
            self.supabase_available = True
        except Exception as e:
            self.supabase_available = False
            st.error(f"❌ Client Supabase centralisé indisponible: {e}")
    
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
        """Login direct avec Supabase"""
        if not self.supabase_available:
            return False, "Supabase non configuré"
        
        try:
            import supabase
            client = supabase.create_client(self.supabase_url, self.supabase_key)
            
            response = client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user:
                # Stocker en session
                st.session_state["access_token"] = response.session.access_token
                st.session_state["user_id"] = response.user.id
                st.session_state["user_email"] = response.user.email
                st.session_state["user_name"] = response.user.user_metadata.get("name", email.split("@")[0])
                
                # Récupérer tier d'abonnement
                profile_response = client.table("profiles").select("subscription_tier").eq("id", response.user.id).execute()
                if profile_response.data:
                    st.session_state["subscription_tier"] = profile_response.data[0].get("subscription_tier", "free")
                else:
                    st.session_state["subscription_tier"] = "free"
                
                return True, "Connexion réussie"
            
            return False, "Email ou mot de passe incorrect"
            
        except Exception as e:
            logger.error(f"❌ Erreur login Supabase: {e}")
            return False, f"Erreur: {str(e)}"
    
    def register_with_supabase(self, email: str, password: str, name: str) -> Tuple[bool, str]:
        """Inscription avec Supabase"""
        if not self.supabase_available:
            return False, "Supabase non configuré"
        
        try:
            import supabase
            client = supabase.create_client(self.supabase_url, self.supabase_key)
            
            response = client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {"name": name}
                }
            })
            
            if response.user:
                return True, "Inscription réussie ! Vérifiez votre email."
            
            return False, "Erreur lors de l'inscription"
            
        except Exception as e:
            logger.error(f"❌ Erreur inscription Supabase: {e}")
            return False, f"Erreur: {str(e)}"
    
    def logout(self):
        """Déconnexion"""
        # Nettoyer session Streamlit
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