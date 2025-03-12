from datetime import UTC, datetime, timedelta
from uuid import UUID

from jose import JWTError, jwt
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
    def create_access_token(email: str, user_id: UUID) -> str:
        """Create JWT access token."""
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode = {"sub": email, "user_id": str(user_id), "exp": expire}
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
            user_id = payload.get("user_id")

            if not email or not user_id:
                raise AuthenticationError("Could not validate credentials")

            return TokenData(email=email, user_id=UUID(user_id))

        except (JWTError, ValueError):
            raise AuthenticationError("Could not validate credentials")
