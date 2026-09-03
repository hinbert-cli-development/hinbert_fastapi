"""Frequently used domain exceptions with stable status codes."""

from app.core.exceptions.base_exception import AppException


class NotFoundError(AppException):
    """Represent a requested resource that is absent."""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, 404)


class UnauthorizedError(AppException):
    """Represent missing or invalid authentication."""

    def __init__(self, message: str = "Authentication required"):
        super().__init__(message, 401)
