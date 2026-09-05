"""Create the FastAPI application and assemble cross-cutting concerns.

The factory pattern keeps imports side-effect-light for tests, workers, and CLI
scripts. Customize middleware and router registration here; business logic
belongs in services rather than in this composition module.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi.middleware import SlowAPIMiddleware

from app.api.v1.routers.api_router import api_router
from app.core.config.settings import get_settings
from app.core.middleware.error_handler import register_exception_handlers
from app.core.middleware.logging import RequestLoggingMiddleware
from app.core.middleware.rate_limit import limiter, register_rate_limit


def create_app() -> FastAPI:
    """Build and configure the application.

    Returns:
        A configured FastAPI instance with OpenAPI documentation enabled.
    """
    settings = get_settings()
    application = FastAPI(title=settings.app_name, version="0.1.0")
    application.state.limiter = limiter
    application.add_middleware(SlowAPIMiddleware)
    application.add_middleware(RequestLoggingMiddleware)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
    )
    application.include_router(api_router, prefix=settings.api_prefix)
    register_exception_handlers(application)
    register_rate_limit(application)

    @application.get("/health", tags=["health"])
    @limiter.limit("120/minute")
    async def health(request: Request) -> dict[str, str]:
        """Return a lightweight liveness response for load balancers and probes."""
        return {"status": "ok"}

    return application


app = create_app()
