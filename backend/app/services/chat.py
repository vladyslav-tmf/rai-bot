from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.app.models.chat import Chat
from backend.app.schemas.chat import ChatCreate


class ChatService:
    """Service for handling chat-related operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_chat(self, chat_data: ChatCreate, user_id: UUID) -> Chat:
        """Create a new chat."""
        try:
            new_chat = Chat(title=chat_data.title, user_id=user_id)
            self.session.add(new_chat)
            await self.session.commit()
            await self.session.refresh(new_chat)

            return new_chat

        except SQLAlchemyError:
            await self.session.rollback()
            raise

    async def get_chat(self, chat_id: UUID, user_id: UUID) -> Chat | None:
        """Get chat by ID."""
        query = await self.session.execute(
            select(Chat)
            .where(Chat.id == chat_id, Chat.user_id == user_id)
            .options(selectinload(Chat.messages))
        )
        return query.scalar_one_or_none()

    async def get_user_chats(
        self, user_id: UUID, skip: int = 0, limit: int = 10
    ) -> list[Chat]:
        """Get user's chats with pagination."""
        query = await self.session.execute(
            select(Chat)
            .where(Chat.user_id == user_id)
            .options(selectinload(Chat.messages))
            .order_by(Chat.updated_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(query.scalars().all())

    async def delete_chat(self, chat_id: UUID, user_id: UUID) -> bool:
        """Delete chat."""
        try:
            query = await self.session.execute(
                select(Chat).where(Chat.id == chat_id, Chat.user_id == user_id)
            )
            chat = query.scalar_one_or_none()

            if not chat:
                return False

            await self.session.delete(chat)
            await self.session.commit()

            return True

        except SQLAlchemyError:
            await self.session.rollback()
            raise
