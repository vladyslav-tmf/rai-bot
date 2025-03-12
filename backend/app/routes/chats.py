from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.dependencies import get_current_user, get_db
from backend.app.exceptions import AIServiceError
from backend.app.schemas.chat import ChatCreate, ChatInDB, ChatWithMessages
from backend.app.schemas.message import MessageCreate, MessageInDB
from backend.app.schemas.token import TokenData
from backend.app.services.chat import ChatService
from backend.app.services.message import MessageService

router = APIRouter(prefix="/chats", tags=["chats"])


@router.post("/", response_model=ChatInDB, status_code=status.HTTP_201_CREATED)
async def create_chat(
    chat_data: ChatCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    session: AsyncSession = Depends(get_db),
) -> ChatInDB:
    """Create a new chat."""
    try:
        chat_service = ChatService(session)
        return await chat_service.create_chat(chat_data, current_user.user_id)

    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create chat: {str(error)}",
        )


@router.get("/", response_model=list[ChatInDB])
async def get_user_chats(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    session: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 10,
) -> list[ChatInDB]:
    """Get list of user's chats."""
    chat_service = ChatService(session)
    return await chat_service.get_user_chats(current_user.user_id, skip, limit)


@router.get("/{chat_id}", response_model=ChatWithMessages)
async def get_chat(
    chat_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    session: AsyncSession = Depends(get_db),
) -> ChatWithMessages:
    """Get chat by ID with messages."""
    chat_service = ChatService(session)
    chat = await chat_service.get_chat(chat_id, current_user.user_id)

    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Chat {chat_id} not found"
        )

    return chat


@router.delete("/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat(
    chat_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    session: AsyncSession = Depends(get_db),
) -> None:
    """Delete chat."""
    try:
        chat_service = ChatService(session)
        deleted = await chat_service.delete_chat(chat_id, current_user.user_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Chat {chat_id} not found",
            )

    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete chat: {str(error)}",
        )


@router.post("/{chat_id}/messages", response_model=list[MessageInDB])
async def create_message(
    chat_id: UUID,
    message_data: MessageCreate,
    current_user: TokenData = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> list[MessageInDB]:
    """Create a new message and get AI response."""
    try:
        message_service = MessageService(session)

        message_data.chat_id = chat_id

        new_user_message = await message_service.create_user_message(
            message_data, current_user.user_id
        )

        if not new_user_message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Chat {chat_id} not found",
            )

        try:
            ai_response = await message_service.get_ai_response(
                chat_id, message_data.content
            )

            assistant_message = await message_service.create_assistant_message(
                chat_id, ai_response
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


@router.get("/{chat_id}/messages", response_model=list[MessageInDB])
async def read_chat_messages(
    chat_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
    skip: int = 0,
    limit: int = 50,
):
    """Get all messages for a specific chat with pagination."""
    message_service = MessageService(db)
    messages = await message_service.get_chat_messages(
        chat_id=chat_id, user_id=current_user.user_id, skip=skip, limit=limit
    )
    return messages
