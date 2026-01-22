"""Role and permission models."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class PermissionCategory(str, Enum):
    """Permission categories."""

    CONTRACTS = "contracts"
    ASSETS = "assets"
    ISSUES = "issues"
    ADMIN = "admin"
    TEAMS = "teams"


class Permission(BaseModel):
    """Individual permission."""

    id: str
    name: str
    description: str
    category: PermissionCategory


# System permissions definition
SYSTEM_PERMISSIONS: list[Permission] = [
    # Contracts
    Permission(id="contracts:view", name="View contracts", description="View contract details", category=PermissionCategory.CONTRACTS),
    Permission(id="contracts:create", name="Create contracts", description="Create new contracts", category=PermissionCategory.CONTRACTS),
    Permission(id="contracts:edit", name="Edit contracts", description="Edit existing contracts", category=PermissionCategory.CONTRACTS),
    Permission(id="contracts:delete", name="Delete contracts", description="Delete/deprecate contracts", category=PermissionCategory.CONTRACTS),
    Permission(id="contracts:approve", name="Approve contracts", description="Approve contract submissions", category=PermissionCategory.CONTRACTS),
    Permission(id="contracts:submit", name="Submit contracts", description="Submit contracts for review", category=PermissionCategory.CONTRACTS),
    # Assets
    Permission(id="assets:view", name="View assets", description="View data assets", category=PermissionCategory.ASSETS),
    Permission(id="assets:create", name="Create assets", description="Create data assets", category=PermissionCategory.ASSETS),
    Permission(id="assets:edit", name="Edit assets", description="Edit data assets", category=PermissionCategory.ASSETS),
    Permission(id="assets:delete", name="Delete assets", description="Delete data assets", category=PermissionCategory.ASSETS),
    # Issues
    Permission(id="issues:view", name="View issues", description="View quality issues", category=PermissionCategory.ISSUES),
    Permission(id="issues:create", name="Create issues", description="Create issues manually", category=PermissionCategory.ISSUES),
    Permission(id="issues:edit", name="Edit issues", description="Edit and assign issues", category=PermissionCategory.ISSUES),
    Permission(id="issues:resolve", name="Resolve issues", description="Resolve/close issues", category=PermissionCategory.ISSUES),
    # Teams
    Permission(id="teams:view", name="View teams", description="View team details", category=PermissionCategory.TEAMS),
    Permission(id="teams:manage", name="Manage teams", description="Create and manage teams", category=PermissionCategory.TEAMS),
    # Admin
    Permission(id="admin:users", name="Manage users", description="Manage user accounts", category=PermissionCategory.ADMIN),
    Permission(id="admin:roles", name="Manage roles", description="Manage roles and permissions", category=PermissionCategory.ADMIN),
    Permission(id="admin:settings", name="Manage settings", description="Manage system settings", category=PermissionCategory.ADMIN),
]


# Default role permission sets
ADMIN_PERMISSIONS = [p.id for p in SYSTEM_PERMISSIONS]

EDITOR_PERMISSIONS = [
    "contracts:view", "contracts:create", "contracts:edit", "contracts:submit",
    "assets:view", "assets:create", "assets:edit",
    "issues:view", "issues:create", "issues:edit", "issues:resolve",
    "teams:view",
]

VIEWER_PERMISSIONS = [
    "contracts:view",
    "assets:view",
    "issues:view",
    "teams:view",
]


class RoleCreate(BaseModel):
    """Role creation request."""

    name: str = Field(..., min_length=2, max_length=50)
    description: str | None = Field(None, max_length=200)
    permissions: list[str] = Field(..., description="List of permission IDs")


class RoleUpdate(BaseModel):
    """Role update request."""

    name: str | None = Field(None, min_length=2, max_length=50)
    description: str | None = Field(None, max_length=200)
    permissions: list[str] | None = Field(None, description="List of permission IDs")


class RoleInDB(BaseModel):
    """Role as stored in database."""

    id: str
    name: str
    description: str | None = None
    permissions: list[str] = []
    is_system: bool = False  # System roles cannot be deleted/modified
    created_at: datetime
    updated_at: datetime


class RoleResponse(BaseModel):
    """Role response for API."""

    id: str
    name: str
    description: str | None = None
    permissions: list[str]
    permission_count: int = Field(0, alias="permissionCount")
    is_system: bool = Field(False, alias="isSystem")
    created_at: datetime = Field(..., alias="createdAt")

    model_config = {"populate_by_name": True}


class RoleListResponse(BaseModel):
    """Role list response."""

    items: list[RoleResponse]
    total: int
