from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.dependencies import get_current_user, get_db
from backend.app.schemas.token import TokenData
from backend.app.schemas.user import UserInDB
from backend.app.services.user import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserInDB)
async def get_current_user_info(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    session: AsyncSession = Depends(get_db),
) -> UserInDB:
    """Get information about the currently authenticated user."""
    user_service = UserService(session)
    user = await user_service.get_user_by_email(current_user.email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return user
