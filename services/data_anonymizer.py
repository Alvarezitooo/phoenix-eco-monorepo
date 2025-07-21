import re
import warnings
import logging

# Désactiver les warnings
warnings.filterwarnings("ignore")
logging.getLogger("presidio-analyzer").setLevel(logging.ERROR)

class DataAnonymizer:
    def __init__(self):
        """Version allégée sans Presidio pour Streamlit Cloud"""
        self.presidio_available = False
        print("DataAnonymizer initialisé en mode simplifié (sans Presidio)")

    def anonymize_text(self, text: str) -> str:
        """Anonymisation basique avec regex uniquement - compatible Streamlit Cloud"""
        
        if not text or not isinstance(text, str):
            return text
            
        anonymized_text = text
        
        try:
            # Anonymisation regex basique mais efficace
            
            # Emails
            anonymized_text = re.sub(
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 
                '<EMAIL>', 
                anonymized_text
            )
            
            # Téléphones français
            anonymized_text = re.sub(
                r'\b0[1-9](?:[0-9]{8})\b', 
                '<TELEPHONE>', 
                anonymized_text
            )
            
            # Numéros de sécurité sociale français (basique)
            anonymized_text = re.sub(
                r'\b[1-2]\s?\d{2}\s?\d{2}\s?\d{2}\s?\d{3}\s?\d{3}\s?\d{2}\b',
                '<SECU>',
                anonymized_text
            )
            
            # Adresses (très basique)
            anonymized_text = re.sub(
                r'\b\d+\s+[A-Za-z\s]+\d{5}\b', 
                '<ADRESSE>', 
                anonymized_text
            )
            
            # URLs
            anonymized_text = re.sub(
                r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
                '<URL>',
                anonymized_text
            )
            
        except Exception as e:
            # En cas d'erreur, retourner le texte original
            print(f"Erreur anonymisation: {e}")
            return text
            
        return anonymized_text

# Pour compatibilité avec l'ancien code
if __name__ == "__main__":
    anonymizer = DataAnonymizer()
    test_text = "Mon email est test@example.com et mon tel 0612345678"
    result = anonymizer.anonymize_text(test_text)
    print(f"Original: {test_text}")
    print(f"Anonymisé: {result}")