"""Authentication endpoints."""

from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr, Field

from griot_registry.auth import (
    CurrentUser,
    JWTAuth,
    TokenResponse,
    User,
    UserRole,
    get_jwt_auth,
)
from griot_registry.config import Settings, get_settings

router = APIRouter()


# =============================================================================
# Request/Response Models
# =============================================================================


class LoginRequest(BaseModel):
    """Login request body."""

    email: EmailStr
    password: str
    remember_me: bool = Field(default=False, alias="rememberMe")

    model_config = {"populate_by_name": True}


class SignupRequest(BaseModel):
    """Signup request body."""

    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., alias="confirmPassword")
    accept_terms: bool = Field(..., alias="acceptTerms")

    model_config = {"populate_by_name": True}


class RoleRef(BaseModel):
    """Role reference."""

    id: str
    name: str


class TeamRef(BaseModel):
    """Team reference."""

    id: str
    name: str


class AuthUserResponse(BaseModel):
    """User data in auth response."""

    id: str
    name: str
    email: str
    avatar: str | None = None
    role: RoleRef
    team: TeamRef | None = None
    status: str = "active"
    last_login_at: datetime | None = Field(None, alias="lastLoginAt")
    created_at: datetime = Field(..., alias="createdAt")

    model_config = {"populate_by_name": True}


class AuthResponse(BaseModel):
    """Authentication response."""

    user: AuthUserResponse
    token: str
    expires_at: datetime = Field(..., alias="expiresAt")

    model_config = {"populate_by_name": True}


class ForgotPasswordRequest(BaseModel):
    """Forgot password request."""

    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Reset password request."""

    token: str
    password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., alias="confirmPassword")

    model_config = {"populate_by_name": True}


class ErrorResponse(BaseModel):
    """Error response."""

    error: dict


# =============================================================================
# Helper Functions
# =============================================================================


def _utc_now() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(timezone.utc)


def _verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


def _hash_password(password: str) -> str:
    """Hash a password with bcrypt (cost factor 12)."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(12)).decode()


def _validate_password_strength(password: str) -> list[str]:
    """Validate password meets requirements. Returns list of errors."""
    errors = []
    if len(password) < 8:
        errors.append("Password must be at least 8 characters")
    if not any(c.isupper() for c in password):
        errors.append("Password must contain at least 1 uppercase letter")
    if not any(c.islower() for c in password):
        errors.append("Password must contain at least 1 lowercase letter")
    if not any(c.isdigit() for c in password):
        errors.append("Password must contain at least 1 number")
    return errors


async def _build_auth_response(
    user_doc: dict,
    role_doc: dict,
    team_doc: dict | None,
    jwt_auth: JWTAuth,
    remember_me: bool = False,
    settings: Settings | None = None,
) -> AuthResponse:
    """Build the auth response with user and token."""
    settings = settings or get_settings()

    # Determine token expiry
    if remember_me:
        expire_minutes = 60 * 24 * 30  # 30 days
    else:
        expire_minutes = 60 * 24  # 24 hours

    # Map role to UserRole enum
    role_name = role_doc.get("name", "Viewer").lower()
    user_roles = [UserRole(role_name) if role_name in ["admin", "editor", "viewer"] else UserRole.VIEWER]

    # Create token
    token_response = jwt_auth.create_token_response(
        user_id=user_doc["id"],
        email=user_doc["email"],
        name=user_doc["name"],
        roles=user_roles,
        expire_minutes=expire_minutes,
    )

    expires_at = _utc_now() + timedelta(minutes=expire_minutes)

    # Build user response
    user_response = AuthUserResponse(
        id=user_doc["id"],
        name=user_doc["name"],
        email=user_doc["email"],
        avatar=user_doc.get("avatar"),
        role=RoleRef(id=role_doc["id"], name=role_doc["name"]),
        team=TeamRef(id=team_doc["id"], name=team_doc["name"]) if team_doc else None,
        status=user_doc.get("status", "active"),
        last_login_at=user_doc.get("last_login_at"),
        created_at=user_doc["created_at"],
    )

    return AuthResponse(
        user=user_response,
        token=token_response.access_token,
        expires_at=expires_at,
    )


# =============================================================================
# Authentication Endpoints
# =============================================================================


