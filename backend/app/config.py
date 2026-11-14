from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    app_name: str = "OpenLMS"
    app_env: str = "development"
    debug: bool = True

    # Database
    database_url: str = "sqlite+aiosqlite:///./openlms.db"

    # Supabase (optional for dev, can use local filesystem storage)
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None
    supabase_service_key: Optional[str] = None

    # Google OAuth
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None
    google_redirect_uri: str = "http://localhost:8000/api/v1/auth/google/callback"

    # JWT
    jwt_secret_key: str = "openlms-super-secret-jwt-key-for-development-change-in-production-min32bytes"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_days: int = 7

    # Email (Resend)
    resend_api_key: Optional[str] = None
    email_from: str = "noreply@openlms.app"

    # CORS
    allowed_origins: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173"

    # File Upload
    max_file_size_mb: int = 25
    upload_dir: str = "uploads"

    # System settings (Admin managed defaults)
    support_email: str = "support@openlms.app"
    app_logo_url: Optional[str] = None
    maintenance_mode: bool = False

    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
