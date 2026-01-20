"""Unified authentication dependencies for FastAPI routes.

This module provides the main authentication dependencies that support
multiple authentication methods (JWT, API key, OAuth) and provides
role-based authorization helpers.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, status

from griot_registry.auth.api_key import get_current_user_api_key
from griot_registry.auth.jwt import get_current_user_jwt
from griot_registry.auth.models import AuthMethod, User, UserRole
from griot_registry.config import Settings, get_settings


async def get_current_user(
    jwt_user: Annotated[User | None, Depends(get_current_user_jwt)],
    api_key_user: Annotated[User | None, Depends(get_current_user_api_key)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> User | None:
    """Get the current authenticated user from any auth method.

    Checks authentication in order:
    1. JWT Bearer token
    2. API Key header

    If authentication is disabled, returns an anonymous user with viewer access.
    If no valid authentication is provided and auth is enabled, raises 401.

    Args:
        jwt_user: User from JWT auth (if any)
        api_key_user: User from API key auth (if any)
        settings: Application settings

    Returns:
        Authenticated User object

    Raises:
        HTTPException: 401 if no valid authentication and auth is enabled
    """
    # If auth is disabled, return anonymous user
    if not settings.auth_enabled:
        return User(
            id="anonymous",
            email=None,
            name="Anonymous",
            roles=[UserRole.ADMIN],  # Full access when auth disabled
            auth_method=AuthMethod.ANONYMOUS,
        )

    # Check for authenticated user
    user = jwt_user or api_key_user

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "UNAUTHORIZED",
                "message": "Authentication required. Provide a Bearer token or API key.",
            },
            headers={"WWW-Authenticate": 'Bearer, ApiKey realm="griot-registry"'},
        )

    return user


async def get_optional_user(
    jwt_user: Annotated[User | None, Depends(get_current_user_jwt)],
    api_key_user: Annotated[User | None, Depends(get_current_user_api_key)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> User | None:
    """Get the current user if authenticated, otherwise return None.

    Use this for endpoints that work with or without authentication,
    but may provide additional features for authenticated users.
    """
    if not settings.auth_enabled:
        return User(
            id="anonymous",
            email=None,
            name="Anonymous",
            roles=[UserRole.ADMIN],
            auth_method=AuthMethod.ANONYMOUS,
        )

    return jwt_user or api_key_user


# Type aliases for dependency injection
CurrentUser = Annotated[User, Depends(get_current_user)]
OptionalUser = Annotated[User | None, Depends(get_optional_user)]


def require_role(*required_roles: UserRole):
    """Create a dependency that requires the user to have one of the specified roles.

    Example::

        @router.post("/admin/action")
        async def admin_action(user: CurrentUser = Depends(require_role(UserRole.ADMIN))):
            pass

    Args:
        *required_roles: One or more roles that grant access

    Returns:
        A dependency function that validates user roles
    """
    async def role_checker(user: CurrentUser) -> User:
        # Admin always has access
        if UserRole.ADMIN in user.roles:
            return user

        # Check if user has any of the required roles
        if not any(role in user.roles for role in required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "FORBIDDEN",
                    "message": f"Requires one of: {[r.value for r in required_roles]}",
                    "user_roles": [r.value for r in user.roles],
                },
            )

        return user

    return role_checker


def require_admin():
    """Dependency that requires admin role."""
    return require_role(UserRole.ADMIN)


def require_editor():
    """Dependency that requires editor (or admin) role."""
    return require_role(UserRole.EDITOR, UserRole.ADMIN)


def require_viewer():
    """Dependency that requires at least viewer role (any authenticated user)."""
    return require_role(UserRole.VIEWER, UserRole.EDITOR, UserRole.ADMIN, UserRole.SERVICE)


# Pre-built role dependencies
RequireAdmin = Annotated[User, Depends(require_role(UserRole.ADMIN))]
RequireEditor = Annotated[User, Depends(require_role(UserRole.EDITOR, UserRole.ADMIN))]
RequireViewer = Annotated[User, Depends(require_role(UserRole.VIEWER, UserRole.EDITOR, UserRole.ADMIN, UserRole.SERVICE))]
