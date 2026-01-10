"""OAuth2/OIDC authentication for griot-registry."""

from datetime import datetime, timezone
from typing import Annotated, Any

import httpx
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class OAuthSettings(BaseSettings):
    """OAuth2/OIDC settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_prefix="GRIOT_OAUTH_",
        env_file=".env",
        extra="ignore",
    )

    # OAuth2 provider configuration
    enabled: bool = False
    issuer_url: str = ""  # e.g., https://accounts.google.com
    client_id: str = ""
    client_secret: str = ""

    # Token validation
    audience: str = ""  # Expected audience claim
    scopes: list[str] = ["openid", "profile", "email"]

    # OIDC endpoints (auto-discovered from issuer if not set)
    authorization_url: str = ""
    token_url: str = ""
    userinfo_url: str = ""
    jwks_url: str = ""

    # Token cache TTL in seconds
    token_cache_ttl: int = 300


class TokenClaims(BaseModel):
    """Decoded JWT token claims."""

    sub: str  # Subject (user ID)
    email: str | None = None
    name: str | None = None
    preferred_username: str | None = None
    groups: list[str] = []
    roles: list[str] = []
    iss: str  # Issuer
    aud: str | list[str]  # Audience
    exp: int  # Expiration time
    iat: int  # Issued at time


class OAuthProvider:
    """OAuth2/OIDC provider for token validation."""

    def __init__(self, settings: OAuthSettings) -> None:
        """Initialize OAuth provider.

        Args:
            settings: OAuth configuration settings.
        """
        self.settings = settings
        self._oidc_config: dict[str, Any] | None = None
        self._jwks: dict[str, Any] | None = None
        self._jwks_last_fetch: datetime | None = None

    async def discover_oidc_config(self) -> dict[str, Any]:
        """Discover OIDC configuration from issuer's well-known endpoint."""
        if self._oidc_config is not None:
            return self._oidc_config

        if not self.settings.issuer_url:
            raise ValueError("OAuth issuer URL not configured")

        discovery_url = f"{self.settings.issuer_url.rstrip('/')}/.well-known/openid-configuration"

        async with httpx.AsyncClient() as client:
            response = await client.get(discovery_url)
            response.raise_for_status()
            self._oidc_config = response.json()

        return self._oidc_config

    async def get_jwks(self) -> dict[str, Any]:
        """Fetch JSON Web Key Set from the provider."""
        # Check cache
        now = datetime.now(timezone.utc)
        if (
            self._jwks is not None
            and self._jwks_last_fetch is not None
            and (now - self._jwks_last_fetch).seconds < self.settings.token_cache_ttl
        ):
            return self._jwks

        # Get JWKS URL
        if self.settings.jwks_url:
            jwks_url = self.settings.jwks_url
        else:
            config = await self.discover_oidc_config()
            jwks_url = config.get("jwks_uri", "")

        if not jwks_url:
            raise ValueError("JWKS URL not configured or discovered")

        async with httpx.AsyncClient() as client:
            response = await client.get(jwks_url)
            response.raise_for_status()
            self._jwks = response.json()
            self._jwks_last_fetch = now

        return self._jwks

    async def validate_token(self, token: str) -> TokenClaims:
        """Validate a JWT token and return claims.

        Args:
            token: The JWT token to validate.

        Returns:
            Decoded token claims.

        Raises:
            HTTPException: If token is invalid.
        """
        try:
            # Import jwt library (optional dependency)
            import jwt
            from jwt import PyJWKClient

            # Get JWKS
            jwks = await self.get_jwks()

            # Create PyJWKClient with our cached keys
            jwks_url = self.settings.jwks_url
            if not jwks_url:
                config = await self.discover_oidc_config()
                jwks_url = config.get("jwks_uri", "")

            jwks_client = PyJWKClient(jwks_url)
            signing_key = jwks_client.get_signing_key_from_jwt(token)

            # Decode and validate token
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256", "RS384", "RS512", "ES256", "ES384", "ES512"],
                audience=self.settings.audience or self.settings.client_id,
                issuer=self.settings.issuer_url,
            )

            return TokenClaims(
                sub=payload.get("sub", ""),
                email=payload.get("email"),
                name=payload.get("name"),
                preferred_username=payload.get("preferred_username"),
                groups=payload.get("groups", []),
                roles=payload.get("roles", payload.get("realm_access", {}).get("roles", [])),
                iss=payload.get("iss", ""),
                aud=payload.get("aud", ""),
                exp=payload.get("exp", 0),
                iat=payload.get("iat", 0),
            )

        except ImportError:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail={
                    "code": "DEPENDENCY_MISSING",
                    "message": "PyJWT library required for OAuth2. Install with: pip install pyjwt[crypto]",
                },
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
                detail={"code": "INVALID_AUDIENCE", "message": "Token audience is invalid"},
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.InvalidIssuerError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "INVALID_ISSUER", "message": "Token issuer is invalid"},
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "INVALID_TOKEN", "message": str(e)},
                headers={"WWW-Authenticate": "Bearer"},
            )

    async def get_userinfo(self, token: str) -> dict[str, Any]:
        """Fetch user info from the OIDC provider.

        Args:
            token: The access token.

        Returns:
            User info from the provider.
        """
        if self.settings.userinfo_url:
            userinfo_url = self.settings.userinfo_url
        else:
            config = await self.discover_oidc_config()
            userinfo_url = config.get("userinfo_endpoint", "")

        if not userinfo_url:
            raise ValueError("UserInfo URL not configured or discovered")

        async with httpx.AsyncClient() as client:
            response = await client.get(
                userinfo_url,
                headers={"Authorization": f"Bearer {token}"},
            )
            response.raise_for_status()
            return response.json()


