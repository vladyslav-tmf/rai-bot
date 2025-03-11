class UserAlreadyExistsError(Exception):
    """Raised when attempting to create a user with an existing email."""


class AuthenticationError(Exception):
    """Raised when authentication fails."""


class AIServiceError(Exception):
    """Raised when an error occurs in the AI service."""
