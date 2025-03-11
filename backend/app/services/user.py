from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.exceptions import UserAlreadyExistsError
from backend.app.models.user import User
from backend.app.schemas.user import UserCreate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    """Service for handling user-related operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Generate password hash."""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        return pwd_context.verify(plain_password, hashed_password)

    async def get_user_by_email(self, email: str) -> User | None:
        """Get user by email."""
        query = await self.session.execute(select(User).where(User.email == email))
        return query.scalar_one_or_none()

    async def create_user(self, user_data: UserCreate) -> User:
        """Create new user."""
        try:
            new_user = User(
                email=str(user_data.email),
                hashed_password=self.get_password_hash(user_data.password),
            )
            self.session.add(new_user)
            await self.session.commit()
            await self.session.refresh(new_user)

            return new_user

        except IntegrityError:
            await self.session.rollback()
            raise UserAlreadyExistsError(
                f"User with email {user_data.email} already exists"
            )
