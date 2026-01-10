"""API key authentication for griot-registry."""

from typing import Annotated

from fastapi import Depends, HTTPException, Request, Security, status
from fastapi.security import APIKeyHeader

from griot_registry.config import Settings, get_settings

# API key header security scheme
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def get_api_key_header() -> APIKeyHeader:
    """Get the API key header security scheme."""
    return api_key_header


async def api_key_auth(
    request: Request,
    api_key: Annotated[str | None, Security(api_key_header)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> str | None:
    """Validate API key authentication.

    If authentication is disabled, returns None.
    If enabled, validates the provided API key against configured keys.

    Args:
        request: The FastAPI request.
        api_key: The API key from the header.
        settings: Application settings.

    Returns:
        The validated API key, or None if auth is disabled.

    Raises:
        HTTPException: If auth is enabled and key is missing or invalid.
    """
    # Skip auth if disabled
    if not settings.auth_enabled:
        return None

    # Check if API key is provided
    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "UNAUTHORIZED", "message": "API key required"},
            headers={"WWW-Authenticate": "ApiKey"},
        )

    # Validate API key
    if api_key not in settings.api_keys:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "FORBIDDEN", "message": "Invalid API key"},
        )

    return api_key


# Dependency for protected routes
ApiKeyAuth = Annotated[str | None, Depends(api_key_auth)]
