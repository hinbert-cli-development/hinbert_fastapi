"""Standard API envelope for predictable clients and observability."""

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

DataT = TypeVar("DataT")


class APIResponse(BaseModel, Generic[DataT]):
    """Envelope containing success state, data, errors, and HTTP status."""

    success: bool = True
    message: str = "OK"
    data: DataT | None = None
    errors: list[str] = Field(default_factory=list)
    status_code: int = 200
