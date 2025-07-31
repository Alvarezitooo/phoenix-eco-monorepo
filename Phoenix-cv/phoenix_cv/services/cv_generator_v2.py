# services/cv_generator_v2.py
import logging
import google.generativeai as genai
from typing import List, Dict, Any, Optional
import asyncio

# NOUVEAU : Imports pour les innovations
import instructor
import yake
import spacy

from models.cv_models import CVRequest, CVResponse, ATSOptimization, Experience, Competence, AccrocheIA # Assumons que ces modèles existent
from services.data_anonymizer import DataAnonymizer
from tenacity import retry, stop_after_attempt, wait_fixed

class CVGeneratorServiceV2:
    """
    Service de génération de CV V2 avec parsing, génération structurée, 
    extraction de mots-clés intelligente et exécution asynchrone.
    """
    
    def __init__(self):
        self.anonymizer = DataAnonymizer()
        # NOUVEAU : Client Gemini "patché" par Instructor
        self.model = instructor.patch(genai.GenerativeModel('models/gemini-1.5-flash'))
        # NOUVEAU : Extracteur de mots-clés Yake
        self.kw_extractor = yake.KeywordExtractor(lan="fr", top=20, n=3)
        # NOUVEAU : Modèle spaCy pour le parsing
        self.nlp = spacy.load("fr_core_news_md")

    # NOUVEAU : Fonction de parsing de CV texte brut
    def parser_cv_texte(self, cv_text: str) -> CVRequest:
        """Parse un CV texte brut pour créer un objet CVRequest."""
        # Ceci est une implémentation simplifiée. Un vrai parsing serait plus complexe.
        # Idéalement, on utiliserait un modèle NER custom.
        doc = self.nlp(cv_text)
        
        # Logique d'extraction à développer...
        # Pour la démo, on retourne un objet pré-rempli.
        logging.info("Parsing du CV via spaCy...")
        # ... la logique d'extraction remplirait dynamiquement cet objet
        return CVRequest(
            prenom="Jean", nom="Valjean", email="test@test.com", telephone="0600000000",
            titre_professionnel="Aide-Soignant en reconversion",
            est_reconversion=True,
            ancien_domaine="Santé / Aide à la personne",
            nouveau_domaine="Cybersécurité",
            secteur_cible="Technologie / Sécurité informatique",
            experiences=[],
            competences=[],
            competences_transferables=[],
            centres_interet=[]
        )

    # NOUVEAU : Fonction asynchrone principale
    async def generer_cv_complet_async(self, cv_text: str, annonce_text: str, template_id: str) -> CVResponse:
        """Point d'entrée principal asynchrone."""
        
        # Étape 1 : Parsing (synchrone pour l'instant)
        request = self.parser_cv_texte(cv_text)
        request.template_id = template_id

        # Étape 2 : Lancement des tâches IA en parallèle
        logging.info("Lancement des tâches IA en parallèle...")
        
        # Anonymisation des données avant envoi à l'IA
        request_anonyme = self._anonymiser_donnees_personnelles(request)
        
        accroche_task = asyncio.create_task(self._generer_accroche_personnalisee_async(request_anonyme))
        experiences_task = asyncio.create_task(self._optimiser_experiences_async(request_anonyme))
        ats_task = asyncio.create_task(self._optimiser_pour_ats_async(request_anonyme, annonce_text))
        
        # Attente des résultats
        accroche_ia, experiences_optimisees, optimisation_ats = await asyncio.gather(
            accroche_task, experiences_task, ats_task
        )
        
        # Étape 3 : Tâches dépendantes (conseils)
        conseils = await self._generer_conseils_amelioration_async(request_anonyme, optimisation_ats.score_global)
        
        logging.info("Génération du CV complet terminée.")
        return CVResponse(
            accroche_ia=accroche_ia.accroche,
            experiences_optimisees=experiences_optimisees,
            competences_mises_en_avant=self._selectionner_competences_cles(request), # synchrone, car rapide
            mots_cles_ats=optimisation_ats.mots_cles_a_ajouter,
            template_utilise=request.template_id,
            score_ats=optimisation_ats.score_global,
            conseils_amelioration=conseils
        )

    def _anonymiser_donnees_personnelles(self, request: CVRequest) -> CVRequest:
        """Anonymise les données personnelles avant envoi IA"""
        
        # Copie de la requête pour modification
        request_dict = request.dict()
        
        # Anonymisation des champs sensibles
        if request_dict.get('email'):
            request_dict['email'] = '<EMAIL>'
        if request_dict.get('telephone'):
            request_dict['telephone'] = '<TELEPHONE>'
            
        # Anonymisation dans les expériences (noms d'entreprises sensibles)
        for exp in request_dict.get('experiences', []):
            exp['entreprise'] = self.anonymizer.anonymize_text(exp['entreprise'])
            
        return CVRequest(**request_dict)
    
    # MODIFIÉ : Méthode asynchrone et utilisant la génération structurée
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    async def _generer_accroche_personnalisee_async(self, request: CVRequest) -> AccrocheIA:
        """Génère une accroche CV structurée (Pydantic) via l'IA."""
        prompt = self._build_prompt_accroche_reconversion(request) # Le prompt reste le même
        
        # L'appel à l'IA change pour utiliser response_model et la version async
        accroche_struct = await self.model.generate_content(
            prompt, 
            response_model=AccrocheIA,
        )
        
        logging.info("Accroche CV structurée générée avec succès.")
        return accroche_struct
        
    def _build_prompt_accroche_reconversion(self, request: CVRequest) -> str:
        """Construit le prompt spécialisé reconversion pour accroche CV"""
        
        competences_str = ", ".join(request.competences_transferables) if request.competences_transferables else "Non spécifiées"
        
        prompt = f"""Tu es Marie-Claire Dubois, experte en reconversions professionnelles et rédaction de CV.

MISSION : Rédiger une accroche CV percutante pour une RECONVERSION PROFESSIONNELLE.

PROFIL CANDIDAT :
- Ancien domaine : {request.ancien_domaine}
- Nouveau domaine visé : {request.nouveau_domaine}
- Secteur cible : {request.secteur_cible}
- Compétences transférables : {competences_str}
- Ton souhaité : {request.style_ton}

CONTEXTE RECONVERSION :
Le candidat passe de "{request.ancien_domaine}" vers "{request.nouveau_domaine}".
Cette transition n'est PAS un handicap, c'est un SUPER-POUVOIR !

RÈGLES ACCROCHE RECONVERSION :
1. JAMAIS de formules négatives ("malgré", "bien que", "sans expérience")
2. VALORISER l'expérience antérieure comme un ATOUT unique
3. BRIDGE logique : montrer le lien naturel ancien → nouveau
4. COMPÉTENCES TRANSFÉRABLES en avant-plan
5. Motivation et détermination transparentes
6. Longueur : 3-4 lignes maximum

EXEMPLES DE TRANSFORMATION :
❌ "En reconversion vers la cybersécurité, je souhaite apporter..."
✅ "Fort de 7 ans en gestion de crise sanitaire, j'apporte une vision unique de la sécurité..."

❌ "Malgré mon parcours en commerce, je suis motivé par..."
✅ "Expert en relation client et négociation, je me tourne vers le développement web pour..."

STRUCTURE RECOMMANDÉE :
"[Expertise actuelle] de X années + [compétences transférables] → [valeur unique pour nouveau domaine] → [ambition/objectif clair]"

Génère UNE SEULE accroche, sans options multiples.
Ton : {request.style_ton}
Secteur : {request.secteur_cible}

ACCROCHE CV :"""

        return prompt
    
    def _build_prompt_accroche_classique(self, request: CVRequest) -> str:
        """Construit le prompt pour accroche CV classique (non-reconversion)"""
        
        experiences_principales = []
        for exp in request.experiences[:3]:  # Top 3 expériences
            experiences_principales.append(f"- {exp.poste} chez {exp.entreprise}")
        
        exp_str = "\n".join(experiences_principales)
        
        prompt = f"""Tu es Marie-Claire Dubois, experte en rédaction de CV et personal branding.

MISSION : Rédiger une accroche CV professionnelle et impactante.

PROFIL CANDIDAT :
- Titre professionnel : {request.titre_professionnel}
- Secteur : {request.secteur_cible}
- Expériences principales :
{exp_str}

- Ton souhaité : {request.style_ton}

RÈGLES ACCROCHE CLASSIQUE :
1. Mettre en avant l'EXPERTISE et les RÉSULTATS
2. Chiffres et réalisations concrètes si possible
3. Valeur ajoutée claire pour l'employeur
4. Différenciation vs autres candidats
5. Langage professionnel adapté au secteur
6. Longueur : 2-3 lignes maximum

STRUCTURE :
"[Expertise/titre] + [années d'expérience] + [compétences clés] + [valeur ajoutée spécifique]"

Génère UNE SEULE accroche percutante.
Secteur : {request.style_ton}
Ton : {request.style_ton}

ACCROCHE CV :"""

        return prompt
    
    async def _optimiser_experiences_async(self, request: CVRequest) -> List[Dict[str, Any]]:
        """Optimise la présentation des expériences pour reconversion ou ATS"""
        
        experiences_optimisees = []
        
        for exp in request.experiences:
            if request.est_reconversion:
                # Reformuler avec angle reconversion
                description_optimisee = await self._reformuler_experience_reconversion_async(
                    exp, request.nouveau_domaine, request.competences_transferables
                )
            else:
                # Optimisation ATS classique
                description_optimisee = self._optimiser_experience_ats(exp, request.secteur_cible)
            
            exp_optimisee = {
                "poste": exp.poste,
                "entreprise": exp.entreprise,
                "periode": f"{exp.date_debut} - {exp.date_fin or 'Actuellement'}",
                "lieu": exp.lieu,
                "description_originale": exp.description,
                "description_optimisee": description_optimisee,
                "competences_mises_en_avant": exp.competences_developpees,
                "angle_reconversion": exp.reconversion_angle
            }
            
            experiences_optimisees.append(exp_optimisee)
        
        return experiences_optimisees
    
    @retry(stop=stop_after_attempt(2), wait=wait_fixed(1))
    async def _reformuler_experience_reconversion_async(
        self, 
        experience: Experience, 
        nouveau_domaine: str, 
        competences_transferables: List[str]
    ) -> str:
        """Reformule une expérience avec angle reconversion"""
        
        competences_str = ", ".join(competences_transferables) if competences_transferables else ""
        
        prompt = f"""Tu es expert en valorisation d'expériences pour reconversions professionnelles.

MISSION : Reformuler cette expérience pour mettre en avant sa valeur pour une reconversion vers {nouveau_domaine}.

EXPÉRIENCE À REFORMULER :
Poste : {experience.poste}
Entreprise : {experience.entreprise}
Description actuelle : {experience.description}
Compétences développées : {', '.join(experience.competences_developpees)}

NOUVEAU DOMAINE : {nouveau_domaine}
COMPÉTENCES TRANSFÉRABLES : {competences_str}

RÈGLES REFORMULATION :
1. Garder les FAITS mais changer l'ANGLE de présentation
2. Mettre en avant les compétences transférables vers {nouveau_domaine}
3. Utiliser le vocabulaire du nouveau secteur quand pertinent
4. Quantifier les résultats quand possible
5. Montrer leadership, initiative, résolution de problèmes
6. 3-4 bullet points maximum

EXEMPLE :
❌ "Aide-soignant : soins aux patients, gestion des dossiers"
✅ "Gestion de crise 24/7 et coordination équipes pluridisciplinaires dans environnement haute sécurité. Application rigoureuse de protocoles complexes. Analyse de risques et prise de décision rapide en situation critique."

Reformule cette expérience pour {nouveau_domaine} :"""

        response = await self.model.generate_content(prompt)
        return response.text.strip() if response.text else experience.description
    
    def _optimiser_experience_ats(self, experience: Experience, secteur_cible: str) -> str:
        """Optimise une expérience pour ATS avec mots-clés secteur"""
        
        # Pour l'instant, retourne la description originale optimisée basiquement
        # TODO: Implémentation complète optimisation ATS
        return experience.description
    
    def _selectionner_competences_cles(self, request: CVRequest) -> List[str]:
        """Sélectionne les compétences les plus pertinentes à mettre en avant"""
        
        competences_prioritaires = []
        
        # Priorité 1 : Compétences transférables (reconversion)
        if request.est_reconversion and request.competences_transferables:
            competences_prioritaires.extend(request.competences_transferables[:5])
        
        # Priorité 2 : Compétences techniques du secteur cible
        competences_techniques = [
            comp.nom for comp in request.competences 
            if comp.categorie == "Technique" and comp.niveau in ["Avancé", "Expert"]
        ]
        competences_prioritaires.extend(competences_techniques[:5])
        
        # Priorité 3 : Compétences transversales fortes
        competences_transversales = [
            comp.nom for comp in request.competences 
            if comp.categorie == "Transversale" and comp.transferable
        ]
        competences_prioritaires.extend(competences_transversales[:3])
        
        # Déduplication et limitation
        competences_uniques = list(dict.fromkeys(competences_prioritaires))
        
        return competences_uniques[:8]  # Max 8 compétences mises en avant
    
    # MODIFIÉ : Logique ATS intelligente avec Yake
    async def _optimiser_pour_ats_async(self, request: CVRequest, annonce_text: str) -> ATSOptimization:
        """Analyse ATS intelligente basée sur l'annonce réelle."""
        logging.info("Analyse ATS avec Yake en cours...")
        
        keywords_annonce_tuples = self.kw_extractor.extract_keywords(annonce_text)
        keywords_annonce = [kw for kw, score in keywords_annonce_tuples]
        
        # Logique de comparaison et de scoring...
        score_global = 75 # Simulé
        
        return ATSOptimization(
            secteur_analyse=request.secteur_cible,
            mots_cles_detectes=keywords_annonce[:10], # Simulé
            mots_cles_manquants=keywords_annonce[10:], # Simulé
            score_global=score_global,
            recommandations=["Intégrer les mots-clés manquants"],
            mots_cles_a_ajouter=keywords_annonce[10:15]
        )
        
    async def _generer_conseils_amelioration_async(self, request: CVRequest, score_ats: Optional[int] = None) -> List[str]:
        """Génère des conseils personnalisés d'amélioration du CV"""
        
        conseils = []
        
        # Conseils basés sur le profil
        if request.est_reconversion:
            conseils.append("Mettez davantage l'accent sur vos compétences transférables dans l'accroche")
            conseils.append("Quantifiez vos réalisations passées pour prouver votre impact")
        
        # Conseils basés sur le score ATS
        if score_ats and score_ats < 70:
            conseils.append("Intégrez plus de mots-clés spécifiques à votre secteur cible")
            conseils.append("Utilisez des verbes d'action forts dans vos descriptions d'expériences")
        
        # Conseils génériques pertinents
        if len(request.experiences) > 5:
            conseils.append("Concentrez-vous sur vos 4-5 expériences les plus pertinentes")
        
        if not request.centres_interet:
            conseils.append("Ajoutez quelques centres d'intérêt qui montrent votre personnalité")
        
        return conseils[:4]  # Maximum 4 conseils pour ne pas surcharger