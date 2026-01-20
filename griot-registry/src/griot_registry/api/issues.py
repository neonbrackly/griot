"""Issue management endpoints.

Provides endpoints for tracking and managing contract issues.
"""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Any

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from griot_registry.api.dependencies import Storage
from griot_registry.auth import CurrentUser, OptionalUser

router = APIRouter()


# =============================================================================
# Request/Response Models
# =============================================================================


class IssueCreateRequest(BaseModel):
    """Request to create an issue."""

    contract_id: str
    run_id: str | None = None
    title: str
    description: str | None = None
    severity: str = Field(
        default="warning",
        description="Severity: error, warning, info",
    )
    category: str | None = Field(
        default=None,
        description="Issue category: quality, schema, sla, compliance",
    )
    affected_field: str | None = None
    affected_schema: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class IssueUpdateRequest(BaseModel):
    """Request to update an issue."""

    title: str | None = None
    description: str | None = None
    severity: str | None = None
    status: str | None = None
    assignee: str | None = None


class IssueResolveRequest(BaseModel):
    """Request to resolve an issue."""

    resolution: str = Field(..., description="Resolution description")


class Issue(BaseModel):
    """An issue record."""

    id: str
    contract_id: str
    run_id: str | None = None
    title: str
    description: str | None = None
    severity: str
    category: str | None = None
    status: str
    affected_field: str | None = None
    affected_schema: str | None = None
    assignee: str | None = None
    resolution: str | None = None
    resolved_by: str | None = None
    resolved_at: datetime | None = None
    created_at: datetime
    updated_at: datetime | None = None
    created_by: str | None = None


class IssueListResponse(BaseModel):
    """Response for listing issues."""

    items: list[Issue]
    total: int
    limit: int
    offset: int


# =============================================================================
# Endpoints
# =============================================================================


@router.post(
    "/issues",
    operation_id="createIssue",
    summary="Create an issue",
    status_code=status.HTTP_201_CREATED,
    response_model=Issue,
)
async def create_issue(
    request: IssueCreateRequest,
    storage: Storage,
    user: CurrentUser,
) -> Issue:
    """Create a new issue.

    Issues track problems found during validation runs or manual review.
    """
    issue = await storage.issues.create({
        "contract_id": request.contract_id,
        "run_id": request.run_id,
        "title": request.title,
        "description": request.description,
        "severity": request.severity,
        "category": request.category,
        "affected_field": request.affected_field,
        "affected_schema": request.affected_schema,
        "metadata": request.metadata,
        "created_by": user.id,
    })

    return Issue(
        id=issue["id"],
        contract_id=issue["contract_id"],
        run_id=issue.get("run_id"),
        title=issue["title"],
        description=issue.get("description"),
        severity=issue["severity"],
        category=issue.get("category"),
        status=issue["status"],
        affected_field=issue.get("affected_field"),
        affected_schema=issue.get("affected_schema"),
        assignee=issue.get("assignee"),
        resolution=issue.get("resolution"),
        resolved_by=issue.get("resolved_by"),
        resolved_at=issue.get("resolved_at"),
        created_at=issue["created_at"],
        updated_at=issue.get("updated_at"),
        created_by=issue.get("created_by"),
    )


@router.get(
    "/issues/{issue_id}",
    operation_id="getIssue",
    summary="Get an issue",
    response_model=Issue,
    responses={404: {"description": "Issue not found"}},
)
async def get_issue(
    issue_id: str,
    storage: Storage,
    user: OptionalUser,
) -> Issue:
    """Get an issue by ID."""
    issue = await storage.issues.get(issue_id)

    if issue is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": f"Issue '{issue_id}' not found"},
        )

    return Issue(
        id=issue["id"],
        contract_id=issue["contract_id"],
        run_id=issue.get("run_id"),
        title=issue["title"],
        description=issue.get("description"),
        severity=issue["severity"],
        category=issue.get("category"),
        status=issue["status"],
        affected_field=issue.get("affected_field"),
        affected_schema=issue.get("affected_schema"),
        assignee=issue.get("assignee"),
        resolution=issue.get("resolution"),
        resolved_by=issue.get("resolved_by"),
        resolved_at=issue.get("resolved_at"),
        created_at=issue["created_at"],
        updated_at=issue.get("updated_at"),
        created_by=issue.get("created_by"),
    )


