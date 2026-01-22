"""JWT authentication for griot-registry.

Provides JWT token creation, validation, and FastAPI dependencies.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Annotated, Any

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from griot_registry.auth.models import (
    AuthMethod,
    TokenPayload,
    TokenResponse,
    User,
    UserRole,
)
from griot_registry.config import Settings, get_settings

# Bearer token security scheme
bearer_scheme = HTTPBearer(auto_error=False)


class JWTAuth:
    """JWT authentication service."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self._secret_key = settings.jwt_secret_key.get_secret_value()
        self._algorithm = settings.jwt_algorithm
        self._issuer = settings.jwt_issuer

    def create_access_token(
        self,
        user_id: str,
        email: str | None = None,
        name: str | None = None,
        roles: list[UserRole] | None = None,
        additional_claims: dict[str, Any] | None = None,
        expire_minutes: int | None = None,
    ) -> str:
        """Create an access token for a user.

        Args:
            user_id: Unique user identifier
            email: User email
            name: User display name
            roles: User roles
            additional_claims: Extra claims to include in the token
            expire_minutes: Custom expiry time in minutes (default from settings)

        Returns:
            Encoded JWT access token
        """
        now = datetime.now(timezone.utc)
        exp_minutes = expire_minutes or self.settings.jwt_access_token_expire_minutes
        expires = now + timedelta(minutes=exp_minutes)

        payload = {
            "sub": user_id,
            "email": email,
            "name": name,
            "roles": [r.value if isinstance(r, UserRole) else r for r in (roles or [])],
            "exp": expires,
            "iat": now,
            "iss": self._issuer,
            "type": "access",
        }

        if additional_claims:
            payload.update(additional_claims)

        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

    def create_refresh_token(
        self,
        user_id: str,
    ) -> str:
        """Create a refresh token for a user.

        Args:
            user_id: Unique user identifier

        Returns:
            Encoded JWT refresh token
        """
        now = datetime.now(timezone.utc)
        expires = now + timedelta(days=self.settings.jwt_refresh_token_expire_days)

        payload = {
            "sub": user_id,
            "exp": expires,
            "iat": now,
            "iss": self._issuer,
            "type": "refresh",
        }

        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

    def create_token_response(
        self,
        user_id: str,
        email: str | None = None,
        name: str | None = None,
        roles: list[UserRole] | None = None,
        include_refresh: bool = True,
        expire_minutes: int | None = None,
    ) -> TokenResponse:
        """Create a complete token response with access and optionally refresh tokens.

        Args:
            user_id: Unique user identifier
            email: User email
            name: User display name
            roles: User roles
            include_refresh: Whether to include a refresh token
            expire_minutes: Custom expiry time in minutes (default from settings)

        Returns:
            TokenResponse with access token and optional refresh token
        """
        exp_minutes = expire_minutes or self.settings.jwt_access_token_expire_minutes

        access_token = self.create_access_token(
            user_id=user_id,
            email=email,
            name=name,
            roles=roles,
            expire_minutes=exp_minutes,
        )

        refresh_token = None
        if include_refresh:
            refresh_token = self.create_refresh_token(user_id)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=exp_minutes * 60,
        )

    def decode_token(self, token: str) -> TokenPayload:
        """Decode and validate a JWT token.

        Args:
            token: Encoded JWT token

        Returns:
            Decoded token payload

        Raises:
            HTTPException: If token is invalid or expired
        """
        try:
            payload = jwt.decode(
                token,
                self._secret_key,
                algorithms=[self._algorithm],
                issuer=self._issuer,
            )
            return TokenPayload(
                sub=payload["sub"],
                email=payload.get("email"),
                name=payload.get("name"),
                roles=payload.get("roles", []),
                exp=datetime.fromtimestamp(payload["exp"], tz=timezone.utc),
                iat=datetime.fromtimestamp(payload["iat"], tz=timezone.utc),
                iss=payload["iss"],
                type=payload.get("type", "access"),
            )
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "TOKEN_EXPIRED", "message": "Token has expired"},
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "INVALID_TOKEN", "message": f"Invalid token: {e}"},
                headers={"WWW-Authenticate": "Bearer"},
            )

    def verify_refresh_token(self, token: str) -> str:
        """Verify a refresh token and return the user ID.

        Args:
            token: Refresh token

        Returns:
            User ID from the token

        Raises:
            HTTPException: If token is invalid, expired, or not a refresh token
        """
        payload = self.decode_token(token)

        if payload.type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "INVALID_TOKEN_TYPE", "message": "Not a refresh token"},
            )

        return payload.sub

    def get_user_from_token(self, token: str) -> User:
        """Extract user information from a valid access token.

        Args:
            token: Access token

        Returns:
            User object with information from the token

        Raises:
            HTTPException: If token is invalid or not an access token
        """
        payload = self.decode_token(token)

        if payload.type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "INVALID_TOKEN_TYPE", "message": "Not an access token"},
            )

        roles = [UserRole(r) for r in payload.roles if r in UserRole._value2member_map_]

        return User(
            id=payload.sub,
            email=payload.email,
            name=payload.name,
            roles=roles or [UserRole.VIEWER],
            auth_method=AuthMethod.JWT,
        )


# Dependency to get JWT auth service
def get_jwt_auth(
    settings: Annotated[Settings, Depends(get_settings)],
) -> JWTAuth:
    """Get JWT authentication service."""
    return JWTAuth(settings)


# Dependency to get current user from JWT
async def get_current_user_jwt(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    jwt_auth: Annotated[JWTAuth, Depends(get_jwt_auth)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> User | None:
    """Get current user from JWT bearer token.

    Returns None if auth is disabled or no token provided.
    Raises HTTPException if token is invalid.
    """
    # Skip auth if disabled
    if not settings.auth_enabled:
        return None

    if credentials is None:
        return None

    return jwt_auth.get_user_from_token(credentials.credentials)


# Type alias for dependency injection
JWTUser = Annotated[User | None, Depends(get_current_user_jwt)]
