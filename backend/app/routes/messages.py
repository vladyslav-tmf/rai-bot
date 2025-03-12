from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.dependencies import get_current_user, get_db
from backend.app.exceptions import AIServiceError
from backend.app.schemas.message import MessageCreate, MessageInDB
from backend.app.schemas.token import TokenData
from backend.app.services.message import MessageService

router = APIRouter(prefix="/messages", tags=["messages"])


@router.post("/", response_model=list[MessageInDB])
async def create_message(
    message_data: MessageCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    session: AsyncSession = Depends(get_db),
) -> list[MessageInDB]:
    """Create a new message and get AI response."""
    try:
        message_service = MessageService(session)

        new_user_message = await message_service.create_user_message(
            message_data, current_user.user_id
        )

        if not new_user_message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Chat {message_data.chat_id} not found",
            )

        try:
            ai_response = await message_service.get_ai_response(
                message_data.chat_id, message_data.content
            )

            assistant_message = await message_service.create_assistant_message(
                message_data.chat_id, ai_response
            )

            return [new_user_message, assistant_message]

        except AIServiceError as error:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to get AI response: {str(error)}",
            )

    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process message: {str(error)}",
        )
