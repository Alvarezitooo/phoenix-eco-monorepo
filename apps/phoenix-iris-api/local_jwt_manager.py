from typing import Optional, Dict, Any

from jose import jwt, JWTError


class JWTManager:
    def __init__(self, secret_key: str, algorithm: str = "HS256") -> None:
        self.secret_key = secret_key
        self.algorithm = algorithm

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload if isinstance(payload, dict) else None
        except JWTError:
            return None


