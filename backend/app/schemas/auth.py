from pydantic import BaseModel, EmailStr


class LoginData(BaseModel):
    """Schema for login credentials."""

    email: EmailStr
    password: str
