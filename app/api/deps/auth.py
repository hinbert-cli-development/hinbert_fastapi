"""Bearer-token dependencies for protected routes."""

from uuid import UUID

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions.custom_exceptions import UnauthorizedError
from app.core.security.jwt import decode_token
from app.db.session import get_db
from app.models.domain.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_db)) -> User:
    """Decode an access token and load its user, failing closed on any error."""
    try:
        subject = UUID(decode_token(token)["sub"])
    except (ValueError, KeyError) as exc:
        raise UnauthorizedError() from exc
    user = await session.get(User, subject)
    if user is None:
        raise UnauthorizedError()
    return user


async def get_current_active_user(user: User = Depends(get_current_user)) -> User:
    """Reject deactivated accounts before protected business operations."""
    if not user.is_active:
        raise UnauthorizedError("Inactive account")
    return user


async def get_current_admin(user: User = Depends(get_current_active_user)) -> User:
    """Require an active account with administrator privileges."""
    if not user.is_admin:
        raise UnauthorizedError("Administrator privileges required")
    return user
