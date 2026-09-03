"""Safe file helper boundaries for future object-storage integration."""

from pathlib import Path


def safe_filename(filename: str) -> str:
    """Strip path components so user input cannot select arbitrary directories."""
    return Path(filename).name
