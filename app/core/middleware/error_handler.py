"""Consistent JSON handling for domain exceptions and unexpected failures."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.exceptions.base_exception import AppException


def register_exception_handlers(application: FastAPI) -> None:
    """Register handlers that preserve the public response contract."""

    @application.exception_handler(AppException)
    async def handle_app_exception(_: Request, exc: AppException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "message": exc.message,
                "data": None,
                "errors": exc.errors,
                "status_code": exc.status_code,
            },
        )
