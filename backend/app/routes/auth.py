from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.dependencies import get_db
from backend.app.exceptions import AuthenticationError, UserAlreadyExistsError
from backend.app.schemas.auth import LoginData
from backend.app.schemas.token import Token
from backend.app.schemas.user import UserCreate, UserInDB
from backend.app.services.auth import AuthService
from backend.app.services.user import UserService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate, session: AsyncSession = Depends(get_db)
) -> UserInDB:
    """Register a new user."""
    try:
        user_service = UserService(session)
        new_user = await user_service.create_user(user_data)

        return new_user

    except UserAlreadyExistsError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error))


@router.post("/login", response_model=Token)
async def login(
    login_data: LoginData, session: AsyncSession = Depends(get_db)
) -> Token:
    try:
        auth_service = AuthService(session)
        await auth_service.authenticate_user(
            email=str(login_data.email), password=login_data.password
        )
        access_token = auth_service.create_access_token(email=str(login_data.email))

        return Token(access_token=access_token)

    except AuthenticationError as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error))
