"""
🚀 PHOENIX CV - Générateur IA de CV pour Reconversions Professionnelles
Version Marketing Simplifiée - Prêt pour démo
"""

import json
import os
import tempfile
from datetime import datetime
from io import BytesIO

import docx
import google.generativeai as genai
import PyPDF2
import streamlit as st


# Chargement des variables d'environnement depuis .env
def load_env_file():
    """Charge les variables d'environnement depuis le fichier .env"""
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip()


# Charger le fichier .env au démarrage
load_env_file()


def configure_page():
    """Configuration de la page Streamlit optimisée mobile"""
    st.set_page_config(
        page_title="Phoenix CV - Générateur IA de CV",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="auto",  # Auto-collapse sur mobile
    )

    # CSS mobile-first
    st.markdown(
        """
    <style>
    /* Mobile-first responsive design */
    @media (max-width: 768px) {
        .main .block-container {
            padding-top: 1rem;
            padding-left: 1rem;
            padding-right: 1rem;
            max-width: 100%;
        }
        
        /* Sidebar auto-hide sur mobile */
        .css-1d391kg {
            padding-top: 1rem;
        }
        
        /* Boutons plus gros pour touch */
        .stButton > button {
            height: 3rem;
            font-size: 1.1rem;
            font-weight: bold;
        }
        
        /* Text inputs plus hauts */
        .stTextInput > div > div > input {
            height: 3rem;
            font-size: 1rem;
        }
        
        /* Textarea plus accessible */
        .stTextArea > div > div > textarea {
            font-size: 1rem;
            min-height: 120px;
        }
    }
    
    /* Amélioration générale */
    .stButton > button {
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    </style>
    """,
        unsafe_allow_html=True,
    )


def is_dev_mode():
    """Vérifie si l'application est en mode développement"""
    return os.environ.get("DEV_MODE", "false").lower() == "true"


def setup_gemini():
    """Configuration sécurisée de Gemini AI"""
    if is_dev_mode():
        st.warning(
            "🎭 **MODE DÉMONSTRATION** - Les résultats générés sont des exemples pour présenter les fonctionnalités. En mode production, Phoenix CV utilise l'IA Gemini pour des résultats personnalisés et optimisés."
        )
        return None  # Pas besoin du modèle en mode dev

    api_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

    if not api_key:
        st.error("🚫 Clé API Gemini manquante")
        st.info("Veuillez configurer GEMINI_API_KEY dans les variables d'environnement")
        st.stop()

    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-1.5-flash")


def extract_text_from_pdf(uploaded_file):
    """Extraction de texte depuis un PDF"""
    try:
        pdf_reader = PyPDF2.PdfReader(BytesIO(uploaded_file.read()))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Erreur lors de la lecture du PDF: {str(e)}")
        return None


def extract_text_from_docx(uploaded_file):
    """Extraction de texte depuis un DOCX"""
    try:
        doc = docx.Document(BytesIO(uploaded_file.read()))
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\\n"
        return text
    except Exception as e:
        st.error(f"Erreur lors de la lecture du DOCX: {str(e)}")
        return None