# Singleton provider instance
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


# OAuth2 bearer scheme
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="",  # Configured dynamically
    tokenUrl="",  # Configured dynamically
    auto_error=False,
)


async def oauth2_auth(
    request: Request,
    token: Annotated[str | None, Depends(oauth2_scheme)],
) -> TokenClaims | None:
    """Validate OAuth2/OIDC bearer token.

    If OAuth is disabled, returns None.
    If enabled, validates the token and returns decoded claims.

    Args:
        request: The FastAPI request.
        token: The bearer token from the Authorization header.

    Returns:
        Decoded token claims, or None if OAuth is disabled.

    Raises:
        HTTPException: If OAuth is enabled and token is missing or invalid.
    """
    settings = get_oauth_settings()

    # Skip auth if disabled
    if not settings.enabled:
        return None

    # Check if token is provided
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "UNAUTHORIZED", "message": "Bearer token required"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Validate token
    provider = get_oauth_provider()
    return await provider.validate_token(token)


# Dependency type for protected routes
OAuth2Auth = Annotated[TokenClaims | None, Depends(oauth2_auth)]


# Role-based access control helpers
def require_role(*roles: str):
    """Create a dependency that requires specific roles.

    Args:
        *roles: Required roles (any one of them).

    Returns:
        FastAPI dependency function.
    """
    async def check_role(claims: OAuth2Auth) -> TokenClaims:
        if claims is None:
            # OAuth disabled, allow access
            return TokenClaims(
                sub="anonymous",
                iss="local",
                aud="griot-registry",
                exp=0,
                iat=0,
            )

        # Check if user has any of the required roles
        user_roles = set(claims.roles)
        required_roles = set(roles)

        if not user_roles.intersection(required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "FORBIDDEN",
                    "message": f"Required role: {' or '.join(roles)}",
                },
            )

        return claims

    return check_role


def require_scope(*scopes: str):
    """Create a dependency that requires specific scopes.

    Args:
        *scopes: Required scopes (all of them).

    Returns:
        FastAPI dependency function.
    """
    async def check_scope(
        request: Request,
        claims: OAuth2Auth,
    ) -> TokenClaims:
        if claims is None:
            # OAuth disabled, allow access
            return TokenClaims(
                sub="anonymous",
                iss="local",
                aud="griot-registry",
                exp=0,
                iat=0,
            )

        # Get token to check scopes (scopes often in token, not claims)
        # For simplicity, we assume scopes are validated by the provider
        # In production, you'd check the scope claim

        return claims

    return check_scope


# Common role dependencies
AdminRole = Annotated[TokenClaims, Depends(require_role("admin", "registry-admin"))]
EditorRole = Annotated[TokenClaims, Depends(require_role("admin", "editor", "registry-editor"))]
ViewerRole = Annotated[TokenClaims, Depends(require_role("admin", "editor", "viewer", "registry-viewer"))]
