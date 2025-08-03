import io
import re
import json
from typing import Dict

import docx
import fitz  # PyMuPDF
import pytesseract
from PIL import Image

from phoenix_cv.models.cv_data import CVProfile, Education, Experience, PersonalInfo, Skill
from phoenix_cv.services.secure_gemini_client import SecureGeminiClient
from phoenix_cv.utils.exceptions import SecurityException, ValidationException
from phoenix_cv.utils.rate_limiter import rate_limit
from phoenix_cv.utils.secure_logging import secure_logger
from phoenix_cv.utils.secure_validator import SecureValidator


class SecureCVParser:
    """
    Parser de CV sécurisé et optimisé avec PyMuPDF et Tesseract OCR.
    Performance et précision maximales.
    """

    def __init__(self, gemini_client: SecureGeminiClient):
        self.gemini = gemini_client
        # Optionnel : Spécifier le chemin de l'exécutable Tesseract si nécessaire
        # pytesseract.pytesseract.tesseract_cmd = r'/usr/local/bin/tesseract'

    def _perform_ocr_on_image(self, image_bytes: bytes) -> str:
        """Effectue l'OCR sur une image avec gestion des erreurs."""
        try:
            image = Image.open(io.BytesIO(image_bytes))
            # Prétraitement simple pour améliorer la qualité de l'OCR
            image = image.convert("L")  # Niveaux de gris
            return pytesseract.image_to_string(image, lang='fra') # Spécifier le français
        except Exception as e:
            secure_logger.log_security_event(
                "OCR_PERFORMANCE_ERROR", {"error": str(e)[:100]}, "WARNING"
            )
            return ""

    @rate_limit(max_requests=5, window_seconds=300)
    def extract_text_from_pdf_secure(self, file_content: bytes) -> str:
        """
        Extraction de texte PDF ultra-performante avec PyMuPDF et OCR Tesseract.
        Combine le texte natif et le texte des images.
        """
        try:
            doc = fitz.open(stream=file_content, filetype="pdf")
            text = ""
            page_count = 0
            image_count = 0

            for page_num, page in enumerate(doc):
                if page_count >= 20:  # Limite de sécurité
                    break

                # 1. Extraction du texte natif (ultra-rapide)
                page_text = page.get_text()
                if len(text + page_text) > 80000: # Limite de taille augmentée
                    break
                text += page_text + "\n"

                # 2. Extraction du texte des images (OCR)
                images = page.get_images(full=True)
                for img_index, img in enumerate(images):
                    image_count += 1
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    
                    ocr_text = self._perform_ocr_on_image(image_bytes)
                    
                    if len(text + ocr_text) > 80000:
                        break
                    text += "\n--- OCR IMAGE ---\n" + ocr_text + "\n"

                page_count += 1

            doc.close()
            clean_text = SecureValidator.validate_text_input(text, 80000, "contenu PDF")

            secure_logger.log_security_event(
                "PDF_TEXT_EXTRACTED_OPTIMIZED",
                {
                    "pages": page_count,
                    "images_processed": image_count,
                    "text_length": len(clean_text),
                },
            )
            return clean_text

        except Exception as e:
            secure_logger.log_security_event(
                "PDF_EXTRACTION_ERROR_OPTIMIZED", {"error": str(e)[:100]}, "CRITICAL"
            )
            raise SecurityException("Erreur critique lors de l'extraction optimisée du PDF")

    def extract_text_from_docx_secure(self, file_content: bytes) -> str:
        """Extraction sécurisée de texte DOCX (inchangée mais bénéficie du logging)"""
        try:
            doc = docx.Document(io.BytesIO(file_content))
            text = "\n".join([para.text for para in doc.paragraphs])

            clean_text = SecureValidator.validate_text_input(
                text, 50000, "contenu DOCX"
            )

            secure_logger.log_security_event(
                "DOCX_TEXT_EXTRACTED", {"text_length": len(clean_text)}
            )

            return clean_text

        except Exception as e:
            secure_logger.log_security_event(
                "DOCX_EXTRACTION_ERROR", {"error": str(e)[:100]}, "ERROR"
            )
            raise SecurityException("Erreur lors de l'extraction du DOCX")

    def parse_cv_with_ai_secure(self, cv_text: str) -> CVProfile:
        """Parsing sécurisé de CV avec IA (bénéficie d'un meilleur texte en entrée)"""
        try:
            clean_cv_text = SecureValidator.validate_text_input(
                cv_text, 80000, "texte CV" # Limite augmentée
            )

            anonymized_text = self._anonymize_text_for_ai(clean_cv_text)

            prompt_data = {"cv_content": anonymized_text}

            response = self.gemini.generate_content_secure("cv_parsing", prompt_data)

            parsed_data = self._parse_json_response_secure(response)

            profile = self._build_cv_profile_secure(parsed_data)

            secure_logger.log_security_event(
                "CV_PARSED_SUCCESSFULLY",
                {
                    "experiences_count": len(profile.experiences),
                    "skills_count": len(profile.skills),
                },
            )

            return profile

        except Exception as e:
            secure_logger.log_security_event(
                "CV_PARSING_FAILED", {"error": str(e)[:100]}, "ERROR"
            )
            raise SecurityException("Erreur lors de l'analyse du CV")

    def _anonymize_text_for_ai(self, text: str) -> str:
        """Anonymisation avancée pour traitement IA"""
        anonymized = text
        patterns = [
            (r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b", "[EMAIL]"),
            (r"\b(?:\+33|0)[1-9](?:[0-9]{8})\b", "[TELEPHONE]"),
            (
                r"\b\d{1,5}\s+(?:rue|avenue|boulevard|place|chemin)\s+[^,\n]{1,50}",
                "[ADRESSE]",
            ),
            (
                r"\b(?:linkedin\\.com/in/|github\\.com/)[a-zA-Z0-9\\-_.]+",
                "[PROFIL_SOCIAL]",
            ),
        ]
        for pattern, replacement in patterns:
            anonymized = re.sub(pattern, replacement, anonymized, flags=re.IGNORECASE)
        return anonymized

    def _parse_json_response_secure(self, response: str) -> Dict:
        """Parsing sécurisé de la réponse JSON de l'IA."""
        try:
            # Nettoyage préliminaire pour extraire le JSON d'un bloc de code markdown
            match = re.search(r"```json\n(.*?)```", response, re.DOTALL)
            if match:
                json_str = match.group(1)
            else:
                json_str = response

            if len(json_str) > 20000: # Limite de sécurité
                raise ValidationException("Réponse IA JSON trop volumineuse")

            parsed = json.loads(json_str)

            if not isinstance(parsed, dict):
                raise ValidationException("Format de réponse IA invalide (pas un dictionnaire)")

            # Validation et nettoyage des champs
            # (Le reste de la logique de validation peut être ajouté ici si nécessaire)

            return parsed

        except json.JSONDecodeError:
            secure_logger.log_security_event("JSON_DECODE_FAILED", {"response_preview": response[:200]}, "ERROR")
            raise ValidationException("Réponse JSON de l'IA invalide ou mal formée")
        except Exception as e:
            secure_logger.log_security_event("JSON_PARSE_UNEXPECTED_ERROR", {"error": str(e)}, "ERROR")
            raise ValidationException(f"Erreur inattendue lors du parsing de la réponse IA: {e}")


    def _build_cv_profile_secure(self, data: Dict) -> CVProfile:
        """Construction sécurisée du profil CV à partir des données parsées."""
        try:
            # Utilise .get() avec des valeurs par défaut pour éviter les KeyErrors
            personal_info = PersonalInfo().anonymize()

            experiences = [
                Experience(
                    title=SecureValidator.validate_text_input(exp.get("title", ""), 200),
                    company=SecureValidator.validate_text_input(exp.get("company", ""), 200),
                    location=SecureValidator.validate_text_input(exp.get("location", ""), 100),
                    start_date=exp.get("start_date", ""),
                    end_date=exp.get("end_date", ""),
                    current=bool(exp.get("current", False)),
                    description=SecureValidator.validate_text_input(exp.get("description", ""), 2000),
                    skills_used=exp.get("skills_used", [])[:20],
                    achievements=exp.get("achievements", [])[:10],
                )
                for exp in data.get("experiences", [])[:10] if isinstance(exp, dict)
            ]

            education = [
                Education(
                    degree=SecureValidator.validate_text_input(edu.get("degree", ""), 200),
                    institution=SecureValidator.validate_text_input(edu.get("institution", ""), 200),
                    location=edu.get("location", ""),
                    graduation_year=edu.get("graduation_year", ""),
                    relevant_courses=edu.get("relevant_courses", [])[:10],
                )
                for edu in data.get("education", [])[:5] if isinstance(edu, dict)
            ]

            skills = [
                Skill(
                    name=SecureValidator.validate_text_input(skill.get("name", ""), 100),
                    level=skill.get("level", ""),
                    category=skill.get("category", ""),
                )
                for skill in data.get("skills", [])[:50] if isinstance(skill, dict)
            ]

            return CVProfile(
                personal_info=personal_info,
                professional_summary=SecureValidator.validate_text_input(data.get("professional_summary", ""), 1000),
                target_position=SecureValidator.validate_text_input(data.get("target_position", ""), 200),
                target_sector=SecureValidator.validate_text_input(data.get("target_sector", ""), 100),
                current_sector=SecureValidator.validate_text_input(data.get("current_sector", ""), 100),
                experiences=experiences,
                education=education,
                skills=skills,
                certifications=data.get("certifications", [])[:20],
                languages=data.get("languages", [])[:10],
            )

        except Exception as e:
            secure_logger.log_security_event(
                "CV_PROFILE_BUILD_ERROR", {"error": str(e)[:100]}, "ERROR"
            )
            raise SecurityException("Erreur critique lors de la construction du profil CV")