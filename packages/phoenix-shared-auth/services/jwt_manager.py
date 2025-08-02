"""
🚀 Phoenix JWT Manager - Gestion des tokens JWT
Création et validation des tokens d'authentification Phoenix
"""

import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import jwt


class JWTManager:
    """
    Gestionnaire de tokens JWT pour l'authentification Phoenix
    """

    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        """
        Initialise le gestionnaire JWT

        Args:
            secret_key: Clé secrète pour signer les tokens
            algorithm: Algorithme de signature (défaut: HS256)
        """
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = 1440  # 24h
        self.refresh_token_expire_days = 30  # 30 jours

    def create_access_token(
        self, user_id: str, additional_claims: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Crée un token d'accès JWT

        Args:
            user_id: ID de l'utilisateur
            additional_claims: Claims additionnels optionnels

        Returns:
            str: Token JWT signé
        """
        now = datetime.utcnow()
        expire = now + timedelta(minutes=self.access_token_expire_minutes)

        payload = {
            "sub": user_id,
            "type": "access",
            "iat": now,
            "exp": expire,
            "jti": str(uuid.uuid4()),  # Token ID unique
        }

        if additional_claims:
            payload.update(additional_claims)

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def create_refresh_token(self, user_id: str) -> str:
        """
        Crée un token de rafraîchissement JWT

        Args:
            user_id: ID de l'utilisateur

        Returns:
            str: Token de rafraîchissement JWT signé
        """
        now = datetime.utcnow()
        expire = now + timedelta(days=self.refresh_token_expire_days)

        payload = {
            "sub": user_id,
            "type": "refresh",
            "iat": now,
            "exp": expire,
            "jti": str(uuid.uuid4()),
        }

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Vérifie et décode un token JWT

        Args:
            token: Token JWT à vérifier

        Returns:
            Optional[Dict[str, Any]]: Payload du token si valide, None sinon
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def get_user_id_from_token(self, token: str) -> Optional[str]:
        """
        Extrait l'ID utilisateur d'un token

        Args:
            token: Token JWT

        Returns:
            Optional[str]: ID utilisateur si token valide
        """
        payload = self.verify_token(token)
        if payload:
            return payload.get("sub")
        return None

    def is_token_expired(self, token: str) -> bool:
        """
        Vérifie si un token est expiré

        Args:
            token: Token JWT à vérifier

        Returns:
            bool: True si expiré
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return False
        except jwt.ExpiredSignatureError:
            return True
        except jwt.InvalidTokenError:
            return True

    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """
        Génère un nouveau token d'accès à partir du refresh token

        Args:
            refresh_token: Token de rafraîchissement

        Returns:
            Optional[str]: Nouveau token d'accès si refresh valide
        """
        payload = self.verify_token(refresh_token)

        if not payload or payload.get("type") != "refresh":
            return None

        user_id = payload.get("sub")
        if user_id:
            return self.create_access_token(user_id)

        return None
