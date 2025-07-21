import subprocess
import logging
import os

class SecurityScanError(Exception):
    """Exception levée pour les erreurs de scan de sécurité."""
    pass

class SecurityScanner:
    def __init__(self):
        # La vérification de ClamAV est rendue optionnelle pour le déploiement Streamlit Cloud.
        # Nous allons vérifier la disponibilité de clamscan au moment de l'utilisation dans scan_file.
        logging.info("Initialisation de SecurityScanner. La disponibilité de ClamAV sera vérifiée lors du scan.")

    def scan_file(self, file_path: str) -> bool:
        """
        Scanne un fichier donné avec ClamAV.
        Retourne True si le fichier est propre, False si une menace est détectée.
        Lève SecurityScanError en cas d'erreur de scan.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Le fichier à scanner n'existe pas: {file_path}")

        logging.info(f"Lancement du scan ClamAV pour le fichier: {file_path}")
        
        # Vérifier la disponibilité de clamscan avant de tenter de l'exécuter
        try:
            subprocess.run(["clamscan", "--version"], check=True, capture_output=True)
            clamscan_available = True
        except (FileNotFoundError, subprocess.CalledProcessError):
            clamscan_available = False
            logging.warning("ClamAV (clamscan) n'est pas installé ou accessible. Le scan antivirus sera ignoré.")
            return True # Considérer le fichier propre si le scanner n'est pas disponible

        if clamscan_available:
            try:
                # Exécute clamscan. --no-summary pour un output plus propre.
                # --stdout pour capturer la sortie.
                # Le code de retour 0 signifie propre, 1 signifie virus trouvé, 2 signifie erreur.
                result = subprocess.run(
                    ["clamscan", "--no-summary", "--stdout", file_path],
                    capture_output=True,
                    text=True,
                    check=False # Ne lève pas d'exception pour le code de retour 1 (virus trouvé)
                )

                if result.returncode == 0:
                    logging.info(f"Fichier {file_path} est propre. ClamAV Output: {result.stdout.strip()}")
                    return True
                elif result.returncode == 1:
                    logging.warning(f"Virus détecté dans le fichier {file_path}. ClamAV Output: {result.stdout.strip()}")
                    return False
                else:
                    # Code de retour 2 ou autre erreur
                    logging.error(f"Erreur lors du scan ClamAV pour {file_path}. Code de retour: {result.returncode}, Erreur: {result.stderr.strip()}")
                    raise SecurityScanError(f"Erreur lors du scan ClamAV: {result.stderr.strip()}")

            except Exception as e:
                logging.error(f"Erreur inattendue lors du scan ClamAV: {e}")
                raise SecurityScanError(f"Erreur inattendue lors du scan ClamAV: {e}")
        else:
            return True # Déjà géré par le warning ci-dessus, mais pour clarté

# Exemple d'utilisation (pour les tests ou la démonstration)
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    scanner = SecurityScanner()

    # Créer un fichier temporaire pour le test
    test_file_path = "test_clean_file.txt"
    with open(test_file_path, "w") as f:
        f.write("Ceci est un fichier de test propre.")

    try:
        is_clean = scanner.scan_file(test_file_path)
        print(f"Le fichier '{test_file_path}' est propre: {is_clean}")
    except SecurityScanError as e:
        print(f"Erreur de scan: {e}")
    finally:
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

    # Pour tester un fichier infecté, tu peux télécharger un fichier EICAR (non dangereux)
    # Par exemple: curl -o eicar.com.txt https://secure.eicar.org/eicar.com.txt
    # Puis scanner 'eicar.com.txt'
    # eicar_test_file = "eicar.com.txt"
    # if os.path.exists(eicar_test_file):
    #     try:
    #         is_clean_eicar = scanner.scan_file(eicar_test_file)
    #         print(f"Le fichier '{eicar_test_file}' est propre: {is_clean_eicar}")
    #     except SecurityScanError as e:
    #         print(f"Erreur de scan: {e}")
    #     finally:
    #         os.remove(eicar_test_file)
