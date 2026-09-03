"""Authentication endpoints; orchestration delegates to services."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.auth import get_current_active_user
from app.core.security.password import verify_password
from app.db.session import get_db
from app.models.domain.refresh_token import RefreshToken
from app.models.domain.user import User
from app.models.schemas.auth import LoginRequest, SignupRequest
from app.models.schemas.response import APIResponse
from app.models.schemas.token import TokenResponse
from app.models.schemas.user import UserOut
from app.repositories.user_repository import get_by_email
from app.services.auth_service import issue_tokens
from app.services.user_service import create_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=APIResponse[UserOut], status_code=201)
async def signup(payload: SignupRequest, session: AsyncSession = Depends(get_db)):
    """Create a user; production deployments should enqueue verification email delivery."""
    user = await create_user(session, payload)
    return APIResponse(message="Account created", data=user, status_code=201)


@router.post("/login", response_model=APIResponse[TokenResponse])
async def login(payload: LoginRequest, session: AsyncSession = Depends(get_db)):
    """Verify credentials and issue access plus opaque refresh credentials."""
    user = await get_by_email(session, str(payload.email))
    if user is None or not verify_password(payload.password, user.password_hash):
        from app.core.exceptions.custom_exceptions import UnauthorizedError

        raise UnauthorizedError("Invalid credentials")
    access, refresh, digest, expiry = issue_tokens(user.id)
    session.add(RefreshToken(user_id=user.id, token_hash=digest, expires_at=expiry))
    await session.commit()
    return APIResponse(message="Login successful", data=TokenResponse(access_token=access, refresh_token=refresh))


@router.get("/me", response_model=APIResponse[UserOut])
async def me(user: User = Depends(get_current_active_user)):
    """Return the authenticated user's safe profile."""
    return APIResponse(data=user)
