from datetime import datetime, timezone
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from app.config import settings
from app.domain.entities.user import User
from app.infrastructure.security.jwt_handler import JWTHandler
from app.infrastructure.external.google_oauth_service import GoogleOAuthService
from app.infrastructure.repositories.sqlalchemy_user_repo import SQLAlchemyUserRepository
from app.infrastructure.repositories.sqlalchemy_refresh_token_repo import SQLAlchemyRefreshTokenRepository
from app.presentation.dependencies.services import (
    get_jwt_handler, get_google_oauth_service, get_user_repo, get_refresh_token_repo
)
from app.presentation.dependencies.auth import get_current_user
from app.presentation.schemas.auth_schemas import (
    GoogleAuthRequest, GoogleAuthResponse, GoogleCallbackRequest,
    TokenPairResponse, RefreshTokenRequest, LogoutRequest, DevLoginRequest
)
from app.presentation.schemas.user_schemas import UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/google", response_model=GoogleAuthResponse)
async def initiate_google_auth(
    req: GoogleAuthRequest = None,
    google_oauth: GoogleOAuthService = Depends(get_google_oauth_service),
):
    state = req.state if req else None
    url = google_oauth.get_authorization_url(state)
    return GoogleAuthResponse(authorization_url=url)


@router.get("/google/callback")
async def google_callback_get(code: str = Query(...)):
    """Handle the browser redirect from Google OAuth consent screen and forward to frontend."""
    frontend = settings.frontend_url.strip()
    if not frontend.startswith("http://") and not frontend.startswith("https://"):
        frontend = f"https://{frontend}"
    frontend_login_url = f"{frontend.rstrip('/')}/login?code={code}"
    return RedirectResponse(url=frontend_login_url)


@router.post("/google/callback", response_model=TokenPairResponse)
async def google_callback(
    req: GoogleCallbackRequest,
    google_oauth: GoogleOAuthService = Depends(get_google_oauth_service),
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repo),
    jwt_handler: JWTHandler = Depends(get_jwt_handler),
    refresh_token_repo: SQLAlchemyRefreshTokenRepository = Depends(get_refresh_token_repo),
):
    try:
        user_info = await google_oauth.get_user_info_from_code(req.code)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    email = user_info["email"].lower().strip()
    user = await user_repo.get_by_email(email)

    now = datetime.now(timezone.utc)
    if not user:
        # Auto-create user on first login, default role is 'student'
        user = User(
            id=uuid4(),
            email=email,
            full_name=user_info.get("full_name") or email.split("@")[0].title(),
            avatar_url=user_info.get("avatar_url"),
            google_id=user_info.get("google_id"),
            role="student",
            created_at=now,
            updated_at=now,
        )
        user = await user_repo.create(user)
    else:
        # Update google_id or avatar if missing
        updated = False
        if not user.google_id and user_info.get("google_id"):
            user.google_id = user_info.get("google_id")
            updated = True
        if not user.avatar_url and user_info.get("avatar_url"):
            user.avatar_url = user_info.get("avatar_url")
            updated = True
        if updated:
            user = await user_repo.update(user)

    # Issue JWT pair
    access_token = jwt_handler.create_access_token(user.id, user.email, user.role)
    raw_refresh_token = jwt_handler.create_refresh_token()
    token_hash = jwt_handler.hash_token(raw_refresh_token)
    expires_at = jwt_handler.get_refresh_expiry()

    await refresh_token_repo.create(user.id, token_hash, expires_at)

    return TokenPairResponse(
        access_token=access_token,
        refresh_token=raw_refresh_token,
        user={
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "avatar_url": user.avatar_url,
            "student_id": user.student_id,
        },
    )


@router.post("/dev-login", response_model=TokenPairResponse)
async def dev_login(
    req: DevLoginRequest,
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repo),
    jwt_handler: JWTHandler = Depends(get_jwt_handler),
    refresh_token_repo: SQLAlchemyRefreshTokenRepository = Depends(get_refresh_token_repo),
):
    """Convenience development endpoint for fast role switching during demos/testing."""
    if settings.app_env.lower() not in {"development", "dev", "test"}:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    email = req.email.lower().strip()
    user = await user_repo.get_by_email(email)
    now = datetime.now(timezone.utc)

    if not user:
        user = User(
            id=uuid4(),
            email=email,
            full_name=req.full_name or email.split("@")[0].title(),
            role=req.role,
            avatar_url=f"https://api.dicebear.com/7.x/avataaars/svg?seed={email}",
            created_at=now,
            updated_at=now,
        )
        user = await user_repo.create(user)

    access_token = jwt_handler.create_access_token(user.id, user.email, user.role)
    raw_refresh_token = jwt_handler.create_refresh_token()
    token_hash = jwt_handler.hash_token(raw_refresh_token)
    expires_at = jwt_handler.get_refresh_expiry()

    await refresh_token_repo.create(user.id, token_hash, expires_at)

    return TokenPairResponse(
        access_token=access_token,
        refresh_token=raw_refresh_token,
        user={
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "avatar_url": user.avatar_url,
            "student_id": user.student_id,
        },
    )


@router.post("/refresh", response_model=TokenPairResponse)
async def refresh_access_token(
    req: RefreshTokenRequest,
    jwt_handler: JWTHandler = Depends(get_jwt_handler),
    refresh_token_repo: SQLAlchemyRefreshTokenRepository = Depends(get_refresh_token_repo),
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repo),
):
    token_hash = jwt_handler.hash_token(req.refresh_token)
    token_record = await refresh_token_repo.get_valid(token_hash)
    if not token_record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    # Rotate refresh token (revoke old)
    await refresh_token_repo.revoke(token_hash)

    user = await user_repo.get_by_id(token_record["user_id"])
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    new_access_token = jwt_handler.create_access_token(user.id, user.email, user.role)
    new_raw_refresh_token = jwt_handler.create_refresh_token()
    new_token_hash = jwt_handler.hash_token(new_raw_refresh_token)
    expires_at = jwt_handler.get_refresh_expiry()

    await refresh_token_repo.create(user.id, new_token_hash, expires_at)

    return TokenPairResponse(
        access_token=new_access_token,
        refresh_token=new_raw_refresh_token,
        user={
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "avatar_url": user.avatar_url,
            "student_id": user.student_id,
        },
    )


@router.post("/logout")
async def logout(
    req: LogoutRequest = None,
    current_user: User = Depends(get_current_user),
    jwt_handler: JWTHandler = Depends(get_jwt_handler),
    refresh_token_repo: SQLAlchemyRefreshTokenRepository = Depends(get_refresh_token_repo),
):
    if req and req.refresh_token:
        token_hash = jwt_handler.hash_token(req.refresh_token)
        await refresh_token_repo.revoke(token_hash)
    else:
        # Revoke all refresh tokens for current user
        await refresh_token_repo.revoke_all_for_user(current_user.id)
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
