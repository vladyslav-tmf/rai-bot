from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.chat import Chat
from backend.app.models.message import Message, MessageRole
from backend.app.schemas.message import MessageCreate


class MessageService:
    """Service for handling message-related operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_user_message(
        self, message_data: MessageCreate, user_id: UUID
    ) -> Message | None:
        """Create a new user message."""
        try:
            query = await self.session.execute(
                select(Chat).where(
                    Chat.id == message_data.chat_id, Chat.user_id == user_id
                )
            )
            chat = query.scalar_one_or_none()

            if not chat:
                return None

            new_message = Message(
                chat_id=message_data.chat_id,
                content=message_data.content,
                role=MessageRole.USER,
            )

            self.session.add(new_message)
            await self.session.commit()
            await self.session.refresh(new_message)

            return new_message

        except SQLAlchemyError:
            await self.session.rollback()
            raise

    async def create_assistant_message(self, chat_id: UUID, content: str) -> Message:
        """Create a new assistant message."""
        try:
            new_message = Message(
                chat_id=chat_id, content=content, role=MessageRole.ASSISTANT
            )
            self.session.add(new_message)
            await self.session.commit()
            await self.session.refresh(new_message)

            return new_message

        except SQLAlchemyError:
            await self.session.rollback()
            raise

    async def get_chat_messages(
        self, chat_id: UUID, user_id: UUID, skip: int = 0, limit: int = 10
    ) -> list[Message]:
        """Get chat messages with pagination."""
        chat_query = await self.session.execute(
            select(Chat).where(Chat.id == chat_id, Chat.user_id == user_id)
        )

        if not chat_query.scalar_one_or_none():
            return []

        query = await self.session.execute(
            select(Message)
            .where(Message.chat_id == chat_id)
            .order_by(Message.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(query.scalars().all())
