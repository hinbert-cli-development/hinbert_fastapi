"""Authentication endpoints for credentials, recovery, MFA, and OAuth."""

import secrets
from datetime import UTC, datetime, timedelta
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.auth import get_current_active_user
from app.core.config.settings import get_settings
from app.core.exceptions.custom_exceptions import UnauthorizedError
from app.core.middleware.rate_limit import limiter
from app.core.security.password import hash_password, verify_password
from app.core.security.totp import new_secret, verify_code
from app.db.session import get_db
from app.models.domain.email_verification import EmailVerification
from app.models.domain.password_reset import PasswordReset
from app.models.domain.refresh_token import RefreshToken
from app.models.domain.totp_secret import TotpSecret
from app.models.domain.user import User
from app.models.schemas.auth import EmailTokenRequest, LoginRequest, SignupRequest
from app.models.schemas.password import ForgotPassword, ResetPassword
from app.models.schemas.response import APIResponse
from app.models.schemas.token import RefreshRequest, TokenResponse
from app.models.schemas.totp import TotpSetupResponse, TotpVerify
from app.models.schemas.user import UserOut
from app.repositories.email_verification_repository import create as create_verification
from app.repositories.email_verification_repository import get_by_token as get_verification
from app.repositories.email_verification_repository import mark_used as mark_verification_used
from app.repositories.password_reset_repository import create as create_reset
from app.repositories.password_reset_repository import get_by_token as get_reset
from app.repositories.password_reset_repository import mark_used as mark_reset_used
from app.repositories.refresh_token_repository import find_active, revoke
from app.repositories.user_repository import get_by_email
from app.services.auth_service import hash_refresh_token, issue_tokens
from app.services.email_service import send_reset_email, send_verification_email
from app.services.social_auth_service import exchange_provider_code
from app.services.user_service import create_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=APIResponse[UserOut], status_code=201)
@limiter.limit("10/minute")
async def signup(request: Request, payload: SignupRequest, session: AsyncSession = Depends(get_db)):
    """Create a user and persist a one-time email verification token."""
    user = await create_user(session, payload)
    raw_token = secrets.token_urlsafe(32)
    await create_verification(
        session,
        EmailVerification(
            user_id=user.id,
            token_hash=hash_refresh_token(raw_token),
            expires_at=datetime.now(UTC) + timedelta(hours=24),
        ),
    )
    send_verification_email(user, raw_token)
    return APIResponse(message="Account created", data=user, status_code=201)


@router.post("/login", response_model=APIResponse[TokenResponse])
@limiter.limit("10/minute")
async def login(request: Request, payload: LoginRequest, session: AsyncSession = Depends(get_db)):
    """Verify credentials and issue access plus opaque refresh credentials."""
    user = await get_by_email(session, str(payload.email))
    if user is None or not user.is_active or not verify_password(payload.password, user.password_hash):
        raise UnauthorizedError("Invalid credentials")
    access, refresh, digest, expiry = issue_tokens(user.id)
    session.add(RefreshToken(user_id=user.id, token_hash=digest, expires_at=expiry))
    await session.commit()
    return APIResponse(message="Login successful", data=TokenResponse(access_token=access, refresh_token=refresh))


@router.post("/refresh", response_model=APIResponse[TokenResponse])
@limiter.limit("30/minute")
async def refresh(request: Request, payload: RefreshRequest, session: AsyncSession = Depends(get_db)):
    """Rotate a valid refresh token and revoke the predecessor."""
    stored = await find_active(session, hash_refresh_token(payload.refresh_token))
    if stored is None:
        raise UnauthorizedError("Invalid refresh token")
    user = await session.get(User, stored.user_id)
    if user is None or not user.is_active:
        raise UnauthorizedError("Inactive account")
    access, raw_refresh, digest, expiry = issue_tokens(user.id)
    await revoke(session, stored)
    session.add(RefreshToken(user_id=user.id, token_hash=digest, expires_at=expiry))
    await session.commit()
    return APIResponse(message="Token refreshed", data=TokenResponse(access_token=access, refresh_token=raw_refresh))


@router.post("/logout", response_model=APIResponse[None])
@limiter.limit("30/minute")
async def logout(request: Request, payload: RefreshRequest, session: AsyncSession = Depends(get_db)):
    """Revoke the supplied refresh token without revealing whether it existed."""
    stored = await find_active(session, hash_refresh_token(payload.refresh_token))
    if stored is not None:
        await revoke(session, stored)
    return APIResponse(message="Logged out", data=None)


@router.post("/verify-email", response_model=APIResponse[None])
@limiter.limit("10/minute")
async def verify_email(request: Request, payload: EmailTokenRequest, session: AsyncSession = Depends(get_db)):
    """Consume a verification token and activate its account."""
    stored = await get_verification(session, hash_refresh_token(payload.token))
    if stored is None:
        raise HTTPException(status_code=400, detail="Invalid verification token")
    user = await session.get(User, stored.user_id)
    if user is None:
        raise HTTPException(status_code=400, detail="Invalid verification token")
    user.is_verified = True
    user.is_active = True
    await mark_verification_used(session, stored)
    return APIResponse(message="Email verified", data=None)


