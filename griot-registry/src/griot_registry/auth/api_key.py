"""API key authentication for griot-registry.

API keys are primarily used for service-to-service authentication.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader

from griot_registry.auth.models import AuthMethod, User, UserRole
from griot_registry.config import Settings, get_settings

# API key header security scheme
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def get_api_key_header() -> APIKeyHeader:
    """Get the API key header security scheme."""
    return api_key_header


async def get_current_user_api_key(
    api_key: Annotated[str | None, Security(api_key_header)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> User | None:
    """Get current user from API key.

    API key authentication creates a service user with editor permissions.
    Returns None if no API key provided or auth is disabled.
    Raises HTTPException if API key is invalid.

    Args:
        api_key: The API key from the header
        settings: Application settings

    Returns:
        User object for the service account, or None

    Raises:
        HTTPException: If API key is provided but invalid
    """
    # Skip auth if disabled
    if not settings.auth_enabled:
        return None

    # No API key provided - let other auth methods handle it
    if api_key is None:
        return None

    # Validate API key
    if api_key not in settings.api_keys:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "INVALID_API_KEY", "message": "Invalid API key"},
        )

    # Create service user with the API key as identifier
    # In production, you might want to map API keys to specific service accounts
    key_index = settings.api_keys.index(api_key)
    service_id = f"service-{key_index}"

    return User(
        id=service_id,
        email=None,
        name=f"Service Account {key_index}",
        roles=[UserRole.SERVICE, UserRole.EDITOR],
        auth_method=AuthMethod.API_KEY,
        metadata={"api_key_index": key_index},
    )


# Type alias for dependency injection
ApiKeyUser = Annotated[User | None, Depends(get_current_user_api_key)]
