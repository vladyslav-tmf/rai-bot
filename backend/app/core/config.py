import secrets
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "RAI Bot"
    VERSION: str = "0.1.0"
    API_PREFIX: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:8000"]

    @classmethod
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, origins: str | list[str]) -> list[str] | str:
        if isinstance(origins, str) and not origins.startswith("["):
            return [origin.strip() for origin in origins.split(",")]
        return origins

    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: str

    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o-2024-08-06"
    SYSTEM_PROMPT: str = (
        "You are RAI Bot, a helpful AI assistant. "
        "You provide clear, accurate, and concise responses. "
        "If you're not sure about something, you'll admit it. "
        "You aim to be helpful while maintaining a natural, conversational tone."
    )

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent.parent.parent / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()
