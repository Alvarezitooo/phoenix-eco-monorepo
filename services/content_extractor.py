import os
import tempfile
import magic
import pdfplumber
from abc import ABC, abstractmethod

class FileProcessingError(Exception):
    """Exception levée pour les erreurs de traitement de fichier."""
    pass

class ContentExtractor(ABC):
    """Classe abstraite pour l'extraction de contenu."""
    @abstractmethod
    def extract(self, uploaded_file) -> str:
        pass

class PdfExtractor(ContentExtractor):
    """Extracteur de contenu pour les fichiers PDF."""
    def extract(self, uploaded_file) -> str:
        cv_content = ""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            temp_pdf.write(uploaded_file.getbuffer())
            temp_pdf_path = temp_pdf.name
        try:
            with pdfplumber.open(temp_pdf_path) as pdf:
                cv_content = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
        finally:
            os.remove(temp_pdf_path)
        return cv_content

class TextExtractor(ContentExtractor):
    """Extracteur de contenu pour les fichiers TXT."""
    def extract(self, uploaded_file) -> str:
        return uploaded_file.getvalue().decode("utf-8")

class ContentExtractorFactory:
    """Factory pour créer des extracteurs de contenu basés sur le type MIME."""
    _extractors = {
        "application/pdf": PdfExtractor(),
        "text/plain": TextExtractor(),
    }

    @classmethod
    def get_extractor(cls, mime_type: str) -> ContentExtractor:
        extractor = cls._extractors.get(mime_type)
        if not extractor:
            raise FileProcessingError(f"Aucun extracteur disponible pour le type MIME: {mime_type}")
        return extractor

def _validate_file(uploaded_file, allowed_types: list, max_size_mb: int) -> str:
    """
    Valide un fichier uploadé (taille, type MIME) et retourne son type MIME.
    """
    if uploaded_file.size == 0:
        raise FileProcessingError("Le fichier est vide. Veuillez charger un fichier valide.")

    file_buffer = uploaded_file.read(2048)
    uploaded_file.seek(0)

    mime_type = magic.from_buffer(file_buffer, mime=True)
    if mime_type not in allowed_types:
        raise FileProcessingError(f"Type de fichier non valide ({mime_type}). Seuls les types {', '.join(allowed_types)} sont autorisés.")

    MAX_FILE_SIZE_BYTES = max_size_mb * 1024 * 1024
    if uploaded_file.size > MAX_FILE_SIZE_BYTES:
        raise FileProcessingError(f"Le fichier est trop volumineux. La taille maximale autorisée est de {max_size_mb} Mo.")
    
    return mime_type

def extract_cv_content(uploaded_cv_file) -> str:
    """
    Extrait le contenu textuel d'un fichier CV uploadé (PDF ou TXT).
    Effectue des validations de taille, de type MIME et de contenu.
    """
    mime_type = _validate_file(uploaded_cv_file, ["application/pdf", "text/plain"], 5)
    extractor = ContentExtractorFactory.get_extractor(mime_type)
    cv_content = extractor.extract(uploaded_cv_file)

    if not cv_content.strip():
        raise FileProcessingError("Le contenu du CV est vide ou illisible après extraction. Veuillez vérifier votre fichier.")

    return cv_content

def extract_annonce_content(uploaded_annonce_file) -> str:
    """
    Extrait le contenu textuel d'un fichier annonce uploadé (TXT).
    Effectue des validations de taille, de type MIME et de contenu.
    """
    mime_type = _validate_file(uploaded_annonce_file, ["text/plain"], 5) # Annonce TXT seulement, même limite de taille
    extractor = ContentExtractorFactory.get_extractor(mime_type)
    annonce_content = extractor.extract(uploaded_annonce_file)

    if not annonce_content.strip():
        raise FileProcessingError("Le contenu de l'annonce est vide ou illisible après extraction. Veuillez vérifier votre fichier.")

    return annonce_content