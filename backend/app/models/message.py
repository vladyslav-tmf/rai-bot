from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    chat_id: Mapped[UUID] = mapped_column(ForeignKey("chats.id", ondelete="CASCADE"))
    content: Mapped[str] = mapped_column(Text)
    role: Mapped[MessageRole] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    chat = relationship("Chat", back_populates="messages")
