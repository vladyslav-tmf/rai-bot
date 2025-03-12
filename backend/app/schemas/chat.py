from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from backend.app.schemas.message import MessageInDB


class ChatBase(BaseModel):
    """Base schema for chat."""

    title: str = Field(min_length=1, max_length=255, description="Title of the chat")


class ChatCreate(ChatBase):
    """Schema for creating a new chat."""


class ChatInDB(ChatBase):
    """Schema for chat from database."""

    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatWithMessages(ChatInDB):
    """Schema for chat with messages."""

    messages: list[MessageInDB] = []
