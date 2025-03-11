from datetime import datetime, UTC, timedelta

from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.config import settings
from backend.app.exceptions import AuthenticationError
from backend.app.schemas.token import TokenData
from backend.app.services.user import UserService


class AuthService:
    """Service for handling authentication operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_service = UserService(session)

    @staticmethod
    def create_access_token(email: str) -> str:
        """Create JWT access token."""
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode = {"sub": email, "exp": expire}
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")

        return encoded_jwt

    async def authenticate_user(self, email: str, password: str) -> bool:
        """Verify user credentials."""
        user = await self.user_service.get_user_by_email(email)

        if not user:
            raise AuthenticationError("Invalid credentials")

        if not self.user_service.verify_password(password, user.hashed_password):
            raise AuthenticationError("Invalid credentials")

        return True

    @staticmethod
    def verify_token(token: str) -> TokenData:
        """Verify JWT token and return token data."""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            email = payload.get("sub")

            if not email:
                raise AuthenticationError("Could not validate credentials")

            return TokenData(email=email)

        except JWTError:
            raise AuthenticationError("Could not validate credentials")
