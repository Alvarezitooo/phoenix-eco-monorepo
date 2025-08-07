"""
DataAnonymizer - Service d'Anonymisation Éthique Phoenix
Anonymisation robuste des données personnelles pour recherche RGPD-compliant

Author: Claude Phoenix DevSecOps Guardian
Version: 1.0.0 - Privacy by Design
"""

import re
import hashlib
import html
import bleach
from typing import Optional, List, Dict, Any
from dataclasses import dataclass


@dataclass
class AnonymizationResult:
    """Résultat d'une opération d'anonymisation"""
    original_length: int
    anonymized_text: str
    pii_detected: List[str]
    anonymization_level: str
    success: bool


class DataAnonymizer:
    """
    Anonymiseur de données sensibles pour logs et recherche.
    Conforme RGPD - protection PII utilisateur avec anonymisation robuste.
    
    Niveaux d'anonymisation :
    - BASIC: Suppression des PII évidentes (emails, téléphones)
    - ADVANCED: Suppression avancée + hachage des identifiants  
    - RESEARCH: Anonymisation complète pour utilisation recherche
    """
    
    def __init__(self, anonymization_level: str = "RESEARCH"):
        """
        Initialisation de l'anonymiseur
        
        Args:
            anonymization_level: BASIC, ADVANCED, ou RESEARCH
        """
        self.level = anonymization_level
        self._setup_patterns()
    
    def _setup_patterns(self):
        """Configuration des patterns de détection PII"""
        
        # Patterns emails
        self.email_pattern = re.compile(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            re.IGNORECASE
        )
        
        # Patterns téléphones français
        self.phone_pattern = re.compile(
            r'(?:\+33|0)[1-9](?:[0-9]{8})|(?:\+33\s?|0)[1-9](?:\s?[0-9]{2}){4}',
            re.IGNORECASE
        )
        
        # Patterns noms/prénoms (patterns simples)
        self.name_patterns = [
            re.compile(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b'),  # Prénom Nom
            re.compile(r'\bMonsieur [A-Z][a-z]+\b'),      # M. Nom
            re.compile(r'\bMadame [A-Z][a-z]+\b'),        # Mme Nom
            re.compile(r'\bMademoiselle [A-Z][a-z]+\b'),  # Mlle Nom
        ]
        
        # Patterns adresses (basique)
        self.address_pattern = re.compile(
            r'\d+\s+(rue|avenue|boulevard|place|impasse|chemin)\s+[A-Za-z\s]+',
            re.IGNORECASE
        )
        
        # Patterns codes postaux français
        self.postal_code_pattern = re.compile(r'\b\d{5}\b')
        
        # Patterns cartes bancaires
        self.credit_card_pattern = re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b')
        
        # Patterns IBAN/RIB
        self.iban_pattern = re.compile(r'\b[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}[A-Z0-9]{1,7}\b')
    
    def anonymize_text(self, text: str, preserve_structure: bool = True) -> AnonymizationResult:
        """
        Anonymise un texte en supprimant/masquant les données personnelles
        
        Args:
            text: Texte à anonymiser
            preserve_structure: Garder la structure du texte (remplacer par [EMAIL], [PHONE])
            
        Returns:
            AnonymizationResult: Résultat de l'anonymisation
        """
        if not text or not isinstance(text, str):
            return AnonymizationResult(
                original_length=0,
                anonymized_text="",
                pii_detected=[],
                anonymization_level=self.level,
                success=True
            )
        
        original_length = len(text)
        anonymized_text = text
        pii_detected = []
        
        # 1. Anonymisation emails
        if self.email_pattern.search(anonymized_text):
            pii_detected.append("email")
            if preserve_structure:
                anonymized_text = self.email_pattern.sub("[EMAIL_ANONYME]", anonymized_text)
            else:
                anonymized_text = self.email_pattern.sub("", anonymized_text)
        
        # 2. Anonymisation téléphones
        if self.phone_pattern.search(anonymized_text):
            pii_detected.append("telephone")
            if preserve_structure:
                anonymized_text = self.phone_pattern.sub("[TELEPHONE_ANONYME]", anonymized_text)
            else:
                anonymized_text = self.phone_pattern.sub("", anonymized_text)
        
        # 3. Anonymisation noms/prénoms (niveau ADVANCED et RESEARCH seulement)
        if self.level in ["ADVANCED", "RESEARCH"]:
            for pattern in self.name_patterns:
                if pattern.search(anonymized_text):
                    pii_detected.append("nom_prenom")
                    if preserve_structure:
                        anonymized_text = pattern.sub("[NOM_ANONYME]", anonymized_text)
                    else:
                        anonymized_text = pattern.sub("", anonymized_text)
        
        # 4. Anonymisation adresses (niveau RESEARCH seulement)
        if self.level == "RESEARCH":
            if self.address_pattern.search(anonymized_text):
                pii_detected.append("adresse")
                if preserve_structure:
                    anonymized_text = self.address_pattern.sub("[ADRESSE_ANONYME]", anonymized_text)
                else:
                    anonymized_text = self.address_pattern.sub("", anonymized_text)
            
            # Codes postaux
            if self.postal_code_pattern.search(anonymized_text):
                pii_detected.append("code_postal")
                anonymized_text = self.postal_code_pattern.sub("[CP_ANONYME]", anonymized_text)
        
        # 5. Anonymisation données financières
        if self.credit_card_pattern.search(anonymized_text):
            pii_detected.append("carte_bancaire")
            anonymized_text = self.credit_card_pattern.sub("[CB_ANONYME]", anonymized_text)
        
        if self.iban_pattern.search(anonymized_text):
            pii_detected.append("iban")
            anonymized_text = self.iban_pattern.sub("[IBAN_ANONYME]", anonymized_text)
        
        # 6. Nettoyage final des espaces multiples
        anonymized_text = re.sub(r'\s+', ' ', anonymized_text).strip()
        
        # 7. Sanitisation HTML si nécessaire
        anonymized_text = html.escape(anonymized_text)
        
        return AnonymizationResult(
            original_length=original_length,
            anonymized_text=anonymized_text,
            pii_detected=list(set(pii_detected)),  # Suppression des doublons
            anonymization_level=self.level,
            success=True
        )
    
    def anonymize_email(self, email: str) -> str:
        """
        Anonymise un email pour logs sécurisés.
        
        Example: jean.dupont@gmail.com -> j***t@g***l.com
        """
        if not email or "@" not in email:
            return "email_invalide"

        local, domain = email.split("@", 1)

        # Anonymisation partie locale
        if len(local) <= 2:
            local_anon = local[0] + "*"
        else:
            local_anon = local[0] + "*" * (len(local) - 2) + local[-1]

        # Anonymisation domaine
        if "." in domain:
            domain_parts = domain.split(".")
            domain_main = domain_parts[0]
            if len(domain_main) <= 2:
                domain_anon = domain_main[0] + "*"
            else:
                domain_anon = (
                    domain_main[0] + "*" * (len(domain_main) - 2) + domain_main[-1]
                )
            domain_anon += "." + ".".join(domain_parts[1:])
        else:
            domain_anon = domain

        return f"{local_anon}@{domain_anon}"

    def anonymize_user_id(self, user_id: str) -> str:
        """
        Anonymise partiellement un UUID pour logs.
        
        Example: 123e4567-e89b-12d3-a456-426614174000 -> 123e****-****-****-****-********4000
        """
        if not user_id or len(user_id) < 8:
            return "id_invalide"

        return user_id[:4] + "****-****-****-****-********" + user_id[-4:]
    
    def hash_for_research(self, data: str, salt: str = "phoenix_research_2025") -> str:
        """
        Génère un hash anonyme pour usage recherche
        
        Args:
            data: Donnée à hasher
            salt: Salt pour le hash (défaut: salt recherche Phoenix)
            
        Returns:
            str: Hash SHA256 tronqué pour anonymisation
        """
        if not data:
            return "hash_vide"
        
        # Combinaison données + salt
        combined = f"{data}_{salt}".encode('utf-8')
        
        # Hash SHA256
        hash_full = hashlib.sha256(combined).hexdigest()
        
        # Retour des 16 premiers caractères (suffisant pour anonymisation)
        return hash_full[:16]
    
    def anonymize_for_research(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Anonymise un dictionnaire de données utilisateur pour la recherche
        
        Args:
            user_data: Données utilisateur à anonymiser
            
        Returns:
            Dict: Données anonymisées pour recherche
        """
        anonymized_data = {}
        
        for key, value in user_data.items():
            if value is None:
                anonymized_data[key] = None
                continue
            
            # Anonymisation spécifique par type de donnée
            if key in ["user_id", "id", "userId"]:
                anonymized_data[key] = self.hash_for_research(str(value))
            elif key in ["email", "mail"]:
                anonymized_data[key] = "[EMAIL_ANONYME]"
            elif key in ["phone", "telephone", "tel"]:
                anonymized_data[key] = "[PHONE_ANONYME]"
            elif key in ["name", "nom", "prenom", "firstname", "lastname"]:
                anonymized_data[key] = "[NOM_ANONYME]"
            elif key in ["address", "adresse", "addr"]:
                anonymized_data[key] = "[ADRESSE_ANONYME]"
            elif isinstance(value, str) and len(value) > 10:
                # Texte long - anonymisation complète
                result = self.anonymize_text(value)
                anonymized_data[key] = result.anonymized_text
            else:
                # Autres données - conservation
                anonymized_data[key] = value
        
        return anonymized_data
    
    def sanitize_for_display(self, text: str, max_length: int = 1000) -> str:
        """
        Sanitise un texte pour affichage sécurisé (protection XSS)
        
        Args:
            text: Texte à sanitiser
            max_length: Longueur maximale
            
        Returns:
            str: Texte sanitisé
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Limitation de longueur (protection DoS)
        text = text[:max_length]
        
        # Suppression des caractères de contrôle dangereux
        text = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", text)
        
        # Sanitisation HTML avec bleach
        clean_text = bleach.clean(
            text,
            tags=['b', 'i', 'em', 'strong', 'p', 'br'],
            attributes={},
            strip=True
        )
        
        return clean_text
    
    def is_data_anonymous(self, text: str) -> bool:
        """
        Vérifie si un texte est suffisamment anonymisé
        
        Args:
            text: Texte à vérifier
            
        Returns:
            bool: True si anonyme, False si PII détectées
        """
        if not text:
            return True
        
        # Test des patterns PII
        pii_patterns = [
            self.email_pattern,
            self.phone_pattern,
            self.credit_card_pattern,
            self.iban_pattern
        ]
        
        for pattern in pii_patterns:
            if pattern.search(text):
                return False
        
        # Test des noms (basique)
        for pattern in self.name_patterns:
            if pattern.search(text):
                return False
        
        return True


# Instance globale pour utilisation facile
default_anonymizer = DataAnonymizer(anonymization_level="RESEARCH")

# Fonctions helper pour compatibilité
def anonymize_text(text: str) -> str:
    """Helper function pour anonymisation rapide"""
    result = default_anonymizer.anonymize_text(text)
    return result.anonymized_text

def anonymize_email(email: str) -> str:
    """Helper function pour anonymisation email"""
    return default_anonymizer.anonymize_email(email)

def anonymize_user_id(user_id: str) -> str:
    """Helper function pour anonymisation user_id"""
    return default_anonymizer.anonymize_user_id(user_id)