"""Base exception carrying safe, client-facing error metadata."""


class AppException(Exception):
    """Domain error with HTTP status and serializable validation details."""

    def __init__(self, message: str, status_code: int = 400, errors: list[str] | None = None):
        super().__init__(message)
        self.message, self.status_code, self.errors = message, status_code, errors or []
