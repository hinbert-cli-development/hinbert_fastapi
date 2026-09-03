"""SlowAPI limiter configuration and exception registration."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
DEFAULT_LIMIT = "100/minute"


def register_rate_limit(application: FastAPI) -> None:
    """Register a uniform response for requests exceeding configured limits."""

    @application.exception_handler(RateLimitExceeded)
    async def handle_rate_limit(_: Request, __: RateLimitExceeded) -> JSONResponse:
        return JSONResponse(
            status_code=429,
            content={
                "success": False,
                "message": "Rate limit exceeded",
                "data": None,
                "errors": [],
                "status_code": 429,
            },
        )
