"""Role and permission management API endpoints."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field

from griot_registry.auth import CurrentUser, require_admin

router = APIRouter(tags=["roles"])


# =============================================================================
# Permission Definitions
# =============================================================================

# System-wide permissions
SYSTEM_PERMISSIONS = [
    # Contract permissions
    {"id": "contracts:read", "name": "View Contracts", "category": "contracts", "description": "View contract details"},
    {"id": "contracts:write", "name": "Create/Edit Contracts", "category": "contracts", "description": "Create and edit contracts"},
    {"id": "contracts:delete", "name": "Delete Contracts", "category": "contracts", "description": "Delete contracts"},
    {"id": "contracts:approve", "name": "Approve Contracts", "category": "contracts", "description": "Approve or reject contract submissions"},

    # Asset permissions
    {"id": "assets:read", "name": "View Assets", "category": "assets", "description": "View data assets"},
    {"id": "assets:write", "name": "Create/Edit Assets", "category": "assets", "description": "Create and edit data assets"},
    {"id": "assets:delete", "name": "Delete Assets", "category": "assets", "description": "Delete data assets"},

    # Issue permissions
    {"id": "issues:read", "name": "View Issues", "category": "issues", "description": "View data quality issues"},
    {"id": "issues:write", "name": "Update Issues", "category": "issues", "description": "Update issue status and assignments"},
    {"id": "issues:resolve", "name": "Resolve Issues", "category": "issues", "description": "Mark issues as resolved"},

    # Admin permissions
    {"id": "admin:users", "name": "Manage Users", "category": "admin", "description": "Invite, update, and deactivate users"},
    {"id": "admin:teams", "name": "Manage Teams", "category": "admin", "description": "Create, update, and delete teams"},
    {"id": "admin:roles", "name": "Manage Roles", "category": "admin", "description": "Create and modify custom roles"},
    {"id": "admin:settings", "name": "System Settings", "category": "admin", "description": "Configure system settings"},

    # Schema permissions
    {"id": "schemas:read", "name": "View Schemas", "category": "schemas", "description": "View schema definitions"},
    {"id": "schemas:write", "name": "Create/Edit Schemas", "category": "schemas", "description": "Create and edit schemas"},

    # Connection permissions
    {"id": "connections:read", "name": "View Connections", "category": "connections", "description": "View database connections"},
    {"id": "connections:write", "name": "Create/Edit Connections", "category": "connections", "description": "Create and edit database connections"},
    {"id": "connections:delete", "name": "Delete Connections", "category": "connections", "description": "Delete database connections"},
]

# Default permission sets for system roles
ADMIN_PERMISSIONS = [p["id"] for p in SYSTEM_PERMISSIONS]
EDITOR_PERMISSIONS = [
    "contracts:read", "contracts:write", "contracts:approve",
    "assets:read", "assets:write",
    "issues:read", "issues:write", "issues:resolve",
    "schemas:read", "schemas:write",
    "connections:read", "connections:write",
]
VIEWER_PERMISSIONS = [
    "contracts:read",
    "assets:read",
    "issues:read",
    "schemas:read",
    "connections:read",
]


# =============================================================================
# Request/Response Models
# =============================================================================


class PermissionResponse(BaseModel):
    """Permission response."""

    id: str
    name: str
    category: str
    description: str | None = None


class RoleResponse(BaseModel):
    """Role response."""

    id: str
    name: str
    description: str | None = None
    permissions: list[str] = []
    is_system: bool = Field(default=False, alias="isSystem")
    user_count: int = Field(default=0, alias="userCount")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")

    model_config = {"populate_by_name": True}


class RoleDetailResponse(BaseModel):
    """Role detail response with full permission objects."""

    id: str
    name: str
    description: str | None = None
    permissions: list[PermissionResponse] = []
    is_system: bool = Field(default=False, alias="isSystem")
    user_count: int = Field(default=0, alias="userCount")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")

    model_config = {"populate_by_name": True}


class RoleListResponse(BaseModel):
    """Role list response."""

    items: list[RoleResponse]


class RoleCreateRequest(BaseModel):
    """Role create request."""

    name: str = Field(..., min_length=2, max_length=50)
    description: str | None = Field(default=None, max_length=200)
    permissions: list[str] = []


class RoleUpdateRequest(BaseModel):
    """Role update request."""

    name: str | None = Field(default=None, min_length=2, max_length=50)
    description: str | None = Field(default=None, max_length=200)
    permissions: list[str] | None = None


class PermissionListResponse(BaseModel):
    """Permission list response."""

    items: list[PermissionResponse]
    categories: list[str]


# =============================================================================
# Helper Functions
# =============================================================================


def _utc_now() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(timezone.utc)


def _get_permission_objects(permission_ids: list[str]) -> list[PermissionResponse]:
    """Get full permission objects for a list of permission IDs."""
    perm_map = {p["id"]: p for p in SYSTEM_PERMISSIONS}
    return [
        PermissionResponse(
            id=p["id"],
            name=p["name"],
            category=p["category"],
            description=p.get("description"),
        )
        for pid in permission_ids
        if (p := perm_map.get(pid))
    ]


async def _build_role_response(role_doc: dict[str, Any], storage: Any) -> RoleResponse:
    """Build role response."""
    # Count users with this role
    users, _ = await storage.users.list(role_id=role_doc["id"], limit=0)

    return RoleResponse(
        id=role_doc["id"],
        name=role_doc["name"],
        description=role_doc.get("description"),
        permissions=role_doc.get("permissions", []),
        is_system=role_doc.get("is_system", False),
        user_count=len(users) if users else 0,
        created_at=role_doc["created_at"],
        updated_at=role_doc.get("updated_at", role_doc["created_at"]),
    )


async def _build_role_detail_response(role_doc: dict[str, Any], storage: Any) -> RoleDetailResponse:
    """Build role detail response with full permission objects."""
    # Count users with this role
    users, total = await storage.users.list(role_id=role_doc["id"], limit=1)

    return RoleDetailResponse(
        id=role_doc["id"],
        name=role_doc["name"],
        description=role_doc.get("description"),
        permissions=_get_permission_objects(role_doc.get("permissions", [])),
        is_system=role_doc.get("is_system", False),
        user_count=total,
        created_at=role_doc["created_at"],
        updated_at=role_doc.get("updated_at", role_doc["created_at"]),
    )


# =============================================================================
# Permission Endpoints
# =============================================================================


@router.get(
    "/permissions",
    operation_id="listPermissions",
    summary="List all available permissions",
    response_model=PermissionListResponse,
)
async def list_permissions(
    request: Request,
    user: CurrentUser,
) -> PermissionListResponse:
    """List all available system permissions."""
    items = [
        PermissionResponse(
            id=p["id"],
            name=p["name"],
            category=p["category"],
            description=p.get("description"),
        )
        for p in SYSTEM_PERMISSIONS
    ]

    categories = sorted(set(p["category"] for p in SYSTEM_PERMISSIONS))

    return PermissionListResponse(items=items, categories=categories)


# =============================================================================
# Role Endpoints
# =============================================================================


@router.get(
    "/roles",
    operation_id="listRoles",
    summary="List all roles",
    response_model=RoleListResponse,
)
async def list_roles(
    request: Request,
    user: CurrentUser,
) -> RoleListResponse:
    """List all roles."""
    storage = request.app.state.storage

    roles = await storage.roles.list()
    items = [await _build_role_response(r, storage) for r in roles]

    return RoleListResponse(items=items)


@router.post(
    "/roles",
    operation_id="createRole",
    summary="Create a custom role",
    response_model=RoleDetailResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
async def create_role(
    request: Request,
    user: CurrentUser,
    body: RoleCreateRequest,
) -> RoleDetailResponse:
    """Create a new custom role.

    Only admins can create roles.
    """
    storage = request.app.state.storage

    # Validate permissions
    valid_perm_ids = {p["id"] for p in SYSTEM_PERMISSIONS}
    invalid = [p for p in body.permissions if p not in valid_perm_ids]
    if invalid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "INVALID_PERMISSIONS", "message": f"Invalid permission IDs: {invalid}"}},
        )

    role_doc = {
        "name": body.name,
        "description": body.description,
        "permissions": body.permissions,
        "is_system": False,
    }

    role = await storage.roles.create(role_doc)
    return await _build_role_detail_response(role, storage)


@router.get(
    "/roles/{role_id}",
    operation_id="getRole",
    summary="Get role by ID",
    response_model=RoleDetailResponse,
)
async def get_role(
    request: Request,
    role_id: str,
    user: CurrentUser,
) -> RoleDetailResponse:
    """Get a specific role with permissions."""
    storage = request.app.state.storage

    role = await storage.roles.get(role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "ROLE_NOT_FOUND", "message": f"Role '{role_id}' not found"}},
        )

    return await _build_role_detail_response(role, storage)


@router.patch(
    "/roles/{role_id}",
    operation_id="updateRole",
    summary="Update a role",
    response_model=RoleDetailResponse,
    dependencies=[Depends(require_admin)],
)
async def update_role(
    request: Request,
    role_id: str,
    user: CurrentUser,
    body: RoleUpdateRequest,
) -> RoleDetailResponse:
    """Update a role.

    Only admins can update roles.
    System roles (Admin, Editor, Viewer) cannot be modified.
    """
    storage = request.app.state.storage

    # Check if role exists
    role = await storage.roles.get(role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "ROLE_NOT_FOUND", "message": f"Role '{role_id}' not found"}},
        )

    # Cannot modify system roles
    if role.get("is_system", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": {"code": "SYSTEM_ROLE", "message": "System roles cannot be modified"}},
        )

    # Validate permissions if provided
    if body.permissions is not None:
        valid_perm_ids = {p["id"] for p in SYSTEM_PERMISSIONS}
        invalid = [p for p in body.permissions if p not in valid_perm_ids]
        if invalid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": {"code": "INVALID_PERMISSIONS", "message": f"Invalid permission IDs: {invalid}"}},
            )

    # Build update dict
    updates: dict[str, Any] = {"updated_at": _utc_now()}
    if body.name is not None:
        updates["name"] = body.name
    if body.description is not None:
        updates["description"] = body.description
    if body.permissions is not None:
        updates["permissions"] = body.permissions

    updated_role = await storage.roles.update(role_id, updates)
    return await _build_role_detail_response(updated_role, storage)


@router.delete(
    "/roles/{role_id}",
    operation_id="deleteRole",
    summary="Delete a role",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
async def delete_role(
    request: Request,
    role_id: str,
    user: CurrentUser,
) -> None:
    """Delete a custom role.

    Only admins can delete roles.
    System roles (Admin, Editor, Viewer) cannot be deleted.
    Roles with assigned users cannot be deleted.
    """
    storage = request.app.state.storage

    # Check if role exists
    role = await storage.roles.get(role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "ROLE_NOT_FOUND", "message": f"Role '{role_id}' not found"}},
        )

    # Cannot delete system roles
    if role.get("is_system", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": {"code": "SYSTEM_ROLE", "message": "System roles cannot be deleted"}},
        )

    # Check if role has users
    users, total = await storage.users.list(role_id=role_id, limit=1)
    if total > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": {
                    "code": "ROLE_IN_USE",
                    "message": f"Cannot delete role. It is assigned to {total} user(s).",
                }
            },
        )

    deleted = await storage.roles.delete(role_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": {"code": "DELETE_FAILED", "message": "Failed to delete role"}},
        )
