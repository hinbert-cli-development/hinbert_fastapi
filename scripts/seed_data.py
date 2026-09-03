"""Idempotently populate a development database with demo users and products."""

import asyncio
from decimal import Decimal

from sqlalchemy import select

from app.core.config.database import SessionLocal
from app.core.config.settings import get_settings
from app.core.security.password import hash_password
from app.models.domain.product import Product
from app.models.domain.user import User


async def seed() -> None:
    """Create safe demo records only when the configured environment is development."""
    if get_settings().environment != "development":
        raise RuntimeError("Refusing to seed a non-development environment")
    async with SessionLocal() as session:
        if await session.scalar(select(User).where(User.email == "demo@example.com")) is None:
            session.add(
                User(
                    email="demo@example.com",
                    full_name="Demo User",
                    password_hash=hash_password("DemoPassword!123"),
                    is_verified=True,
                )
            )
        if await session.scalar(select(Product).where(Product.name == "Demo Product")) is None:
            session.add(Product(name="Demo Product", description="Development-only sample", price=Decimal("19.99")))
        await session.commit()


def main() -> None:
    """Run the asynchronous seed workflow."""
    asyncio.run(seed())


if __name__ == "__main__":
    main()
