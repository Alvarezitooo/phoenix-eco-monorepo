import streamlit as st

def render_primary_button(label: str, key: str = None, **kwargs):
    """Rend un bouton primaire stylisé selon le Design System Phoenix."""
    return st.button(label, type="primary", key=key, **kwargs)

def render_info_card(title: str, content: str, icon: str = "💡"):
    """Rend une carte d'information stylisée."""
    st.markdown(f"""
    <div style="
        background-color: var(--phoenix-surface);
        border-radius: var(--phoenix-border-radius-lg);
        box-shadow: var(--phoenix-shadow-sm);
        padding: var(--phoenix-spacing-lg);
        margin-bottom: var(--phoenix-spacing-md);
        border-left: 5px solid var(--phoenix-primary);
    ">
        <h3 style="color: var(--phoenix-primary); margin-top: 0;">{icon} {title}</h3>
        <p style="color: var(--phoenix-text-dark);">{content}</p>
    </div>
    """, unsafe_allow_html=True)

def render_section_header(title: str, subtitle: str = None):
    """Rend un en-tête de section stylisé."""
    st.markdown(f"""
    <h1 style="color: var(--phoenix-primary); text-align: center; margin-bottom: var(--phoenix-spacing-sm);">{title}</h1>
    """, unsafe_allow_html=True)
    if subtitle:
        st.markdown(f"""
        <p style="color: var(--phoenix-text-dark); text-align: center; font-size: 1.1em; margin-bottom: var(--phoenix-spacing-lg);">{subtitle}</p>
        """, unsafe_allow_html=True)

def render_alert(message: str, alert_type: str = "info"):
    """Rend une alerte stylisée (info, success, warning, error)."""
    # Utilise les classes CSS définies dans style.css
    st.markdown(f"""
    <div class="stAlert {alert_type}">
        {message}
    </div>
    """, unsafe_allow_html=True)

def render_metric_card(label: str, value: str, delta: str = None, help_text: str = None):
    """Rend une carte de métrique stylisée."""
    st.markdown(f"""
    <div style="
        background-color: var(--phoenix-surface);
        border-radius: var(--phoenix-border-radius-md);
        box-shadow: var(--phoenix-shadow-sm);
        padding: var(--phoenix-spacing-md);
        text-align: center;
        margin-bottom: var(--phoenix-spacing-sm);
    ">
        <p style="color: var(--phoenix-text-dark); font-size: 0.9em; margin-bottom: var(--phoenix-spacing-xs);">{label}</p>
        <h3 style="color: var(--phoenix-primary); margin-top: 0; margin-bottom: var(--phoenix-spacing-xs);">{value}</h3>
        {f'<p style="color: var(--phoenix-success); font-size: 0.8em;">{delta}</p>' if delta else ''}
        {f'<p style="color: var(--phoenix-text-dark); font-size: 0.7em; opacity: 0.7;">{help_text}</p>' if help_text else ''}
    </div>
    """, unsafe_allow_html=True)

def render_ariadne_thread(steps: list, current_step_index: int = 0):
    """
    Rend un composant visuel de progression (Fil d'Ariane).

    Args:
        steps (list): Liste des noms d'étapes.
        current_step_index (int): Index de l'étape actuelle (0-basé).
    """
    html_content = """
    <style>
        .ariadne-thread {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin: var(--phoenix-spacing-lg) 0;
            padding: 0 var(--phoenix-spacing-md);
            background-color: var(--phoenix-surface);
            border-radius: var(--phoenix-border-radius-md);
            box-shadow: var(--phoenix-shadow-sm);
        }
        .ariadne-step {
            flex: 1;
            text-align: center;
            padding: var(--phoenix-spacing-md) 0;
            position: relative;
            color: var(--phoenix-text-dark);
            opacity: 0.6;
            font-weight: 500;
        }
        .ariadne-step.active {
            opacity: 1;
            color: var(--phoenix-primary);
        }
        .ariadne-step.completed {
            opacity: 1;
            color: var(--phoenix-success);
        }
        .ariadne-step-indicator {
            width: 20px;
            height: 20px;
            background-color: var(--phoenix-background);
            border-radius: 50%;
            border: 2px solid var(--phoenix-primary);
            margin: 0 auto var(--phoenix-spacing-sm);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.8em;
            font-weight: 700;
            color: var(--phoenix-primary);
        }
        .ariadne-step.active .ariadne-step-indicator {
            background-color: var(--phoenix-primary);
            color: var(--phoenix-text-light);
        }
        .ariadne-step.completed .ariadne-step-indicator {
            background-color: var(--phoenix-success);
            border-color: var(--phoenix-success);
            color: var(--phoenix-text-light);
        }
        .ariadne-line {
            position: absolute;
            top: 50%;
            left: 50%;
            width: 100%;
            height: 2px;
            background-color: var(--phoenix-background);
            z-index: -1;
            transform: translateY(-50%);
        }
        .ariadne-step:not(:last-child) .ariadne-line {
            width: calc(100% - 40px); /* Ajustement pour les indicateurs */
            left: calc(50% + 20px);
        }
        .ariadne-step:first-child .ariadne-line {
            left: 50%;
            width: 50%;
        }
        .ariadne-step:last-child .ariadne-line {
            width: 50%;
            right: 50%;
            left: auto;
        }
    </style>
    <div class="ariadne-thread">
    """

    for i, step in enumerate(steps):
        status_class = ""
        if i < current_step_index:
            status_class = "completed"
        elif i == current_step_index:
            status_class = "active"

        html_content += f"""
        <div class="ariadne-step {status_class}">
            <div class="ariadne-step-indicator">{i + 1}</div>
            <div>{step}</div>
            {f'<div class="ariadne-line"></div>' if i < len(steps) - 1 else ''}
        </div>
        """
    html_content += "</div>"
    st.markdown(html_content, unsafe_allow_html=True)