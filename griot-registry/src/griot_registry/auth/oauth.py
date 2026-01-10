"""OAuth2/OIDC authentication for griot-registry (stub for future implementation)."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer

# OAuth2 scheme (stub - not yet configured)
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="",  # Will be configured when implemented
    tokenUrl="",  # Will be configured when implemented
    auto_error=False,
)


async def oauth2_auth(
    token: Annotated[str | None, Depends(oauth2_scheme)],
) -> dict | None:
    """Validate OAuth2/OIDC token.

    TODO: Implement in T-100

    Args:
        token: The bearer token from the header.

    Returns:
        Decoded token claims, or None if auth is disabled.

    Raises:
        HTTPException: If token is invalid.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail={
            "code": "NOT_IMPLEMENTED",
            "message": "OAuth2/OIDC authentication not yet implemented (T-100)",
        },
    )


# Dependency for OAuth2 protected routes
OAuth2Auth = Annotated[dict | None, Depends(oauth2_auth)]
