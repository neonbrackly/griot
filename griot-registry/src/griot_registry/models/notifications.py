"""Notification models."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class NotificationType(str, Enum):
    """Notification types."""

    CONTRACT_APPROVED = "contract_approved"
    CONTRACT_REJECTED = "contract_rejected"
    CONTRACT_SUBMITTED = "contract_submitted"
    CONTRACT_REAPPROVAL = "contract_reapproval"
    ISSUE_DETECTED = "issue_detected"
    ISSUE_ASSIGNED = "issue_assigned"
    ISSUE_RESOLVED = "issue_resolved"
    SLA_BREACH = "sla_breach"
    SCHEMA_DRIFT = "schema_drift"
    COMMENT_ADDED = "comment_added"
    COMMENT_MENTION = "comment_mention"
    TASK_ASSIGNED = "task_assigned"
    TASK_COMPLETED = "task_completed"
    TEAM_INVITE = "team_invite"
    ROLE_CHANGED = "role_changed"


class NotificationCreate(BaseModel):
    """Notification creation (internal use)."""

    user_id: str
    type: NotificationType
    title: str
    message: str
    data: dict[str, Any] | None = None  # Additional context data
    href: str | None = None  # Link to related resource


class NotificationInDB(BaseModel):
    """Notification as stored in database."""

    id: str
    user_id: str
    type: NotificationType
    title: str
    message: str
    data: dict[str, Any] | None = None
    href: str | None = None
    read: bool = False
    read_at: datetime | None = None
    created_at: datetime


class NotificationResponse(BaseModel):
    """Notification response for API."""

    id: str
    type: NotificationType
    title: str
    message: str
    data: dict[str, Any] | None = None
    href: str | None = None
    read: bool
    read_at: datetime | None = Field(None, alias="readAt")
    created_at: datetime = Field(..., alias="createdAt")

    model_config = {"populate_by_name": True}


class NotificationListResponse(BaseModel):
    """Notification list response."""

    items: list[NotificationResponse]
    total: int
    unread_count: int = Field(0, alias="unreadCount")

    model_config = {"populate_by_name": True}
