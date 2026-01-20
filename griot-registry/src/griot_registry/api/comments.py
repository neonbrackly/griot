"""Comment endpoints.

Provides endpoints for collaboration comments on contracts.
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


class CommentCreateRequest(BaseModel):
    """Request to create a comment."""

    contract_id: str
    content: str = Field(..., min_length=1, max_length=5000)
    thread_id: str | None = Field(
        default=None,
        description="Thread ID for replies (leave empty for new threads)",
    )
    section: str | None = Field(
        default=None,
        description="Contract section being commented on",
    )
    field_path: str | None = Field(
        default=None,
        description="Specific field path being commented on",
    )


class CommentUpdateRequest(BaseModel):
    """Request to update a comment."""

    content: str = Field(..., min_length=1, max_length=5000)


class ReactionRequest(BaseModel):
    """Request to add a reaction."""

    reaction: str = Field(
        ...,
        description="Reaction emoji or name: thumbsup, thumbsdown, heart, eyes, etc.",
    )


class Comment(BaseModel):
    """A comment record."""

    id: str
    contract_id: str
    content: str
    thread_id: str | None = None
    section: str | None = None
    field_path: str | None = None
    reactions: dict[str, list[str]] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime | None = None
    created_by: str
    updated_by: str | None = None


class CommentListResponse(BaseModel):
    """Response for listing comments."""

    items: list[Comment]
    total: int
    limit: int
    offset: int


# =============================================================================
# Endpoints
# =============================================================================


@router.post(
    "/comments",
    operation_id="createComment",
    summary="Create a comment",
    status_code=status.HTTP_201_CREATED,
    response_model=Comment,
)
async def create_comment(
    request: CommentCreateRequest,
    storage: Storage,
    user: CurrentUser,
) -> Comment:
    """Create a new comment on a contract.

    Comments support threading for discussions. Leave thread_id empty to start
    a new thread, or provide an existing comment ID to reply to a thread.
    """
    comment = await storage.comments.create({
        "contract_id": request.contract_id,
        "content": request.content,
        "thread_id": request.thread_id,
        "section": request.section,
        "field_path": request.field_path,
        "created_by": user.id,
    })

    return Comment(
        id=comment["id"],
        contract_id=comment["contract_id"],
        content=comment["content"],
        thread_id=comment.get("thread_id"),
        section=comment.get("section"),
        field_path=comment.get("field_path"),
        reactions=comment.get("reactions", {}),
        created_at=comment["created_at"],
        updated_at=comment.get("updated_at"),
        created_by=comment["created_by"],
        updated_by=comment.get("updated_by"),
    )


@router.get(
    "/comments/{comment_id}",
    operation_id="getComment",
    summary="Get a comment",
    response_model=Comment,
    responses={404: {"description": "Comment not found"}},
)
async def get_comment(
    comment_id: str,
    storage: Storage,
    user: OptionalUser,
) -> Comment:
    """Get a comment by ID."""
    comment = await storage.comments.get(comment_id)

    if comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": f"Comment '{comment_id}' not found"},
        )

    return Comment(
        id=comment["id"],
        contract_id=comment["contract_id"],
        content=comment["content"],
        thread_id=comment.get("thread_id"),
        section=comment.get("section"),
        field_path=comment.get("field_path"),
        reactions=comment.get("reactions", {}),
        created_at=comment["created_at"],
        updated_at=comment.get("updated_at"),
        created_by=comment["created_by"],
        updated_by=comment.get("updated_by"),
    )


@router.patch(
    "/comments/{comment_id}",
    operation_id="updateComment",
    summary="Update a comment",
    response_model=Comment,
    responses={404: {"description": "Comment not found"}},
)
async def update_comment(
    comment_id: str,
    request: CommentUpdateRequest,
    storage: Storage,
    user: CurrentUser,
) -> Comment:
    """Update a comment's content."""
    try:
        comment = await storage.comments.update(
            comment_id=comment_id,
            content=request.content,
            updated_by=user.id,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": str(e)},
        )

    return Comment(
        id=comment["id"],
        contract_id=comment["contract_id"],
        content=comment["content"],
        thread_id=comment.get("thread_id"),
        section=comment.get("section"),
        field_path=comment.get("field_path"),
        reactions=comment.get("reactions", {}),
        created_at=comment["created_at"],
        updated_at=comment.get("updated_at"),
        created_by=comment["created_by"],
        updated_by=comment.get("updated_by"),
    )


@router.delete(
    "/comments/{comment_id}",
    operation_id="deleteComment",
    summary="Delete a comment",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"description": "Comment not found"}},
)
async def delete_comment(
    comment_id: str,
    storage: Storage,
    user: CurrentUser,
) -> None:
    """Delete a comment."""
    success = await storage.comments.delete(comment_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": f"Comment '{comment_id}' not found"},
        )


@router.post(
    "/comments/{comment_id}/reactions",
    operation_id="addReaction",
    summary="Add a reaction to a comment",
    response_model=Comment,
    responses={404: {"description": "Comment not found"}},
)
async def add_reaction(
    comment_id: str,
    request: ReactionRequest,
    storage: Storage,
    user: CurrentUser,
) -> Comment:
    """Add a reaction to a comment."""
    try:
        comment = await storage.comments.add_reaction(
            comment_id=comment_id,
            reaction=request.reaction,
            user_id=user.id,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": str(e)},
        )

    return Comment(
        id=comment["id"],
        contract_id=comment["contract_id"],
        content=comment["content"],
        thread_id=comment.get("thread_id"),
        section=comment.get("section"),
        field_path=comment.get("field_path"),
        reactions=comment.get("reactions", {}),
        created_at=comment["created_at"],
        updated_at=comment.get("updated_at"),
        created_by=comment["created_by"],
        updated_by=comment.get("updated_by"),
    )


@router.get(
    "/contracts/{contract_id}/comments",
    operation_id="listContractComments",
    summary="List comments for a contract",
    response_model=CommentListResponse,
)
async def list_contract_comments(
    contract_id: str,
    storage: Storage,
    user: OptionalUser,
    thread_id: str | None = Query(
        default=None,
        description="Filter by thread ID to get a specific conversation",
    ),
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> CommentListResponse:
    """List comments for a contract.

    Optionally filter by thread_id to get a specific conversation.
    """
    comments, total = await storage.comments.list(
        contract_id=contract_id,
        thread_id=thread_id,
        limit=limit,
        offset=offset,
    )

    return CommentListResponse(
        items=[
            Comment(
                id=c["id"],
                contract_id=c["contract_id"],
                content=c["content"],
                thread_id=c.get("thread_id"),
                section=c.get("section"),
                field_path=c.get("field_path"),
                reactions=c.get("reactions", {}),
                created_at=c["created_at"],
                updated_at=c.get("updated_at"),
                created_by=c["created_by"],
                updated_by=c.get("updated_by"),
            )
            for c in comments
        ],
        total=total,
        limit=limit,
        offset=offset,
    )
