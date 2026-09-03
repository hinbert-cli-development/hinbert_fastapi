"""Create an administrator through an interactive, non-echoed password prompt."""

import argparse
import asyncio
import getpass

from app.core.config.database import SessionLocal
from app.core.security.password import hash_password
from app.models.domain.user import User
from app.repositories.user_repository import create, get_by_email


async def create_admin(email: str, full_name: str, password: str) -> User:
    """Create an administrator or fail when the normalized email already exists."""
    async with SessionLocal() as session:
        if await get_by_email(session, email):
            raise ValueError("A user with this email already exists")
        return await create(
            session,
            User(
                email=email.lower(),
                full_name=full_name,
                password_hash=hash_password(password),
                is_admin=True,
                is_verified=True,
            ),
        )


def main() -> None:
    """Parse CLI input and execute the asynchronous administrator workflow."""
    parser = argparse.ArgumentParser(description="Create an Hinbert FastAPI administrator")
    parser.add_argument("--email", required=True)
    parser.add_argument("--full-name", required=True)
    args = parser.parse_args()
    password = getpass.getpass("Password: ")
    asyncio.run(create_admin(args.email, args.full_name, password))


if __name__ == "__main__":
    main()
