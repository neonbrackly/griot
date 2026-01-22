"""Team management API endpoints."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, Field

from griot_registry.auth import CurrentUser, require_admin

router = APIRouter(tags=["teams"])


# =============================================================================
# Request/Response Models
# =============================================================================


class TeamMemberResponse(BaseModel):
    """Team member response."""

    id: str
    user_id: str = Field(..., alias="userId")
    user_name: str = Field(..., alias="userName")
    user_email: str = Field(..., alias="userEmail")
    user_avatar: str | None = Field(None, alias="userAvatar")
    role_id: str = Field(..., alias="roleId")
    role_name: str = Field(..., alias="roleName")
    joined_at: datetime = Field(..., alias="joinedAt")

    model_config = {"populate_by_name": True}


class TeamResponse(BaseModel):
    """Team response."""

    id: str
    name: str
    description: str | None = None
    member_count: int = Field(..., alias="memberCount")
    domains: list[str] = []
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")

    model_config = {"populate_by_name": True}


class TeamDetailResponse(BaseModel):
    """Team detail response with members."""

    id: str
    name: str
    description: str | None = None
    member_count: int = Field(..., alias="memberCount")
    domains: list[str] = []
    members: list[TeamMemberResponse] = []
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")

    model_config = {"populate_by_name": True}


class TeamListResponse(BaseModel):
    """Team list response."""

    items: list[TeamResponse]
    total: int
    limit: int
    offset: int


class TeamCreateRequest(BaseModel):
    """Team create request."""

    name: str = Field(..., min_length=2, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    domains: list[str] = []

    model_config = {"populate_by_name": True}


class TeamUpdateRequest(BaseModel):
    """Team update request."""

    name: str | None = Field(default=None, min_length=2, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    domains: list[str] | None = None

    model_config = {"populate_by_name": True}


class TeamMemberAddRequest(BaseModel):
    """Add member to team request."""

    user_id: str = Field(..., alias="userId")
    role_id: str = Field(default="role-viewer", alias="roleId")

    model_config = {"populate_by_name": True}


class TeamMemberRoleUpdateRequest(BaseModel):
    """Update member role request."""

    role_id: str = Field(..., alias="roleId")

    model_config = {"populate_by_name": True}


# =============================================================================
# Helper Functions
# =============================================================================


def _utc_now() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(timezone.utc)


async def _build_team_response(team_doc: dict[str, Any]) -> TeamResponse:
    """Build team response."""
    return TeamResponse(
        id=team_doc["id"],
        name=team_doc["name"],
        description=team_doc.get("description"),
        member_count=team_doc.get("member_count", 0),
        domains=team_doc.get("domains", []),
        created_at=team_doc["created_at"],
        updated_at=team_doc.get("updated_at", team_doc["created_at"]),
    )


async def _build_team_detail_response(
    team_doc: dict[str, Any],
    storage: Any,
) -> TeamDetailResponse:
    """Build team detail response with members."""
    # Get members
    members = team_doc.get("members", [])
    member_responses = []

    for member in members:
        user = await storage.users.get(member["user_id"])
        role = await storage.roles.get(member.get("role_id", "role-viewer"))

        if user:
            member_responses.append(TeamMemberResponse(
                id=member.get("id", f"{team_doc['id']}-{member['user_id']}"),
                user_id=member["user_id"],
                user_name=user["name"],
                user_email=user["email"],
                user_avatar=user.get("avatar"),
                role_id=role["id"] if role else "role-viewer",
                role_name=role["name"] if role else "Viewer",
                joined_at=member.get("joined_at", team_doc["created_at"]),
            ))

    return TeamDetailResponse(
        id=team_doc["id"],
        name=team_doc["name"],
        description=team_doc.get("description"),
        member_count=len(member_responses),
        domains=team_doc.get("domains", []),
        members=member_responses,
        created_at=team_doc["created_at"],
        updated_at=team_doc.get("updated_at", team_doc["created_at"]),
    )


# =============================================================================
# Team Endpoints
# =============================================================================


@router.get(
    "/teams",
    operation_id="listTeams",
    summary="List all teams",
    response_model=TeamListResponse,
)
async def list_teams(
    request: Request,
    user: CurrentUser,
    search: Annotated[str | None, Query(description="Search by team name")] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> TeamListResponse:
    """List all teams with optional search."""
    storage = request.app.state.storage

    teams, total = await storage.teams.list(
        search=search,
        limit=limit,
        offset=offset,
    )

    items = [await _build_team_response(t) for t in teams]

    return TeamListResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post(
    "/teams",
    operation_id="createTeam",
    summary="Create a new team",
    response_model=TeamDetailResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
async def create_team(
    request: Request,
    user: CurrentUser,
    body: TeamCreateRequest,
) -> TeamDetailResponse:
    """Create a new team.

    Only admins can create teams.
    """
    storage = request.app.state.storage

    team_doc = {
        "name": body.name,
        "description": body.description,
        "domains": body.domains,
        "members": [],
        "member_count": 0,
    }

    team = await storage.teams.create(team_doc)
    return await _build_team_detail_response(team, storage)


@router.get(
    "/teams/{team_id}",
    operation_id="getTeam",
    summary="Get team by ID",
    response_model=TeamDetailResponse,
)
async def get_team(
    request: Request,
    team_id: str,
    user: CurrentUser,
) -> TeamDetailResponse:
    """Get a specific team with members."""
    storage = request.app.state.storage

    team = await storage.teams.get(team_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "TEAM_NOT_FOUND", "message": f"Team '{team_id}' not found"}},
        )

    return await _build_team_detail_response(team, storage)


@router.patch(
    "/teams/{team_id}",
    operation_id="updateTeam",
    summary="Update team",
    response_model=TeamDetailResponse,
    dependencies=[Depends(require_admin)],
)
async def update_team(
    request: Request,
    team_id: str,
    user: CurrentUser,
    body: TeamUpdateRequest,
) -> TeamDetailResponse:
    """Update a team.

    Only admins can update teams.
    """
    storage = request.app.state.storage

    # Check if team exists
    team = await storage.teams.get(team_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "TEAM_NOT_FOUND", "message": f"Team '{team_id}' not found"}},
        )

    # Build update dict
    updates: dict[str, Any] = {"updated_at": _utc_now()}
    if body.name is not None:
        updates["name"] = body.name
    if body.description is not None:
        updates["description"] = body.description
    if body.domains is not None:
        updates["domains"] = body.domains

    updated_team = await storage.teams.update(team_id, updates)
    return await _build_team_detail_response(updated_team, storage)


@router.delete(
    "/teams/{team_id}",
    operation_id="deleteTeam",
    summary="Delete team",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
async def delete_team(
    request: Request,
    team_id: str,
    user: CurrentUser,
) -> None:
    """Delete a team.

    Only admins can delete teams.
    Cannot delete teams that have members.
    """
    storage = request.app.state.storage

    # Check if team exists
    team = await storage.teams.get(team_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "TEAM_NOT_FOUND", "message": f"Team '{team_id}' not found"}},
        )

    # Check if team has members
    if team.get("members") and len(team["members"]) > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": {
                    "code": "TEAM_HAS_MEMBERS",
                    "message": "Cannot delete team with members. Remove all members first.",
                }
            },
        )

    deleted = await storage.teams.delete(team_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": {"code": "DELETE_FAILED", "message": "Failed to delete team"}},
        )


# =============================================================================
# Team Member Endpoints
# =============================================================================


@router.post(
    "/teams/{team_id}/members",
    operation_id="addTeamMember",
    summary="Add member to team",
    response_model=TeamDetailResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
async def add_team_member(
    request: Request,
    team_id: str,
    user: CurrentUser,
    body: TeamMemberAddRequest,
) -> TeamDetailResponse:
    """Add a member to a team.

    Only admins can add members.
    """
    storage = request.app.state.storage

    # Check if team exists
    team = await storage.teams.get(team_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "TEAM_NOT_FOUND", "message": f"Team '{team_id}' not found"}},
        )

    # Check if user exists
    target_user = await storage.users.get(body.user_id)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "USER_NOT_FOUND", "message": f"User '{body.user_id}' not found"}},
        )

    # Validate role
    role = await storage.roles.get(body.role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "INVALID_ROLE", "message": f"Role '{body.role_id}' not found"}},
        )

    # Check if user is already a member
    members = team.get("members", [])
    if any(m["user_id"] == body.user_id for m in members):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": {"code": "ALREADY_MEMBER", "message": "User is already a member of this team"}},
        )

    updated_team = await storage.teams.add_member(team_id, body.user_id, body.role_id)

    # Also update user's team_id
    await storage.users.update(body.user_id, {"team_id": team_id})

    return await _build_team_detail_response(updated_team, storage)


@router.patch(
    "/teams/{team_id}/members/{member_user_id}/role",
    operation_id="updateTeamMemberRole",
    summary="Update member's role in team",
    response_model=TeamDetailResponse,
    dependencies=[Depends(require_admin)],
)
async def update_team_member_role(
    request: Request,
    team_id: str,
    member_user_id: str,
    user: CurrentUser,
    body: TeamMemberRoleUpdateRequest,
) -> TeamDetailResponse:
    """Update a member's role in a team.

    Only admins can update member roles.
    """
    storage = request.app.state.storage

    # Check if team exists
    team = await storage.teams.get(team_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "TEAM_NOT_FOUND", "message": f"Team '{team_id}' not found"}},
        )

    # Check if user is a member
    members = team.get("members", [])
    if not any(m["user_id"] == member_user_id for m in members):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_A_MEMBER", "message": "User is not a member of this team"}},
        )

    # Validate role
    role = await storage.roles.get(body.role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "INVALID_ROLE", "message": f"Role '{body.role_id}' not found"}},
        )

    updated_team = await storage.teams.update_member_role(team_id, member_user_id, body.role_id)
    return await _build_team_detail_response(updated_team, storage)


@router.delete(
    "/teams/{team_id}/members/{member_user_id}",
    operation_id="removeTeamMember",
    summary="Remove member from team",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
async def remove_team_member(
    request: Request,
    team_id: str,
    member_user_id: str,
    user: CurrentUser,
) -> None:
    """Remove a member from a team.

    Only admins can remove members.
    """
    storage = request.app.state.storage

    # Check if team exists
    team = await storage.teams.get(team_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "TEAM_NOT_FOUND", "message": f"Team '{team_id}' not found"}},
        )

    # Check if user is a member
    members = team.get("members", [])
    if not any(m["user_id"] == member_user_id for m in members):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_A_MEMBER", "message": "User is not a member of this team"}},
        )

    removed = await storage.teams.remove_member(team_id, member_user_id)
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": {"code": "REMOVE_FAILED", "message": "Failed to remove member"}},
        )

    # Also clear user's team_id
    await storage.users.update(member_user_id, {"team_id": None})
