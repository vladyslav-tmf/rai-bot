from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from backend.app.models.message import MessageRole


class MessageBase(BaseModel):
    """Base schema for message."""

    content: str
    role: MessageRole = Field(
        default=MessageRole.USER, description="Role of the message sender"
    )


class MessageCreate(MessageBase):
    """Schema for creating a new message."""

    chat_id: UUID | None = None


class MessageInDB(MessageBase):
    """Schema for message from database."""

    id: UUID
    chat_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
