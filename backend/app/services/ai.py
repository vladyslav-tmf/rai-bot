from openai import (
    APIError,
    AsyncOpenAI,
    AuthenticationError,
    BadRequestError,
    ConflictError,
    NotFoundError,
    RateLimitError,
)
from openai.types.chat import ChatCompletion

from backend.app.core.config import Settings
from backend.app.exceptions import AIServiceError


class AIService:
    """Service for interacting with OpenAI API."""

    def __init__(self, settings: Settings) -> None:
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL

    async def get_response(self, messages: list[dict[str, str]]) -> str:
        """Get response from OpenAI API."""
        try:
            response: ChatCompletion = await self.client.chat.completions.create(
                model=self.model, messages=messages
            )
            return response.choices[0].message.content or ""

        except RateLimitError:
            raise AIServiceError("Rate limit exceeded. Please try again later")
        except AuthenticationError:
            raise AIServiceError("Invalid API key or unauthorized access")
        except BadRequestError as error:
            raise AIServiceError(f"Invalid request parameters: {str(error)}")
        except NotFoundError:
            raise AIServiceError(f"Model '{self.model}' not found or unavailable")
        except ConflictError:
            raise AIServiceError("Request conflicts with current API state")
        except APIError as error:
            raise AIServiceError(f"OpenAI API error: {str(error)}")

    @staticmethod
    def format_chat_history(
        system_prompt: str, user_messages: list[dict[str, str]]
    ) -> list[dict[str, str]]:
        """Format chat history for OpenAI API."""
        messages = [{"role": "system", "content": system_prompt}]

        for msg in user_messages:
            messages.append({"role": "user", "content": msg["content"]})

            if msg.get("response"):
                messages.append({"role": "assistant", "content": msg["response"]})

        return messages
