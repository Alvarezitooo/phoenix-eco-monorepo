"""
🎨 Phoenix CV - Composant Navigation Unifiée
Navigation cross-app style Phoenix Letters pour cohérence écosystème

Author: Claude Phoenix DevSecOps Guardian  
Version: 4.1.0 - Cross-App Navigation
"""

import streamlit as st
from typing import Dict, Any, Optional, List


class PhoenixCVNavigation:
    """Composant navigation unifiée Phoenix"""
    
    @staticmethod
    def render_main_nav():
        """Navigation principale Phoenix CV"""
        
        # Navigation horizontale
        nav_html = """
        <div style="
            background: white;
            border-bottom: 2px solid #e5e7eb;
            padding: 1rem 0;
            margin-bottom: 2rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        ">
            <div style="display: flex; justify-content: space-between; align-items: center; max-width: 1200px; margin: 0 auto; padding: 0 2rem;">
                <div style="display: flex; align-items: center; gap: 2rem;">
                    <div style="font-size: 1.5rem; font-weight: 700; color: #1e3a8a;">
                        📄 Phoenix CV
                    </div>
                    <nav style="display: flex; gap: 1.5rem;">
                        <a href="#create" style="color: #6b7280; text-decoration: none; font-weight: 500; padding: 0.5rem 1rem; border-radius: 0.5rem; transition: all 0.3s;">
                            🆕 Créer
                        </a>
                        <a href="#upload" style="color: #6b7280; text-decoration: none; font-weight: 500; padding: 0.5rem 1rem; border-radius: 0.5rem; transition: all 0.3s;">
                            📂 Analyser
                        </a>
                        <a href="#templates" style="color: #6b7280; text-decoration: none; font-weight: 500; padding: 0.5rem 1rem; border-radius: 0.5rem; transition: all 0.3s;">
                            🎨 Templates
                        </a>
                    </nav>
                </div>
                <div style="display: flex; align-items: center; gap: 1rem;">
                    <div style="font-size: 0.9rem; color: #6b7280;">
                        🔗 Écosystème Phoenix
                    </div>
                </div>
            </div>
        </div>
        """
        
        st.markdown(nav_html, unsafe_allow_html=True)
        
        # Navigation par onglets Streamlit
        PhoenixCVNavigation._render_tab_navigation()
    
    @staticmethod
    def _render_tab_navigation():
        """Navigation par onglets intégrée"""
        
        # Stockage de l'onglet actuel
        if "current_tab" not in st.session_state:
            st.session_state.current_tab = "create"
        
        # Onglets principaux
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🆕 Créer CV", use_container_width=True, 
                        type="primary" if st.session_state.current_tab == "create" else "secondary"):
                st.session_state.current_tab = "create"
                st.rerun()
        
        with col2:
            if st.button("📂 Analyser CV", use_container_width=True,
                        type="primary" if st.session_state.current_tab == "upload" else "secondary"):
                st.session_state.current_tab = "upload"
                st.rerun()
        
        with col3:
            if st.button("🎨 Templates", use_container_width=True,
                        type="primary" if st.session_state.current_tab == "templates" else "secondary"):
                st.session_state.current_tab = "templates"
                st.rerun()
        
        with col4:
            if st.button("📊 Historique", use_container_width=True,
                        type="primary" if st.session_state.current_tab == "history" else "secondary"):
                st.session_state.current_tab = "history"
                st.rerun()
    
    @staticmethod
    def render_cross_app_nav():
        """Navigation cross-app vers autres apps Phoenix"""
        
        st.markdown("---")
        st.markdown("### 🔗 Écosystème Phoenix")
        
        # Apps Phoenix disponibles
        phoenix_apps = [
            {
                "name": "Phoenix Letters",
                "icon": "✉️",
                "description": "Générez des lettres de motivation parfaites",
                "url": "https://phoenix-letters.streamlit.app",
                "color": "#f59e0b"
            },
            {
                "name": "Phoenix Rise", 
                "icon": "🧘",
                "description": "Coaching et développement personnel",
                "url": "https://phoenix-rise.streamlit.app",
                "color": "#8b5cf6"
            },
            {
                "name": "Phoenix Site",
                "icon": "🌐", 
                "description": "Portail principal et dashboard",
                "url": "https://phoenix-ecosystem.com",
                "color": "#10b981"
            }
        ]
        
        # Grid des apps
        cols = st.columns(len(phoenix_apps))
        
        for i, app in enumerate(phoenix_apps):
            with cols[i]:
                PhoenixCVNavigation._render_app_card(app)
    
    @staticmethod
    def _render_app_card(app: Dict[str, str]):
        """Card individuelle pour app Phoenix"""
        
        card_html = f"""
        <div style="
            border: 2px solid {app['color']};
            border-radius: 1rem;
            padding: 1.5rem;
            text-align: center;
            background: white;
            margin: 0.5rem 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease;
        " onmouseover="this.style.transform='translateY(-5px)'" onmouseout="this.style.transform='translateY(0)'">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">{app['icon']}</div>
            <h4 style="color: {app['color']}; margin: 0 0 0.5rem 0; font-weight: 600;">{app['name']}</h4>
            <p style="color: #6b7280; margin: 0; font-size: 0.9rem; line-height: 1.4;">{app['description']}</p>
        </div>
        """
        
        st.markdown(card_html, unsafe_allow_html=True)
        
        # Bouton navigation
        if st.button(f"Ouvrir {app['name']}", key=f"nav_{app['name']}", use_container_width=True):
            # Future: Navigation avec token auth cross-app
            st.info(f"🔗 Redirection vers {app['name']}...")
            # st.switch_page(app['url'])  # Future feature
    
    @staticmethod
    def render_breadcrumb(pages: List[str]):
        """Breadcrumb navigation"""
        
        breadcrumb_html = "<div style='margin: 1rem 0; color: #6b7280; font-size: 0.9rem;'>"
        
        for i, page in enumerate(pages):
            if i > 0:
                breadcrumb_html += " → "
            
            if i == len(pages) - 1:  # Page actuelle
                breadcrumb_html += f"<span style='color: #1e3a8a; font-weight: 600;'>{page}</span>"
            else:
                breadcrumb_html += f"<span>{page}</span>"
        
        breadcrumb_html += "</div>"
        
        st.markdown(breadcrumb_html, unsafe_allow_html=True)
    
    @staticmethod
    def render_sidebar_nav():
        """Navigation sidebar complète"""
        
        with st.sidebar:
            st.markdown("### 📄 Phoenix CV")
            
            # Menu principal
            menu_options = [
                ("🆕", "Créer CV", "create"),
                ("📂", "Analyser CV", "upload"), 
                ("🎨", "Templates", "templates"),
                ("📊", "Mes CV", "history"),
                ("⚙️", "Paramètres", "settings")
            ]
            
            for icon, label, key in menu_options:
                selected = st.session_state.get("current_tab") == key
                
                if st.button(f"{icon} {label}", key=f"sidebar_{key}", 
                           use_container_width=True,
                           type="primary" if selected else "secondary"):
                    st.session_state.current_tab = key
                    st.rerun()
            
            st.markdown("---")
            
            # User info
            user_id = st.session_state.get("user_id", "anonymous")
            if user_id != "anonymous":
                PhoenixCVNavigation._render_user_sidebar_info()
            else:
                PhoenixCVNavigation._render_anonymous_sidebar()
            
            st.markdown("---")
            
            # Cross-app links
            st.markdown("### 🔗 Autres Apps")
            
            cross_app_links = [
                ("✉️", "Phoenix Letters", "#letters"),
                ("🧘", "Phoenix Rise", "#rise"),
                ("🌐", "Phoenix Site", "#site")
            ]
            
            for icon, name, url in cross_app_links:
                if st.button(f"{icon} {name}", key=f"cross_{name}", use_container_width=True):
                    st.info(f"🔗 Redirection vers {name}...")
    
    @staticmethod
    def _render_user_sidebar_info():
        """Infos utilisateur sidebar"""
        
        user_tier = st.session_state.get("user_tier", "free")
        
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
            padding: 1rem;
            border-radius: 0.5rem;
            color: white;
            text-align: center;
            margin: 1rem 0;
        ">
            <div style="font-size: 1.2rem; margin-bottom: 0.5rem;">👤</div>
            <div style="font-weight: 600; margin-bottom: 0.25rem;">
                {st.session_state.get("user_name", "Utilisateur")}
            </div>
            <div style="opacity: 0.8; font-size: 0.9rem;">
                Plan {user_tier.title()}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def _render_anonymous_sidebar():
        """Info utilisateur anonyme"""
        
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%);
            padding: 1rem;
            border-radius: 0.5rem;
            color: white;
            text-align: center;
            margin: 1rem 0;
        ">
            <div style="font-size: 1.2rem; margin-bottom: 0.5rem;">🚀</div>
            <div style="font-weight: 600; margin-bottom: 0.5rem;">
                Créez votre compte
            </div>
            <div style="opacity: 0.8; font-size: 0.9rem;">
                Accès aux fonctionnalités avancées
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📝 S'inscrire", use_container_width=True, type="primary"):
            st.info("🔗 Redirection vers inscription...")


class PhoenixCVQuickActions:
    """Composant actions rapides"""
    
    @staticmethod
    def render():
        """Actions rapides principales"""
        
        st.markdown("### ⚡ Actions rapides")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🚀 Nouveau CV Express", use_container_width=True, type="primary"):
                st.session_state.current_tab = "create"
                st.session_state.quick_mode = True
                st.rerun()
        
        with col2:
            if st.button("📂 Analyser CV Rapidement", use_container_width=True):
                st.session_state.current_tab = "upload"
                st.session_state.quick_mode = True
                st.rerun()
        
        # Actions secondaires
        col3, col4, col5 = st.columns(3)
        
        with col3:
            if st.button("🎨 Templates", use_container_width=True):
                st.session_state.current_tab = "templates"
                st.rerun()
        
        with col4:
            if st.button("📊 Mes CV", use_container_width=True):
                st.session_state.current_tab = "history"
                st.rerun()
        
        with col5:
            if st.button("🔥 Premium", use_container_width=True):
                st.session_state.show_premium_modal = True
                st.rerun()