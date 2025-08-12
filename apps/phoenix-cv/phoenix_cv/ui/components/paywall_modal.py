import streamlit as st
from phoenix_cv.main import initiate_stripe_checkout # Assurez-vous que initiate_stripe_checkout est importable

def show_paywall_modal(title: str, message: str, cta_label: str = "Passer Premium pour 9,99€/mois", plan_id: str = "premium"):
    """
    Affiche une modale de mur payant et arrête l'exécution de la page.
    """
    st.markdown(
        """
        <style>
        .paywall-modal {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.7);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }
        .paywall-content {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px;
            border-radius: 15px;
            text-align: center;
            color: white;
            max-width: 600px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            animation: fadeIn 0.3s ease-out;
        }
        .paywall-content h2 {
            font-size: 2.5em;
            margin-bottom: 20px;
            color: #FFD700; /* Gold color for emphasis */
        }
        .paywall-content p {
            font-size: 1.2em;
            margin-bottom: 30px;
            line-height: 1.5;
        }
        .paywall-content .stButton > button {
            background-color: #FFD700; /* Gold button */
            color: #333;
            font-size: 1.3em;
            padding: 15px 30px;
            border-radius: 10px;
            border: none;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }
        .paywall-content .stButton > button:hover {
            background-color: #e6c200; /* Darker gold on hover */
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: scale(0.9); } 
            to { opacity: 1; transform: scale(1); }
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="paywall-modal">
            <div class="paywall-content">
                <h2>{title}</h2>
                <p>{message}</p>
                <div style="display: flex; justify-content: center;">
                    <div class="stButton">
                        <button onclick="window.streamlit.setComponentValue('paywall_cta_clicked', true)">
                            {cta_label}
                        </button>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Pour l'instant, je vais juste afficher le message et le bouton Streamlit
    # et arrêter l'exécution. La "modale" sera juste un conteneur stylisé.

    st.markdown(f"## {title}")
    st.markdown(f"### {message}")

    if st.button(cta_label, key="paywall_cta", type="primary"):
        user_id = st.session_state.get("user_id", "guest_user")
        user_email = st.session_state.get("user_email", None)
        initiate_stripe_checkout(user_id, plan_id, user_email)

    st.stop() # Arrête l'exécution du reste de la page