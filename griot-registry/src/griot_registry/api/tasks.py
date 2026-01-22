"""Task management API endpoints for My Tasks page."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated, Any

from fastapi import APIRouter, HTTPException, Query, Request, status
from pydantic import BaseModel, Field

from griot_registry.auth import CurrentUser

router = APIRouter(tags=["tasks"])


# =============================================================================
# Request/Response Models
# =============================================================================


class AuthorizationTask(BaseModel):
    """Pending authorization task."""

    id: str
    contract_id: str = Field(..., alias="contractId")
    contract_name: str = Field(..., alias="contractName")
    contract_version: str = Field(..., alias="contractVersion")
    requested_by: str = Field(..., alias="requestedBy")
    requested_by_name: str = Field(..., alias="requestedByName")
    requested_by_avatar: str | None = Field(None, alias="requestedByAvatar")
    requested_at: datetime = Field(..., alias="requestedAt")
    domain: str | None = None
    priority: str = "normal"
    change_type: str = Field(..., alias="changeType")
    change_summary: str | None = Field(None, alias="changeSummary")
    message: str | None = None
    href: str

    model_config = {"populate_by_name": True}


class CommentTask(BaseModel):
    """Comment to review task."""

    id: str
    contract_id: str = Field(..., alias="contractId")
    contract_name: str = Field(..., alias="contractName")
    author_id: str = Field(..., alias="authorId")
    author_name: str = Field(..., alias="authorName")
    author_avatar: str | None = Field(None, alias="authorAvatar")
    content: str
    content_preview: str = Field(..., alias="contentPreview")
    type: str = "comment"
    created_at: datetime = Field(..., alias="createdAt")
    href: str

    model_config = {"populate_by_name": True}


class DraftTask(BaseModel):
    """Draft contract/asset task."""

    id: str
    type: str
    name: str
    domain: str | None = None
    updated_at: datetime = Field(..., alias="updatedAt")
    completion_percent: int = Field(..., alias="completionPercent")
    completion_details: dict[str, bool] = Field(default_factory=dict, alias="completionDetails")
    href: str

    model_config = {"populate_by_name": True}


class ReapprovalTask(BaseModel):
    """Reapproval task for changed contracts."""

    id: str
    contract_id: str = Field(..., alias="contractId")
    contract_name: str = Field(..., alias="contractName")
    contract_version: str = Field(..., alias="contractVersion")
    previous_version: str = Field(..., alias="previousVersion")
    changed_by: str = Field(..., alias="changedBy")
    changed_by_name: str = Field(..., alias="changedByName")
    changed_at: datetime = Field(..., alias="changedAt")
    change_reason: str | None = Field(None, alias="changeReason")
    schema_diff_summary: str | None = Field(None, alias="schemaDiffSummary")
    priority: str = "normal"
    href: str

    model_config = {"populate_by_name": True}


class TaskCategory(BaseModel):
    """Task category with items."""

    items: list[Any]
    total: int


class TaskSummary(BaseModel):
    """Summary of all task counts."""

    total_pending: int = Field(..., alias="totalPending")
    authorizations: int
    comments: int
    drafts: int
    reapprovals: int

    model_config = {"populate_by_name": True}


class TaskListResponse(BaseModel):
    """Full task list response for My Tasks page."""

    pending_authorizations: TaskCategory = Field(..., alias="pendingAuthorizations")
    comments_to_review: TaskCategory = Field(..., alias="commentsToReview")
    drafts: TaskCategory
    reapproval_tasks: TaskCategory = Field(..., alias="reapprovalTasks")
    summary: TaskSummary

    model_config = {"populate_by_name": True}


class TaskCreateRequest(BaseModel):
    """Generic task create request."""

    type: str
    title: str
    description: str | None = None
    contract_id: str | None = Field(None, alias="contractId")
    priority: str = "normal"
    due_date: datetime | None = Field(None, alias="dueDate")
    metadata: dict[str, Any] = {}

    model_config = {"populate_by_name": True}


class TaskResponse(BaseModel):
    """Generic task response."""

    id: str
    type: str
    title: str
    description: str | None = None
    status: str = "pending"
    contract_id: str | None = Field(None, alias="contractId")
    user_id: str = Field(..., alias="userId")
    priority: str = "normal"
    due_date: datetime | None = Field(None, alias="dueDate")
    completed_at: datetime | None = Field(None, alias="completedAt")
    metadata: dict[str, Any] = {}
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")

    model_config = {"populate_by_name": True}


class TaskUpdateRequest(BaseModel):
    """Task update request."""

    status: str | None = None
    priority: str | None = None
    due_date: datetime | None = Field(None, alias="dueDate")
    metadata: dict[str, Any] | None = None

    model_config = {"populate_by_name": True}


# =============================================================================
# Helper Functions
# =============================================================================


def _utc_now() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(timezone.utc)


def _truncate(text: str, max_length: int = 100) -> str:
    """Truncate text with ellipsis if too long."""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


# =============================================================================
# Task Endpoints
# =============================================================================


@router.get(
    "/tasks",
    operation_id="listTasks",
    summary="Get all tasks for current user",
    response_model=TaskListResponse,
)
async def list_tasks(
    request: Request,
    user: CurrentUser,
    type: Annotated[str | None, Query(description="Filter by task type")] = None,
    status_filter: Annotated[str | None, Query(alias="status", description="Filter by status")] = None,
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
) -> TaskListResponse:
    """Get all tasks for the current user organized by category.

    This is the main endpoint for the My Tasks page.
    Returns pending authorizations, comments to review, drafts, and reapproval tasks.
    """
    storage = request.app.state.storage

    # Initialize categories
    pending_authorizations: list[AuthorizationTask] = []
    comments_to_review: list[CommentTask] = []
    drafts: list[DraftTask] = []
    reapproval_tasks: list[ReapprovalTask] = []

    # 1. Get pending authorizations (contracts where user is reviewer and status is pending_review)
    try:
        contracts, _ = await storage.contracts.list(
            status="pending_review",
            reviewer_id=user.id,
            limit=limit,
        )

        for contract in contracts:
            # Get submitter info
            submitter = await storage.users.get(contract.get("submitted_by", ""))
            pending_authorizations.append(AuthorizationTask(
                id=f"auth-{contract['id']}",
                contract_id=contract["id"],
                contract_name=contract.get("name", "Unknown"),
                contract_version=contract.get("version", "1.0.0"),
                requested_by=contract.get("submitted_by", ""),
                requested_by_name=submitter["name"] if submitter else "Unknown",
                requested_by_avatar=submitter.get("avatar") if submitter else None,
                requested_at=contract.get("submitted_at", contract.get("updated_at", _utc_now())),
                domain=contract.get("domain"),
                priority="high" if contract.get("priority") == "high" else "normal",
                change_type="update" if contract.get("version", "1.0.0") != "1.0.0" else "new",
                change_summary=contract.get("change_summary"),
                message=contract.get("submission_message"),
                href=f"/studio/contracts/{contract['id']}",
            ))
    except Exception:
        pass  # Contracts endpoint might not support all filters yet

    # 2. Get comments on user's contracts that need response
    try:
        # Get contracts owned by user
        user_contracts, _ = await storage.contracts.list(
            created_by=user.id,
            limit=100,
        )

        for contract in user_contracts:
            # Get comments on this contract
            comments, _ = await storage.comments.list(
                contract_id=contract["id"],
                limit=5,
            )

            for comment in comments:
                # Skip user's own comments
                if comment.get("author_id") == user.id:
                    continue

                author = await storage.users.get(comment.get("author_id", ""))
                comments_to_review.append(CommentTask(
                    id=comment["id"],
                    contract_id=contract["id"],
                    contract_name=contract.get("name", "Unknown"),
                    author_id=comment.get("author_id", ""),
                    author_name=author["name"] if author else "Unknown",
                    author_avatar=author.get("avatar") if author else None,
                    content=comment.get("content", ""),
                    content_preview=_truncate(comment.get("content", ""), 100),
                    type=comment.get("type", "comment"),
                    created_at=comment.get("created_at", _utc_now()),
                    href=f"/studio/contracts/{contract['id']}#comments",
                ))
    except Exception:
        pass  # Comments might not be fully implemented yet

    # 3. Get user's draft contracts
    try:
        draft_contracts, _ = await storage.contracts.list(
            status="draft",
            created_by=user.id,
            limit=limit,
        )

        for contract in draft_contracts:
            # Calculate completion percentage
            has_basic = bool(contract.get("name") and contract.get("description"))
            has_schema = bool(contract.get("schema") and len(contract.get("schema", [])) > 0)
            has_rules = bool(contract.get("quality_rules") and len(contract.get("quality_rules", [])) > 0)
            has_reviewer = bool(contract.get("reviewer_id"))

            completed = sum([has_basic, has_schema, has_rules, has_reviewer])
            completion_percent = int((completed / 4) * 100)

            drafts.append(DraftTask(
                id=f"draft-{contract['id']}",
                type="contract",
                name=contract.get("name", "Untitled Contract"),
                domain=contract.get("domain"),
                updated_at=contract.get("updated_at", contract.get("created_at", _utc_now())),
                completion_percent=completion_percent,
                completion_details={
                    "basic_info": has_basic,
                    "schema": has_schema,
                    "quality_rules": has_rules,
                    "review": has_reviewer,
                },
                href=f"/studio/contracts/new/wizard?draft={contract['id']}",
            ))
    except Exception:
        pass  # Handle gracefully

    # 4. Get reapproval tasks (contracts that were previously approved but have changes)
    # This is simplified - in a full implementation, you'd track which contracts
    # were approved by this user and have since been modified
    try:
        # For now, return empty - this would require tracking approval history
        pass
    except Exception:
        pass

    # Build summary
    summary = TaskSummary(
        total_pending=len(pending_authorizations) + len(comments_to_review) + len(drafts) + len(reapproval_tasks),
        authorizations=len(pending_authorizations),
        comments=len(comments_to_review),
        drafts=len(drafts),
        reapprovals=len(reapproval_tasks),
    )

    return TaskListResponse(
        pending_authorizations=TaskCategory(items=pending_authorizations, total=len(pending_authorizations)),
        comments_to_review=TaskCategory(items=comments_to_review, total=len(comments_to_review)),
        drafts=TaskCategory(items=drafts, total=len(drafts)),
        reapproval_tasks=TaskCategory(items=reapproval_tasks, total=len(reapproval_tasks)),
        summary=summary,
    )


@router.post(
    "/tasks",
    operation_id="createTask",
    summary="Create a new task",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_task(
    request: Request,
    user: CurrentUser,
    body: TaskCreateRequest,
) -> TaskResponse:
    """Create a new task for the current user."""
    storage = request.app.state.storage

    task_doc = {
        "type": body.type,
        "title": body.title,
        "description": body.description,
        "status": "pending",
        "contract_id": body.contract_id,
        "user_id": user.id,
        "priority": body.priority,
        "due_date": body.due_date,
        "metadata": body.metadata,
    }

    task = await storage.tasks.create(task_doc)

    return TaskResponse(
        id=task["id"],
        type=task["type"],
        title=task["title"],
        description=task.get("description"),
        status=task.get("status", "pending"),
        contract_id=task.get("contract_id"),
        user_id=task["user_id"],
        priority=task.get("priority", "normal"),
        due_date=task.get("due_date"),
        completed_at=task.get("completed_at"),
        metadata=task.get("metadata", {}),
        created_at=task["created_at"],
        updated_at=task.get("updated_at", task["created_at"]),
    )


@router.get(
    "/tasks/{task_id}",
    operation_id="getTask",
    summary="Get task by ID",
    response_model=TaskResponse,
)
async def get_task(
    request: Request,
    task_id: str,
    user: CurrentUser,
) -> TaskResponse:
    """Get a specific task by ID."""
    storage = request.app.state.storage

    task = await storage.tasks.get(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "TASK_NOT_FOUND", "message": f"Task '{task_id}' not found"}},
        )

    # Verify ownership
    if task.get("user_id") != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": {"code": "NOT_AUTHORIZED", "message": "You can only view your own tasks"}},
        )

    return TaskResponse(
        id=task["id"],
        type=task["type"],
        title=task["title"],
        description=task.get("description"),
        status=task.get("status", "pending"),
        contract_id=task.get("contract_id"),
        user_id=task["user_id"],
        priority=task.get("priority", "normal"),
        due_date=task.get("due_date"),
        completed_at=task.get("completed_at"),
        metadata=task.get("metadata", {}),
        created_at=task["created_at"],
        updated_at=task.get("updated_at", task["created_at"]),
    )


@router.patch(
    "/tasks/{task_id}",
    operation_id="updateTask",
    summary="Update a task",
    response_model=TaskResponse,
)
async def update_task(
    request: Request,
    task_id: str,
    user: CurrentUser,
    body: TaskUpdateRequest,
) -> TaskResponse:
    """Update a task's status or details."""
    storage = request.app.state.storage

    # Get existing task
    task = await storage.tasks.get(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "TASK_NOT_FOUND", "message": f"Task '{task_id}' not found"}},
        )

    # Verify ownership
    if task.get("user_id") != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": {"code": "NOT_AUTHORIZED", "message": "You can only update your own tasks"}},
        )

    # Build update dict
    updates: dict[str, Any] = {"updated_at": _utc_now()}

    if body.status is not None:
        updates["status"] = body.status
        if body.status == "completed":
            updates["completed_at"] = _utc_now()
    if body.priority is not None:
        updates["priority"] = body.priority
    if body.due_date is not None:
        updates["due_date"] = body.due_date
    if body.metadata is not None:
        updates["metadata"] = body.metadata

    updated_task = await storage.tasks.update(task_id, updates)

    return TaskResponse(
        id=updated_task["id"],
        type=updated_task["type"],
        title=updated_task["title"],
        description=updated_task.get("description"),
        status=updated_task.get("status", "pending"),
        contract_id=updated_task.get("contract_id"),
        user_id=updated_task["user_id"],
        priority=updated_task.get("priority", "normal"),
        due_date=updated_task.get("due_date"),
        completed_at=updated_task.get("completed_at"),
        metadata=updated_task.get("metadata", {}),
        created_at=updated_task["created_at"],
        updated_at=updated_task.get("updated_at", updated_task["created_at"]),
    )
