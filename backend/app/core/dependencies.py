from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from backend.app.db.session import AsyncSessionLocal
from backend.app.exceptions import AuthenticationError
from backend.app.schemas.token import TokenData
from backend.app.services.auth import AuthService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def get_db():
    """Dependency for getting async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session

        finally:
            await session.close()


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> TokenData:
    """Dependency for getting current authenticated user from JWT token."""
    try:
        return AuthService.verify_token(token)

    except AuthenticationError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error),
            headers={"WWW-Authenticate": "Bearer"},
        )
