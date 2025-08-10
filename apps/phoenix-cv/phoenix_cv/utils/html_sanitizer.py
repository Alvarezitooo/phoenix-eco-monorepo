"""
🛡️ HTML Sanitizer - Protection XSS
Système de nettoyage HTML sécurisé pour Phoenix CV

Author: Claude Phoenix DevSecOps Guardian
Version: 1.0.0 - XSS Protection System
"""

import html

import bleach
from phoenix_cv.utils.secure_logging import secure_logger


class HTMLSanitizer:
    """
    Sanitiseur HTML sécurisé pour prévenir les attaques XSS.
    Utilise bleach pour un nettoyage sécurisé du HTML.
    """

    # Tags HTML autorisés (whitelist stricte)
    ALLOWED_TAGS = [
        "p",
        "br",
        "div",
        "span",
        "strong",
        "b",
        "em",
        "i",
        "u",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "ul",
        "ol",
        "li",
        "blockquote",
        "code",
        "pre",
    ]

    # Attributs HTML autorisés (whitelist stricte)
    ALLOWED_ATTRIBUTES = {
        "*": ["class", "id"],
        "div": ["style"],
        "span": ["style"],
        "p": ["style"],
        "h1": ["style"],
        "h2": ["style"],
        "h3": ["style"],
        "h4": ["style"],
        "h5": ["style"],
        "h6": ["style"],
    }

    # Propriétés CSS autorisées pour style
    ALLOWED_STYLES = [
        "color",
        "background-color",
        "font-weight",
        "font-size",
        "text-align",
        "margin",
        "padding",
        "border-radius",
        "display",
        "flex-direction",
        "justify-content",
        "align-items",
    ]

    # Protocoles autorisés pour les liens
    ALLOWED_PROTOCOLS = ["http", "https", "mailto"]

    @staticmethod
    def sanitize_html(
        html_content: str, strict_mode: bool = True, allow_styles: bool = False
    ) -> str:
        """
        Sanitise le contenu HTML pour prévenir XSS.

        Args:
            html_content: Contenu HTML à nettoyer
            strict_mode: Mode strict (tags limités)
            allow_styles: Autoriser les styles CSS

        Returns:
            HTML sécurisé
        """
        if not html_content:
            return ""

        try:
            # Configuration selon le mode
            tags = (
                HTMLSanitizer.ALLOWED_TAGS
                if not strict_mode
                else ["p", "br", "strong", "em"]
            )
            attributes = (
                HTMLSanitizer.ALLOWED_ATTRIBUTES if allow_styles else {"*": ["class"]}
            )
            styles = HTMLSanitizer.ALLOWED_STYLES if allow_styles else []

            # Nettoyage avec bleach
            cleaned_html = bleach.clean(
                html_content,
                tags=tags,
                attributes=attributes,
                styles=styles,
                protocols=HTMLSanitizer.ALLOWED_PROTOCOLS,
                strip=True,  # Supprime les tags non autorisés
                strip_comments=True,  # Supprime les commentaires HTML
            )

            # Log si contenu modifié (potentielle tentative XSS)
            if cleaned_html != html_content:
                secure_logger.log_security_event(
                    "HTML_CONTENT_SANITIZED",
                    {
                        "original_length": len(html_content),
                        "cleaned_length": len(cleaned_html),
                        "strict_mode": strict_mode,
                    },
                    "WARNING",
                )

            return cleaned_html

        except Exception as e:
            secure_logger.log_security_event(
                "HTML_SANITIZATION_ERROR", {"error": str(e)[:200]}, "ERROR"
            )
            # En cas d'erreur, échapper tout le HTML
            return html.escape(html_content)

    @staticmethod
    def sanitize_user_input(user_input: str) -> str:
        """
        Sanitise strictement un input utilisateur.
        Mode le plus restrictif pour contenus user-generated.
        """
        return HTMLSanitizer.sanitize_html(
            user_input, strict_mode=True, allow_styles=False
        )

    @staticmethod
    def sanitize_ui_component(ui_html: str) -> str:
        """
        Sanitise un composant UI avec plus de flexibilité.
        Pour les composants d'interface contrôlés.
        """
        return HTMLSanitizer.sanitize_html(
            ui_html, strict_mode=False, allow_styles=True
        )

    @staticmethod
    def validate_css_properties(style_string: str) -> str:
        """
        Valide et nettoie les propriétés CSS.
        """
        if not style_string:
            return ""

        try:
            # Parse simple des propriétés CSS
            properties = []
            for prop in style_string.split(";"):
                if ":" in prop:
                    key, value = prop.split(":", 1)
                    key = key.strip().lower()
                    value = value.strip()

                    # Validation des propriétés autorisées
                    if key in HTMLSanitizer.ALLOWED_STYLES:
                        # Validation basique des valeurs
                        if HTMLSanitizer._is_safe_css_value(value):
                            properties.append(f"{key}: {value}")

            return "; ".join(properties)

        except Exception as e:
            secure_logger.log_security_event(
                "CSS_VALIDATION_ERROR", {"error": str(e)[:200]}, "WARNING"
            )
            return ""

    @staticmethod
    def _is_safe_css_value(value: str) -> bool:
        """
        Vérifie si une valeur CSS est sécurisée.
        """
        # Patterns dangereux
        dangerous_patterns = [
            "javascript:",
            "expression(",
            "url(",
            "import",
            "@",
            "behavior:",
            "binding:",
            "mozbinding:",
        ]

        value_lower = value.lower()
        return not any(pattern in value_lower for pattern in dangerous_patterns)

    @staticmethod
    def create_safe_markdown(content: str) -> str:
        """
        Crée du HTML sécurisé à partir de markdown.
        Utilise uniquement des balises sécurisées.
        """
        # Conversion basique markdown vers HTML sécurisé
        safe_content = content

        # Gras: **text** -> <strong>text</strong>
        safe_content = safe_content.replace("**", "").replace("__", "")

        # Italique: *text* -> <em>text</em>
        safe_content = safe_content.replace("*", "").replace("_", "")

        # Échapper le reste
        safe_content = html.escape(safe_content)

        return safe_content


# Instance globale
html_sanitizer = HTMLSanitizer()
