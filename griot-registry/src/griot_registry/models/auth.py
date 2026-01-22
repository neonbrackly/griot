"""Authentication models."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field, field_validator
import re


class LoginRequest(BaseModel):
    """Login request body."""

    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=1, description="User's password")
    remember_me: bool = Field(default=False, alias="rememberMe", description="Extend token expiry")

    model_config = {"populate_by_name": True}


class SignupRequest(BaseModel):
    """Signup request body."""

    name: str = Field(..., min_length=2, max_length=100, description="User's full name")
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, description="Password")
    confirm_password: str = Field(..., alias="confirmPassword", description="Password confirmation")
    accept_terms: bool = Field(..., alias="acceptTerms", description="Terms acceptance")

    model_config = {"populate_by_name": True}

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password meets requirements."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least 1 uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least 1 lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least 1 number")
        return v

    @field_validator("accept_terms")
    @classmethod
    def validate_terms_accepted(cls, v: bool) -> bool:
        """Validate terms are accepted."""
        if not v:
            raise ValueError("You must accept the terms of service")
        return v


class RoleRef(BaseModel):
    """Role reference in auth response."""

    id: str
    name: str


class TeamRef(BaseModel):
    """Team reference in auth response."""

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
    """Authentication response with user and token."""

    user: AuthUserResponse
    token: str
    expires_at: datetime = Field(..., alias="expiresAt")

    model_config = {"populate_by_name": True}


class ForgotPasswordRequest(BaseModel):
    """Forgot password request body."""

    email: EmailStr = Field(..., description="User's email address")


class ResetPasswordRequest(BaseModel):
    """Reset password request body."""

    token: str = Field(..., description="Password reset token")
    password: str = Field(..., min_length=8, description="New password")
    confirm_password: str = Field(..., alias="confirmPassword", description="Password confirmation")

    model_config = {"populate_by_name": True}

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password meets requirements."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least 1 uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least 1 lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least 1 number")
        return v


class PasswordResetToken(BaseModel):
    """Password reset token stored in DB."""

    id: str
    user_id: str
    token: str
    expires_at: datetime
    used: bool = False
    created_at: datetime