@router.post(
    "/auth/login",
    operation_id="login",
    summary="User login",
    response_model=AuthResponse,
    responses={
        401: {"description": "Invalid credentials", "model": ErrorResponse},
        422: {"description": "Validation error", "model": ErrorResponse},
        423: {"description": "Account locked", "model": ErrorResponse},
    },
)
async def login(
    request: Request,
    body: LoginRequest,
    jwt_auth: JWTAuth = Depends(get_jwt_auth),
) -> AuthResponse:
    """Authenticate user with email and password.

    Returns user data and JWT token on success.
    Account is locked after 5 failed attempts for 15 minutes.
    """
    storage = request.app.state.storage

    # Find user by email
    user = await storage.users.get_by_email(body.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "INVALID_CREDENTIALS", "message": "Invalid email or password"}},
        )

    # Check if account is locked
    if user.get("locked_until"):
        lock_time = user["locked_until"]
        if isinstance(lock_time, datetime) and lock_time > _utc_now():
            remaining = int((lock_time - _utc_now()).total_seconds() / 60)
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail={
                    "error": {
                        "code": "ACCOUNT_LOCKED",
                        "message": f"Account locked due to too many failed attempts. Try again in {remaining} minutes.",
                    }
                },
            )

    # Verify password
    if not _verify_password(body.password, user["password_hash"]):
        # Increment failed login attempts
        failed_count = await storage.users.increment_failed_login(user["id"])

        # Lock account after 5 failures
        if failed_count >= 5:
            lock_until = _utc_now() + timedelta(minutes=15)
            await storage.users.update(user["id"], {"locked_until": lock_until})
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail={
                    "error": {
                        "code": "ACCOUNT_LOCKED",
                        "message": "Account locked due to too many failed attempts. Try again in 15 minutes.",
                    }
                },
            )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "INVALID_CREDENTIALS", "message": "Invalid email or password"}},
        )

    # Reset failed login counter on success
    await storage.users.reset_failed_login(user["id"])

    # Update last login time
    await storage.users.update(user["id"], {"last_login_at": _utc_now()})

    # Get role and team
    role = await storage.roles.get(user["role_id"])
    if not role:
        role = {"id": "role-viewer", "name": "Viewer"}

    team = None
    if user.get("team_id"):
        team = await storage.teams.get(user["team_id"])

    return await _build_auth_response(user, role, team, jwt_auth, body.remember_me)


@router.post(
    "/auth/signup",
    operation_id="signup",
    summary="User registration",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        409: {"description": "Email already exists", "model": ErrorResponse},
        422: {"description": "Validation error", "model": ErrorResponse},
    },
)
async def signup(
    request: Request,
    body: SignupRequest,
    jwt_auth: JWTAuth = Depends(get_jwt_auth),
) -> AuthResponse:
    """Register a new user account.

    Password requirements:
    - Minimum 8 characters
    - At least 1 uppercase letter
    - At least 1 lowercase letter
    - At least 1 number

    New users receive the default "Viewer" role.
    """
    storage = request.app.state.storage

    # Validate terms acceptance
    if not body.accept_terms:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Validation failed",
                    "details": [{"field": "acceptTerms", "message": "You must accept the terms of service"}],
                }
            },
        )

    # Validate password confirmation
    if body.password != body.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Validation failed",
                    "details": [{"field": "confirmPassword", "message": "Passwords do not match"}],
                }
            },
        )

    # Validate password strength
    password_errors = _validate_password_strength(body.password)
    if password_errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Validation failed",
                    "details": [{"field": "password", "message": err} for err in password_errors],
                }
            },
        )

    # Check if email already exists
    existing = await storage.users.get_by_email(body.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": {"code": "EMAIL_EXISTS", "message": "An account with this email already exists"}},
        )

    # Create user
    user_doc = {
        "name": body.name,
        "email": body.email,
        "password_hash": _hash_password(body.password),
        "role_id": "role-viewer",  # Default role
        "team_id": None,
        "status": "active",
        "avatar": None,
    }

    user = await storage.users.create(user_doc)

    # Get viewer role
    role = await storage.roles.get("role-viewer")
    if not role:
        role = {"id": "role-viewer", "name": "Viewer"}

    return await _build_auth_response(user, role, None, jwt_auth)


@router.post(
    "/auth/logout",
    operation_id="logout",
    summary="User logout",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout(user: CurrentUser) -> None:
    """Logout the current user.

    This endpoint invalidates the current session.
    Note: For stateless JWT, actual invalidation requires token blacklisting
    which is not implemented in this version. The client should discard the token.
    """
    # In a stateless JWT system, we simply return success
    # The client is responsible for discarding the token
    # For production, implement token blacklisting with Redis or similar
    return None


@router.get(
    "/auth/me",
    operation_id="getCurrentUser",
    summary="Get current user",
    response_model=AuthUserResponse,
)
async def get_me(request: Request, user: CurrentUser) -> AuthUserResponse:
    """Get the current authenticated user's profile.

    Returns complete user information including role and team.
    """
    storage = request.app.state.storage

    # Get full user data from storage
    user_doc = await storage.users.get(user.id)
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "USER_NOT_FOUND", "message": "User not found"}},
        )

    # Get role
    role = await storage.roles.get(user_doc.get("role_id", "role-viewer"))
    if not role:
        role = {"id": "role-viewer", "name": "Viewer"}

    # Get team
    team = None
    if user_doc.get("team_id"):
        team = await storage.teams.get(user_doc["team_id"])

    return AuthUserResponse(
        id=user_doc["id"],
        name=user_doc["name"],
        email=user_doc["email"],
        avatar=user_doc.get("avatar"),
        role=RoleRef(id=role["id"], name=role["name"]),
        team=TeamRef(id=team["id"], name=team["name"]) if team else None,
        status=user_doc.get("status", "active"),
        last_login_at=user_doc.get("last_login_at"),
        created_at=user_doc["created_at"],
    )


