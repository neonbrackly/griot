"""User models."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, EmailStr, Field


class UserStatus(str, Enum):
    """User account status."""

    ACTIVE = "active"
    PENDING = "pending"  # Invited but not yet registered
    DEACTIVATED = "deactivated"


class RoleRef(BaseModel):
    """Role reference."""

    id: str
    name: str


class TeamRef(BaseModel):
    """Team reference."""

    id: str
    name: str


class UserCreate(BaseModel):
    """User creation (for signup)."""

    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserInvite(BaseModel):
    """User invitation request."""

    email: EmailStr = Field(..., description="Email to invite")
    role_id: str = Field(..., alias="roleId", description="Role to assign")
    team_id: str | None = Field(None, alias="teamId", description="Team to add to")

    model_config = {"populate_by_name": True}


class UserUpdate(BaseModel):
    """User update request."""

    name: str | None = Field(None, min_length=2, max_length=100)
    avatar: str | None = None
    email: EmailStr | None = None


class UserRoleChange(BaseModel):
    """User role change request."""

    role_id: str = Field(..., alias="roleId", description="New role ID")

    model_config = {"populate_by_name": True}


class UserInDB(BaseModel):
    """User as stored in database."""

    id: str
    name: str
    email: str
    password_hash: str
    avatar: str | None = None
    role_id: str
    team_id: str | None = None
    status: UserStatus = UserStatus.ACTIVE
    failed_login_attempts: int = 0
    locked_until: datetime | None = None
    last_login_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    created_by: str | None = None


class UserResponse(BaseModel):
    """User response for API."""

    id: str
    name: str
    email: str
    avatar: str | None = None
    role: RoleRef
    team: TeamRef | None = None
    status: UserStatus
    last_login_at: datetime | None = Field(None, alias="lastLoginAt")
    created_at: datetime = Field(..., alias="createdAt")

    model_config = {"populate_by_name": True}


class UserListResponse(BaseModel):
    """Paginated user list response."""

    items: list[UserResponse]
    total: int
    page: int = 1
    limit: int = 20
