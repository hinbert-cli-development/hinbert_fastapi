"""Request timing middleware with correlation-friendly structured logging."""

import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.utils.logger import logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log method, path, status, and duration without logging request bodies."""

    async def dispatch(self, request: Request, call_next):
        """Process one request and record an operational timing event."""
        started = time.perf_counter()
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        logger.info(
            "{method} {path} {status} {duration:.3f}s",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            duration=time.perf_counter() - started,
        )
        return response
