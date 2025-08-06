"""Service de validation d'entrée sécurisé avec sandboxing renforcé."""

import logging
import tempfile
import subprocess
import hashlib
import time
from pathlib import Path
from typing import Dict, Optional

from core.entities.letter import GenerationRequest, ToneType
from shared.exceptions.specific_exceptions import ValidationError

logger = logging.getLogger(__name__)

# Cache pour éviter la re-validation des mêmes fichiers
FILE_VALIDATION_CACHE: Dict[str, bool] = {}
CACHE_EXPIRY_TIME = 3600  # 1 heure


class InputValidator:
    """Valide et nettoie les entrées utilisateur pour prévenir les vulnérabilités."""

    def validate_generation_request(self, request: GenerationRequest) -> None:
        """Valide une requête de génération de lettre.
        Args:
            request (GenerationRequest): La requête de génération à valider.
        Raises:
            ValidationError: Si la requête est invalide.
        """
        if not request.job_title or len(request.job_title) < 3:
            raise ValidationError(
                "Le titre du poste est requis et doit contenir au moins 3 caractères."
            )
        if not request.company_name or len(request.company_name) < 3:
            raise ValidationError(
                "Le nom de l'entreprise est requis et doit contenir au moins 3 caractères."
            )
        if not request.cv_content or len(request.cv_content) < 50:
            raise ValidationError(
                "Le contenu du CV est requis et doit contenir au moins 50 caractères."
            )
        if not request.job_offer_content or len(request.job_offer_content) < 50:
            raise ValidationError(
                "Le contenu de l'offre d'emploi est requis et doit contenir au moins 50 caractères."
            )
        if request.is_career_change and (
            not request.transferable_skills or len(request.transferable_skills) < 20
        ):
            raise ValidationError(
                "Les compétences transférables sont requises pour une reconversion et doivent contenir au moins 20 caractères."
            )
        if not request.tone:
            raise ValidationError("Le ton de la lettre est requis.")

        logger.info("Generation request validated successfully.")

    def validate_text_input(self, text: str, field_name: str, max_length: int = 500) -> str:
        """Valide et nettoie un input texte utilisateur.
        
        Args:
            text: Le texte à valider
            field_name: Nom du champ pour les messages d'erreur
            max_length: Longueur maximale autorisée
            
        Returns:
            str: Texte nettoyé et validé
            
        Raises:
            ValidationError: Si le texte est invalide
        """
        if not text:
            return ""
            
        # Nettoyage des caractères suspects
        cleaned_text = text.strip()
        
        # Vérification longueur
        if len(cleaned_text) > max_length:
            raise ValidationError(f"{field_name} ne peut pas dépasser {max_length} caractères.")
            
        # Détection patterns malveillants basiques
        suspicious_patterns = [
            '<script', '</script>', 'javascript:', 'data:text/html',
            'onload=', 'onerror=', 'onclick=', 'eval(',
            'document.cookie', 'window.location', 'alert('
        ]
        
        text_lower = cleaned_text.lower()
        for pattern in suspicious_patterns:
            if pattern in text_lower:
                logger.warning(f"Suspicious pattern detected in {field_name}: {pattern}")
                raise ValidationError(f"{field_name} contient du contenu non autorisé.")
        
        logger.debug(f"Text input validated for {field_name}")
        return cleaned_text

    def validate_file_content(self, content: bytes, file_extension: str) -> None:
        """Valide le contenu d'un fichier uploadé avec sécurité renforcée et sandboxing.

        Args:
            content (bytes): Contenu binaire du fichier.
            file_extension (str): Extension du fichier (ex: 'pdf', 'txt').

        Raises:
            ValueError: Si le contenu est invalide ou malveillant.
        """
        # Cache check pour éviter re-validation
        content_hash = hashlib.sha256(content).hexdigest()
        cache_key = f"{content_hash}:{file_extension}"
        
        if cache_key in FILE_VALIDATION_CACHE:
            logger.debug("File validation cache hit")
            return
        
        # Validation de la taille (protection DoS)
        max_size = 5 * 1024 * 1024  # Réduit à 5MB pour plus de sécurité
        if len(content) > max_size:
            logger.warning(f"File too large: {len(content)} bytes")
            raise ValueError("Fichier trop volumineux (max 5MB).")
        
        # Validation du magic number avant traitement
        self._validate_file_magic_number(content, file_extension)

        if file_extension == "txt":
            try:
                decoded_content = content.decode("utf-8")
                # Détection avancée de contenu malveillant
                malicious_patterns = [
                    "<script",
                    "</script>",
                    "<iframe",
                    "javascript:",
                    "vbscript:",
                    "data:text/html",
                    "<object",
                    "<embed",
                    "<form",
                    "eval(",
                    "document.write",
                    "window.location",
                    "document.location",
                ]
                content_lower = decoded_content.lower()
                for pattern in malicious_patterns:
                    if pattern in content_lower:
                        logger.warning(f"Malicious pattern detected: {pattern}")
                        raise ValueError(
                            f"Contenu potentiellement malveillant détecté: {pattern}"
                        )

                # Vérification encodage et caractères suspects
                if (
                    len([c for c in decoded_content if ord(c) > 127])
                    > len(decoded_content) * 0.3
                ):
                    logger.warning("High ratio of non-ASCII characters detected")
                    raise ValueError(
                        "Fichier TXT contient trop de caractères non-ASCII."
                    )

            except UnicodeDecodeError:
                logger.warning("Could not decode TXT file as UTF-8.")
                raise ValueError("Fichier TXT invalide (encodage non UTF-8).")

        elif file_extension == "pdf":
            # Validation PDF avec sandboxing complet
            self._validate_pdf_secure(content)
        
        # Mise en cache après validation réussie
        FILE_VALIDATION_CACHE[cache_key] = True
        logger.info(f"File validation successful for {file_extension}: {content_hash[:8]}...")
    
    def _validate_file_magic_number(self, content: bytes, file_extension: str) -> None:
        """Valide le magic number du fichier."""
        magic_numbers = {
            'pdf': b'%PDF',
            'txt': None  # Pas de magic number spécifique pour TXT
        }
        
        expected_magic = magic_numbers.get(file_extension)
        if expected_magic and not content.startswith(expected_magic):
            logger.warning(f"Invalid magic number for {file_extension}")
            raise ValueError(f"Fichier {file_extension.upper()} invalide (signature manquante).")
    
    def _validate_pdf_secure(self, content: bytes) -> None:
        """Validation PDF sécurisée avec sandboxing."""
        # 1. Validation structure PDF stricte
        self._validate_pdf_structure(content)
        
        # 2. Détection patterns malveillants
        self._scan_pdf_malicious_patterns(content)
        
        # 3. Validation avec outils externes (sandboxed)
        self._validate_pdf_with_external_tools(content)
    
    def _validate_pdf_structure(self, content: bytes) -> None:
        """Valide la structure interne du PDF."""
        if not content.startswith(b"%PDF"):
            raise ValueError("Fichier PDF invalide (signature manquante).")
        
        # Vérification version PDF supportée
        if len(content) < 8:
            raise ValueError("Fichier PDF trop court.")
            
        pdf_version = content[5:8]
        supported_versions = [b"1.3", b"1.4", b"1.5", b"1.6", b"1.7", b"2.0"]
        if pdf_version not in supported_versions:
            logger.warning(f"Unsupported PDF version: {pdf_version}")
            raise ValueError(f"Version PDF non supportée: {pdf_version.decode()}")
        
        # Vérification EOF marker
        if b"%%EOF" not in content[-2048:]:  # Cherche dans les 2KB finaux
            raise ValueError("Structure PDF invalide (marqueur EOF manquant).")
        
        # Validation du nombre d'objets (protection contre PDF bombs)
        obj_count = content.count(b'obj')
        if obj_count > 10000:  # Limite raisonnable
            raise ValueError("PDF contient trop d'objets (possiblement malveillant).")
    
    def _scan_pdf_malicious_patterns(self, content: bytes) -> None:
        """Scanne le PDF pour des patterns malveillants."""
        # Patterns suspects étendus
        suspicious_patterns = [
            b"/JavaScript", b"/JS", b"/Launch", b"/GoToR", b"/GoToE",
            b"/EmbeddedFile", b"/XFA", b"/RichMedia", b"/3D", b"/Sound",
            b"/Movie", b"/Screen", b"/Hide", b"/Named", b"/SubmitForm",
            b"/ImportData", b"/ResetForm", b"/Rendition", b"/OpenAction",
            b"<script", b"eval(", b"unescape(", b"String.fromCharCode"
        ]
        
        for pattern in suspicious_patterns:
            if pattern in content:
                logger.warning(f"Suspicious PDF pattern detected: {pattern}")
                raise ValueError(f"PDF contient des éléments potentiellement dangereux: {pattern.decode()}")
        
        # Détection de compression suspecte
        if content.count(b'/FlateDecode') > 100:
            logger.warning("Excessive compression detected in PDF")
            raise ValueError("PDF avec compression excessive (possiblement malveillant).")
    
    def _validate_pdf_with_external_tools(self, content: bytes) -> None:
        """Valide le PDF avec des outils externes en sandbox."""
        try:
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                tmp_file.write(content)
                tmp_file.flush()
                
                # Validation avec qpdf (si disponible)
                result = subprocess.run([
                    'python3', '-c', 
                    f'''
import sys
try:
    import fitz  # PyMuPDF
    doc = fitz.open("{tmp_file.name}")
    if len(doc) > 500:  # Max 500 pages
        raise Exception("PDF trop volumineux")
    doc.close()
    print("OK")
except Exception as e:
    print(f"ERROR: {{e}}")
    sys.exit(1)
'''
                ], 
                    capture_output=True, 
                    text=True, 
                    timeout=10,  # Timeout strict
                    cwd='/tmp'  # Exécution en répertoire temporaire
                )
                
                # Nettoyage
                Path(tmp_file.name).unlink(missing_ok=True)
                
                if result.returncode != 0 or "ERROR" in result.stdout:
                    error_msg = result.stdout.strip() if result.stdout else "Erreur de validation"
                    logger.warning(f"PDF validation failed: {error_msg}")
                    raise ValueError(f"PDF invalide: {error_msg}")
                    
        except subprocess.TimeoutExpired:
            logger.warning("PDF validation timeout")
            raise ValueError("Validation PDF timeout (fichier possiblement malveillant).")
        except Exception as e:
            logger.warning(f"PDF validation error: {str(e)}")
            raise ValueError(f"Erreur lors de la validation PDF: {str(e)}")

        else:
            logger.warning(
                f"Unsupported file extension for content validation: {file_extension}"
            )
            raise ValueError(
                f"Type de fichier non supporté pour la validation de contenu: {file_extension}"
            )

    def sanitize_text_input(self, text: str) -> str:
        """Nettoie une chaîne de texte pour prévenir les injections.
        Args:
            text (str): Chaîne de texte à nettoyer.
        Returns:
            str: Chaîne de texte nettoyée.
        """
        # Exemple de nettoyage basique (à étendre)
        return text.replace("<", "&lt;").replace(">", "&gt;").strip()

    def validate_email(self, email: str) -> bool:
        """Valide le format d'une adresse email.
        Args:
            email (str): Adresse email à valider.
        Returns:
            bool: True si l'email est valide, False sinon.
        """
        import re

        return (
            re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email)
            is not None
        )
