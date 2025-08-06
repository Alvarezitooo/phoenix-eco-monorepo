"""
Utilitaires de sécurité pour Phoenix Rise.
Protection des données sensibles selon principes RGPD.
"""

import html
import re
import bleach
from typing import Optional

# Configuration de base pour bleach (tags et attributs autorisés)
ALLOWED_TAGS = [
    'a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol',
    'p', 'strong', 'ul', 'br', 'div', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'
]
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title'],
    '*': ['class', 'style']
}


class InputValidator:
    """
    Validateur sécurisé pour inputs utilisateur.
    Protection contre XSS, injection, données malveillantes.
    """

    @staticmethod
    def sanitize_text(text: str, max_length: int = 500) -> str:
        """
        Nettoie et sécurise un texte utilisateur.

        Args:
            text: Texte à nettoyer
            max_length: Longueur maximale autorisée

        Returns:
            Texte sécurisé et validé
        """
        if not text or not isinstance(text, str):
            return ""

        # Limitation de longueur (protection DoS)
        text = text[:max_length]

        # Suppression des caractères de contrôle dangereux
        text = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", text)

        # Échappement HTML pour prévenir XSS (première passe)
        escaped_text = html.escape(text, quote=True)

        # Assainissement HTML avec bleach pour une protection robuste
        # Ceci remplace les regex moins fiables pour le HTML
        sanitized_text = bleach.clean(
            escaped_text,
            tags=ALLOWED_TAGS,
            attributes=ALLOWED_ATTRIBUTES,
            strip=True  # Supprime les balises non autorisées
        )

        return sanitized_text.strip()

    @staticmethod
    def validate_mood_score(score: any) -> Optional[int]:
        """
        Valide un score d'humeur (1-10).

        Returns:
            Score validé ou None si invalide
        """
        try:
            score = int(score)
            return score if 1 <= score <= 10 else None
        except (ValueError, TypeError):
            return None

    @staticmethod
    def validate_user_id(user_id: str) -> bool:
        """
        Valide un identifiant utilisateur Supabase.

        Args:
            user_id: UUID utilisateur à valider

        Returns:
            True si valide, False sinon
        """
        if not user_id or not isinstance(user_id, str):
            return False

        # Format UUID basique
        uuid_pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
        return bool(re.match(uuid_pattern, user_id, re.IGNORECASE))


class DataAnonymizer:
    """
    Anonymiseur de données sensibles pour logs et debugging.
    Conforme RGPD - protection PII utilisateur.
    """

    @staticmethod
    def anonymize_email(email: str) -> str:
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

    @staticmethod
    def anonymize_user_id(user_id: str) -> str:
        """
        Anonymise partiellement un UUID pour logs.

        Example: 123e4567-e89b-12d3-a456-426614174000 -> 123e****-****-****-****-********4000
        """
        if not user_id or len(user_id) < 8:
            return "id_invalide"

        return user_id[:4] + "****-****-****-****-********" + user_id[-4:]
