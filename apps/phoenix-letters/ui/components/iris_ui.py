import streamlit as st
import httpx
import logging
from typing import Optional

# Define the URL of the Iris agent API
IRIS_API_URL = "http://localhost:8003/api/v1/chat"

logger = logging.getLogger(__name__)

def get_user_auth_token() -> Optional[str]:
    """
    Récupère le token d'authentification de l'utilisateur Phoenix Letters.
    Intégration avec le système d'auth Phoenix.
    """
    # Vérifier si l'utilisateur est connecté via Phoenix Letters
    if 'authenticated_user' not in st.session_state:
        return None
    
    # Récupérer le token depuis la session Phoenix
    return st.session_state.get('access_token')

def render_chat_ui():
    """
    Renders a chat interface for interacting with Iris.
    Accessible à tous pour découvrir Phoenix Letters (stratégie d'acquisition).
    """
    # 🎯 ACCÈS LIBRE pour appâter les utilisateurs - Plus de vérification auth
    # auth_token = get_user_auth_token()  # Désactivé pour accès libre
    
    st.subheader("🤖 Iris - Votre Copilote Carrière IA")
    
    # Mode démo pour tous les utilisateurs (stratégie d'acquisition)
    st.info("✨ **Mode Découverte** - Testez Iris gratuitement ! Créez un compte pour sauvegarder vos conversations.")

    # Initialize chat history in session state if it doesn't exist
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display prior chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Handle user input
    if prompt := st.chat_input("Parlez-moi de vos défis de reconversion..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get AI response - Mode démo avec réponses intelligentes
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            with st.spinner("Iris réfléchit..."):
                # 🎯 Mode démo : réponses intelligentes selon le contexte
                try:
                    ai_reply = get_demo_response(prompt)
                    message_placeholder.markdown(ai_reply)
                except Exception:
                    ai_reply = "Une erreur inattendue s'est produite."
            
            # Add AI response to chat history
            st.session_state.messages.append({"role": "assistant", "content": ai_reply})

def render_iris_status():
    """
    Affiche le statut et les informations sur l'agent Iris.
    """
    with st.sidebar:
        st.markdown("### 🤖 Iris - Statut")
        
        auth_token = get_user_auth_token()
        if auth_token:
            st.success("✅ Connecté à Iris")
            user_tier = st.session_state.get('user_tier', 'FREE')
            
            if user_tier == 'FREE':
                st.info("🎆 Plan FREE\n5 messages/jour")
                st.markdown("[Passer à PREMIUM 🚀](/premium)")
            elif user_tier == 'PREMIUM':
                st.success("🎆 Plan PREMIUM\nAccès illimité")
            
            # Conseils d'utilisation
            with st.expander("💡 Conseils d'utilisation d'Iris"):
                st.markdown("""
                **Iris peut vous aider à :**
                - Analyser vos lettres de motivation
                - Optimiser votre stratégie de reconversion
                - Identifier des opportunités de carrière
                - Améliorer vos candidatures
                - Planifier votre trajectoire professionnelle
                
                **Pour de meilleurs résultats :**
                - Soyez spécifique dans vos questions
                - Mentionnez votre secteur cible
                - Partagez le contexte de votre reconversion
                """)
        else:
            st.warning("⚠️ Non connecté")
            st.info("Connectez-vous pour accéder à Iris")


def get_demo_response(user_message: str) -> str:
    """
    Génère une réponse démo intelligente basée sur le contexte du message utilisateur.
    Mode acquisition - réponses engageantes sans API externe.
    """
    message_lower = user_message.lower()
    
    # Détection des sujets principaux
    if any(word in message_lower for word in ['lettre', 'motivation', 'candidature', 'postuler']):
        return """
🎯 **Excellent choix de sujet !** Les lettres de motivation sont cruciales pour une reconversion réussie.

Voici mes conseils clés :
• **Valorisez votre parcours** : Transformez vos expériences passées en atouts
• **Personnalisez** : Adaptez chaque lettre à l'entreprise et au poste
• **Soyez authentique** : Expliquez clairement votre motivation pour ce changement

💡 *Avec Phoenix Letters Premium, je peux analyser vos lettres en temps réel et vous proposer des améliorations personnalisées !*

**Créez un compte gratuit pour sauvegarder nos échanges et débloquer plus de fonctionnalités !** 🚀
        """
    
    elif any(word in message_lower for word in ['reconversion', 'changer', 'métier', 'carrière', 'transition']):
        return """
🌟 **La reconversion, c'est mon domaine d'expertise !** 

Mes recommandations pour votre transition :
• **Bilan de compétences** : Identifiez vos forces transférables
• **Formation ciblée** : Comblez les gaps techniques si nécessaire  
• **Réseau professionnel** : Échangez avec des professionnels du secteur cible
• **Storytelling** : Construisez un récit cohérent de votre évolution

🎁 *Phoenix Letters propose des outils IA uniques pour optimiser votre stratégie de reconversion !*

**Passez au Premium pour accéder au Smart Coach et Mirror Match !** ✨
        """
    
    elif any(word in message_lower for word in ['cv', 'curriculum', 'expérience', 'compétence']):
        return """
📄 **Votre CV est votre carte de visite professionnelle !**

Points d'attention pour une reconversion :
• **Section "Projet professionnel"** : Clarifiez votre objectif en 2-3 lignes
• **Compétences transférables** : Mettez en avant ce qui s'applique au nouveau secteur
• **Formation continue** : Montrez votre montée en compétences
• **ATS-friendly** : Optimisez pour les logiciels de tri automatique

🔍 *Avec Phoenix CV Premium, j'analyse votre CV et l'optimise pour passer les filtres ATS !*

**Découvrez nos templates professionnels et nos conseils personnalisés !** 📈
        """
    
    elif any(word in message_lower for word in ['phoenix', 'fonctionnalité', 'feature', 'service']):
        return """
🚀 **Phoenix Letters, c'est l'application française de référence pour la reconversion !**

Nos super-pouvoirs IA :
• **Génération intelligente** : Lettres ultra-personnalisées avec Gemini IA
• **Mirror Match** : Adaptation automatique du ton selon l'entreprise
• **ATS Analyzer** : Optimisation pour passer les filtres de recrutement
• **Smart Coach** : Conseils temps réel pendant votre rédaction

🎯 *Application 100% française, spécialisée reconversion professionnelle*

**Testez gratuitement puis passez Premium pour débloquer tout le potentiel !** 💎
        """
    
    elif any(word in message_lower for word in ['prix', 'tarif', 'cost', 'premium', 'paiement']):
        return """
💰 **Tarification transparente et accessible !**

**Plan Gratuit** : 3 lettres/mois + découverte des fonctionnalités
**Phoenix Letters Premium** : 9,99€/mois - Lettres illimitées + tous les outils IA
**Phoenix CV Premium** : 7,99€/mois - CV illimités + optimisation ATS
**Bundle Complet** : 15,99€/mois (économie 1,99€) - Tout Phoenix !

✅ *Annulation en 1 clic, aucun engagement, paiement sécurisé Stripe*

**Commencez par le gratuit pour tester, puis choisissez ce qui vous convient !** 🎁
        """
    
    elif any(word in message_lower for word in ['aide', 'help', 'comment', 'débuter', 'commencer']):
        return """
🤝 **Je suis là pour vous accompagner !**

**Pour bien commencer :**
1. **Testez le générateur gratuit** - 3 lettres offertes
2. **Uploadez votre CV** - Je personnalise selon votre profil  
3. **Collez l'offre d'emploi** - Adaptation précise au poste
4. **Laissez la magie opérer** - IA Gemini + expertise reconversion

**Besoin d'aide spécifique ?** Dites-moi :
• Quel secteur vous visez ?
• Quel défi vous rencontrez ?
• À quelle étape êtes-vous ?

**Créez votre compte pour sauvegarder nos conversations !** 💾
        """
    
    else:
        # Réponse générique engageante
        return f"""
💡 **Merci pour votre question !** 

Je suis Iris, votre conseillère IA spécialisée dans la reconversion professionnelle. Je peux vous aider avec :

🎯 **Lettres de motivation** - Génération et optimisation personnalisées
📄 **CV et candidatures** - Conseils et templates professionnels  
🚀 **Stratégie de reconversion** - Planification et accompagnement
💼 **Recherche d'emploi** - Tips et bonnes pratiques

*Votre message : "{user_message[:50]}{'...' if len(user_message) > 50 else ''}"*

**Posez-moi une question plus spécifique ou créez un compte pour découvrir tout Phoenix Letters !** ✨
        """
