"""Timezone-aware date formatting helpers."""

from datetime import UTC, datetime


def utc_iso(value: datetime | None = None) -> str:
    """Format a datetime as an explicit UTC ISO-8601 string."""
    return (value or datetime.now(UTC)).astimezone(UTC).isoformat()
