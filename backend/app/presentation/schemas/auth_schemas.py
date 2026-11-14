from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr


class GoogleAuthRequest(BaseModel):
    state: Optional[str] = None


class GoogleAuthResponse(BaseModel):
    authorization_url: str


class GoogleCallbackRequest(BaseModel):
    code: str
    role: Optional[str] = None  # for dev mode selection


class DevLoginRequest(BaseModel):
    email: EmailStr
    role: str = "student"  # admin | teacher | student
    full_name: Optional[str] = None


class TokenPairResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 900  # 15 minutes in seconds
    user: dict


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: Optional[str] = None