@router.post("/forgot-password", response_model=APIResponse[None])
@limiter.limit("5/minute")
async def forgot_password(request: Request, payload: ForgotPassword, session: AsyncSession = Depends(get_db)):
    """Issue a reset token and send it without disclosing account existence."""
    user = await get_by_email(session, str(payload.email))
    if user is not None:
        raw_token = secrets.token_urlsafe(32)
        await create_reset(
            session,
            PasswordReset(
                user_id=user.id,
                token_hash=hash_refresh_token(raw_token),
                expires_at=datetime.now(UTC) + timedelta(hours=1),
            ),
        )
        send_reset_email(user, raw_token)
    return APIResponse(message="If the account exists, a reset email was sent", data=None)


@router.post("/reset-password", response_model=APIResponse[None])
@limiter.limit("5/minute")
async def reset_password(request: Request, payload: ResetPassword, session: AsyncSession = Depends(get_db)):
    """Consume a reset token and replace the stored bcrypt password hash."""
    stored = await get_reset(session, hash_refresh_token(payload.token))
    if stored is None:
        raise HTTPException(status_code=400, detail="Invalid reset token")
    user = await session.get(User, stored.user_id)
    if user is None:
        raise HTTPException(status_code=400, detail="Invalid reset token")
    user.password_hash = hash_password(payload.password)
    await mark_reset_used(session, stored)
    return APIResponse(message="Password reset", data=None)


@router.post("/totp/setup", response_model=APIResponse[TotpSetupResponse])
@limiter.limit("10/minute")
async def setup_totp(
    request: Request, user: User = Depends(get_current_active_user), session: AsyncSession = Depends(get_db)
):
    """Generate encrypted TOTP provisioning data for the current user."""
    secret = new_secret()
    record = TotpSecret(user_id=user.id)
    record.secret = secret
    session.add(record)
    await session.commit()
    uri = __import__("pyotp").TOTP(secret).provisioning_uri(name=user.email, issuer_name=get_settings().app_name)
    return APIResponse(message="TOTP configured", data=TotpSetupResponse(secret=secret, provisioning_uri=uri))


@router.post("/totp/verify", response_model=APIResponse[None])
@limiter.limit("10/minute")
async def verify_totp(
    request: Request,
    payload: TotpVerify,
    user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
):
    """Verify the user's encrypted TOTP secret and enable the factor."""
    record = await session.get(TotpSecret, user.id)
    if record is None or not verify_code(record.secret, payload.code):
        raise HTTPException(status_code=400, detail="Invalid TOTP code")
    return APIResponse(message="TOTP verified", data=None)


@router.get("/google")
async def google_login():
    """Redirect to Google's OAuth authorization endpoint."""
    settings = get_settings()
    params = urlencode(
        {
            "client_id": settings.google_client_id,
            "redirect_uri": "/api/v1/auth/google/callback",
            "response_type": "code",
            "scope": "openid email profile",
        }
    )
    return RedirectResponse(f"https://accounts.google.com/o/oauth2/v2/auth?{params}")


@router.get("/google/callback", response_model=APIResponse[TokenResponse])
async def google_callback(code: str, session: AsyncSession = Depends(get_db)):
    """Exchange Google's code and provision or authenticate the user."""
    return await _social_login("google", code, session)


@router.get("/facebook")
async def facebook_login():
    """Redirect to Facebook's OAuth authorization endpoint."""
    settings = get_settings()
    params = urlencode(
        {
            "client_id": settings.facebook_client_id,
            "redirect_uri": "/api/v1/auth/facebook/callback",
            "response_type": "code",
            "scope": "email,public_profile",
        }
    )
    return RedirectResponse(f"https://www.facebook.com/v19.0/dialog/oauth?{params}")


@router.get("/facebook/callback", response_model=APIResponse[TokenResponse])
async def facebook_callback(code: str, session: AsyncSession = Depends(get_db)):
    """Exchange Facebook's code and provision or authenticate the user."""
    return await _social_login("facebook", code, session)


async def _social_login(provider: str, code: str, session: AsyncSession):
    """Normalize a provider profile and issue the same token pair as password login."""
    profile = await exchange_provider_code(provider, code)
    user = await get_by_email(session, profile["email"])
    if user is None:
        user = User(
            email=profile["email"],
            full_name=profile["full_name"],
            password_hash=hash_password(secrets.token_urlsafe(32)),
            is_verified=True,
        )
        session.add(user)
        await session.flush()
    access, refresh_token, digest, expiry = issue_tokens(user.id)
    session.add(RefreshToken(user_id=user.id, token_hash=digest, expires_at=expiry))
    await session.commit()
    return APIResponse(
        message=f"{provider.title()} login successful",
        data=TokenResponse(access_token=access, refresh_token=refresh_token),
    )


@router.get("/me", response_model=APIResponse[UserOut])
async def me(user: User = Depends(get_current_active_user)):
    """Return the authenticated user's safe profile."""
    return APIResponse(data=user)
