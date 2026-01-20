"""Authentication endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from griot_registry.auth import (
    CurrentUser,
    JWTAuth,
    TokenResponse,
    User,
    UserRole,
    get_jwt_auth,
)

router = APIRouter()


@router.post(
    "/auth/token",
    operation_id="createToken",
    summary="Create access token",
    response_model=TokenResponse,
    responses={
        401: {"description": "Invalid credentials"},
    },
)
async def create_token(
    user_id: str,
    email: str | None = None,
    name: str | None = None,
    roles: list[str] | None = Query(default=None, description="User roles (admin, editor, viewer)"),
    jwt_auth: JWTAuth = Depends(get_jwt_auth),
) -> TokenResponse:
    """Create an access token for a user.

    This is a simplified token endpoint for development/testing.
    In production, integrate with your identity provider.

    Args:
        user_id: Unique user identifier
        email: User email
        name: User display name
        roles: User roles (admin, editor, viewer)

    Returns:
        Access and refresh tokens
    """
    # Parse roles
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
    """Refresh an access token using a refresh token.

    Args:
        refresh_token: The refresh token

    Returns:
        New access token (and optionally new refresh token)
    """
    # Verify refresh token and get user ID
    user_id = jwt_auth.verify_refresh_token(refresh_token)

    # Create new tokens
    return jwt_auth.create_token_response(
        user_id=user_id,
        include_refresh=True,
    )


@router.get(
    "/auth/me",
    operation_id="getCurrentUser",
    summary="Get current user",
    response_model=dict,
)
async def get_current_user(user: CurrentUser) -> dict:
    """Get the current authenticated user's information.

    Returns:
        User information including ID, email, name, and roles.
    """
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "roles": [r.value for r in user.roles],
        "auth_method": user.auth_method.value,
    }
