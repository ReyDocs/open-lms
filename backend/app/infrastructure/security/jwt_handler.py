import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from uuid import UUID
from jose import jwt, JWTError
from app.config import settings
from app.application.interfaces.services.i_auth_service import IAuthService


class JWTHandler(IAuthService):
    def __init__(
        self,
        secret_key: str = settings.jwt_secret_key,
        algorithm: str = settings.jwt_algorithm,
        access_token_expire_minutes: int = settings.jwt_access_token_expire_minutes,
        refresh_token_expire_days: int = settings.jwt_refresh_token_expire_days,
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_expire = access_token_expire_minutes
        self.refresh_expire = refresh_token_expire_days

    def create_access_token(self, user_id: UUID, email: str, role: str) -> str:
        now = datetime.now(timezone.utc)
        exp = now + timedelta(minutes=self.access_expire)
        payload = {
            "sub": str(user_id),
            "email": email,
            "role": role,
            "iat": int(now.timestamp()),
            "exp": int(exp.timestamp()),
            "type": "access",
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def create_refresh_token(self) -> str:
        # Generate 64-char URL-safe random string
        return secrets.token_urlsafe(48)

    def hash_token(self, token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    def get_refresh_expiry(self) -> datetime:
        return datetime.now(timezone.utc) + timedelta(days=self.refresh_expire)

    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            if payload.get("type") != "access":
                return None
            return payload
        except JWTError:
            return None
