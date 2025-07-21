import streamlit as st
import os
from dotenv import load_dotenv
from services.api_client import (
    suggerer_competences_transferables,
    get_france_travail_offer_details,
    analyser_culture_entreprise,
    APIError
)
from services.letter_service import (
    generer_lettre,
    extraire_mots_cles_annonce,
    evaluate_letter
)
from models.letter_request import LetterRequest
from models.user_profile import UserProfile
from services.content_extractor import extract_cv_content, extract_annonce_content, FileProcessingError
from services.trajectory_service import generate_reconversion_plan
from services.rgpd_manager import RGPDUserManager, SecurePremiumStorage, RGPDViolationError # Nouveaux imports
from services.data_anonymizer import DataAnonymizer # Ajout pour l'anonymisation
from services.cv_optimization_service import CvOptimizationService # Ajout pour l'optimisation du CV
from services.security_scanner import SecurityScanner, SecurityScanError # Ajout pour le scan de sécurité
import logging
import random # Ajout pour les astuces aléatoires
from docx import Document # Ajout pour la génération DOCX
import io # Ajout pour la gestion des flux de bytes en mémoire
import time # Ajout pour la logique de limitation de taux
import uuid # Ajout pour la génération d'UUID
import tempfile # Ajout pour la gestion des fichiers temporaires

load_dotenv() # Charge les variables d'environnement à partir du fichier .env

# --- Configuration de la Page ---
st.set_page_config(
    page_title="Générateur de Lettre de Motivation IA",
    page_icon="🤖",
    layout="centered",
)

# --- Conseils utiles (pour l'attente) ---
TIPS = [
    "💡 Conseil utile : Saviez-vous que 80% des recruteurs parcourent d'abord votre CV en diagonale ? Assurez-vous que les informations clés sont visibles en un coup d'œil !",
    "💡 Conseil utile : Une lettre de motivation n'est pas un résumé de votre CV. C'est une histoire qui explique POURQUOI vous êtes le candidat idéal pour CE poste.",
    "💡 Conseil utile : L'IA est un outil puissant, mais la touche humaine reste irremplaçable. Relisez toujours et personnalisez !",
    "💡 Conseil utile : Votre réseau professionnel est une mine d'or. Cultivez-le, échangez, et n'hésitez pas à demander conseil.",
    "💡 Conseil utile : La persévérance est la clé. Chaque refus est une opportunité d'apprendre et de s'améliorer.",
    "💡 Conseil utile : Un bon prompt pour l'IA, c'est comme une bonne question à un expert : plus elle est précise, plus la réponse sera pertinente.",
    "💡 Conseil utile : La clarté et la concision sont vos meilleurs atouts dans toute communication professionnelle.",
    "💡 Conseil utile : N'ayez pas peur de mettre en avant vos compétences transférables, surtout en reconversion. Elles sont votre force !",
    "💡 Conseil utile : Préparez-vous aux entretiens en anticipant les questions et en ayant des exemples concrets de vos réalisations.",
    "💡 Conseil utile : Le marché du travail évolue constamment. Restez curieux et continuez à apprendre tout au long de votre carrière.",
]

# --- Fonctions de l'Application ---

def generate_docx(text_content: str) -> bytes:
    """Génère un document DOCX à partir d'une chaîne de caractères."""
    document = Document()
    # Remplacer les doubles retours à la ligne par des paragraphes pour un meilleur formatage
    paragraphs = text_content.split('\n\n')
    for para_text in paragraphs:
        document.add_paragraph(para_text)
    
    # Sauvegarder le document en mémoire
    byte_io = io.BytesIO()
    document.save(byte_io)
    byte_io.seek(0) # Remettre le curseur au début du fichier
    return byte_io.getvalue()

