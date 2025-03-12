from uuid import UUID

from pydantic import BaseModel, ConfigDict


class Token(BaseModel):
    """Schema for access token."""

    access_token: str
    token_type: str = "bearer"

    model_config = ConfigDict(from_attributes=True)


class TokenData(BaseModel):
    """Schema for token payload."""

    email: str
    user_id: UUID

    model_config = ConfigDict(from_attributes=True)
