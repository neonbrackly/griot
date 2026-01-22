"""Task models for My Tasks page."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class TaskType(str, Enum):
    """Task types."""

    AUTHORIZATION = "authorization"  # Pending contract approvals
    COMMENT = "comment"  # Comments to review
    DRAFT = "draft"  # Incomplete contracts/assets
    REAPPROVAL = "reapproval"  # Schema changes requiring re-approval
    ISSUE = "issue"  # Assigned issues


class TaskStatus(str, Enum):
    """Task status."""

    PENDING = "pending"
    COMPLETED = "completed"
    DISMISSED = "dismissed"


class TaskCreate(BaseModel):
    """Task creation request."""

    type: TaskType
    user_id: str = Field(..., alias="userId")
    title: str
    description: str | None = None
    priority: str = "normal"  # low, normal, high
    data: dict[str, Any] | None = None  # Additional context
    href: str | None = None  # Link to related resource

    model_config = {"populate_by_name": True}


class TaskUpdate(BaseModel):
    """Task update request."""

    status: TaskStatus | None = None
    title: str | None = None
    description: str | None = None
    priority: str | None = None


class TaskInDB(BaseModel):
    """Task as stored in database."""

    id: str
    type: TaskType
    user_id: str
    title: str
    description: str | None = None
    priority: str = "normal"
    status: TaskStatus = TaskStatus.PENDING
    data: dict[str, Any] | None = None
    href: str | None = None
    completed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class TaskResponse(BaseModel):
    """Task response for API."""

    id: str
    type: TaskType
    title: str
    description: str | None = None
    priority: str
    status: TaskStatus
    data: dict[str, Any] | None = None
    href: str | None = None
    completed_at: datetime | None = Field(None, alias="completedAt")
    created_at: datetime = Field(..., alias="createdAt")

    model_config = {"populate_by_name": True}


# Specific task types for My Tasks page

class PendingAuthorization(BaseModel):
    """Pending authorization task item."""

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
    change_type: str = Field(..., alias="changeType")  # new, update
    change_summary: str | None = Field(None, alias="changeSummary")
    message: str | None = None
    href: str

    model_config = {"populate_by_name": True}


class CommentToReview(BaseModel):
    """Comment to review task item."""

    id: str
    contract_id: str = Field(..., alias="contractId")
    contract_name: str = Field(..., alias="contractName")
    author_id: str = Field(..., alias="authorId")
    author_name: str = Field(..., alias="authorName")
    author_avatar: str | None = Field(None, alias="authorAvatar")
    content: str
    content_preview: str = Field(..., alias="contentPreview")
    type: str  # question, suggestion, etc.
    created_at: datetime = Field(..., alias="createdAt")
    href: str

    model_config = {"populate_by_name": True}


class DraftItem(BaseModel):
    """Draft contract/asset task item."""

    id: str
    type: str  # contract, asset
    name: str
    domain: str | None = None
    updated_at: datetime = Field(..., alias="updatedAt")
    completion_percent: int = Field(..., alias="completionPercent")
    completion_details: dict[str, bool] = Field(..., alias="completionDetails")
    href: str

    model_config = {"populate_by_name": True}


class ReapprovalTask(BaseModel):
    """Reapproval task item."""

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
    priority: str = "high"
    href: str

    model_config = {"populate_by_name": True}


class TaskSummary(BaseModel):
    """Task summary counts."""

    total_pending: int = Field(0, alias="totalPending")
    authorizations: int = 0
    comments: int = 0
    drafts: int = 0
    reapprovals: int = 0

    model_config = {"populate_by_name": True}


class TaskListResponse(BaseModel):
    """Full task list response for My Tasks page."""

    pending_authorizations: dict[str, Any] = Field(..., alias="pendingAuthorizations")
    comments_to_review: dict[str, Any] = Field(..., alias="commentsToReview")
    drafts: dict[str, Any]
    reapproval_tasks: dict[str, Any] = Field(..., alias="reapprovalTasks")
    summary: TaskSummary

    model_config = {"populate_by_name": True}
