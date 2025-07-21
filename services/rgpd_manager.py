from datetime import datetime, timedelta
from typing import List, Dict
import os
from cryptography.fernet import Fernet
import uuid
import logging

class RGPDViolationError(Exception):
    """Exception levée en cas de violation RGPD."""
    pass

class RGPDUserManager:
    def __init__(self):
        self.storage_policies = {
            'free': 'no_storage',
            'premium': 'history_30_days',
            'premium_plus': 'history_12_months'
        }
    
    def can_store_data(self, user_tier: str, explicit_consent: bool) -> bool:
        """Vérifie si on peut stocker selon le tier et le consentement."""
        if user_tier == 'free':
            return False
        return explicit_consent and user_tier in ['premium', 'premium_plus']

    def request_premium_consent(self, user_id: str, tier: str) -> Dict:
        """Simule la demande de consentement explicite pour conservation."""
        # En production, cela impliquerait une interaction UI/DB pour enregistrer le consentement
        consent_request = {
            'user_id': user_id,
            'tier': tier,
            'timestamp': datetime.now().isoformat(),
            'purposes': [
                'conservation_historique_lettres',
                'analyse_progression_candidatures',
                'suggestions_personnalisees'
            ],
            'retention_period': '30_days' if tier == 'premium' else '12_months',
            'rights_info': True,  # Info droits RGPD fournie
            'consent_method': 'explicit_checkbox'
        }
        logging.info(f"Consentement premium demandé pour l'utilisateur {user_id}: {consent_request}")
        return consent_request

class SecurePremiumStorage:
    def __init__(self):
        # La clé de chiffrement doit être gérée de manière sécurisée en production (ex: HSM, KMS)
        # Pour cet exemple, nous la lisons depuis une variable d'environnement.
        self.encryption_key = os.getenv('USER_DATA_ENCRYPTION_KEY')
        if not self.encryption_key:
            raise ValueError("USER_DATA_ENCRYPTION_KEY environment variable not set.")
        self.fernet = Fernet(self.encryption_key.encode())
        # Simule une base de données pour le stockage
        self.db: List[Dict] = [] 

    def user_has_storage_consent(self, user_id: str) -> bool:
        """Simule la vérification du consentement de l'utilisateur."""
        # En production, cela interrogerait une base de données de consentements
        return True # Pour l'exemple, on suppose le consentement acquis

    def calculate_retention_date(self, user_id: str, tier: str) -> datetime:
        """Calcule la date de rétention basée sur le tier de l'utilisateur."""
        if tier == 'premium':
            return datetime.now() + timedelta(days=30)
        elif tier == 'premium_plus':
            return datetime.now() + timedelta(days=365)
        return datetime.now() # Par défaut, pas de rétention

    def store_user_document(self, user_id: str, document_type: str, content: str, tier: str):
        """Stockage chiffré des documents Premium."""
        if not self.user_has_storage_consent(user_id):
            raise RGPDViolationError("No storage consent for user")
        
        # Chiffrement avant stockage
        encrypted_content = self.fernet.encrypt(content.encode())
        
        document = {
            'user_id': user_id,
            'type': document_type,
            'content': encrypted_content.decode(), # Stocker en string pour la simulation DB
            'created_at': datetime.now().isoformat(),
            'retention_until': self.calculate_retention_date(user_id, tier).isoformat(),
            'consent_version': '1.0' # Version du consentement
        }
        
        self.db.append(document)
        logging.info(f"Document chiffré stocké pour l'utilisateur {user_id}, type {document_type}.")

    def get_user_history(self, user_id: str) -> List[Dict]:
        """Récupération historique avec déchiffrement."""
        decrypted_history = []
        for doc in self.db:
            if doc['user_id'] == user_id:
                retention_until = datetime.fromisoformat(doc['retention_until'])
                if datetime.now() > retention_until:
                    logging.info(f"Document expiré pour l'utilisateur {user_id}, type {doc['type']}. Suppression simulée.")
                    # En production, cela déclencherait une suppression réelle de la DB
                    continue
                    
                # Déchiffrer uniquement si pas expiré
                decrypted_content = self.fernet.decrypt(doc['content'].encode()).decode()
                decrypted_history.append({
                    'id': str(uuid.uuid4()), # ID unique pour chaque entrée
                    'type': doc['type'],
                    'content': decrypted_content,
                    'created_at': doc['created_at']
                })
        logging.info(f"Historique récupéré pour l'utilisateur {user_id}. Nombre de documents: {len(decrypted_history)}")
        return decrypted_history

    def delete_all_user_data(self, user_id: str):
        """Simule la suppression de toutes les données d'un utilisateur."""
        initial_count = len(self.db)
        self.db = [doc for doc in self.db if doc['user_id'] != user_id]
        logging.info(f"Données de l'utilisateur {user_id} supprimées. {initial_count - len(self.db)} documents purgés.")

# Exemple d'utilisation (pour les tests ou la démonstration)
if __name__ == "__main__":
    # Assurez-vous que la variable d'environnement est définie pour le test
    os.environ['USER_DATA_ENCRYPTION_KEY'] = Fernet.generate_key().decode()

    rgpd_manager = RGPDUserManager()
    secure_storage = SecurePremiumStorage()

    user_id_premium = "user_premium_123"
    user_id_free = "user_free_456"

    # Test utilisateur gratuit (pas de stockage)
    if rgpd_manager.can_store_data(user_tier='free', explicit_consent=False):
        print("Erreur: Ne devrait pas stocker pour un utilisateur gratuit sans consentement.")
    else:
        print("Utilisateur gratuit: Pas de stockage, conforme.")

    # Test utilisateur premium avec consentement
    if rgpd_manager.can_store_data(user_tier='premium', explicit_consent=True):
        print("Utilisateur premium avec consentement: Stockage autorisé.")
        secure_storage.store_user_document(user_id_premium, 'letter', 'Contenu de la lettre 1.', 'premium')
        secure_storage.store_user_document(user_id_premium, 'cv', 'Contenu du CV 1.', 'premium')
        
        history = secure_storage.get_user_history(user_id_premium)
        print(f"Historique de {user_id_premium}: {history}")

        # Simuler le temps qui passe pour l'expiration
        print("\nSimuler le temps qui passe (31 jours)...")
        # Pour un test réel, il faudrait modifier la date de création ou la date actuelle
        # Ici, on va juste montrer que get_user_history filtrerait les expirés
        # (ce test est plus conceptuel sans une vraie DB avec dates modifiables)
        
        # Test de suppression
        secure_storage.delete_all_user_data(user_id_premium)
        history_after_delete = secure_storage.get_user_history(user_id_premium)
        print(f"Historique après suppression pour {user_id_premium}: {history_after_delete}")

    else:
        print("Utilisateur premium sans consentement: Stockage non autorisé.")

    # Test utilisateur premium_plus
    if rgpd_manager.can_store_data(user_tier='premium_plus', explicit_consent=True):
        print("\nUtilisateur premium_plus avec consentement: Stockage autorisé.")
        secure_storage.store_user_document(user_id_premium, 'letter', 'Contenu de la lettre Premium+.', 'premium_plus')
        history_plus = secure_storage.get_user_history(user_id_premium)
        print(f"Historique de {user_id_premium} (Premium+): {history_plus}")

    # Nettoyage de la variable d'environnement pour ne pas interférer avec d'autres tests
    del os.environ['USER_DATA_ENCRYPTION_KEY']
