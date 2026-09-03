"""Run Alembic migrations from deployment automation."""

from alembic import command
from alembic.config import Config


def main() -> None:
    """Upgrade the configured database to the latest revision."""
    command.upgrade(Config("alembic.ini"), "head")


if __name__ == "__main__":
    main()
