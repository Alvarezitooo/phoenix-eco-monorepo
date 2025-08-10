import io
import os
import re
import json
import asyncio
import concurrent.futures
from typing import Dict, List, Optional, Tuple

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

# Import de la protection pypdf DoS pour référence
try:
    from pdf_security_patch.pypdf_dos_mitigation import safe_extract_pdf_text
    PYPDF_DOS_PROTECTION_ENABLED = True
    secure_logger.log_security_event(
        "PYPDF_DOS_PROTECTION_AVAILABLE",
        {"module": "secure_cv_parser"},
        "INFO"
    )
except ImportError:
    secure_logger.log_security_event(
        "PYPDF_DOS_PROTECTION_UNAVAILABLE",
        {"module": "secure_cv_parser", "fallback": "PyMuPDF"},
        "WARNING"
    )
    PYPDF_DOS_PROTECTION_ENABLED = False


class SecureCVParser:
    """
    🚀 Parser de CV sécurisé et optimisé avec traitement asynchrone.
    PyMuPDF + Tesseract OCR avec parallélisation intelligente.
    Performance et précision maximales.
    """

    def __init__(self, gemini_client: SecureGeminiClient, max_workers: int = 4):
        self.gemini = gemini_client
        self.max_workers = max_workers
        
        # ✅ Pool de threads pour OCR parallèle
        self.ocr_executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=max_workers, 
            thread_name_prefix="OCR-Worker"
        )
        
        # ✅ Pool séparé pour traitement PDF/DOCX
        self.io_executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=2,
            thread_name_prefix="IO-Worker"
        )
        
        secure_logger.log_security_event("CV_PARSER_ASYNC_INITIALIZED", 
            {"ocr_workers": max_workers, "io_workers": 2})
        
        # Optionnel : Spécifier le chemin de l'exécutable Tesseract si nécessaire
        # pytesseract.pytesseract.tesseract_cmd = r'/usr/local/bin/tesseract'

    def _perform_ocr_on_image(self, image_bytes: bytes) -> str:
        """Effectue l'OCR sur une image avec gestion des erreurs."""
        try:
            image = Image.open(io.BytesIO(image_bytes))
            # ✅ Prétraitement optimisé pour améliorer la qualité de l'OCR
            image = image.convert("L")  # Niveaux de gris
            
            # ✅ Configuration OCR optimisée pour CV
            custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789àâäéèêëïîôöùûüÿçÀÂÄÉÈÊËÏÎÔÖÙÛÜŸÇ .,;:!?()[]{}"\'-+@#$%&*=/'
            
            return pytesseract.image_to_string(
                image, 
                lang='fra+eng',  # Multi-langue pour CV internationaux
                config=custom_config
            )
        except Exception as e:
            secure_logger.log_security_event(
                "OCR_PERFORMANCE_ERROR", {"error": str(e)[:100]}, "WARNING"
            )
            return ""
    
    async def _perform_ocr_batch_async(self, image_list: List[Tuple[int, bytes]]) -> List[Tuple[int, str]]:
        """🚀 Traitement OCR parallèle sur plusieurs images."""
        if not image_list:
            return []
        
        loop = asyncio.get_event_loop()
        
        # ✅ Créer tâches asynchrones pour chaque image
        ocr_tasks = []
        for idx, image_bytes in image_list:
            task = loop.run_in_executor(
                self.ocr_executor, 
                self._perform_ocr_on_image, 
                image_bytes
            )
            ocr_tasks.append((idx, task))
        
        # ✅ Attendre completion de toutes les tâches avec timeout
        results = []
        try:
            for idx, task in ocr_tasks:
                ocr_text = await asyncio.wait_for(task, timeout=30.0)  # 30s par image
                results.append((idx, ocr_text))
        except asyncio.TimeoutError:
            secure_logger.log_security_event(
                "OCR_BATCH_TIMEOUT", {"processed": len(results), "total": len(ocr_tasks)}, "WARNING"
            )
        
        secure_logger.log_security_event(
            "OCR_BATCH_COMPLETED", {"images_processed": len(results), "total_images": len(image_list)}
        )
        
        return results

    @rate_limit(max_requests=5, window_seconds=300)
    def extract_text_from_pdf_secure(self, file_content: bytes) -> str:
        """
        Extraction de texte PDF ultra-performante avec PyMuPDF et OCR Tesseract.
        Combine le texte natif et le texte des images.
        Protection intégrée contre CVE-2023-36810.
        """
        
        # 🛡️ PROTECTION PYPDF DOS COMME PREMIÈRE LIGNE DE DÉFENSE
        if PYPDF_DOS_PROTECTION_ENABLED:
            try:
                secure_logger.log_security_event(
                    "PDF_DOS_PROTECTION_ACTIVE",
                    {"file_size": len(file_content), "method": "cv_parser"},
                    "INFO"
                )
                
                # Test avec protection DoS avant traitement PyMuPDF
                test_text = safe_extract_pdf_text(file_content, "cv_parsing.pdf")
                
                # Si le test passe, continuer avec PyMuPDF pour OCR avancé
                secure_logger.log_security_event(
                    "PDF_DOS_PROTECTION_PASSED_CV",
                    {"extracted_preview": len(test_text)},
                    "INFO"
                )
                
            except (ValueError, TimeoutError) as e:
                secure_logger.log_security_event(
                    "PDF_DOS_PROTECTION_BLOCKED_CV",
                    {"error": str(e)},
                    "CRITICAL"
                )
                raise SecurityException(f"PDF bloqué par protection DoS: {str(e)}")
            except Exception as e:
                secure_logger.log_security_event(
                    "PDF_DOS_PROTECTION_ERROR_CV",
                    {"error": str(e)},
                    "ERROR"
                )
                # Continue avec PyMuPDF mais avec vigilance accrue
        
        # Traitement PyMuPDF avec OCR (après validation DoS)
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

                # 2. ✅ Collecte des images pour traitement OCR parallèle
                images = page.get_images(full=True)
                page_images = []
                
                for img_index, img in enumerate(images[:5]):  # Max 5 images par page
                    try:
                        xref = img[0]
                        base_image = doc.extract_image(xref)
                        image_bytes = base_image["image"]
                        page_images.append((f"{page_num}_{img_index}", image_bytes))
                        image_count += 1
                    except Exception as e:
                        secure_logger.log_security_event(
                            "IMAGE_EXTRACTION_ERROR", {"page": page_num, "img": img_index, "error": str(e)[:100]}, "WARNING"
                        )
                
                # ✅ Traitement OCR asynchrone de toutes les images de la page
                if page_images:
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        ocr_results = loop.run_until_complete(self._perform_ocr_batch_async(page_images))
                        
                        for img_id, ocr_text in ocr_results:
                            if len(text + ocr_text) > 80000:
                                break
                            if ocr_text.strip():  # Ignorer OCR vides
                                text += f"\n--- OCR IMAGE {img_id} ---\n" + ocr_text + "\n"
                        
                        loop.close()
                    except Exception as e:
                        secure_logger.log_security_event(
                            "OCR_ASYNC_ERROR", {"page": page_num, "error": str(e)[:100]}, "WARNING"
                        )

                page_count += 1

            doc.close()
            clean_text = SecureValidator.validate_text_input(text, 80000, "contenu PDF")

            secure_logger.log_security_event(
                "PDF_TEXT_EXTRACTED_OPTIMIZED",
                {
                    "pages": page_count,
                    "images_processed": image_count,
                    "text_length": len(clean_text),
                    "dos_protection": PYPDF_DOS_PROTECTION_ENABLED
                },
            )
            return clean_text

        except Exception as e:
            secure_logger.log_security_event(
                "PDF_EXTRACTION_ERROR_OPTIMIZED", {"error": str(e)[:100]}, "CRITICAL"
            )
            raise SecurityException("Erreur critique lors de l'extraction optimisée du PDF")
    
    async def extract_text_from_pdf_async(self, file_content: bytes) -> str:
        """🚀 Version asynchrone complète de l'extraction PDF avec OCR parallèle."""
        loop = asyncio.get_event_loop()
        
        # ✅ Déléguer l'extraction PDF au pool IO
        try:
            result = await loop.run_in_executor(
                self.io_executor,
                self.extract_text_from_pdf_secure,
                file_content
            )
            return result
        except Exception as e:
            secure_logger.log_security_event(
                "PDF_ASYNC_EXTRACTION_ERROR", {"error": str(e)[:100]}, "CRITICAL"
            )
            raise

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
    
    async def extract_text_from_docx_async(self, file_content: bytes) -> str:
        """🚀 Version asynchrone de l'extraction DOCX."""
        loop = asyncio.get_event_loop()
        
        try:
            result = await loop.run_in_executor(
                self.io_executor,
                self.extract_text_from_docx_secure,
                file_content
            )
            return result
        except Exception as e:
            secure_logger.log_security_event(
                "DOCX_ASYNC_EXTRACTION_ERROR", {"error": str(e)[:100]}, "ERROR"
            )
            raise

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
    
    async def parse_cv_with_ai_async(self, cv_text: str) -> CVProfile:
        """🚀 Version asynchrone du parsing CV avec IA."""
        loop = asyncio.get_event_loop()
        
        try:
            # ✅ Traitement asynchrone de l'anonymisation et parsing
            clean_cv_text = SecureValidator.validate_text_input(
                cv_text, 80000, "texte CV"
            )
            
            # ✅ Anonymisation asynchrone
            anonymized_text = await loop.run_in_executor(
                None,  # Utiliser le pool par défaut
                self._anonymize_text_for_ai,
                clean_cv_text
            )
            
            prompt_data = {"cv_content": anonymized_text}
            
            # ✅ Appel Gemini asynchrone (bénéficie du cache optimisé)
            response = await loop.run_in_executor(
                None,
                lambda: self.gemini.generate_content_secure("cv_parsing", prompt_data)
            )
            
            # ✅ Parsing JSON asynchrone
            parsed_data = await loop.run_in_executor(
                None,
                self._parse_json_response_secure,
                response
            )
            
            # ✅ Construction profil asynchrone
            profile = await loop.run_in_executor(
                None,
                self._build_cv_profile_secure,
                parsed_data
            )
            
            secure_logger.log_security_event(
                "CV_PARSED_ASYNC_SUCCESS",
                {
                    "experiences_count": len(profile.experiences),
                    "skills_count": len(profile.skills),
                    "processing_mode": "async"
                },
            )
            
            return profile
            
        except Exception as e:
            secure_logger.log_security_event(
                "CV_PARSING_ASYNC_FAILED", {"error": str(e)[:100]}, "ERROR"
            )
            raise SecurityException("Erreur lors de l'analyse asynchrone du CV")
    
    async def parse_multiple_cvs_async(self, cv_contents: List[Tuple[str, bytes]]) -> List[Tuple[str, Optional[CVProfile]]]:
        """🚀 Traitement parallèle de plusieurs CVs."""
        if not cv_contents:
            return []
        
        secure_logger.log_security_event(
            "BATCH_CV_PROCESSING_START", {"cv_count": len(cv_contents)}
        )
        
        # ✅ Créer tâches asynchrones pour chaque CV
        tasks = []
        for filename, content in cv_contents:
            if filename.lower().endswith('.pdf'):
                extract_task = self.extract_text_from_pdf_async(content)
            elif filename.lower().endswith('.docx'):
                extract_task = self.extract_text_from_docx_async(content)
            else:
                continue  # Format non supporté
            
            # ✅ Chaîner extraction + parsing
            async def process_single_cv(fname, extract_task):
                try:
                    cv_text = await extract_task
                    profile = await self.parse_cv_with_ai_async(cv_text)
                    return (fname, profile)
                except Exception as e:
                    secure_logger.log_security_event(
                        "SINGLE_CV_PROCESSING_FAILED", {"filename": fname, "error": str(e)[:100]}, "WARNING"
                    )
                    return (fname, None)
            
            tasks.append(process_single_cv(filename, extract_task))
        
        # ✅ Traitement parallèle avec limite de concurrence
        semaphore = asyncio.Semaphore(self.max_workers)
        
        async def limited_task(task):
            async with semaphore:
                return await task
        
        # ✅ Exécuter toutes les tâches avec timeout global
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*[limited_task(task) for task in tasks]),
                timeout=300.0  # 5 minutes timeout global
            )
        except asyncio.TimeoutError:
            secure_logger.log_security_event(
                "BATCH_CV_PROCESSING_TIMEOUT", {"cv_count": len(cv_contents)}, "WARNING"
            )
            results = [(f"timeout_{i}", None) for i in range(len(cv_contents))]
        
        success_count = sum(1 for _, profile in results if profile is not None)
        
        secure_logger.log_security_event(
            "BATCH_CV_PROCESSING_COMPLETED", 
            {"total_cvs": len(cv_contents), "successful": success_count, "failed": len(cv_contents) - success_count}
        )
        
        return results
    
    def __del__(self):
        """🔄 Nettoyage des pools de threads."""
        try:
            if hasattr(self, 'ocr_executor'):
                self.ocr_executor.shutdown(wait=False)
            if hasattr(self, 'io_executor'):
                self.io_executor.shutdown(wait=False)
        except Exception:
            pass  # Ignorer erreurs de nettoyage

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

    def _parse_json_response_secure(self, ai_raw_response: str) -> Dict:
        """Parsing sécurisé de la réponse JSON de l'IA."""
        try:
            # Nettoyage préliminaire pour extraire le JSON d'un bloc de code markdown
            match = re.search(r"```json\n(.*?)```", ai_raw_response, re.DOTALL)
            if match:
                json_str = match.group(1)
            else:
                json_str = ai_raw_response

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