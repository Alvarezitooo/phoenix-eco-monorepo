import re
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

class DataAnonymizer:
    def __init__(self):
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()

    def anonymize_text(self, text: str) -> str:
        """Anonymise le texte en détectant les PII et en les remplaçant."""
        # Utilisation de Presidio pour détecter les PII
        results = self.analyzer.analyze(text=text, language='en') # Utiliser 'en' pour l'instant, à adapter si besoin de français

        # Configuration de l'anonymisation (remplacement par un libellé générique)
        anonymized_text = self.anonymizer.anonymize(
            text=text,
            analyzer_results=results,
            operators={
                "DEFAULT": OperatorConfig("replace", {"new_value": "<ANONYMIZED_PII>"})
            }
        ).text

        # Anonymisation supplémentaire avec des regex pour des cas spécifiques (ex: numéros de téléphone français)
        anonymized_text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '<EMAIL>', anonymized_text)
        anonymized_text = re.sub(r'0[1-9](?:[0-9]{8})', '<TELEPHONE>', anonymized_text)
        # Cette regex pour les adresses est très basique et pourrait nécessiter des ajustements
        anonymized_text = re.sub(r'\d+\s+[A-Za-z\s]+\d{5}\b', '<ADRESSE>', anonymized_text)

        return anonymized_text

# Exemple d'utilisation (pour les tests ou la démonstration)
if __name__ == "__main__":
    anonymizer = DataAnonymizer()
    sample_text = "Mon nom est Jean Dupont, mon email est jean.dupont@example.com et mon numéro est 0612345678. J'habite au 123 Rue de la Paix 75001 Paris."
    anonymized_sample = anonymizer.anonymize_text(sample_text)
    print(f"Original: {sample_text}")
    print(f"Anonymisé: {anonymized_sample}")

    sample_cv_content = """
    Jean Dupont
    123 Rue de la Paix, 75001 Paris
    jean.dupont@example.com | 0612345678

    Expérience Professionnelle:
    Développeur Senior chez TechCorp (2020-2025)
    """
    anonymized_cv = anonymizer.anonymize_text(sample_cv_content)
    print(f"\nOriginal CV: {sample_cv_content}")
    print(f"Anonymisé CV: {anonymized_cv}")

