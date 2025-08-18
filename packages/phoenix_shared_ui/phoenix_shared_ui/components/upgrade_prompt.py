import streamlit as st

def render_upgrade_prompt(feature_name: str):
    """
    Affiche un message standardisé pour inciter à passer au Premium.

    Args:
        feature_name: Le nom de la fonctionnalité premium bloquée.
    """
    st.markdown(
        f"""
        <div style="text-align: center; padding: 2rem; background: #fff3cd; border-radius: 10px; border: 2px solid #ffc107;">
            <h3>⭐ La fonctionnalité '{feature_name}' est réservée aux membres Premium</h3>
            <p>Passez au niveau supérieur pour débloquer cette fonctionnalité et bien d'autres avantages.</p>
            <p>
                <a href="/pricing" target="_self" style="text-decoration: none;">
                    <button style="background: #ffc107; color: #333; border: none; padding: 0.75rem 1.5rem; border-radius: 8px; font-weight: bold; cursor: pointer;">
                        Découvrir l'offre Premium
                    </button>
                </a>
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )