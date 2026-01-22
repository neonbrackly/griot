"""User management API endpoints."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, EmailStr, Field

from griot_registry.auth import CurrentUser, require_admin

router = APIRouter(tags=["users"])


# =============================================================================
# Request/Response Models
# =============================================================================


class RoleRef(BaseModel):
    """Role reference in user response."""

    id: str
    name: str


class TeamRef(BaseModel):
    """Team reference in user response."""

    id: str
    name: str


class UserResponse(BaseModel):
    """User response."""

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


class UserListResponse(BaseModel):
    """User list response."""

    items: list[UserResponse]
    total: int
    limit: int
    offset: int


class UserInviteRequest(BaseModel):
    """User invite request."""

    email: EmailStr
    name: str = Field(..., min_length=2, max_length=100)
    role_id: str = Field(default="role-viewer", alias="roleId")
    team_id: str | None = Field(default=None, alias="teamId")
    send_invite: bool = Field(default=True, alias="sendInvite")

    model_config = {"populate_by_name": True}


class UserUpdateRequest(BaseModel):
    """User update request."""

    name: str | None = Field(default=None, min_length=2, max_length=100)
    avatar: str | None = None
    role_id: str | None = Field(default=None, alias="roleId")
    team_id: str | None = Field(default=None, alias="teamId")

    model_config = {"populate_by_name": True}


class UserRoleChangeRequest(BaseModel):
    """User role change request."""

    role_id: str = Field(..., alias="roleId")

    model_config = {"populate_by_name": True}


class MessageResponse(BaseModel):
    """Simple message response."""

    message: str


# =============================================================================
# Helper Functions
# =============================================================================


def _utc_now() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(timezone.utc)


async def _build_user_response(
    user_doc: dict[str, Any],
    storage: Any,
) -> UserResponse:
    """Build user response with role and team data."""
    # Get role
    role = await storage.roles.get(user_doc.get("role_id", "role-viewer"))
    if not role:
        role = {"id": "role-viewer", "name": "Viewer"}

    # Get team
    team = None
    if user_doc.get("team_id"):
        team = await storage.teams.get(user_doc["team_id"])

    return UserResponse(
        id=user_doc["id"],
        name=user_doc["name"],
        email=user_doc["email"],
        avatar=user_doc.get("avatar"),
        role=RoleRef(id=role["id"], name=role["name"]),
        team=TeamRef(id=team["id"], name=team["name"]) if team else None,
        status=user_doc.get("status", "active"),
        last_login_at=user_doc.get("last_login_at"),
        created_at=user_doc["created_at"],
    )


# =============================================================================
# User Endpoints
# =============================================================================


@router.get(
    "/users",
    operation_id="listUsers",
    summary="List all users",
    response_model=UserListResponse,
)
async def list_users(
    request: Request,
    user: CurrentUser,
    search: Annotated[str | None, Query(description="Search by name or email")] = None,
    role_id: Annotated[str | None, Query(alias="roleId", description="Filter by role")] = None,
    team_id: Annotated[str | None, Query(alias="teamId", description="Filter by team")] = None,
    status: Annotated[str | None, Query(description="Filter by status")] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> UserListResponse:
    """List all users with optional filtering."""
    storage = request.app.state.storage

    users, total = await storage.users.list(
        search=search,
        role_id=role_id,
        team_id=team_id,
        status=status,
        limit=limit,
        offset=offset,
    )

    # Build responses with role and team data
    items = [await _build_user_response(u, storage) for u in users]

    return UserListResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post(
    "/users/invite",
    operation_id="inviteUser",
    summary="Invite a new user",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
async def invite_user(
    request: Request,
    user: CurrentUser,
    body: UserInviteRequest,
) -> UserResponse:
    """Invite a new user to the system.

    Only admins can invite users.
    """
    storage = request.app.state.storage

    # Check if email already exists
    existing = await storage.users.get_by_email(body.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": {"code": "EMAIL_EXISTS", "message": "A user with this email already exists"}},
        )

    # Validate role exists
    role = await storage.roles.get(body.role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "INVALID_ROLE", "message": f"Role '{body.role_id}' not found"}},
        )

    # Validate team exists (if provided)
    if body.team_id:
        team = await storage.teams.get(body.team_id)
        if not team:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": {"code": "INVALID_TEAM", "message": f"Team '{body.team_id}' not found"}},
            )

    # Create user with pending status (no password yet)
    user_doc = {
        "name": body.name,
        "email": body.email,
        "password_hash": None,  # Will be set when user accepts invite
        "role_id": body.role_id,
        "team_id": body.team_id,
        "status": "pending",  # Pending until invite accepted
        "avatar": None,
        "invited_by": user.id,
        "invited_at": _utc_now(),
    }

    new_user = await storage.users.create(user_doc)

    # TODO: Send invite email if send_invite is True

    return await _build_user_response(new_user, storage)


@router.get(
    "/users/{user_id}",
    operation_id="getUser",
    summary="Get user by ID",
    response_model=UserResponse,
)
async def get_user(
    request: Request,
    user_id: str,
    user: CurrentUser,
) -> UserResponse:
    """Get a specific user by ID."""
    storage = request.app.state.storage

    user_doc = await storage.users.get(user_id)
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "USER_NOT_FOUND", "message": f"User '{user_id}' not found"}},
        )

    return await _build_user_response(user_doc, storage)


@router.patch(
    "/users/{user_id}",
    operation_id="updateUser",
    summary="Update user",
    response_model=UserResponse,
)
async def update_user(
    request: Request,
    user_id: str,
    user: CurrentUser,
    body: UserUpdateRequest,
) -> UserResponse:
    """Update a user's profile.

    Users can update their own profile. Admins can update any user.
    """
    storage = request.app.state.storage

    # Check if user exists
    user_doc = await storage.users.get(user_id)
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "USER_NOT_FOUND", "message": f"User '{user_id}' not found"}},
        )

    # Check authorization
    is_admin = any(r.value == "admin" for r in user.roles)
    is_self = user.id == user_id

    if not is_admin and not is_self:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": {"code": "NOT_AUTHORIZED", "message": "You can only update your own profile"}},
        )

    # Non-admins cannot change their own role
    if not is_admin and body.role_id is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": {"code": "NOT_AUTHORIZED", "message": "Only admins can change user roles"}},
        )

    # Build update dict
    updates: dict[str, Any] = {}
    if body.name is not None:
        updates["name"] = body.name
    if body.avatar is not None:
        updates["avatar"] = body.avatar
    if body.role_id is not None:
        # Validate role
        role = await storage.roles.get(body.role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": {"code": "INVALID_ROLE", "message": f"Role '{body.role_id}' not found"}},
            )
        updates["role_id"] = body.role_id
    if body.team_id is not None:
        # Validate team
        if body.team_id != "":
            team = await storage.teams.get(body.team_id)
            if not team:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={"error": {"code": "INVALID_TEAM", "message": f"Team '{body.team_id}' not found"}},
                )
        updates["team_id"] = body.team_id if body.team_id != "" else None

    if not updates:
        return await _build_user_response(user_doc, storage)

    updated_user = await storage.users.update(user_id, updates)
    return await _build_user_response(updated_user, storage)


@router.post(
    "/users/{user_id}/deactivate",
    operation_id="deactivateUser",
    summary="Deactivate user",
    response_model=UserResponse,
    dependencies=[Depends(require_admin)],
)
async def deactivate_user(
    request: Request,
    user_id: str,
    user: CurrentUser,
) -> UserResponse:
    """Deactivate a user account.

    Only admins can deactivate users.
    Deactivated users cannot log in but their data is preserved.
    """
    storage = request.app.state.storage

    # Check if user exists
    user_doc = await storage.users.get(user_id)
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "USER_NOT_FOUND", "message": f"User '{user_id}' not found"}},
        )

    # Cannot deactivate yourself
    if user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "CANNOT_DEACTIVATE_SELF", "message": "You cannot deactivate your own account"}},
        )

    updated_user = await storage.users.update(user_id, {
        "status": "deactivated",
        "deactivated_at": _utc_now(),
        "deactivated_by": user.id,
    })

    return await _build_user_response(updated_user, storage)


@router.post(
    "/users/{user_id}/reactivate",
    operation_id="reactivateUser",
    summary="Reactivate user",
    response_model=UserResponse,
    dependencies=[Depends(require_admin)],
)
async def reactivate_user(
    request: Request,
    user_id: str,
    user: CurrentUser,
) -> UserResponse:
    """Reactivate a deactivated user account.

    Only admins can reactivate users.
    """
    storage = request.app.state.storage

    # Check if user exists
    user_doc = await storage.users.get(user_id)
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "USER_NOT_FOUND", "message": f"User '{user_id}' not found"}},
        )

    if user_doc.get("status") != "deactivated":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "USER_NOT_DEACTIVATED", "message": "User is not deactivated"}},
        )

    updated_user = await storage.users.update(user_id, {
        "status": "active",
        "deactivated_at": None,
        "deactivated_by": None,
    })

    return await _build_user_response(updated_user, storage)


@router.post(
    "/users/{user_id}/role",
    operation_id="changeUserRole",
    summary="Change user role",
    response_model=UserResponse,
    dependencies=[Depends(require_admin)],
)
async def change_user_role(
    request: Request,
    user_id: str,
    user: CurrentUser,
    body: UserRoleChangeRequest,
) -> UserResponse:
    """Change a user's role.

    Only admins can change user roles.
    """
    storage = request.app.state.storage

    # Check if user exists
    user_doc = await storage.users.get(user_id)
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "USER_NOT_FOUND", "message": f"User '{user_id}' not found"}},
        )

    # Validate role
    role = await storage.roles.get(body.role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "INVALID_ROLE", "message": f"Role '{body.role_id}' not found"}},
        )

    updated_user = await storage.users.update(user_id, {"role_id": body.role_id})
    return await _build_user_response(updated_user, storage)
