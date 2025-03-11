class UserAlreadyExistsError(Exception):
    """Raised when attempting to create a user with an existing email."""


class AuthenticationError(Exception):
    """Raised when authentication fails."""
