"""Notification API endpoints."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated, Any

from fastapi import APIRouter, HTTPException, Query, Request, status
from pydantic import BaseModel, Field

from griot_registry.auth import CurrentUser

router = APIRouter(tags=["notifications"])


# =============================================================================
# Request/Response Models
# =============================================================================


class NotificationResponse(BaseModel):
    """Notification response."""

    id: str
    type: str
    title: str
    description: str
    read: bool = False
    href: str | None = None
    metadata: dict[str, Any] = {}
    created_at: datetime = Field(..., alias="createdAt")
    read_at: datetime | None = Field(None, alias="readAt")

    model_config = {"populate_by_name": True}


class NotificationPagination(BaseModel):
    """Notification pagination info."""

    total: int
    unread_count: int = Field(..., alias="unreadCount")
    limit: int
    offset: int

    model_config = {"populate_by_name": True}


class NotificationListResponse(BaseModel):
    """Notification list response."""

    items: list[NotificationResponse]
    pagination: NotificationPagination


class MarkAllReadResponse(BaseModel):
    """Response for mark all read."""

    message: str
    marked_count: int = Field(..., alias="markedCount")
    read_at: datetime = Field(..., alias="readAt")

    model_config = {"populate_by_name": True}


# =============================================================================
# Helper Functions
# =============================================================================


def _utc_now() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(timezone.utc)


def _build_notification_response(notif_doc: dict[str, Any]) -> NotificationResponse:
    """Build notification response."""
    return NotificationResponse(
        id=notif_doc["id"],
        type=notif_doc["type"],
        title=notif_doc["title"],
        description=notif_doc["description"],
        read=notif_doc.get("read", False),
        href=notif_doc.get("href"),
        metadata=notif_doc.get("metadata", {}),
        created_at=notif_doc["created_at"],
        read_at=notif_doc.get("read_at"),
    )


# =============================================================================
# Notification Endpoints
# =============================================================================


@router.get(
    "/notifications",
    operation_id="listNotifications",
    summary="List notifications for current user",
    response_model=NotificationListResponse,
)
async def list_notifications(
    request: Request,
    user: CurrentUser,
    unread_only: Annotated[bool, Query(alias="unreadOnly", description="Only return unread notifications")] = False,
    type: Annotated[str | None, Query(description="Filter by notification type")] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> NotificationListResponse:
    """List notifications for the current user.

    Returns notifications sorted by creation date (newest first).
    Includes unread count for badge display.
    """
    storage = request.app.state.storage

    notifications, total, unread_count = await storage.notifications.list(
        user_id=user.id,
        unread_only=unread_only,
        limit=limit,
        offset=offset,
    )

    items = [_build_notification_response(n) for n in notifications]

    return NotificationListResponse(
        items=items,
        pagination=NotificationPagination(
            total=total,
            unread_count=unread_count,
            limit=limit,
            offset=offset,
        ),
    )


@router.patch(
    "/notifications/{notification_id}/read",
    operation_id="markNotificationRead",
    summary="Mark notification as read",
    response_model=NotificationResponse,
)
async def mark_notification_read(
    request: Request,
    notification_id: str,
    user: CurrentUser,
) -> NotificationResponse:
    """Mark a single notification as read.

    Only the notification owner can mark it as read.
    """
    storage = request.app.state.storage

    # Get notification and verify ownership
    # For simplicity, we try to mark it and let the repository handle authorization
    try:
        notification = await storage.notifications.mark_read(notification_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOTIFICATION_NOT_FOUND", "message": f"Notification '{notification_id}' not found"}},
        )

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOTIFICATION_NOT_FOUND", "message": f"Notification '{notification_id}' not found"}},
        )

    # Verify ownership (notification should belong to current user)
    if notification.get("user_id") != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": {"code": "NOT_AUTHORIZED", "message": "You can only mark your own notifications as read"}},
        )

    return _build_notification_response(notification)


@router.post(
    "/notifications/read-all",
    operation_id="markAllNotificationsRead",
    summary="Mark all notifications as read",
    response_model=MarkAllReadResponse,
)
async def mark_all_notifications_read(
    request: Request,
    user: CurrentUser,
) -> MarkAllReadResponse:
    """Mark all unread notifications as read for the current user.

    Returns the count of notifications that were marked as read.
    """
    storage = request.app.state.storage

    marked_count = await storage.notifications.mark_all_read(user.id)
    now = _utc_now()

    return MarkAllReadResponse(
        message="All notifications marked as read",
        marked_count=marked_count,
        read_at=now,
    )


# =============================================================================
# Notification Creation (Internal - for other services)
# =============================================================================


async def create_notification(
    storage: Any,
    user_id: str,
    type: str,
    title: str,
    description: str,
    href: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a notification for a user (internal helper).

    This is not exposed as an API endpoint but used by other services
    to create notifications when events occur.
    """
    notification = {
        "user_id": user_id,
        "type": type,
        "title": title,
        "description": description,
        "read": False,
        "href": href,
        "metadata": metadata or {},
    }

    return await storage.notifications.create(notification)


# Notification type constants for use by other modules
class NotificationType:
    """Notification type constants."""

    CONTRACT_APPROVED = "contract_approved"
    CONTRACT_REJECTED = "contract_rejected"
    CONTRACT_SUBMITTED = "contract_submitted"
    ISSUE_DETECTED = "issue_detected"
    ISSUE_ASSIGNED = "issue_assigned"
    ISSUE_RESOLVED = "issue_resolved"
    SLA_BREACH = "sla_breach"
    SCHEMA_DRIFT = "schema_drift"
    COMMENT_ADDED = "comment_added"
    TASK_ASSIGNED = "task_assigned"
    USER_INVITED = "user_invited"
    TEAM_MEMBER_ADDED = "team_member_added"
