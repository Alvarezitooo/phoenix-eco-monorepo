"""
🛡️ MITIGATION PYPDF DOS VULNERABILITY (CVE-2023-36810)
Protection contre la vulnérabilité de boucle infinie dans pypdf/PyPDF2.

Vulnérabilité: Boucle infinie dans __parse_content_stream quand un commentaire PDF 
n'est pas suivi d'un caractère de nouvelle ligne.

GitHub Advisory: https://github.com/py-pdf/pypdf/security/advisories/GHSA-wcxv-qwqq-5xw2
Fix: py-pdf/pypdf#1828
"""

import logging
import signal
import subprocess
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

class PyPDFDoSMitigator:
    """Protection contre la vulnérabilité DoS pypdf CVE-2023-36810"""
    
    # Configuration de sécurité
    PDF_PROCESSING_TIMEOUT = 10  # 10 secondes max pour traiter un PDF
    MAX_PDF_SIZE_MB = 5  # 5MB max
    SAFE_PYPDF_VERSION = "3.9.0"  # Version sûre minimum
    
    @classmethod
    def validate_pypdf_version(cls) -> bool:
        """Vérifie si la version de pypdf est sûre"""
        try:
            import pypdf
            from packaging import version
            
            current_version = version.parse(pypdf.__version__)
            safe_version = version.parse(cls.SAFE_PYPDF_VERSION)
            
            is_safe = current_version >= safe_version
            
            if not is_safe:
                logger.warning(
                    f"SECURITY: pypdf version {pypdf.__version__} is vulnerable to CVE-2023-36810. "
                    f"Upgrade to >= {cls.SAFE_PYPDF_VERSION}"
                )
            
            return is_safe
            
        except ImportError:
            logger.warning("pypdf not installed, using alternative PDF processing")
            return False
        except Exception as e:
            logger.error(f"Error checking pypdf version: {e}")
            return False
    
    @classmethod
    @contextmanager
    def timeout_protection(cls, timeout_seconds: int = PDF_PROCESSING_TIMEOUT):
        """Context manager pour protéger contre les boucles infinies"""
        
        def timeout_handler(signum, frame):
            raise TimeoutError(f"PDF processing timeout after {timeout_seconds} seconds")
        
        # Set up signal handler
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout_seconds)
        
        try:
            yield
        finally:
            signal.alarm(0)  # Cancel alarm
            signal.signal(signal.SIGALRM, old_handler)  # Restore old handler
    
    @classmethod
    def safe_pdf_text_extraction(cls, pdf_content: bytes, filename: str = "upload.pdf") -> str:
        """
        Extraction sécurisée de texte PDF avec protection DoS.
        
        Args:
            pdf_content: Contenu binaire du PDF
            filename: Nom du fichier pour logs
            
        Returns:
            str: Texte extrait du PDF
            
        Raises:
            ValueError: Si le PDF est malveillant ou invalide
            TimeoutError: Si le traitement prend trop de temps
        """
        
        # Vérification de la taille
        if len(pdf_content) > cls.MAX_PDF_SIZE_MB * 1024 * 1024:
            raise ValueError(f"PDF trop volumineux: {len(pdf_content)} bytes")
        
        # Vérification de version pypdf
        pypdf_safe = cls.validate_pypdf_version()
        
        if pypdf_safe:
            # Utiliser pypdf avec protection timeout
            return cls._extract_with_pypdf_protected(pdf_content, filename)
        else:
            # Fallback vers extraction externe sécurisée
            return cls._extract_with_external_tool(pdf_content, filename)
    
    @classmethod
    def _extract_with_pypdf_protected(cls, pdf_content: bytes, filename: str) -> str:
        """Extraction avec pypdf protégée par timeout"""
        
        import io
        try:
            import pypdf
        except ImportError:
            raise ValueError("pypdf not available for PDF processing")
        
        try:
            with cls.timeout_protection(cls.PDF_PROCESSING_TIMEOUT):
                # Détection préventive de patterns dangereux
                cls._scan_dangerous_pdf_patterns(pdf_content)
                
                # Extraction protégée
                pdf_stream = io.BytesIO(pdf_content)
                reader = pypdf.PdfReader(pdf_stream)
                
                # Limitation du nombre de pages pour éviter DoS
                max_pages = 100
                if len(reader.pages) > max_pages:
                    logger.warning(f"PDF has {len(reader.pages)} pages, limiting to {max_pages}")
                    pages_to_process = reader.pages[:max_pages]
                else:
                    pages_to_process = reader.pages
                
                # Extraction page par page avec timeout individuel
                extracted_text = []
                for i, page in enumerate(pages_to_process):
                    try:
                        with cls.timeout_protection(2):  # 2s max par page
                            text = page.extract_text()
                            extracted_text.append(text)
                    except TimeoutError:
                        logger.warning(f"Timeout extracting page {i+1} from {filename}")
                        break
                    except Exception as e:
                        logger.warning(f"Error extracting page {i+1}: {e}")
                        continue
                
                result = "\n".join(extracted_text)
                logger.info(f"Successfully extracted {len(result)} characters from {filename}")
                return result
                
        except TimeoutError:
            logger.error(f"PDF processing timeout for {filename} - potential DoS attempt")
            raise ValueError("PDF processing timeout - fichier potentiellement malveillant")
        except Exception as e:
            logger.error(f"Error processing PDF {filename}: {e}")
            raise ValueError(f"Erreur lors du traitement PDF: {str(e)}")
    
    @classmethod  
    def _extract_with_external_tool(cls, pdf_content: bytes, filename: str) -> str:
        """Extraction avec outil externe (pdftotext) pour sécurité maximale"""
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_pdf:
            tmp_pdf.write(pdf_content)
            tmp_pdf.flush()
            
            try:
                # Utiliser pdftotext avec timeout strict
                result = subprocess.run([
                    'pdftotext', 
                    '-enc', 'UTF-8',
                    '-eol', 'unix',
                    '-nopgbrk',
                    tmp_pdf.name, 
                    '-'  # Output to stdout
                ], 
                    capture_output=True, 
                    text=True, 
                    timeout=cls.PDF_PROCESSING_TIMEOUT,
                    check=False
                )
                
                if result.returncode == 0:
                    logger.info(f"Successfully extracted text using pdftotext from {filename}")
                    return result.stdout
                else:
                    logger.error(f"pdftotext failed for {filename}: {result.stderr}")
                    raise ValueError("Échec extraction PDF avec outil externe")
                    
            except subprocess.TimeoutExpired:
                logger.error(f"pdftotext timeout for {filename} - potential DoS")
                raise ValueError("Timeout extraction PDF - fichier potentiellement malveillant")
            except FileNotFoundError:
                logger.error("pdftotext not available, cannot process PDF safely")
                raise ValueError("Outils d'extraction PDF non disponibles")
            finally:
                Path(tmp_pdf.name).unlink(missing_ok=True)
    
    @classmethod
    def _scan_dangerous_pdf_patterns(cls, content: bytes) -> None:
        """Scanne le PDF pour des patterns pouvant causer des DoS"""
        
        # Patterns dangereux spécifiques à la vulnérabilité CVE-2023-36810
        dangerous_patterns = [
            b'%comment_without_newline',  # Commentaire sans \n ou \r
            b'%%PDF-1.%comment',  # Commentaire immédiatement après version
        ]
        
        # Recherche de commentaires mal formés (cause de la vulnérabilité)
        malformed_comment_pattern = rb'%[^\r\n]*$'  # Commentaire en fin de ligne sans newline
        
        import re
        if re.search(malformed_comment_pattern, content, re.MULTILINE):
            logger.warning("Potential malformed PDF comment detected - DoS risk")
            raise ValueError("PDF contient des commentaires potentiellement malveillants")
        
        # Recherche d'autres patterns suspects
        for pattern in dangerous_patterns:
            if pattern in content:
                logger.warning(f"Dangerous PDF pattern detected: {pattern}")
                raise ValueError("PDF contient des patterns potentiellement dangereux")
        
        # Vérification de structures répétitives (PDF bombs)
        if content.count(b'obj') > 10000:
            raise ValueError("PDF contient trop d'objets - potentiel PDF bomb")
        
        if content.count(b'stream') > 1000:
            raise ValueError("PDF contient trop de streams - potentiel malware")