@router.patch(
    "/issues/{issue_id}",
    operation_id="updateIssue",
    summary="Update an issue",
    response_model=Issue,
    responses={404: {"description": "Issue not found"}},
)
async def update_issue(
    issue_id: str,
    request: IssueUpdateRequest,
    storage: Storage,
    user: CurrentUser,
) -> Issue:
    """Update an issue."""
    updates = request.model_dump(exclude_unset=True)
    updates["updated_by"] = user.id

    try:
        issue = await storage.issues.update(issue_id, updates)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": str(e)},
        )

    return Issue(
        id=issue["id"],
        contract_id=issue["contract_id"],
        run_id=issue.get("run_id"),
        title=issue["title"],
        description=issue.get("description"),
        severity=issue["severity"],
        category=issue.get("category"),
        status=issue["status"],
        affected_field=issue.get("affected_field"),
        affected_schema=issue.get("affected_schema"),
        assignee=issue.get("assignee"),
        resolution=issue.get("resolution"),
        resolved_by=issue.get("resolved_by"),
        resolved_at=issue.get("resolved_at"),
        created_at=issue["created_at"],
        updated_at=issue.get("updated_at"),
        created_by=issue.get("created_by"),
    )


@router.post(
    "/issues/{issue_id}/resolve",
    operation_id="resolveIssue",
    summary="Resolve an issue",
    response_model=Issue,
    responses={404: {"description": "Issue not found"}},
)
async def resolve_issue(
    issue_id: str,
    request: IssueResolveRequest,
    storage: Storage,
    user: CurrentUser,
) -> Issue:
    """Mark an issue as resolved."""
    try:
        issue = await storage.issues.resolve(
            issue_id=issue_id,
            resolution=request.resolution,
            resolved_by=user.id,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": str(e)},
        )

    return Issue(
        id=issue["id"],
        contract_id=issue["contract_id"],
        run_id=issue.get("run_id"),
        title=issue["title"],
        description=issue.get("description"),
        severity=issue["severity"],
        category=issue.get("category"),
        status=issue["status"],
        affected_field=issue.get("affected_field"),
        affected_schema=issue.get("affected_schema"),
        assignee=issue.get("assignee"),
        resolution=issue.get("resolution"),
        resolved_by=issue.get("resolved_by"),
        resolved_at=issue.get("resolved_at"),
        created_at=issue["created_at"],
        updated_at=issue.get("updated_at"),
        created_by=issue.get("created_by"),
    )


@router.get(
    "/issues",
    operation_id="listIssues",
    summary="List issues",
    response_model=IssueListResponse,
)
async def list_issues(
    storage: Storage,
    user: OptionalUser,
    contract_id: str | None = Query(default=None, description="Filter by contract ID"),
    run_id: str | None = Query(default=None, description="Filter by run ID"),
    status_filter: str | None = Query(
        default=None,
        alias="status",
        description="Filter by status: open, resolved",
    ),
    severity: str | None = Query(
        default=None,
        description="Filter by severity: error, warning, info",
    ),
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> IssueListResponse:
    """List issues with optional filtering."""
    issues, total = await storage.issues.list(
        contract_id=contract_id,
        run_id=run_id,
        status=status_filter,
        severity=severity,
        limit=limit,
        offset=offset,
    )

    return IssueListResponse(
        items=[
            Issue(
                id=i["id"],
                contract_id=i["contract_id"],
                run_id=i.get("run_id"),
                title=i["title"],
                description=i.get("description"),
                severity=i["severity"],
                category=i.get("category"),
                status=i["status"],
                affected_field=i.get("affected_field"),
                affected_schema=i.get("affected_schema"),
                assignee=i.get("assignee"),
                resolution=i.get("resolution"),
                resolved_by=i.get("resolved_by"),
                resolved_at=i.get("resolved_at"),
                created_at=i["created_at"],
                updated_at=i.get("updated_at"),
                created_by=i.get("created_by"),
            )
            for i in issues
        ],
        total=total,
        limit=limit,
        offset=offset,
    )
