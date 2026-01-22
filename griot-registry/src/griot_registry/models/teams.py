"""Team models."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class RoleRef(BaseModel):
    """Role reference."""

    id: str
    name: str


class TeamMember(BaseModel):
    """Team member with role."""

    user_id: str = Field(..., alias="userId")
    user_name: str = Field(..., alias="userName")
    user_email: str = Field(..., alias="userEmail")
    user_avatar: str | None = Field(None, alias="userAvatar")
    role: RoleRef
    joined_at: datetime = Field(..., alias="joinedAt")

    model_config = {"populate_by_name": True}


class TeamMemberCreate(BaseModel):
    """Add member to team request."""

    user_id: str = Field(..., alias="userId")
    role_id: str | None = Field(None, alias="roleId", description="Override team default role")

    model_config = {"populate_by_name": True}


class TeamMemberUpdate(BaseModel):
    """Update team member role."""

    role_id: str = Field(..., alias="roleId")

    model_config = {"populate_by_name": True}


class TeamCreate(BaseModel):
    """Team creation request."""

    name: str = Field(..., min_length=2, max_length=100)
    description: str | None = Field(None, max_length=500)
    default_role_id: str = Field(..., alias="defaultRoleId", description="Default role for new members")

    model_config = {"populate_by_name": True}


class TeamUpdate(BaseModel):
    """Team update request."""

    name: str | None = Field(None, min_length=2, max_length=100)
    description: str | None = Field(None, max_length=500)
    default_role_id: str | None = Field(None, alias="defaultRoleId")

    model_config = {"populate_by_name": True}


class TeamInDB(BaseModel):
    """Team as stored in database."""

    id: str
    name: str
    description: str | None = None
    default_role_id: str
    members: list[dict[str, Any]] = []  # List of {user_id, role_id, joined_at}
    created_at: datetime
    updated_at: datetime
    created_by: str | None = None


class TeamResponse(BaseModel):
    """Team response for API."""

    id: str
    name: str
    description: str | None = None
    default_role: RoleRef = Field(..., alias="defaultRole")
    member_count: int = Field(0, alias="memberCount")
    members: list[TeamMember] | None = None  # Only included on detail endpoint
    created_at: datetime = Field(..., alias="createdAt")

    model_config = {"populate_by_name": True}


class TeamListResponse(BaseModel):
    """Paginated team list response."""

    items: list[TeamResponse]
    total: int
    page: int = 1
    limit: int = 20
