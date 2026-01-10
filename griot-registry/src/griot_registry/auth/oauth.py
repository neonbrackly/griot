"""OAuth2/OIDC authentication for griot-registry."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Annotated, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from pydantic import BaseModel
from pydantic_settings import BaseSettings


class OAuthSettings(BaseSettings):
    """OAuth2/OIDC configuration settings."""

    oauth_enabled: bool = False
    oauth_issuer: str = ""
    oauth_client_id: str = ""
    oauth_client_secret: str = ""
    oauth_audience: str = ""
    oauth_scopes: str = "openid profile email"

    model_config = {"env_prefix": "GRIOT_"}


@dataclass
class TokenClaims:
    """Validated JWT token claims."""

    sub: str
    email: str | None
    name: str | None
    roles: list[str]
    scopes: list[str]
    exp: datetime
    iat: datetime
    iss: str
    aud: str | list[str]
    raw: dict[str, Any]

    @property
    def is_expired(self) -> bool:
        """Check if token is expired."""
        return datetime.now(timezone.utc) > self.exp

    def has_role(self, role: str) -> bool:
        """Check if user has a specific role."""
        return role in self.roles

    def has_scope(self, scope: str) -> bool:
        """Check if token has a specific scope."""
        return scope in self.scopes


class OAuthProvider:
    """OAuth2/OIDC provider for token validation."""

    def __init__(self, settings: OAuthSettings) -> None:
        """Initialize OAuth provider.

        Args:
            settings: OAuth configuration settings.
        """
        self.settings = settings
        self._jwks_client = None
        self._discovery_doc = None

    async def _get_discovery_document(self) -> dict[str, Any]:
        """Fetch OIDC discovery document."""
        if self._discovery_doc:
            return self._discovery_doc

        try:
            import httpx
        except ImportError as e:
            raise ImportError(
                "httpx is required for OAuth. Install with: pip install griot-registry[oauth]"
            ) from e

        discovery_url = f"{self.settings.oauth_issuer.rstrip('/')}/.well-known/openid-configuration"

        async with httpx.AsyncClient() as client:
            response = await client.get(discovery_url)
            response.raise_for_status()
            self._discovery_doc = response.json()

        return self._discovery_doc

    async def _get_jwks_uri(self) -> str:
        """Get JWKS URI from discovery document."""
        doc = await self._get_discovery_document()
        return doc["jwks_uri"]

    async def validate_token(self, token: str) -> TokenClaims:
        """Validate JWT token and return claims.

        Args:
            token: The JWT token to validate.

        Returns:
            TokenClaims with validated claims.

        Raises:
            HTTPException: If token is invalid.
        """
        try:
            import jwt
            from jwt import PyJWKClient
        except ImportError as e:
            raise ImportError(
                "PyJWT is required for OAuth. Install with: pip install griot-registry[oauth]"
            ) from e

        try:
            # Get JWKS URI and create client
            jwks_uri = await self._get_jwks_uri()
            jwks_client = PyJWKClient(jwks_uri)

            # Get signing key from token
            signing_key = jwks_client.get_signing_key_from_jwt(token)

            # Decode and validate token
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256", "ES256"],
                audience=self.settings.oauth_audience or self.settings.oauth_client_id,
                issuer=self.settings.oauth_issuer,
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_iat": True,
                    "verify_aud": True,
                    "verify_iss": True,
                },
            )

            # Extract claims
            return TokenClaims(
                sub=payload.get("sub", ""),
                email=payload.get("email"),
                name=payload.get("name"),
                roles=payload.get("roles", payload.get("realm_access", {}).get("roles", [])),
                scopes=payload.get("scope", "").split() if isinstance(payload.get("scope"), str) else payload.get("scope", []),
                exp=datetime.fromtimestamp(payload["exp"], timezone.utc),
                iat=datetime.fromtimestamp(payload["iat"], timezone.utc),
                iss=payload["iss"],
                aud=payload["aud"],
                raw=payload,
            )

        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "TOKEN_EXPIRED", "message": "Token has expired"},
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.InvalidAudienceError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "INVALID_AUDIENCE", "message": "Invalid token audience"},
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.InvalidIssuerError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "INVALID_ISSUER", "message": "Invalid token issuer"},
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "INVALID_TOKEN", "message": str(e)},
                headers={"WWW-Authenticate": "Bearer"},
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "AUTH_ERROR", "message": f"Authentication failed: {e}"},
                headers={"WWW-Authenticate": "Bearer"},
            )


# Global OAuth settings and provider
_oauth_settings: OAuthSettings | None = None
_oauth_provider: OAuthProvider | None = None


def get_oauth_settings() -> OAuthSettings:
    """Get OAuth settings singleton."""
    global _oauth_settings
    if _oauth_settings is None:
        _oauth_settings = OAuthSettings()
    return _oauth_settings


def get_oauth_provider() -> OAuthProvider:
    """Get OAuth provider singleton."""
    global _oauth_provider
    if _oauth_provider is None:
        _oauth_provider = OAuthProvider(get_oauth_settings())
    return _oauth_provider


# OAuth2 scheme for FastAPI
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="",
    tokenUrl="",
    auto_error=False,
)


async def oauth2_auth(
    token: Annotated[str | None, Depends(oauth2_scheme)],
) -> TokenClaims | None:
    """Validate OAuth2/OIDC token.

    Args:
        token: The bearer token from the header.

    Returns:
        Decoded token claims, or None if auth is disabled.

    Raises:
        HTTPException: If token is invalid.
    """
    settings = get_oauth_settings()

    if not settings.oauth_enabled:
        return None

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "MISSING_TOKEN", "message": "Authorization token required"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    provider = get_oauth_provider()
    return await provider.validate_token(token)


# Type alias for dependency injection
OAuth2Auth = Annotated[TokenClaims | None, Depends(oauth2_auth)]


# Role-based access control helpers
def require_role(role: str):
    """Create a dependency that requires a specific role.

    Usage:
        @router.get("/admin", dependencies=[Depends(require_role("admin"))])
        async def admin_endpoint():
            ...
    """

    async def check_role(claims: OAuth2Auth) -> TokenClaims:
        if claims is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "AUTH_REQUIRED", "message": "Authentication required"},
            )
        if not claims.has_role(role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "FORBIDDEN", "message": f"Role '{role}' required"},
            )
        return claims

    return check_role


def require_scope(scope: str):
    """Create a dependency that requires a specific scope.

    Usage:
        @router.get("/read", dependencies=[Depends(require_scope("read:contracts"))])
        async def read_endpoint():
            ...
    """

    async def check_scope(claims: OAuth2Auth) -> TokenClaims:
        if claims is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "AUTH_REQUIRED", "message": "Authentication required"},
            )
        if not claims.has_scope(scope):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "FORBIDDEN", "message": f"Scope '{scope}' required"},
            )
        return claims

    return check_scope


# Convenience role checks
AdminRole = Annotated[TokenClaims, Depends(require_role("admin"))]
EditorRole = Annotated[TokenClaims, Depends(require_role("editor"))]
ViewerRole = Annotated[TokenClaims, Depends(require_role("viewer"))]
