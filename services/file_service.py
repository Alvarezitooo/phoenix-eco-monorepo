import logging
from pathlib import Path
from typing import Optional, Union
import pdfplumber

# --- Constantes de Sécurité ---
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_EXTENSIONS = {'.txt', '.pdf'}

# --- Exceptions Personnalisées ---
class FileProcessingError(Exception):
    """Exception pour les erreurs de traitement de fichiers."""
    pass

# --- Fonctions de Service Fichier ---

def lire_cv(chemin_cv: Union[str, Path]) -> Optional[str]:
    """Lit le contenu d'un CV, qu'il soit en .txt ou .pdf."""
    path = Path(chemin_cv)

    if not path.exists():
        logging.error(f"ERREUR : Le fichier CV '{chemin_cv}' n'a pas été trouvé.")
        raise FileProcessingError(f"Fichier CV non trouvé : {chemin_cv}")

    if path.stat().st_size > MAX_FILE_SIZE:
        logging.error(f"ERREUR : Le fichier CV '{chemin_cv}' est trop volumineux (max {MAX_FILE_SIZE / (1024 * 1024):.0f}MB).")
        raise FileProcessingError(f"Fichier CV trop volumineux : {chemin_cv}")

    if path.suffix.lower() not in ALLOWED_EXTENSIONS:
        logging.error(f"ERREUR : Extension de fichier non supportée pour le CV : '{chemin_cv}'. Utilisez .txt ou .pdf.")
        raise FileProcessingError(f"Format de fichier CV non supporté : {chemin_cv}")

    if path.suffix.lower() == '.pdf':
        try:
            with pdfplumber.open(chemin_cv) as pdf:
                texte_cv = ''
                for page in pdf.pages:
                    texte_cv += page.extract_text() or ''
            return texte_cv
        except Exception as e:
            logging.error(f"ERREUR : Impossible de lire le fichier PDF '{chemin_cv}'. Il est peut-être corrompu. Erreur : {e}")
            raise FileProcessingError(f"Impossible de lire le PDF CV : {e}")
    elif path.suffix.lower() == '.txt':
        try:
            with open(chemin_cv, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logging.error(f"ERREUR : Impossible de lire le fichier texte '{chemin_cv}'. Erreur : {e}")
            raise FileProcessingError(f"Impossible de lire le fichier texte CV : {e}")
    return None

def lire_annonce(chemin_annonce: Union[str, Path]) -> Optional[str]:
    """Lit le contenu de l'annonce d'emploi (format .txt)."""
    path = Path(chemin_annonce)

    if not path.exists():
        logging.error(f"ERREUR : Le fichier annonce '{chemin_annonce}' n'a pas été trouvé.")
        raise FileProcessingError(f"Fichier annonce non trouvé : {chemin_annonce}")

    if path.stat().st_size > MAX_FILE_SIZE:
        logging.error(f"ERREUR : Le fichier annonce '{chemin_annonce}' est trop volumineux (max {MAX_FILE_SIZE / (1024 * 1024):.0f}MB).")
        raise FileProcessingError(f"Fichier annonce trop volumineux : {chemin_annonce}")

    if path.suffix.lower() != '.txt':
        logging.error(f"ERREUR : Le fichier annonce '{chemin_annonce}' doit être un fichier .txt.")
        raise FileProcessingError(f"Le fichier annonce doit être un fichier .txt : {chemin_annonce}")
    
    try:
        with open(chemin_annonce, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logging.error(f"ERREUR : Impossible de lire le fichier annonce '{chemin_annonce}'. Erreur : {e}")
        raise FileProcessingError(f"Impossible de lire le fichier annonce : {e}")

def sauvegarder_lettre(contenu: str, nom_fichier: str = 'lettre_generee.txt') -> None:
    """Sauvegarde la lettre générée dans un fichier texte."""
    try:
        with open(nom_fichier, 'w', encoding='utf-8') as f:
            f.write(contenu)
        logging.info(f"Succès ! La lettre de motivation a été générée dans le fichier : {nom_fichier}")
    except Exception as e:
        logging.error(f"ERREUR : Impossible de sauvegarder la lettre. Erreur : {e}")
        raise FileProcessingError(f"Impossible de sauvegarder la lettre : {e}")