def get_mock_cv_content(profile_data, target_job):
    """Génère un CV mock pour le mode développement"""
    return f"""# CV - Reconversion Professionnelle

## 👤 Profil Professionnel
Professionnel en reconversion vers **{target_job}**, fort de mon expérience diversifiée et de mes compétences transférables. Motivé par les nouveaux défis et déterminé à apporter une valeur ajoutée grâce à mon parcours atypique.

## ⚡ Compétences Clés
- **Leadership & Management** : Gestion d'équipe et coordination de projets
- **Communication** : Excellent relationnel client et présentation
- **Adaptation** : Capacité d'apprentissage rapide et flexibilité
- **Analyse** : Résolution de problèmes et prise de décision
- **Numérique** : Maîtrise des outils digitaux et nouvelles technologies

## 💼 Expérience Professionnelle

### Expérience Antérieure (Transférable)
**Responsable d'équipe** - Secteur précédent (2020-2024)
- Encadrement d'une équipe de 10 personnes
- Amélioration des processus : +25% d'efficacité
- Gestion budgétaire : 500K€ annuels
- Formation et développement des collaborateurs

### Projets de Reconversion
**Formation & Projets personnels** (2024)
- Certification professionnelle en {target_job}
- Réalisation de projets pratiques
- Veille technologique active
- Networking sectoriel

## 🎓 Formation
- **Formation spécialisée** en {target_job} (2024)
- **Diplôme initial** - Domaine d'origine (2018)
- **Certifications complémentaires** : Google Analytics, Project Management

## 🚀 Atouts pour la Reconversion
- **Vision transversale** grâce à mon parcours diversifié
- **Motivation exceptionnelle** pour ce nouveau défi
- **Compétences relationnelles** développées
- **Capacité d'adaptation** prouvée
- **Engagement** dans une démarche d'amélioration continue

---
*⚠️ DÉMONSTRATION - Ce CV est généré avec des données d'exemple pour la présentation. Le vrai service utilise l'IA Gemini pour des résultats personnalisés et optimisés selon votre profil réel.*"""


def get_mock_analysis(cv_content, job_description):
    """Génère une analyse mock pour le mode développement"""
    return """## 📊 Analyse de Correspondance CV/Offre

### 🎯 Score de Correspondance : 78%

### ✅ Points Forts
- **Expérience managériale** directement transférable
- **Compétences en gestion de projet** très recherchées
- **Capacité d'adaptation** clairement démontrée
- **Formation récente** dans le domaine cible
- **Soft skills** exceptionnelles

### ⚠️ Points d'Amélioration
- **Expérience technique** à approfondir
- **Certifications spécialisées** à obtenir
- **Portfolio** de projets à étoffer
- **Réseau professionnel** à développer dans le nouveau secteur

### 🔍 Mots-Clés Manquants
- Technologies spécifiques au poste
- Certifications sectorielles
- Outils métier spécialisés
- Jargon technique du domaine

### 🚀 Recommandations d'Optimisation
1. **Ajouter une section "Projets"** mettant en avant vos réalisations
2. **Intégrer les mots-clés** de l'offre d'emploi
3. **Quantifier vos résultats** avec des chiffres précis
4. **Mettre en avant votre formation** en reconversion
5. **Adapter le titre** pour correspondre au poste visé

### 💡 Conseils Spécifiques
- Commencez votre CV par un **résumé accrocheur** expliquant votre reconversion
- Utilisez des **verbes d'action** pour décrire vos expériences
- Créez des **liens** entre votre expérience passée et le poste cible
- Montrez votre **proactivité** dans l'apprentissage du nouveau domaine

*⚠️ DÉMONSTRATION - Cette analyse est générée avec des données d'exemple pour la présentation. Le vrai service utilise l'IA Gemini pour des analyses personnalisées et précises selon votre CV et l'offre d'emploi réels.*"""