@router.post(
    "/auth/forgot-password",
    operation_id="forgotPassword",
    summary="Request password reset",
    status_code=status.HTTP_200_OK,
)
async def forgot_password(request: Request, body: ForgotPasswordRequest) -> dict:
    """Request a password reset link.

    If the email exists, a reset token is generated.
    For security, always returns success even if email doesn't exist.
    """
    storage = request.app.state.storage

    # Find user (but don't reveal if they exist)
    user = await storage.users.get_by_email(body.email)

    if user:
        # Generate reset token
        token = secrets.token_urlsafe(32)
        expires_at = _utc_now() + timedelta(hours=1)

        await storage.password_resets.create({
            "user_id": user["id"],
            "token": token,
            "expires_at": expires_at,
        })

        # In production, send email with reset link
        # For now, we just log it (token would be in the reset link)

    # Always return success for security
    return {"message": "If an account exists with that email, a password reset link has been sent."}


@router.post(
    "/auth/reset-password",
    operation_id="resetPassword",
    summary="Reset password with token",
    status_code=status.HTTP_200_OK,
    responses={
        400: {"description": "Invalid or expired token", "model": ErrorResponse},
        422: {"description": "Validation error", "model": ErrorResponse},
    },
)
async def reset_password(request: Request, body: ResetPasswordRequest) -> dict:
    """Reset password using a valid reset token.

    Token must not be expired and must not have been used before.
    """
    storage = request.app.state.storage

    # Validate password confirmation
    if body.password != body.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Validation failed",
                    "details": [{"field": "confirmPassword", "message": "Passwords do not match"}],
                }
            },
        )

    # Validate password strength
    password_errors = _validate_password_strength(body.password)
    if password_errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Validation failed",
                    "details": [{"field": "password", "message": err} for err in password_errors],
                }
            },
        )

    # Find token
    token_doc = await storage.password_resets.get_by_token(body.token)
    if not token_doc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "INVALID_TOKEN", "message": "Invalid or expired reset token"}},
        )

    # Check expiry
    if token_doc["expires_at"] < _utc_now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "TOKEN_EXPIRED", "message": "Reset token has expired"}},
        )

    # Update password
    new_hash = _hash_password(body.password)
    await storage.users.update(token_doc["user_id"], {"password_hash": new_hash})

    # Mark token as used
    await storage.password_resets.mark_used(token_doc["id"])

    return {"message": "Password has been reset successfully. You can now log in with your new password."}


# =============================================================================
# OAuth Stubs (501 Not Implemented)
# =============================================================================


@router.post(
    "/auth/oauth/google",
    operation_id="oauthGoogle",
    summary="Google OAuth callback",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def oauth_google() -> dict:
    """Google OAuth callback (not implemented)."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail={"error": {"code": "NOT_IMPLEMENTED", "message": "Google OAuth is not yet implemented"}},
    )


@router.post(
    "/auth/oauth/microsoft",
    operation_id="oauthMicrosoft",
    summary="Microsoft OAuth callback",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def oauth_microsoft() -> dict:
    """Microsoft OAuth callback (not implemented)."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail={"error": {"code": "NOT_IMPLEMENTED", "message": "Microsoft OAuth is not yet implemented"}},
    )


@router.post(
    "/auth/oauth/sso",
    operation_id="oauthSSO",
    summary="Enterprise SSO callback",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def oauth_sso() -> dict:
    """Enterprise SSO callback (not implemented)."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail={"error": {"code": "NOT_IMPLEMENTED", "message": "Enterprise SSO is not yet implemented"}},
    )


# =============================================================================
# Legacy Token Endpoints (for backward compatibility)
# =============================================================================


@router.post(
    "/auth/token",
    operation_id="createToken",
    summary="Create access token (legacy)",
    response_model=TokenResponse,
    responses={
        401: {"description": "Invalid credentials"},
    },
    include_in_schema=False,  # Hide from docs, kept for backward compatibility
)
async def create_token(
    user_id: str,
    email: str | None = None,
    name: str | None = None,
    roles: list[str] | None = None,
    jwt_auth: JWTAuth = Depends(get_jwt_auth),
) -> TokenResponse:
    """Create an access token for a user (legacy endpoint for dev/testing)."""
    user_roles = []
    for role in (roles or ["viewer"]):
        try:
            user_roles.append(UserRole(role))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role: {role}. Valid roles: admin, editor, viewer",
            )

    return jwt_auth.create_token_response(
        user_id=user_id,
        email=email,
        name=name,
        roles=user_roles,
    )


@router.post(
    "/auth/refresh",
    operation_id="refreshToken",
    summary="Refresh access token",
    response_model=TokenResponse,
    responses={
        401: {"description": "Invalid or expired refresh token"},
    },
)
async def refresh_token(
    refresh_token: str,
    jwt_auth: JWTAuth = Depends(get_jwt_auth),
) -> TokenResponse:
    """Refresh an access token using a refresh token."""
    user_id = jwt_auth.verify_refresh_token(refresh_token)
    return jwt_auth.create_token_response(
        user_id=user_id,
        include_refresh=True,
    )
