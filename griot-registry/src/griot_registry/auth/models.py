"""Authentication models and types."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class UserRole(str, Enum):
    """User roles for authorization."""

    ADMIN = "admin"  # Full access to all operations
    EDITOR = "editor"  # Can create/update contracts
    VIEWER = "viewer"  # Read-only access
    SERVICE = "service"  # Service account (API key auth)


class AuthMethod(str, Enum):
    """Authentication method used."""

    JWT = "jwt"
    API_KEY = "api_key"
    OAUTH = "oauth"
    ANONYMOUS = "anonymous"


class User(BaseModel):
    """Authenticated user information."""

    id: str = Field(..., description="Unique user identifier")
    email: str | None = Field(None, description="User email")
    name: str | None = Field(None, description="User display name")
    roles: list[UserRole] = Field(default_factory=lambda: [UserRole.VIEWER])
    auth_method: AuthMethod = Field(..., description="How the user was authenticated")
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def is_admin(self) -> bool:
        """Check if user has admin role."""
        return UserRole.ADMIN in self.roles

    @property
    def is_editor(self) -> bool:
        """Check if user has editor or admin role."""
        return UserRole.EDITOR in self.roles or UserRole.ADMIN in self.roles

    @property
    def is_service(self) -> bool:
        """Check if this is a service account."""
        return self.auth_method == AuthMethod.API_KEY


class TokenPayload(BaseModel):
    """JWT token payload."""

    sub: str = Field(..., description="Subject (user ID)")
    email: str | None = None
    name: str | None = None
    roles: list[str] = Field(default_factory=list)
    exp: datetime = Field(..., description="Expiration time")
    iat: datetime = Field(..., description="Issued at time")
    iss: str = Field(..., description="Issuer")
    type: str = Field(default="access", description="Token type (access/refresh)")


class TokenResponse(BaseModel):
    """Token response for login/refresh."""

    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Access token expiry in seconds")


class LoginRequest(BaseModel):
    """Login request body."""

    email: str
    password: str


class RefreshRequest(BaseModel):
    """Refresh token request."""

    refresh_token: str
