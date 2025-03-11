from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    """Base user schema with email attribute."""

    email: EmailStr


class UserCreate(UserBase):
    """Schema for user creation."""

    password: str


class UserInDB(UserBase):
    """Schema for user data from database."""

    id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