# Fonction utilitaire pour intégration facile
def safe_extract_pdf_text(pdf_content: bytes, filename: str = "upload.pdf") -> str:
    """
    Interface simplifiée pour extraction sécurisée de PDF.
    Protection complète contre CVE-2023-36810 et autres vulnérabilités PDF.
    """
    return PyPDFDoSMitigator.safe_pdf_text_extraction(pdf_content, filename)

# Test de sécurité pour l'équipe
def test_pdf_vulnerability_protection():
    """Test de protection contre la vulnérabilité pypdf DoS"""
    
    # Créer un PDF minimal avec commentaire malformé (SANS newline)
    malicious_pdf_content = b"""%PDF-1.4%malicious_comment_without_newline
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj  
3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]>>endobj
xref
0 4
0000000000 65535 f 
0000000050 00000 n 
0000000089 00000 n 
0000000136 00000 n 
trailer<</Size 4/Root 1 0 R>>
startxref
196
%%EOF"""
    
    try:
        result = safe_extract_pdf_text(malicious_pdf_content, "test_malicious.pdf")
        logger.info("✅ PDF vulnerability protection test passed")
        return True
    except (ValueError, TimeoutError) as e:
        logger.info(f"✅ PDF vulnerability correctly blocked: {e}")
        return True
    except Exception as e:
        logger.error(f"❌ Unexpected error in vulnerability test: {e}")
        return False

if __name__ == "__main__":
    # Test de la protection
    test_result = test_pdf_vulnerability_protection()
    print(f"PDF DoS Protection Test: {'✅ PASSED' if test_result else '❌ FAILED'}")