import logging
import google.generativeai as genai
from services.api_client import APIError
from services.data_anonymizer import DataAnonymizer

class CvOptimizationService:
    def __init__(self):
        self.anonymizer = DataAnonymizer()

    def optimize_cv(self, cv_content: str, competences_transferables: str, user_tier: str, max_retries: int = 3) -> str:
        """Optimise le contenu du CV en mettant en avant les compétences transférables, selon le niveau d'abonnement."""
        anonymized_cv = self.anonymizer.anonymize_text(cv_content)

        for tentative in range(max_retries):
            try:
                model = genai.GenerativeModel('models/gemini-1.5-flash')

                prompt_lines = []

                # Adaptation du prompt en fonction du niveau d'abonnement
                if user_tier == "premium_plus":
                    prompt_lines.append(
                        "Tu es un expert en recrutement et un coach de carrière de renommée mondiale, spécialisé dans l'optimisation de CV pour les reconversions professionnelles complexes. "
                        "Ton objectif est de transformer un CV existant en un document percutant qui met en lumière les compétences transférables du candidat, "
                        "en adaptant le langage et la structure pour maximiser son impact auprès des recruteurs et des ATS. "
                        "Chaque section doit être optimisée pour la clarté, la concision et la pertinence."
                    )
                    prompt_lines.append(
                        f"Optimise le CV suivant en insistant particulièrement sur les compétences transférables : {competences_transferables}. "
                        "Réécris les sections clés (résumé, expérience, compétences) pour qu'elles résonnent avec un nouveau domaine, "
                        "en utilisant un vocabulaire professionnel et des verbes d'action forts. "
                        "Le CV doit être prêt à l'emploi, sans fioritures, et directement exploitable."
                    )
                elif user_tier == "premium":
                    prompt_lines.append(
                        "Tu es un expert en recrutement, spécialisé dans l'optimisation de CV pour les reconversions. "
                        "Ton objectif est d'améliorer un CV existant en valorisant les compétences transférables du candidat."
                    )
                    prompt_lines.append(
                        f"Optimise le CV suivant en mettant en avant les compétences transférables : {competences_transferables}. "
                        "Concentre-toi sur la clarté et la pertinence des expériences passées pour le nouveau domaine."
                    )
                else: # free tier (basic suggestion, not full optimization)
                    prompt_lines.append(
                        "Tu es un assistant qui aide à améliorer les CV. "
                    )
                    prompt_lines.append(
                        f"Suggère des améliorations pour le CV suivant en lien avec les compétences transférables : {competences_transferables}. "
                        "Ne réécris pas le CV entier, donne juste des pistes."
                    )

                prompt_lines.extend([
                    "\n--- CV à optimiser ---",
                    anonymized_cv,
                    "\n--- CV Optimisé / Suggestions ---"
                ])
                prompt = "\n".join(prompt_lines)

                response = model.generate_content(prompt)

                if not response.text or len(response.text) < 50:
                    raise APIError("Réponse API invalide ou trop courte pour l'optimisation du CV")

                logging.info("CV optimisé avec succès")
                return response.text

            except Exception as e:
                logging.error(f"Erreur inattendue lors de l'optimisation du CV (tentative {tentative + 1}): {e}")
                if tentative == max_retries - 1:
                    raise APIError(f"Échec de l'optimisation du CV après {max_retries} tentatives: {e}")
                import time
                time.sleep(2 ** tentative)
        
        raise APIError("Toutes les tentatives d'optimisation du CV ont échoué")

# Exemple d'utilisation (pour les tests ou la démonstration)
if __name__ == "__main__":
    cv_opt_service = CvOptimizationService()
    sample_cv = """
    Jean Dupont
    Expérience: Vendeur pendant 5 ans. Gestion de stock, relation client.
    """
    transferable_skills = "Communication, Organisation, Négociation"

    print("\n--- Optimisation CV (Free Tier) ---")
    optimized_cv_free = cv_opt_service.optimize_cv(sample_cv, transferable_skills, "free")
    print(optimized_cv_free)

    print("\n--- Optimisation CV (Premium Tier) ---")
    optimized_cv_premium = cv_opt_service.optimize_cv(sample_cv, transferable_skills, "premium")
    print(optimized_cv_premium)

    print("\n--- Optimisation CV (Premium Plus Tier) ---")
    optimized_cv_premium_plus = cv_opt_service.optimize_cv(sample_cv, transferable_skills, "premium_plus")
    print(optimized_cv_premium_plus)
