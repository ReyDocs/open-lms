from typing import Optional
from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.application.interfaces.repositories.i_user_repository import IUserRepository
from app.domain.entities.user import User
from app.presentation.dependencies.services import get_jwt_handler, get_user_repo
from app.infrastructure.security.jwt_handler import JWTHandler

security = HTTPBearer(auto_error=False)


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    jwt_handler: JWTHandler = Depends(get_jwt_handler),
    user_repo: IUserRepository = Depends(get_user_repo),
) -> Optional[User]:
    if not credentials:
        return None
    token = credentials.credentials
    payload = jwt_handler.decode_token(token)
    if not payload:
        return None

    user_id_str = payload.get("sub")
    if not user_id_str:
        return None

    try:
        user_id = UUID(user_id_str)
    except ValueError:
        return None

    return await user_repo.get_by_id(user_id)


async def get_current_user(
    user: Optional[User] = Depends(get_current_user_optional),
) -> User:
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def require_admin(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user


async def require_teacher(user: User = Depends(get_current_user)) -> User:
    if not user.is_teacher():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Teacher access required",
        )
    return user


async def require_student(user: User = Depends(get_current_user)) -> User:
    return user
