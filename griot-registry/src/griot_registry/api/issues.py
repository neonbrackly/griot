"""Issue management endpoints.

Provides endpoints for tracking and managing contract issues.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated, Any

from fastapi import APIRouter, HTTPException, Query, Request, status
from pydantic import BaseModel, Field

from griot_registry.api.dependencies import Storage
from griot_registry.auth import CurrentUser, OptionalUser

router = APIRouter()


# =============================================================================
# Request/Response Models
# =============================================================================


class IssueCreateRequest(BaseModel):
    """Request to create an issue."""

    contract_id: str = Field(..., alias="contractId")
    run_id: str | None = Field(None, alias="runId")
    title: str
    description: str | None = None
    severity: str = Field(
        default="warning",
        description="Severity: critical, warning, info",
    )
    category: str | None = Field(
        default=None,
        description="Issue category: pii_exposure, schema_drift, sla_breach, quality_failure, other",
    )
    table: str | None = None
    field: str | None = None
    quality_rule_id: str | None = Field(None, alias="qualityRuleId")
    assigned_team: str | None = Field(None, alias="assignedTeam")
    assigned_user: str | None = Field(None, alias="assignedUser")
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = {"populate_by_name": True}


class IssueUpdateRequest(BaseModel):
    """Request to update an issue."""

    status: str | None = None
    assigned_team: str | None = Field(None, alias="assignedTeam")
    assigned_user: str | None = Field(None, alias="assignedUser")
    resolution: str | None = None
    resolution_notes: str | None = Field(None, alias="resolutionNotes")
    tags: list[str] | None = None

    model_config = {"populate_by_name": True}


class IssueResolveRequest(BaseModel):
    """Request to resolve an issue."""

    resolution: str = Field(..., description="Resolution type: fixed, wont_fix, false_positive, deferred")
    resolution_notes: str | None = Field(None, alias="resolutionNotes", description="Resolution notes")

    model_config = {"populate_by_name": True}


class ContractRef(BaseModel):
    """Contract reference in issue."""

    id: str
    name: str
    version: str
    status: str
    owner_team: str | None = Field(None, alias="ownerTeam")
    owner_team_name: str | None = Field(None, alias="ownerTeamName")

    model_config = {"populate_by_name": True}


class LocationInfo(BaseModel):
    """Issue location info."""

    table: str | None = None
    field: str | None = None
    physical_table: str | None = Field(None, alias="physicalTable")
    physical_column: str | None = Field(None, alias="physicalColumn")

    model_config = {"populate_by_name": True}


class QualityRuleInfo(BaseModel):
    """Quality rule info in issue."""

    id: str
    name: str
    type: str
    threshold: float | None = None
    actual_value: float | None = Field(None, alias="actualValue")
    last_run_at: datetime | None = Field(None, alias="lastRunAt")

    model_config = {"populate_by_name": True}


class AssignmentInfo(BaseModel):
    """Assignment info in issue."""

    team_id: str | None = Field(None, alias="teamId")
    team_name: str | None = Field(None, alias="teamName")
    user_id: str | None = Field(None, alias="userId")
    user_name: str | None = Field(None, alias="userName")
    assigned_at: datetime | None = Field(None, alias="assignedAt")
    assigned_by: str | None = Field(None, alias="assignedBy")

    model_config = {"populate_by_name": True}


class TimelineInfo(BaseModel):
    """Issue timeline info."""

    detected_at: datetime = Field(..., alias="detectedAt")
    acknowledged_at: datetime | None = Field(None, alias="acknowledgedAt")
    in_progress_at: datetime | None = Field(None, alias="inProgressAt")
    resolved_at: datetime | None = Field(None, alias="resolvedAt")
    resolution: str | None = None
    resolution_notes: str | None = Field(None, alias="resolutionNotes")
    resolved_by: str | None = Field(None, alias="resolvedBy")

    model_config = {"populate_by_name": True}


class ActivityEntry(BaseModel):
    """Issue activity entry."""

    id: str
    type: str
    description: str
    actor_id: str = Field(..., alias="actorId")
    actor_name: str = Field(..., alias="actorName")
    created_at: datetime = Field(..., alias="createdAt")

    model_config = {"populate_by_name": True}


class CommentEntry(BaseModel):
    """Issue comment entry."""

    id: str
    content: str
    author_id: str = Field(..., alias="authorId")
    author_name: str = Field(..., alias="authorName")
    author_avatar: str | None = Field(None, alias="authorAvatar")
    created_at: datetime = Field(..., alias="createdAt")

    model_config = {"populate_by_name": True}


class Issue(BaseModel):
    """An issue record."""

    id: str
    title: str
    description: str | None = None
    severity: str
    category: str | None = None
    status: str
    contract_id: str = Field(..., alias="contractId")
    contract_name: str | None = Field(None, alias="contractName")
    contract_version: str | None = Field(None, alias="contractVersion")
    table: str | None = None
    field: str | None = None
    quality_rule_id: str | None = Field(None, alias="qualityRuleId")
    assigned_team: str | None = Field(None, alias="assignedTeam")
    assigned_team_name: str | None = Field(None, alias="assignedTeamName")
    assigned_user: str | None = Field(None, alias="assignedUser")
    assigned_user_name: str | None = Field(None, alias="assignedUserName")
    detected_at: datetime = Field(..., alias="detectedAt")
    acknowledged_at: datetime | None = Field(None, alias="acknowledgedAt")
    resolved_at: datetime | None = Field(None, alias="resolvedAt")
    resolution: str | None = None
    resolution_notes: str | None = Field(None, alias="resolutionNotes")
    resolved_by: str | None = Field(None, alias="resolvedBy")
    tags: list[str] = []
    run_id: str | None = Field(None, alias="runId")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime | None = Field(None, alias="updatedAt")

    model_config = {"populate_by_name": True}


class IssueDetail(BaseModel):
    """Detailed issue response."""

    id: str
    title: str
    description: str | None = None
    severity: str
    category: str | None = None
    status: str
    contract: ContractRef | None = None
    location: LocationInfo | None = None
    quality_rule: QualityRuleInfo | None = Field(None, alias="qualityRule")
    assignment: AssignmentInfo | None = None
    timeline: TimelineInfo | None = None
    activity: list[ActivityEntry] = []
    comments: list[CommentEntry] = []
    metadata: dict[str, Any] = {}
    tags: list[str] = []
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime | None = Field(None, alias="updatedAt")

    model_config = {"populate_by_name": True}


class IssueSummary(BaseModel):
    """Issue count summary."""

    critical: int = 0
    warning: int = 0
    info: int = 0
    open: int = 0
    in_progress: int = Field(0, alias="inProgress")
    resolved: int = 0
    ignored: int = 0

    model_config = {"populate_by_name": True}


class IssueListResponse(BaseModel):
    """Response for listing issues."""

    items: list[Issue]
    pagination: dict[str, Any]
    summary: IssueSummary


# =============================================================================
# Helper Functions
# =============================================================================


def _utc_now() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(timezone.utc)


def _build_issue_from_doc(doc: dict[str, Any]) -> Issue:
    """Build Issue model from document."""
    return Issue(
        id=doc["id"],
        title=doc["title"],
        description=doc.get("description"),
        severity=doc.get("severity", "warning"),
        category=doc.get("category"),
        status=doc.get("status", "open"),
        contract_id=doc["contract_id"],
        contract_name=doc.get("contract_name"),
        contract_version=doc.get("contract_version"),
        table=doc.get("table"),
        field=doc.get("field"),
        quality_rule_id=doc.get("quality_rule_id"),
        assigned_team=doc.get("assigned_team"),
        assigned_team_name=doc.get("assigned_team_name"),
        assigned_user=doc.get("assigned_user"),
        assigned_user_name=doc.get("assigned_user_name"),
        detected_at=doc.get("detected_at") or doc.get("created_at"),
        acknowledged_at=doc.get("acknowledged_at"),
        resolved_at=doc.get("resolved_at"),
        resolution=doc.get("resolution"),
        resolution_notes=doc.get("resolution_notes"),
        resolved_by=doc.get("resolved_by"),
        tags=doc.get("tags", []),
        run_id=doc.get("run_id"),
        created_at=doc["created_at"],
        updated_at=doc.get("updated_at"),
    )


# =============================================================================
# Endpoints
# =============================================================================


@router.get(
    "/issues",
    operation_id="listIssues",
    summary="List issues with filtering",
    response_model=IssueListResponse,
)
async def list_issues(
    request: Request,
    storage: Storage,
    user: OptionalUser,
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    severity: str | None = Query(default=None, description="Filter by severity: critical, warning, info"),
    status_filter: str | None = Query(default=None, alias="status", description="Filter by status: open, in_progress, resolved, ignored"),
    category: str | None = Query(default=None, description="Filter by category: pii_exposure, schema_drift, sla_breach, quality_failure, other"),
    contract_id: str | None = Query(default=None, alias="contractId", description="Filter by contract ID"),
    assigned_team: str | None = Query(default=None, alias="assignedTeam", description="Filter by assigned team"),
    assigned_user: str | None = Query(default=None, alias="assignedUser", description="Filter by assigned user"),
    search: str | None = Query(default=None, description="Search in title, description, contract name"),
    detected_after: datetime | None = Query(default=None, alias="detectedAfter", description="Issues detected after this date"),
    detected_before: datetime | None = Query(default=None, alias="detectedBefore", description="Issues detected before this date"),
    sort_by: str = Query(default="detected_at", alias="sortBy", description="Sort field: detected_at, severity, status"),
    sort_order: str = Query(default="desc", alias="sortOrder", description="Sort order: asc, desc"),
) -> IssueListResponse:
    """List issues with filtering, pagination, and summary counts."""
    offset = (page - 1) * limit

    issues, total = await storage.issues.list(
        contract_id=contract_id,
        status=status_filter,
        severity=severity,
        limit=limit,
        offset=offset,
    )

    # Enrich issues with contract and user info
    items = []
    for issue_doc in issues:
        # Get contract info
        contract = await storage.contracts.get(issue_doc["contract_id"])
        if contract:
            issue_doc["contract_name"] = contract.to_dict().get("name", "Unknown")
            issue_doc["contract_version"] = contract.to_dict().get("version", "1.0.0")

        # Get team name
        if issue_doc.get("assigned_team"):
            team = await storage.teams.get(issue_doc["assigned_team"])
            if team:
                issue_doc["assigned_team_name"] = team.get("name")

        # Get user name
        if issue_doc.get("assigned_user"):
            user_doc = await storage.users.get(issue_doc["assigned_user"])
            if user_doc:
                issue_doc["assigned_user_name"] = user_doc.get("name")

        items.append(_build_issue_from_doc(issue_doc))

    # Calculate summary counts (simplified - in production, this should be a separate query)
    summary = IssueSummary(
        critical=sum(1 for i in items if i.severity == "critical"),
        warning=sum(1 for i in items if i.severity == "warning"),
        info=sum(1 for i in items if i.severity == "info"),
        open=sum(1 for i in items if i.status == "open"),
        in_progress=sum(1 for i in items if i.status == "in_progress"),
        resolved=sum(1 for i in items if i.status == "resolved"),
        ignored=sum(1 for i in items if i.status == "ignored"),
    )

    return IssueListResponse(
        items=items,
        pagination={
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit,
        },
        summary=summary,
    )


@router.post(
    "/issues",
    operation_id="createIssue",
    summary="Create an issue",
    status_code=status.HTTP_201_CREATED,
    response_model=Issue,
)
async def create_issue(
    request_body: IssueCreateRequest,
    request: Request,
    storage: Storage,
    user: CurrentUser,
) -> Issue:
    """Create a new issue.

    Issues track problems found during validation runs or manual review.
    """
    now = _utc_now()

    issue_doc = {
        "contract_id": request_body.contract_id,
        "run_id": request_body.run_id,
        "title": request_body.title,
        "description": request_body.description,
        "severity": request_body.severity,
        "category": request_body.category,
        "table": request_body.table,
        "field": request_body.field,
        "quality_rule_id": request_body.quality_rule_id,
        "assigned_team": request_body.assigned_team,
        "assigned_user": request_body.assigned_user,
        "status": "open",
        "detected_at": now,
        "metadata": request_body.metadata,
        "created_by": user.id,
        "tags": [],
    }

    issue = await storage.issues.create(issue_doc)

    # Enrich with names
    if issue.get("assigned_team"):
        team = await storage.teams.get(issue["assigned_team"])
        if team:
            issue["assigned_team_name"] = team.get("name")

    if issue.get("assigned_user"):
        user_doc = await storage.users.get(issue["assigned_user"])
        if user_doc:
            issue["assigned_user_name"] = user_doc.get("name")

    return _build_issue_from_doc(issue)


@router.get(
    "/issues/{issue_id}",
    operation_id="getIssue",
    summary="Get issue detail",
    response_model=IssueDetail,
    responses={404: {"description": "Issue not found"}},
)
async def get_issue(
    issue_id: str,
    request: Request,
    storage: Storage,
    user: OptionalUser,
) -> IssueDetail:
    """Get detailed issue information including activity and comments."""
    issue = await storage.issues.get(issue_id)

    if issue is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "ISSUE_NOT_FOUND", "message": f"Issue '{issue_id}' not found"}},
        )

    # Get contract info
    contract_ref = None
    if issue.get("contract_id"):
        contract = await storage.contracts.get(issue["contract_id"])
        if contract:
            contract_dict = contract.to_dict()
            owner_team = None
            owner_team_name = None
            if contract_dict.get("owner_team"):
                team = await storage.teams.get(contract_dict["owner_team"])
                if team:
                    owner_team = team["id"]
                    owner_team_name = team.get("name")

            contract_ref = ContractRef(
                id=contract_dict["id"],
                name=contract_dict.get("name", "Unknown"),
                version=contract_dict.get("version", "1.0.0"),
                status=contract_dict.get("status", "draft"),
                owner_team=owner_team,
                owner_team_name=owner_team_name,
            )

    # Build location info
    location = None
    if issue.get("table") or issue.get("field"):
        location = LocationInfo(
            table=issue.get("table"),
            field=issue.get("field"),
            physical_table=issue.get("physical_table"),
            physical_column=issue.get("physical_column"),
        )

    # Build assignment info
    assignment = None
    team_name = None
    user_name = None

    if issue.get("assigned_team"):
        team = await storage.teams.get(issue["assigned_team"])
        if team:
            team_name = team.get("name")

    if issue.get("assigned_user"):
        user_doc = await storage.users.get(issue["assigned_user"])
        if user_doc:
            user_name = user_doc.get("name")

    if issue.get("assigned_team") or issue.get("assigned_user"):
        assignment = AssignmentInfo(
            team_id=issue.get("assigned_team"),
            team_name=team_name,
            user_id=issue.get("assigned_user"),
            user_name=user_name,
            assigned_at=issue.get("assigned_at"),
            assigned_by=issue.get("assigned_by"),
        )

    # Build timeline
    timeline = TimelineInfo(
        detected_at=issue.get("detected_at") or issue.get("created_at"),
        acknowledged_at=issue.get("acknowledged_at"),
        in_progress_at=issue.get("in_progress_at"),
        resolved_at=issue.get("resolved_at"),
        resolution=issue.get("resolution"),
        resolution_notes=issue.get("resolution_notes"),
        resolved_by=issue.get("resolved_by"),
    )

    # Build activity (simplified - would need activity tracking in storage)
    activity = [
        ActivityEntry(
            id=f"activity-{issue['id']}-1",
            type="issue_created",
            description="Issue detected by automated quality check",
            actor_id=issue.get("created_by") or "system",
            actor_name="System",
            created_at=issue.get("created_at"),
        )
    ]

    return IssueDetail(
        id=issue["id"],
        title=issue["title"],
        description=issue.get("description"),
        severity=issue.get("severity", "warning"),
        category=issue.get("category"),
        status=issue.get("status", "open"),
        contract=contract_ref,
        location=location,
        quality_rule=None,  # Would need quality rule info from contract
        assignment=assignment,
        timeline=timeline,
        activity=activity,
        comments=[],  # Would need comments from storage
        metadata=issue.get("metadata", {}),
        tags=issue.get("tags", []),
        created_at=issue["created_at"],
        updated_at=issue.get("updated_at"),
    )


@router.patch(
    "/issues/{issue_id}",
    operation_id="updateIssue",
    summary="Update an issue",
    response_model=Issue,
    responses={
        400: {"description": "Invalid status transition or missing required fields"},
        403: {"description": "Not authorized"},
        404: {"description": "Issue not found"},
    },
)
async def update_issue(
    issue_id: str,
    body: IssueUpdateRequest,
    request: Request,
    storage: Storage,
    user: CurrentUser,
) -> Issue:
    """Update an issue's status, assignment, or resolution.

    Status transitions:
    - open -> in_progress, resolved, ignored
    - in_progress -> resolved, ignored, open (re-open)
    - resolved -> open (re-open only)
    - ignored -> open (re-open only)
    """
    issue = await storage.issues.get(issue_id)

    if issue is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "ISSUE_NOT_FOUND", "message": f"Issue '{issue_id}' not found"}},
        )

    now = _utc_now()
    updates: dict[str, Any] = {"updated_at": now}

    # Handle status change
    if body.status is not None:
        current_status = issue.get("status", "open")
        new_status = body.status

        # Validate status transitions
        valid_transitions = {
            "open": ["in_progress", "resolved", "ignored"],
            "in_progress": ["resolved", "ignored", "open"],
            "resolved": ["open"],
            "ignored": ["open"],
        }

        if new_status not in valid_transitions.get(current_status, []):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": {
                        "code": "INVALID_STATUS_TRANSITION",
                        "message": f"Cannot transition from '{current_status}' to '{new_status}'",
                    }
                },
            )

        updates["status"] = new_status

        # Set timestamps based on status
        if new_status == "in_progress" and not issue.get("in_progress_at"):
            updates["in_progress_at"] = now
        elif new_status == "resolved":
            updates["resolved_at"] = now
            updates["resolved_by"] = user.id

            # Resolution is required when resolving
            if not body.resolution and not issue.get("resolution"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": {
                            "code": "RESOLUTION_REQUIRED",
                            "message": "Resolution notes are required when marking an issue as resolved",
                        }
                    },
                )

    # Handle assignment changes
    if body.assigned_team is not None:
        updates["assigned_team"] = body.assigned_team
        updates["assigned_at"] = now
        updates["assigned_by"] = user.id

    if body.assigned_user is not None:
        updates["assigned_user"] = body.assigned_user
        if "assigned_at" not in updates:
            updates["assigned_at"] = now
            updates["assigned_by"] = user.id

    # Handle resolution
    if body.resolution is not None:
        updates["resolution"] = body.resolution

    if body.resolution_notes is not None:
        updates["resolution_notes"] = body.resolution_notes

    # Handle tags
    if body.tags is not None:
        updates["tags"] = body.tags

    # Update the issue
    updated_issue = await storage.issues.update(issue_id, updates)

    # Enrich with names
    if updated_issue.get("assigned_team"):
        team = await storage.teams.get(updated_issue["assigned_team"])
        if team:
            updated_issue["assigned_team_name"] = team.get("name")

    if updated_issue.get("assigned_user"):
        user_doc = await storage.users.get(updated_issue["assigned_user"])
        if user_doc:
            updated_issue["assigned_user_name"] = user_doc.get("name")

    return _build_issue_from_doc(updated_issue)


@router.post(
    "/issues/{issue_id}/resolve",
    operation_id="resolveIssue",
    summary="Resolve an issue",
    response_model=Issue,
    responses={404: {"description": "Issue not found"}},
)
async def resolve_issue(
    issue_id: str,
    body: IssueResolveRequest,
    request: Request,
    storage: Storage,
    user: CurrentUser,
) -> Issue:
    """Mark an issue as resolved with resolution type and notes."""
    try:
        issue = await storage.issues.resolve(
            issue_id=issue_id,
            resolution=body.resolution,
            resolved_by=user.id,
        )

        # Also update resolution notes if provided
        if body.resolution_notes:
            issue = await storage.issues.update(issue_id, {
                "resolution_notes": body.resolution_notes,
            })

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "ISSUE_NOT_FOUND", "message": str(e)}},
        )

    return _build_issue_from_doc(issue)