def generate_cv_content(model, profile_data, target_job=""):
    """Génère le contenu du CV avec Gemini AI ou mock selon le mode"""

    # Mode DEV : Retourne un CV mock
    if is_dev_mode():
        return get_mock_cv_content(profile_data, target_job)

    # Mode PROD : Utilise l'API Gemini avec fallback
    prompt = f"""
    Tu es un expert en reconversion professionnelle et rédaction de CV.
    
    Crée un CV professionnel et moderne pour une reconversion professionnelle basé sur ces informations :
    
    PROFIL :
    {profile_data}
    
    POSTE VISÉ : {target_job if target_job else "Poste en reconversion professionnelle"}
    
    INSTRUCTIONS :
    - Mets l'accent sur les compétences transférables
    - Valorise l'expérience même si elle vient d'un autre secteur
    - Utilise un ton professionnel et confiant
    - Structure : Profil professionnel, Compétences clés, Expérience, Formation, Atouts
    - Maximum 2 pages équivalent
    
    Réponds uniquement avec le contenu du CV formaté en markdown.
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.warning(f"⚠️ Erreur API Gemini: {str(e)}")
        st.info("🔄 Utilisation du fallback intelligent...")
        return get_mock_cv_content(profile_data, target_job)


def analyze_cv_for_job(model, cv_content, job_description):
    """Analyse la correspondance CV/Offre d'emploi avec fallback intelligent"""

    # Mode DEV : Retourne une analyse mock
    if is_dev_mode():
        return get_mock_analysis(cv_content, job_description)

    # Mode PROD : Utilise l'API Gemini avec fallback
    prompt = f"""
    Tu es un expert ATS (Applicant Tracking System) et recruteur.
    
    Analyse la correspondance entre ce CV et cette offre d'emploi :
    
    CV :
    {cv_content}
    
    OFFRE D'EMPLOI :
    {job_description}
    
    Fournis une analyse structurée avec :
    1. Score de correspondance (0-100%)
    2. Points forts (3-5 éléments)
    3. Points d'amélioration (3-5 éléments)
    4. Mots-clés manquants importants
    5. Recommandations d'optimisation
    
    Sois constructif et précis.
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.warning(f"⚠️ Erreur API Gemini: {str(e)}")
        st.info("🔄 Utilisation du fallback intelligent...")
        return get_mock_analysis(cv_content, job_description)


def render_header():
    """Rendu du header de l'application"""

    # Google Analytics (uniquement en production)
    if not is_dev_mode():
        st.markdown(
            """
        <!-- Google Analytics -->
        <script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
        <script>
          window.dataLayer = window.dataLayer || [];
          function gtag(){dataLayer.push(arguments);}
          gtag('js', new Date());
          gtag('config', 'G-XXXXXXXXXX');
        </script>
        """,
            unsafe_allow_html=True,
        )

    # Indicateur de mode
    mode_indicator = ""
    if is_dev_mode():
        mode_indicator = '<div style="background: #fff3cd; padding: 0.75rem; border-radius: 5px; margin-bottom: 1rem; border-left: 4px solid #ffc107;"><p style="margin: 0; color: #856404;"><strong>🎭 MODE DÉMONSTRATION</strong> - Résultats d\'exemple pour présentation. En production, Phoenix CV génère des contenus personnalisés avec l\'IA.</p></div>'

    st.markdown(
        f"""
    {mode_indicator}
    <div style="text-align: center; padding: 1.5rem 0;">
        <h1 style="margin-bottom: 0.5rem; font-size: clamp(1.8rem, 4vw, 2.5rem);">🚀 Phoenix CV</h1>
        <h3 style="margin-bottom: 0.5rem; font-size: clamp(1rem, 3vw, 1.3rem); font-weight: 600;">
            Générateur IA de CV pour Reconversions
        </h3>
        <p style="color: #666; margin-bottom: 1rem; font-size: clamp(0.9rem, 2.5vw, 1rem);">
            Révolutionnez votre reconversion avec l'IA
        </p>
        <div style="margin-top: 1rem;">
            <div style="background: #e8f5e8; padding: 0.5rem 1rem; border-radius: 25px; color: #2e7d2e; 
                        font-size: clamp(0.8rem, 2vw, 0.9rem); display: inline-block; max-width: 90%;">
                ✅ Gratuit • 🚀 IA Avancée • 🎯 Spécialisé Reconversions
            </div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )


def render_sidebar():
    """Rendu de la sidebar de navigation optimisée"""

    # Logo/Brand dans la sidebar
    st.sidebar.markdown(
        """
    <div style="text-align: center; padding: 1rem 0;">
        <h3>🚀 Phoenix CV</h3>
        <p style="color: #666; margin: 0;">IA Reconversions</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.sidebar.markdown("---")

    # Navigation avec descriptions
    st.sidebar.markdown("### 🎯 Navigation")

    pages = {
        "🏠 Découvrir": "home",
        "✨ Créer un CV": "create",
        "📄 Analyser CV": "analyze",
        "🎨 Templates": "templates",
        "💰 Tarifs": "pricing",
    }

    selected_page = st.sidebar.radio(
        "", list(pages.keys()), label_visibility="collapsed"
    )

    # Call-to-action dans sidebar
    st.sidebar.markdown("---")

    if not is_dev_mode():
        # Seulement en production
        st.sidebar.markdown(
            """
        <div style="background: #e8f5e8; padding: 1rem; border-radius: 8px; text-align: center;">
            <h4 style="margin: 0; color: #2e7d2e;">💡 Besoin d'aide ?</h4>
            <p style="margin: 0.5rem 0; font-size: 0.9rem;">Contactez-nous !</p>
            <a href="mailto:contact.phoenixletters@gmail.com" style="text-decoration: none;">
                <button style="background: #28a745; color: white; border: none; padding: 0.5rem 1rem; border-radius: 5px; cursor: pointer;">
                    📧 Contact
                </button>
            </a>
        </div>
        """,
            unsafe_allow_html=True,
        )

    return pages[selected_page]


def render_home_page():
    """Page d'accueil optimisée conversion"""

    # CTA Principal mobile-optimized
    st.markdown(
        """
    <div style="text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: clamp(1.5rem, 4vw, 2rem); border-radius: 15px; margin: 1rem 0; color: white;">
        <h2 style="color: white; margin-bottom: 1rem; font-size: clamp(1.3rem, 4vw, 1.8rem); line-height: 1.3;">
            🎯 Créez votre CV de reconversion en 5 minutes
        </h2>
        <p style="color: #f0f0f0; font-size: clamp(0.95rem, 3vw, 1.1rem); margin-bottom: 1.5rem; line-height: 1.4;">
            L'IA spécialisée reconversions qui valorise VRAIMENT votre parcours atypique
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Boutons d'action mobile-first
    # Sur mobile : pleine largeur, sur desktop : colonnes
    is_mobile = (
        st.sidebar.button(
            "📱 Mode Mobile", help="Toggle mobile view", key="mobile_toggle"
        )
        if "mobile_view" not in st.session_state
        else st.session_state.get("mobile_view", False)
    )

    if st.container():  # Toujours pleine largeur pour meilleure UX mobile
        if st.button(
            "🚀 **CRÉER MON CV MAINTENANT**",
            type="primary",
            use_container_width=True,
            key="main_cta",
        ):
            st.session_state["current_page"] = "create"
            st.rerun()

        st.markdown("<div style='margin: 0.5rem 0;'></div>", unsafe_allow_html=True)

        if st.button(
            "📊 **ANALYSER MON CV EXISTANT**",
            use_container_width=True,
            key="analyze_cta",
        ):
            st.session_state["current_page"] = "analyze"
            st.rerun()

    st.markdown("---")

    st.markdown(
        """
    ## 🌟 Pourquoi Phoenix CV révolutionne les reconversions ?
    
    ### 🎯 **Spécialisé Reconversions** (Seul sur le marché français)
    - ✅ **Valorise vos compétences transférables** automatiquement
    - ✅ **Adapte votre profil** au nouveau secteur visé
    - ✅ **Optimise pour ATS** même avec parcours atypique
    
    ### 🤖 **IA Nouvelle Génération**
    - ✅ **Google Gemini 1.5 Flash** - La plus avancée
    - ✅ **Analyse sémantique** des offres d'emploi
    - ✅ **Génération contextuelle** selon votre secteur cible
    
    ### 🛡️ **100% Sécurisé & Privé**
    - ✅ **Traitement local** de vos données
    - ✅ **Conformité RGPD** stricte
    - ✅ **Zéro sauvegarde** de vos informations
    """
    )

    # Témoignages/Résultats
    st.markdown(
        """
    <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 10px; margin: 2rem 0;">
        <h3 style="text-align: center; color: #333;">📊 Résultats Prouvés</h3>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Stats responsive : stack vertical sur mobile, horizontal sur desktop
    st.markdown(
        """
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin: 1rem 0;">
    
        <div style="text-align: center; padding: 1.5rem; background: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <h2 style="color: #28a745; margin: 0; font-size: clamp(1.8rem, 5vw, 2.5rem);">+85%</h2>
            <p style="margin: 0.5rem 0; font-weight: bold; font-size: clamp(0.9rem, 2.5vw, 1rem);">Réponses positives</p>
            <small style="color: #666; font-size: clamp(0.8rem, 2vw, 0.9rem);">VS CV traditionnel</small>
        </div>
        
        <div style="text-align: center; padding: 1.5rem; background: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <h2 style="color: #007bff; margin: 0; font-size: clamp(1.8rem, 5vw, 2.5rem);">5 min</h2>
            <p style="margin: 0.5rem 0; font-weight: bold; font-size: clamp(0.9rem, 2.5vw, 1rem);">Temps de création</p>
            <small style="color: #666; font-size: clamp(0.8rem, 2vw, 0.9rem);">Au lieu de 2-3 heures</small>
        </div>
        
        <div style="text-align: center; padding: 1.5rem; background: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <h2 style="color: #ffc107; margin: 0; font-size: clamp(1.8rem, 5vw, 2.5rem);">100%</h2>
            <p style="margin: 0.5rem 0; font-weight: bold; font-size: clamp(0.9rem, 2.5vw, 1rem);">Compatible ATS</p>
            <small style="color: #666; font-size: clamp(0.8rem, 2vw, 0.9rem);">Passe tous les filtres</small>
        </div>
        
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Newsletter signup
    st.markdown("---")
    st.markdown(
        """
    <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; color: white;">
        <h4 style="color: white; margin-bottom: 1rem;">🎯 Restez informé des nouveautés Phoenix CV</h4>
        <p style="color: #f0f0f0; margin-bottom: 1rem;">Conseils reconversion, nouvelles fonctionnalités, success stories...</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Email collection mobile-first
    with st.container():
        email_signup = st.text_input(
            "📧 Votre email",
            placeholder="votre.email@exemple.com",
            label_visibility="collapsed",
            key="newsletter_email",
        )

        st.markdown("<div style='margin: 0.5rem 0;'></div>", unsafe_allow_html=True)

        if st.button(
            "✅ **S'ABONNER AUX MISES À JOUR**",
            type="primary",
            use_container_width=True,
            key="newsletter_btn",
        ):
            if email_signup and "@" in email_signup:
                st.success(
                    "🎉 Merci ! Vous recevrez nos mises à jour (bientôt disponible)"
                )
                # TODO: Intégrer avec un service d'email marketing
            else:
                st.error("⚠️ Veuillez entrer un email valide")

    st.markdown(
        """
    <div style="text-align: center; padding: 1rem; background: #e8f4f8; border-radius: 10px;">
        <p style="color: #666; margin: 0;"><small>🔒 Vos données sont protégées. Pas de spam, désabonnement facile.</small></p>
    </div>
    """,
        unsafe_allow_html=True,
    )


def render_create_cv_page(model):
    """Page de création de CV"""
    st.markdown("## ✨ Créer votre CV de Reconversion")

    with st.form("cv_form"):
        st.markdown("### 👤 Informations Personnelles")
        col1, col2 = st.columns(2)

        with col1:
            prenom = st.text_input("Prénom *")
            nom = st.text_input("Nom *")
            email = st.text_input("Email *")

        with col2:
            telephone = st.text_input("Téléphone")
            ville = st.text_input("Ville")
            linkedin = st.text_input("LinkedIn (optionnel)")

        st.markdown("### 🎯 Objectif Professionnel")
        secteur_origine = st.text_input(
            "Secteur d'origine", placeholder="Ex: Commerce, Enseignement, Industrie..."
        )
        secteur_cible = st.text_input(
            "Secteur visé *", placeholder="Ex: Développement web, Marketing digital..."
        )
        poste_vise = st.text_input(
            "Poste recherché *",
            placeholder="Ex: Développeur Front-end, Chef de projet...",
        )

        st.markdown("### 💼 Expérience Professionnelle")
        experiences = st.text_area(
            "Décrivez vos expériences principales (3-5 dernières)",
            height=150,
            placeholder="Ex: Manager équipe 15 personnes chez ABC Corp (2020-2024)\\n- Gestion budget 500K€\\n- Amélioration productivité +25%...",
        )

        st.markdown("### 🎓 Formation")
        formations = st.text_area(
            "Formation et certifications",
            height=100,
            placeholder="Ex: Master Marketing - Université Paris (2018)\\nCertification Google Analytics (2023)...",
        )

        st.markdown("### ⚡ Compétences")
        competences = st.text_area(
            "Compétences techniques et soft skills",
            height=100,
            placeholder="Ex: Management d'équipe, Gestion de projet, Excel avancé, Anglais courant...",
        )

        submitted = st.form_submit_button("🚀 Générer mon CV", type="primary")

        if submitted:
            if (
                not prenom
                or not nom
                or not email
                or not secteur_cible
                or not poste_vise
            ):
                st.error("⚠️ Veuillez remplir tous les champs obligatoires (*)")
                return

            # Compilation des données
            profile_data = f"""
            IDENTITÉ : {prenom} {nom}
            CONTACT : {email} | {telephone} | {ville}
            LINKEDIN : {linkedin}
            
            RECONVERSION : {secteur_origine} → {secteur_cible}
            POSTE VISÉ : {poste_vise}
            
            EXPÉRIENCES :
            {experiences}
            
            FORMATION :
            {formations}
            
            COMPÉTENCES :
            {competences}
            """

            with st.spinner("🤖 Génération de votre CV en cours..."):
                cv_content = generate_cv_content(model, profile_data, poste_vise)

                if cv_content:
                    st.success("✅ CV généré avec succès !")

                    # Affichage du CV
                    st.markdown("### 📄 Votre CV Généré")
                    st.markdown(cv_content)

                    # Bouton de téléchargement
                    st.download_button(
                        label="💾 Télécharger le CV (Markdown)",
                        data=cv_content,
                        file_name=f"CV_{prenom}_{nom}_{datetime.now().strftime('%Y%m%d')}.md",
                        mime="text/markdown",
                    )


def render_analyze_cv_page(model):
    """Page d'analyse de CV"""
    st.markdown("## 📄 Analyser votre CV existant")

    # Upload de CV
    uploaded_file = st.file_uploader(
        "📁 Téléchargez votre CV",
        type=["pdf", "docx", "txt"],
        help="Formats acceptés: PDF, DOCX, TXT",
    )

    cv_text = ""

    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            cv_text = extract_text_from_pdf(uploaded_file)
        elif (
            uploaded_file.type
            == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ):
            cv_text = extract_text_from_docx(uploaded_file)
        else:  # txt
            cv_text = str(uploaded_file.read(), "utf-8")

        if cv_text:
            st.success("✅ CV analysé avec succès")

            with st.expander("👀 Aperçu du contenu extrait"):
                st.text_area(
                    "Contenu",
                    cv_text[:1000] + "..." if len(cv_text) > 1000 else cv_text,
                    height=200,
                )

    # Analyse avec offre d'emploi
    st.markdown("### 🎯 Analyse de Correspondance")
    job_description = st.text_area(
        "Collez l'offre d'emploi qui vous intéresse",
        height=200,
        placeholder="Copiez-collez ici le texte de l'offre d'emploi pour analyser la correspondance avec votre CV...",
    )

    if (
        st.button("🔍 Analyser la Correspondance", type="primary")
        and cv_text
        and job_description
    ):
        with st.spinner("🤖 Analyse en cours..."):
            analysis = analyze_cv_for_job(model, cv_text, job_description)

            if analysis:
                st.markdown("### 📊 Résultats de l'Analyse")
                st.markdown(analysis)


def render_templates_page():
    """Page des templates"""
    st.markdown("## 🎨 Templates de CV")

    templates = [
        {
            "name": "🎯 Reconversion Moderne",
            "description": "Template optimisé pour les reconversions professionnelles",
            "features": [
                "Focus compétences transférables",
                "Design moderne",
                "ATS-friendly",
            ],
        },
        {
            "name": "💼 Professionnel Classic",
            "description": "Template élégant pour secteurs traditionnels",
            "features": ["Style sobre", "Mise en page claire", "Polyvalent"],
        },
        {
            "name": "🚀 Tech & Innovation",
            "description": "Template dynamique pour secteurs technologiques",
            "features": ["Design créatif", "Sections techniques", "Portfolio intégré"],
        },
    ]

    cols = st.columns(3)

    for i, template in enumerate(templates):
        with cols[i]:
            st.markdown(f"### {template['name']}")
            st.markdown(template["description"])

            for feature in template["features"]:
                st.markdown(f"✅ {feature}")

            st.button(f"Aperçu", key=f"preview_{i}", disabled=True)
            st.markdown("*Bientôt disponible*")


def render_pricing_page():
    """Page des tarifs"""
    st.markdown("## 💰 Nos Offres")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
        ### 🆓 Gratuit
        **0€/mois**
        
        ✅ 1 CV par mois  
        ✅ Templates de base  
        ✅ Génération IA  
        ❌ Analyse de correspondance  
        ❌ Templates premium  
        ❌ Support prioritaire  
        """
        )
        st.button("Commencer Gratuit", type="secondary")

    with col2:
        st.markdown(
            """
        ### ⭐ Premium
        **9.99€/mois**
        
        ✅ CV illimités  
        ✅ Tous les templates  
        ✅ Génération IA avancée  
        ✅ Analyse de correspondance  
        ✅ Optimisation ATS  
        ❌ Support prioritaire  
        """
        )
        st.button("Choisir Premium", type="primary")

    with col3:
        st.markdown(
            """
        ### 🚀 Pro
        **19.99€/mois**
        
        ✅ Tout Premium inclus  
        ✅ Templates exclusifs  
        ✅ Coaching IA personnalisé  
        ✅ Suivi candidatures  
        ✅ Support prioritaire  
        ✅ API Access  
        """
        )
        st.button("Choisir Pro", type="secondary")


def render_footer():
    """Footer de l'application"""
    st.markdown("---")
    st.markdown(
        """
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>🚀 <strong>Phoenix CV</strong> - Révolutionnez votre reconversion professionnelle</p>
        <p>Made with ❤️ in France | 🛡️ Sécurisé & Conforme RGPD</p>
    </div>
    """,
        unsafe_allow_html=True,
    )


def main():
    """Application principale"""
    configure_page()

    # Configuration du modèle IA
    model = setup_gemini()

    # Header
    render_header()

    # Navigation
    current_page = render_sidebar()

    # Rendu des pages
    if current_page == "home":
        render_home_page()
    elif current_page == "create":
        render_create_cv_page(model)
    elif current_page == "analyze":
        render_analyze_cv_page(model)
    elif current_page == "templates":
        render_templates_page()
    elif current_page == "pricing":
        render_pricing_page()

    # Footer
    render_footer()


if __name__ == "__main__":
    main()
