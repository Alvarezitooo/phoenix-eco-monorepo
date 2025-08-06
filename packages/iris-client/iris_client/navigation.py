"""
🧭 IRIS NAVIGATION - Navigation inter-applications Phoenix
Composants pour la navigation entre applications avec Iris intégré.
"""

import streamlit as st
from typing import Optional, Dict, Any
from .config import phoenix_config, IRIS_CONTEXTS, get_cross_app_navigation

def render_phoenix_navigation(current_app: str, show_iris_links: bool = True):
    """
    Rend la navigation Phoenix dans la sidebar.
    
    Args:
        current_app: Application courante (phoenix-letters, phoenix-cv, etc.)
        show_iris_links: Afficher les liens vers Iris des autres apps
    """
    
    with st.sidebar:
        st.markdown("### 🌐 Écosystème Phoenix")
        
        # Navigation vers les autres applications
        other_apps = phoenix_config.get_navigation_links(current_app)
        cross_app_urls = get_cross_app_navigation()
        
        for app_name, config in other_apps.items():
            context = IRIS_CONTEXTS.get(app_name, {})
            icon = context.get("icon", "🔗")
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                if st.button(f"{icon} {config.name}", key=f"nav_{app_name}"):
                    st.markdown(f"""
                    <script>
                    window.open('{config.url}', '_blank');
                    </script>
                    """, unsafe_allow_html=True)
                    st.info(f"Ouverture de {config.name}...")
            
            with col2:
                if show_iris_links and config.iris_enabled:
                    iris_url = cross_app_urls.get(f"{app_name}_iris")
                    if iris_url and st.button("🤖", key=f"iris_{app_name}", help=f"Iris {context.get('name', 'Assistant')}"):
                        st.markdown(f"""
                        <script>
                        window.open('{iris_url}', '_blank');
                        </script>
                        """, unsafe_allow_html=True)
                        st.info(f"Ouverture d'{context.get('name', 'Iris')}...")
        
        st.markdown("---")
        
        # Informations sur l'app courante
        current_config = phoenix_config.get_app_config(current_app)
        current_context = IRIS_CONTEXTS.get(current_app, {})
        
        if current_config:
            st.markdown(f"### {current_context.get('icon', '📱')} {current_config.name}")
            st.markdown(f"*{current_config.description}*")
            
            if current_config.iris_enabled:
                st.success(f"🤖 {current_context.get('name', 'Iris')} disponible")

def render_iris_app_selector(current_context: str = "phoenix-website"):
    """
    Rend un sélecteur d'application pour Iris.
    Utilisé dans les interfaces web pour basculer entre les contextes.
    
    Args:
        current_context: Contexte Iris actuel
    """
    
    st.markdown("### 🤖 Choisir votre assistant Iris")
    
    # Options disponibles
    iris_options = {}
    for app_name, context in IRIS_CONTEXTS.items():
        if phoenix_config.get_app_config(app_name).iris_enabled:
            iris_options[app_name] = f"{context['icon']} {context['name']} - {context['specialization']}"
    
    selected_app = st.selectbox(
        "Spécialisation Iris :",
        options=list(iris_options.keys()),
        format_func=lambda x: iris_options[x],
        index=list(iris_options.keys()).index(current_context) if current_context in iris_options else 0
    )
    
    if selected_app != current_context:
        st.info(f"Basculement vers {IRIS_CONTEXTS[selected_app]['name']}")
        return selected_app
    
    return current_context

def render_phoenix_ecosystem_overview():
    """
    Rend un aperçu de l'écosystème Phoenix avec liens Iris.
    """
    
    st.markdown("## 🌟 Écosystème Phoenix complet")
    
    cols = st.columns(len(IRIS_CONTEXTS))
    
    for i, (app_name, context) in enumerate(IRIS_CONTEXTS.items()):
        config = phoenix_config.get_app_config(app_name)
        
        if not config:
            continue
            
        with cols[i]:
            st.markdown(f"""
            <div style="
                border: 2px solid #{context['color']};
                border-radius: 10px;
                padding: 15px;
                text-align: center;
                margin: 10px 0;
                background: linear-gradient(135deg, #{context['color']}15, #{context['color']}05);
            ">
                <h3>{context['icon']} {config.name}</h3>
                <p style="font-size: 14px; opacity: 0.8;">{config.description}</p>
                <br>
                <p><strong>🤖 {context['name']}</strong></p>
                <p style="font-size: 12px;">{context['specialization']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            col_app, col_iris = st.columns(2)
            
            with col_app:
                if st.button(f"Ouvrir {config.name}", key=f"open_{app_name}"):
                    st.markdown(f"[🔗 Accéder à {config.name}]({config.url})")
            
            with col_iris:
                if config.iris_enabled and st.button(f"Chat {context['name']}", key=f"chat_{app_name}"):
                    cross_app_urls = get_cross_app_navigation()
                    iris_url = cross_app_urls.get(f"{app_name}_iris", config.url)
                    st.markdown(f"[🤖 Iris {context['name']}]({iris_url})")

def get_app_switch_urls(current_app: str) -> Dict[str, str]:
    """
    Génère les URLs pour basculer vers d'autres applications.
    
    Args:
        current_app: Application courante
        
    Returns:
        Dict des URLs de bascule
    """
    urls = {}
    cross_app_urls = get_cross_app_navigation()
    
    for app_name, config in phoenix_config.get_navigation_links(current_app).items():
        urls[app_name] = {
            "app_url": config.url,
            "iris_url": cross_app_urls.get(f"{app_name}_iris"),
            "name": config.name,
            "context": IRIS_CONTEXTS.get(app_name, {})
        }
    
    return urls

def render_cross_app_iris_buttons(current_app: str):
    """
    Rend des boutons rapides pour accéder aux autres assistants Iris.
    
    Args:
        current_app: Application courante
    """
    
    st.markdown("### 🚀 Autres assistants Iris")
    
    switch_urls = get_app_switch_urls(current_app)
    
    if not switch_urls:
        st.info("Vous êtes sur l'application principale de l'écosystème Phoenix")
        return
    
    # Affichage en colonnes
    cols = st.columns(min(len(switch_urls), 3))
    
    for i, (app_name, info) in enumerate(switch_urls.items()):
        context = info["context"]
        
        with cols[i % len(cols)]:
            if st.button(
                f"{context.get('icon', '🤖')} {context.get('name', 'Iris')}",
                key=f"switch_{app_name}",
                help=context.get('specialization', 'Assistant IA')
            ):
                if info["iris_url"]:
                    st.markdown(f"[🔗 Accéder à {context['name']}]({info['iris_url']})")
                else:
                    st.markdown(f"[🔗 Accéder à {info['name']}]({info['app_url']})")

# Utilitaires pour les développeurs
def inject_cross_app_css():
    """Injecte le CSS pour la navigation cross-app"""
    st.markdown("""
    <style>
    .phoenix-nav-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 6px;
        font-weight: 500;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .phoenix-nav-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);
    }
    
    .iris-context-badge {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
        margin: 2px;
    }
    
    .iris-purple { background: #e9d5ff; color: #7c3aed; }
    .iris-blue { background: #dbeafe; color: #2563eb; }
    .iris-green { background: #dcfce7; color: #16a34a; }
    .iris-orange { background: #fed7aa; color: #ea580c; }
    </style>
    """, unsafe_allow_html=True)