def main():

    """
    Fonction principale de l'application Streamlit.
    """
    st.title("📄 Générateur de Lettre de Motivation IA")
    st.subheader("Spécialement affiné pour la reconversion professionnelle")

    # Initialiser les variables de session si elles n'existent pas
    if 'annonce_content' not in st.session_state:
        st.session_state.annonce_content = ""
    if 'user_id' not in st.session_state:
        st.session_state.user_id = "simulated_user_" + str(uuid.uuid4()) # ID utilisateur simulé
    
    # Initialisation des gestionnaires RGPD
    rgpd_user_manager = RGPDUserManager()
    try:
        secure_storage = SecurePremiumStorage()
    except ValueError as e:
        st.error(f"Erreur de configuration RGPD : {e}. Veuillez définir la variable d'environnement 'USER_DATA_ENCRYPTION_KEY'.")
        st.stop()

    data_anonymizer = DataAnonymizer() # Instanciation du DataAnonymizer
    cv_optimization_service = CvOptimizationService() # Instanciation du CvOptimizationService
    security_scanner = SecurityScanner() # Instanciation du SecurityScanner

    # --- Simulation du niveau d'abonnement et du consentement (pour la démo) ---
    st.sidebar.header("Paramètres Utilisateur (Démo RGPD)")
    user_tier = st.sidebar.radio(
        "Niveau d'abonnement simulé :",
        ('free', 'premium', 'premium_plus'),
        index=0, # 'free' par défaut
        key='user_tier_radio'
    )
    explicit_consent = st.sidebar.checkbox(
        "Je consens à la conservation de mes données (CV anonymisé, lettres) pour la durée de mon abonnement.",
        value=False,
        key='explicit_consent_checkbox'
    )

    if user_tier != 'free' and not explicit_consent:
        st.sidebar.warning("Pour les abonnements Premium, le consentement explicite est requis pour la conservation des données.")

    # --- Bandeau de consentement RGPD ---
    st.info("""
    **Protection des données** : Vos données (CV, lettre générée) sont traitées **uniquement en mémoire** et **supprimées immédiatement** après génération. Aucune sauvegarde n'est effectuée sur nos serveurs. Le traitement IA est réalisé via Gemini (Google). Pour plus de détails, consultez notre politique de confidentialité (à venir).
    """)

    

    with st.expander("💡 Comment ça marche ? / À propos de l'outil"):
        st.markdown("""
        Bienvenue dans votre **Générateur de Lettre de Motivation IA** ! Cet outil a été conçu pour vous aider à rédiger des lettres percutantes et personnalisées, en particulier si vous êtes en **reconversion professionnelle**.

        **Notre Philosophie :**
        Nous croyons que chaque parcours est unique. L'IA n'est pas là pour remplacer votre créativité, mais pour l'amplifier. Elle agit comme un co-pilote intelligent, transformant vos informations brutes (CV, annonce) en un narratif convaincant, tout en valorisant votre expérience et votre motivation.

        **Comment ça marche ?**
        1.  **Votre CV & l'Annonce :** Fournissez votre CV (PDF ou TXT) et le texte de l'annonce. L'IA analyse ces documents pour comprendre votre profil et les exigences du poste.
        2.  **Personnalisation :** Choisissez le ton souhaité et, si vous êtes en reconversion, donnez des détails sur votre ancien et nouveau domaine. Plus vous êtes précis, plus la lettre sera pertinente !
        3.  **Génération Intelligente :** Notre IA, entraînée spécifiquement pour la rédaction de lettres de motivation, rédige un brouillon. Elle est particulièrement douée pour transformer les parcours de reconversion en atouts, en mettant en lumière vos compétences transférables et votre motivation.
        4.  **Édition & Téléchargement :** La lettre générée apparaît dans une zone éditable. Vous pouvez la peaufiner, la personnaliser davantage, puis la télécharger au format TXT ou DOCX, ou la copier directement dans votre presse-papiers.

        **Pourquoi cet outil ?**
        Dans un marché du travail compétitif, une lettre de motivation bien rédigée fait toute la différence. Cet outil vous fait gagner du temps, réduit le stress de la page blanche, et vous aide à présenter votre candidature sous son meilleur jour, en particulier lorsque votre parcours nécessite une explication claire et valorisante.

        Né de l'expérience des défis de la reconversion, cet outil est conçu pour transformer vos doutes en atouts et vous guider vers un nouveau chapitre professionnel.
        """)

    st.markdown("""
    Cet outil vous aide à créer une lettre de motivation percutante en quelques secondes.
    1.  **Chargez votre CV** (PDF ou TXT)
    2.  **Chargez l'annonce** (TXT)
    3.  **Précisez votre situation** et laissez l'IA transformer votre parcours en atout !
    """)

    # --- Zone de Téléversement ---
    uploaded_cv = st.file_uploader(
        "1. Chargez votre CV",
        type=['pdf', 'txt'],
        help="Le fichier ne doit pas dépasser 5MB."
    )

    uploaded_annonce = st.file_uploader(
        "2. Chargez l'annonce",
        type=['txt', 'pdf'],
        help="Un simple fichier texte avec le contenu de l'annonce."
    )

    st.markdown("**OU**")

    offer_id = st.text_input(
        "2.1. Entrez l'ID d'une offre France Travail (si vous ne chargez pas de fichier annonce)",
        help="Ex: 167XQYV"
    )

    # --- Options de Génération ---
    st.markdown("**3. Personnalisez votre lettre**")
    col1, col2 = st.columns(2)

    with col1:
        ton_choisi = st.selectbox(
            "Choisissez le ton",
            ("Formel", "Dynamique", "Sobre", "Créatif", "Startup", "Associatif"),
            index=0, # "Formel" par défaut
            help="Le ton influence le style d'écriture de l'IA."
        )

    with col2:
        est_reconversion = st.checkbox(
            "C'est une reconversion",
            value=True, # Coché par défaut pour mettre en avant la fonctionnalité
            help="Cochez cette case si vous changez de carrière. L'IA adaptera son discours pour valoriser votre parcours."
        )

    ancien_domaine = ""
    nouveau_domaine = ""
    competences_transferables = ""

    if est_reconversion:
        st.markdown("**Détails de votre reconversion :**")
        ancien_domaine = st.text_input(
            "Votre ancien domaine d'activité (ex: Marketing, Comptabilité, Bâtiment)",
            help="Soyez précis pour aider l'IA à faire les liens."
        )
        nouveau_domaine = st.text_input(
            "Votre nouveau domaine d'activité souhaité (ex: Cybersécurité, Développement Web, Data Science)",
            help="C'est ici que vous projetez votre avenir !"
        )

        # Initialiser la session_state pour les compétences suggérées si elle n'existe pas
        if 'suggested_competences' not in st.session_state:
            st.session_state.suggested_competences = ""

        # Bouton pour suggérer les compétences
        if st.button("✨ Suggérer les compétences transférables"):
            if ancien_domaine and nouveau_domaine:
                with st.spinner("L'IA analyse les domaines pour suggérer les compétences..."):
                    try:
                        suggested_text = suggerer_competences_transferables(ancien_domaine, nouveau_domaine)
                        st.session_state.suggested_competences = suggested_text
                        st.success("Compétences suggérées ! Vous pouvez les modifier si besoin.")
                    except APIError as e:
                        st.error(f"❌ Erreur lors de la suggestion des compétences. Problème avec l'API Gemini : {e}. Veuillez réessayer plus tard.")
                    except Exception as e:
                        st.error(f"🚨 Une erreur inattendue est survenue lors de la suggestion : {e}")
            else:
                st.warning("Veuillez renseigner l'ancien et le nouveau domaine pour obtenir des suggestions.")

        # Zone de texte pour afficher/éditer les compétences transférables
        competences_transferables = st.text_area(
            "Compétences clés transférables (vous pouvez éditer ou utiliser la suggestion) :",
            value=st.session_state.suggested_competences,
            help="Listez les compétences de votre ancienne carrière qui sont pertinentes pour votre nouveau projet."
        )

    # --- Section Analyse de la Culture d'Entreprise (Mirror Match) ---
    st.markdown("**4. Affinez avec l'analyse de la culture d'entreprise (Optionnel)**")
    with st.expander("🔍 Analyse de la Culture d'Entreprise (Mirror Match)"):
        st.markdown("""
        Collez le contenu de la page "À propos" de l'entreprise et/ou des posts LinkedIn récents.
        L'IA analysera ces informations pour adapter le ton et les valeurs de votre lettre.
        """)
        company_about_page = st.text_area(
            "Contenu de la page 'À propos' de l'entreprise :",
            key="company_about_page",
            height=150,
            help="Copiez-collez le texte de la section 'À propos' ou 'Notre histoire' du site web de l'entreprise."
        )
        linkedin_posts = st.text_area(
            "Posts LinkedIn récents (un post par ligne) :",
            key="linkedin_posts",
            height=150,
            help="Copiez-collez quelques posts récents de la page LinkedIn de l'entreprise, un par ligne."
        )



    # --- Section Trajectory Builder ---
    st.markdown("**5. Construisez votre Trajectoire de Reconversion (Expérimental)**")
    with st.expander("🚀 Trajectory Builder"):
        st.markdown("""
        Décrivez votre profil actuel et votre objectif de reconversion pour obtenir un plan détaillé.
        """)
        current_skills_input = st.text_area(
            "Vos compétences actuelles (séparées par des virgules) :",
            key="current_skills_input",
            height=100,
            help="Ex: Gestion de projet, Marketing digital, Analyse de données"
        )
        current_experience_input = st.text_area(
            "Votre expérience professionnelle actuelle ou passée :",
            key="current_experience_input",
            height=150,
            help="Décrivez vos rôles, responsabilités et réalisations clés."
        )
        aspirations_input = st.text_area(
            "Vos aspirations de carrière ou le nouveau domaine souhaité :",
            key="aspirations_input",
            height=100,
            help="Ex: Devenir Data Scientist, Travailler dans la cybersécurité, Lancer ma startup"
        )
        target_role_input = st.text_input(
            "Rôle cible de reconversion (ex: Développeur Python, Analyste SOC) :",
            key="target_role_input",
            help="Soyez précis sur le rôle que vous visez."
        )

        if st.button("✨ Générer mon Plan de Reconversion"):
            if current_skills_input and current_experience_input and aspirations_input and target_role_input:
                with st.spinner("L'IA élabore votre plan de reconversion..."):
                    try:
                        user_profile = UserProfile(
                            current_skills=[s.strip() for s in current_skills_input.split(',') if s.strip()],
                            current_experience=current_experience_input,
                            aspirations=aspirations_input
                        )
                        reconversion_plan = generate_reconversion_plan(user_profile, target_role_input)
                        st.success("Votre plan de reconversion a été généré !")
                        
                        st.subheader(f" Objectif : {reconversion_plan.goal}")
                        st.write(reconversion_plan.summary)
                        
                        # Affichage des métadonnées du plan
                        col1, col2 = st.columns(2)
                        with col1:
                            if reconversion_plan.estimated_total_duration_weeks:
                                st.metric("⏱️ Durée totale", f"{reconversion_plan.estimated_total_duration_weeks} semaines")
                        with col2:
                            if reconversion_plan.success_probability is not None:
                                st.metric(" Probabilité de succès", f"{reconversion_plan.success_probability:.0%}")

                        st.markdown("###  Étapes du Plan de Reconversion")
                        
                        for i, step in enumerate(reconversion_plan.steps):
                            with st.expander(f"**Étape {i+1}: {step.title}**", expanded=i==0):
                                st.write(step.description)
                                
                                if step.duration_weeks:
                                    st.info(f"⏱️ **Durée estimée** : {step.duration_weeks} semaines")
                                
                                if step.resources:
                                    st.markdown("####  Ressources Recommandées")
                                    
                                    for resource in step.resources:
                                        # Icônes par type de ressource
                                        icons = {
                                            "cours_en_ligne": "📚",
                                            "livre": "📖", 
                                            "certification": "🏅",
                                            "mentorat": "🤝",
                                            "projet_pratique": "💡",
                                            "article": "📰",
                                            "outil": "⚙️",
                                            "autre": "🔗"
                                        }
                                        
                                        icon = icons.get(resource.type, "")
                                        
                                        # Affichage propre de chaque ressource
                                        st.markdown(f"**{icon} {resource.name}**")
                                        
                                        if resource.description:
                                            st.write(f" {resource.description}")
                                        
                                        if resource.link:
                                            st.write(f" [Accéder à la ressource]({resource.link})")
                                        
                                        st.write("--- ")  # Séparateur entre ressources

                    except APIError as e:
                        st.error(f"Impossible de générer le plan de reconversion : {e}")
                    except Exception as e:
                        st.error(f"Une erreur inattendue est survenue lors de la génération du plan : {e}")
            else:
                st.warning("Veuillez remplir tous les champs du profil et du rôle cible pour générer le plan.")

    # --- Section Optimisation CV (Premium) ---
    st.markdown("**6. Optimisez votre CV (Fonctionnalité Premium)**")
    with st.expander("📝 Optimisation de CV"):
        if user_tier == 'free':
            st.info("Cette fonctionnalité est réservée aux abonnements Premium et Premium Plus.")
        else:
            st.markdown("""
            Optimisez votre CV pour mieux mettre en avant vos compétences transférables.
            """)
            if uploaded_cv is None:
                st.warning("Veuillez d'abord charger votre CV pour utiliser cette fonctionnalité.")
            else:
                if st.button("✨ Optimiser mon CV"):
                    if competences_transferables:
                        with st.spinner("L'IA optimise votre CV..."):
                            try:
                                # Récupérer le contenu du CV uploadé
                                cv_content_for_opt = extract_cv_content(uploaded_cv)
                                optimized_cv_text = cv_optimization_service.optimize_cv(
                                    cv_content_for_opt, competences_transferables, user_tier
                                )
                                st.success("Votre CV a été optimisé !")
                                st.text_area(
                                    "Voici votre CV optimisé (vous pouvez le copier) :",
                                    optimized_cv_text,
                                    height=400,
                                    key="optimized_cv_editor"
                                )
                                # Option de téléchargement DOCX pour le CV optimisé
                                docx_file_opt = generate_docx(optimized_cv_text)
                                st.download_button(
                                    label="📄 Télécharger le CV optimisé (DOCX)",
                                    data=docx_file_opt,
                                    file_name='cv_optimise.docx',
                                    mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                                )
                            except APIError as e:
                                st.error(f"Impossible d'optimiser le CV : {e}")
                            except FileProcessingError as e:
                                st.error(f"Erreur lors du traitement du CV pour l'optimisation : {e}")
                            except Exception as e:
                                st.error(f"Une erreur inattendue est survenue lors de l'optimisation du CV : {e}")
                    else:
                        st.warning("Veuillez d'abord suggérer ou entrer vos compétences transférables.")

    # --- Boutons d'action ---
    col_buttons_1, col_buttons_2 = st.columns(2)

    # --- Logique de Limitation de Taux (Rate Limiting) ---
    if 'last_generation_time' not in st.session_state:
        st.session_state.last_generation_time = 0

    cooldown_time = 60 # en secondes
    time_since_last_generation = time.time() - st.session_state.last_generation_time
    is_on_cooldown = time_since_last_generation < cooldown_time

    with col_buttons_1:
        if st.button("✨ Générer la lettre de motivation", disabled=is_on_cooldown):
            if is_on_cooldown:
                st.warning(f"Veuillez attendre {int(cooldown_time - time_since_last_generation)} secondes avant de générer une nouvelle lettre.")
            elif uploaded_cv is not None and (uploaded_annonce is not None or offer_id):
                with st.spinner("Préparation des documents... Votre CV et l'annonce sont en cours d'analyse."):
                    try:
                        progress_text = st.empty()
                        progress_bar = st.progress(0)

                        progress_text.info("Étape 1/3 : Lecture et traitement de vos fichiers...")
                        progress_bar.progress(33)
                        
                        cv_content = ""
                        annonce_content = ""

                        # --- Validation et Lecture Sécurisée du CV ---
                        try:
                            with tempfile.NamedTemporaryFile(delete=False) as temp_cv_file:
                                temp_cv_file.write(uploaded_cv.getvalue())
                                temp_cv_path = temp_cv_file.name
                            
                            if not security_scanner.scan_file(temp_cv_path):
                                st.error("🚨 Fichier CV détecté comme potentiellement malveillant. Scan de sécurité échoué.")
                                st.stop()

                            cv_content = extract_cv_content(uploaded_cv)
                        except FileProcessingError as e:
                            st.error(f"🚨 Erreur lors du traitement du CV : {e}")
                            st.stop()
                        except SecurityScanError as e:
                            st.error(f"🚨 Erreur de sécurité lors du scan du CV : {e}")
                            st.stop()
                        finally:
                            if 'temp_cv_path' in locals() and os.path.exists(temp_cv_path):
                                os.remove(temp_cv_path) # S'assurer que le fichier temporaire est supprimé

                        annonce_content = ""
                        offer_details = None # Initialiser offer_details

                        if offer_id: # Si un ID d'offre est fourni
                            try:
                                offer_details = get_france_travail_offer_details(offer_id)
                                if offer_details and 'description' in offer_details:
                                    annonce_content = offer_details['description']
                                    st.session_state.annonce_content = annonce_content # Sauvegarde dans session_state
                                    st.info(f"Annonce récupérée via France Travail API (ID: {offer_id}).")
                                else:
                                    st.warning("Impossible de récupérer la description de l'offre via l'API. Veuillez vérifier l'ID.")
                                    return # Arrête l'exécution si l'API échoue
                            except APIError as e:
                                st.error(f"Erreur lors de la récupération de l'offre France Travail : {e}. Veuillez vérifier l'ID ou réessayer plus tard.")
                                return # Arrête l'exécution en cas d'erreur API
                        elif uploaded_annonce is not None: # Sinon, si un fichier est uploadé
                            try:
                                with tempfile.NamedTemporaryFile(delete=False) as temp_annonce_file:
                                    temp_annonce_file.write(uploaded_annonce.getvalue())
                                    temp_annonce_path = temp_annonce_file.name

                                if not security_scanner.scan_file(temp_annonce_path):
                                    st.error("🚨 Fichier annonce détecté comme potentiellement malveillant. Scan de sécurité échoué.")
                                    st.stop()

                                annonce_content = extract_annonce_content(uploaded_annonce)
                                st.session_state.annonce_content = annonce_content # Sauvegarde dans session_state
                            except FileProcessingError as e:
                                st.error(f"🚨 Erreur lors du traitement de l'annonce : {e}")
                                st.stop()
                            except SecurityScanError as e:
                                st.error(f"🚨 Erreur de sécurité lors du scan de l'annonce : {e}")
                                st.stop()
                            finally:
                                if 'temp_annonce_path' in locals() and os.path.exists(temp_annonce_path):
                                    os.remove(temp_annonce_path) # S'assurer que le fichier temporaire est supprimé
                        else:
                            st.warning("Veuillez charger une annonce ou fournir un ID d'offre France Travail.")
                            return # Arrête l'exécution si aucune annonce n'est fournie

                        progress_text.info(f"Étape 2/3 : L'intelligence artificielle rédige votre lettre... Cela peut prendre quelques instants.\n\n{random.choice(TIPS)}")  # nosec B311
                        progress_bar.progress(66)
                        # Génération de la lettre
                        company_insights = None
                        if company_about_page or linkedin_posts:
                            with st.spinner("Étape 2.5/3 : Analyse de la culture d'entreprise..."):
                                try:
                                    company_insights = analyser_culture_entreprise(company_about_page, linkedin_posts)
                                    st.success("Analyse de la culture d'entreprise terminée !")
                                except APIError as e:
                                    st.warning(f"Impossible d'analyser la culture d'entreprise. Problème avec l'API Gemini : {e}. La lettre sera générée sans cette personnalisation. Veuillez réessayer plus tard.")
                                except Exception as e:
                                    st.warning(f"Une erreur inattendue est survenue lors de l'analyse de la culture d'entreprise : {e}. La lettre sera générée sans cette personnalisation.")

                        request_data = LetterRequest(
                            cv_contenu=cv_content,
                            annonce_contenu=annonce_content,
                            ton_souhaite=ton_choisi.lower(),
                            est_reconversion=est_reconversion,
                            ancien_domaine=ancien_domaine,
                            nouveau_domaine=nouveau_domaine,
                            competences_transferables=competences_transferables,
                            offer_details=offer_details,
                            company_insights=company_insights, # Ajout des insights de l'entreprise
                            user_tier=user_tier # Ajout du niveau d'abonnement
                        )
                        lettre_response = generer_lettre(request_data)
                        lettre_generee = lettre_response.lettre_generee

                        # --- Gestion des utilisateurs et RGPD (pour la démo) ---
                        if rgpd_user_manager.can_store_data(user_tier, explicit_consent):
                            try:
                                # Anonymisation des données avant stockage
                                anonymized_cv_content = data_anonymizer.anonymize_text(cv_content)
                                anonymized_lettre_generee = data_anonymizer.anonymize_text(lettre_generee)

                                secure_storage.store_user_document(
                                    st.session_state.user_id, 'cv', anonymized_cv_content, user_tier
                                )
                                secure_storage.store_user_document(
                                    st.session_state.user_id, 'letter', anonymized_lettre_generee, user_tier
                                )
                                st.success("Vos données (anonymisées) ont été sauvegardées en toute sécurité.")
                            except RGPDViolationError as e:
                                st.error(f"Erreur RGPD : {e}")
                            except Exception as e:
                                st.error(f"Erreur lors de la sauvegarde sécurisée : {e}")
                        else:
                            st.info("Vos données ne sont pas conservées (utilisateur gratuit ou consentement non donné).")

                        # Mettre à jour le temps de la dernière génération pour le rate limiting
                        st.session_state.last_generation_time = time.time()

                        progress_text.info("Étape 3/3 : Finalisation et affichage de votre lettre...")
                        progress_bar.progress(100)
                        progress_text.empty() # Efface le texte de progression
                        progress_bar.empty() # Efface la barre de progression
                        # Affichage du résultat
                        st.success("🎉 Votre lettre de motivation a été générée !")
                        
                        # Stocker la lettre générée dans session_state pour l'édition
                        st.session_state.lettre_editable = lettre_generee

                        # Zone de texte éditable
                        edited_letter = st.text_area(
                            "Voici votre lettre (vous pouvez l'éditer ici) :",
                            st.session_state.lettre_editable,
                            height=400,
                            key="lettre_motivation_editor"
                        )

                        # Mettre à jour la lettre dans session_state si l'utilisateur l'édite
                        st.session_state.lettre_editable = edited_letter

                        # Bouton Copier dans le presse-papiers
                        if st.button("📋 Copier la lettre"):
                            st.components.v1.html(
                                f"""
                                <script>
                                    navigator.clipboard.writeText(`{st.session_state.lettre_editable}`).then(function() {{{{ 
                                        console.log('Async: Copying to clipboard was successful!');
}}}}, function(err) {{{{ 
                                    console.error('Async: Could not copy text: ', err);
                                }}}});
                            </script>
                            """,
                            height=0, width=0
                        )
                        st.success("Lettre copiée dans le presse-papiers !")

                        # Option pour afficher l'analyse ATS
                        show_ats_analysis = st.checkbox("Afficher l'analyse ATS (pour les experts !)", value=False)

                        if show_ats_analysis:
                            st.markdown("--- ")
                            st.subheader(" Analyse ATS (Applicant Tracking System)")
                            st.info("Cette section vous aide à vérifier la pertinence de votre lettre par rapport aux mots-clés de l'annonce.")

                            try:
                                # Vérification que les données nécessaires sont disponibles
                                if 'lettre_editable' not in st.session_state:
                                    st.error("❌ Aucune lettre générée. Veuillez d'abord générer une lettre.")
                                elif 'annonce_content' not in st.session_state or not st.session_state.annonce_content:
                                    st.error("❌ Contenu de l'annonce manquant. Veuillez recharger l'annonce.")
                                else:
                                    # Debug : afficher les longueurs
                                    st.write(f" Debug - Longueur lettre: {len(st.session_state.lettre_editable)} caractères")
                                    st.write(f" Debug - Longueur annonce: {len(st.session_state.annonce_content)} caractères")
                                    
                                    # Extraction des mots-clés avec gestion d'erreur
                                    try:
                                        mots_cles_annonce = extraire_mots_cles_annonce(st.session_state.annonce_content)
                                        st.write(f" Debug - Mots-clés annonce extraits: {len(mots_cles_annonce)}")
                                        
                                        mots_cles_lettre = extraire_mots_cles_annonce(st.session_state.lettre_editable)
                                        st.write(f" Debug - Mots-clés lettre extraits: {len(mots_cles_lettre)}")
                                        
                                        mots_trouves = set(mots_cles_annonce).intersection(set(mots_cles_lettre))
                                        mots_manquants = set(mots_cles_annonce) - set(mots_cles_lettre)
                                        
                                        # Affichage des résultats
                                        st.markdown(f"**Mots-clés de l'annonce ({len(mots_cles_annonce)}) :**")
                                        if mots_cles_annonce:
                                            # Limiter l'affichage pour éviter les problèmes
                                            mots_affiches = sorted(list(mots_cles_annonce))[:50]  # Max 50 mots
                                            st.code(", ".join(mots_affiches) + ("..." if len(mots_cles_annonce) > 50 else ""))
                                        else:
                                            st.warning("Aucun mot-clé extrait de l'annonce")

                                        st.markdown(f"**Mots-clés trouvés dans la lettre ({len(mots_trouves)}) :**")
                                        if mots_trouves:
                                            mots_trouves_affiches = sorted(list(mots_trouves))[:50]
                                            st.success(", ".join(mots_trouves_affiches) + ("..." if len(mots_trouves) > 50 else ""))
                                        else:
                                            st.warning("Aucun mot-clé de l'annonce trouvé dans la lettre.")

                                        st.markdown(f"**Mots-clés manquants dans la lettre ({len(mots_manquants)}) :**")
                                        if mots_manquants:
                                            mots_manquants_affiches = sorted(list(mots_manquants))[:50]
                                            st.error(", ".join(mots_manquants_affiches) + ("..." if len(mots_manquants) > 50 else ""))
                                        else:
                                            st.success("Tous les mots-clés de l'annonce sont présents dans la lettre !")
                                            
                                        # Calcul du pourcentage de correspondance
                                        if mots_cles_annonce:
                                            pourcentage = (len(mots_trouves) / len(mots_cles_annonce)) * 100
                                            st.metric(" Taux de correspondance ATS", f"{pourcentage:.1f}%")
                                        
                                    except Exception as e:
                                        st.error(f"❌ Erreur lors de l'extraction des mots-clés : {str(e)}")
                                        st.write(f" Debug - Type d'erreur: {type(e).__name__}")
                                        
                            except Exception as e:
                                st.error(f"❌ Erreur générale dans l'analyse ATS : {str(e)}")
                                st.write(f" Debug - Erreur complète: {e}")
                                
                            st.markdown("--- ")

                        # Option pour afficher l'analyse Smart Coach
                        show_smart_coach_analysis = st.checkbox("Afficher l'analyse Smart Coach (Feedback IA !)", value=False)

                        if show_smart_coach_analysis:
                            st.markdown("--- ")
                            st.subheader("🧠 Analyse Smart Coach (Feedback IA)")
                            st.info("L'IA évalue votre lettre et vous propose des pistes d'amélioration.")
                            with st.spinner("L'IA analyse votre lettre..."):
                                try:
                                    coaching_report = evaluate_letter(st.session_state.lettre_editable, st.session_state.annonce_content)
                                    st.markdown(f"**Score Global : {coaching_report.score:.1f}/10**")
                                    for suggestion in coaching_report.suggestions:
                                        st.write(f"- {suggestion}")
                                    st.markdown("**Détail des Critères :**")
                                    for critere, detail in coaching_report.rationale.items():
                                        st.write(f"**{critere.replace('_', ' ').title()}** : {detail}")
                                except APIError as e:
                                    st.error(f"Impossible d'obtenir l'analyse Smart Coach : {e}")
                                except Exception as e:
                                    st.error(f"Une erreur inattendue est survenue lors de l'analyse Smart Coach : {e}")
                            st.markdown("--- ")

                        # Option de téléchargement TXT
                            st.download_button(
                                label="📥 Télécharger la lettre (TXT)",
                                data=st.session_state.lettre_editable.encode('utf-8'),
                                file_name='lettre_de_motivation.txt',
                                mime='text/plain'
                            )

                            # Option de téléchargement DOCX
                            docx_file = generate_docx(st.session_state.lettre_editable)
                            st.download_button(
                                label="📄 Télécharger la lettre (DOCX)",
                                data=docx_file,
                                file_name='lettre_de_motivation.docx',
                                mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                            )

                        # --- Historique des Lettres et Gestion des Données (Premium) ---
                        st.markdown("--- ")
                        st.subheader("📚 Historique et Gestion des Données")
                        if user_tier != 'free' and explicit_consent:
                            st.info("En tant qu'utilisateur Premium, vous pouvez consulter l'historique de vos lettres et gérer vos données.")
                            user_history = secure_storage.get_user_history(st.session_state.user_id)
                            if user_history:
                                for i, doc in enumerate(user_history):
                                    st.markdown(f"#### Document {i+1} ({doc['type']}) - Généré le {doc['created_at']}")
                                    st.text_area(f"Contenu du document {doc['id']}", doc['content'], height=200, key=f"history_doc_{doc['id']}", disabled=True)
                                    st.markdown("--- ")
                                if st.button("🗑️ Supprimer toutes mes données sauvegardées"):
                                    secure_storage.delete_all_user_data(st.session_state.user_id)
                                    st.success("Toutes vos données sauvegardées ont été supprimées.")
                                    st.rerun() # Rafraîchir pour montrer l'historique vide
                            else:
                                st.info("Aucun historique de lettres trouvé pour le moment.")
                        else:
                            st.info("L'historique des lettres est une fonctionnalité Premium. Abonnez-vous pour en bénéficier !")

                    except (APIError, FileProcessingError, ValueError) as e:
                        st.error("❌ Une erreur est survenue lors de la génération. Veuillez réessayer.")
                        logging.exception("Erreur lors de la génération via l'interface web.")
                    except Exception as e:
                        st.error("🚨 Une erreur inattendue est survenue. L'ingénieur est sur le coup !")
                        logging.exception("Erreur critique inattendue dans l'app Streamlit.")
            else:
                st.warning("⚠️ Veuillez charger votre CV et l'annonce avant de continuer.")

    with col_buttons_2:
        if st.button("🔄 Réinitialiser"):
            st.session_state.clear() # Efface toutes les variables de session
            st.rerun() # Relance l'application pour tout réinitialiser


if __name__ == "__main__":
    # Vérification de la clé API au démarrage (fail-fast)
    if not os.getenv('GOOGLE_API_KEY'):
        st.error("ERREUR CRITIQUE : La variable d'environnement 'GOOGLE_API_KEY' n'est pas configurée.")
        st.info("Veuillez configurer cette variable d'environnement avant de lancer l'application.")
        st.stop() # Arrête l'exécution si la clé est manquante

    main()
