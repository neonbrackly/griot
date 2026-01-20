"""Approval workflow endpoints.

Provides endpoints for contract approval workflows.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from griot_registry.api.dependencies import ContractSvc, Storage
from griot_registry.auth import CurrentUser, RequireEditor

router = APIRouter()


# =============================================================================
# Request/Response Models
# =============================================================================


class ApprovalRequestCreate(BaseModel):
    """Request to create an approval request."""

    contract_id: str
    approvers: list[str] = Field(
        ...,
        min_length=1,
        description="List of user IDs who need to approve",
    )
    notes: str | None = Field(
        default=None,
        description="Notes about the approval request",
    )


class ApproveRequest(BaseModel):
    """Request to approve."""

    comments: str | None = None


class RejectRequest(BaseModel):
    """Request to reject."""

    reason: str = Field(..., min_length=1, description="Reason for rejection")


class ApprovalEntry(BaseModel):
    """A single approval entry."""

    approver: str
    comments: str | None = None
    approved_at: datetime


class RejectionEntry(BaseModel):
    """A single rejection entry."""

    rejector: str
    reason: str
    rejected_at: datetime


class ApprovalRequest(BaseModel):
    """An approval request record."""

    id: str
    contract_id: str
    requested_by: str
    approvers: list[str]
    notes: str | None = None
    status: str
    approvals: list[ApprovalEntry] = Field(default_factory=list)
    rejections: list[RejectionEntry] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime | None = None
    completed_at: datetime | None = None


class ApprovalRequestList(BaseModel):
    """List of approval requests."""

    items: list[ApprovalRequest]


# =============================================================================
# Helper function to build ApprovalRequest response
# =============================================================================


def _build_approval_response(approval: dict[str, Any]) -> ApprovalRequest:
    """Build an ApprovalRequest from a storage dict."""
    return ApprovalRequest(
        id=approval["id"],
        contract_id=approval["contract_id"],
        requested_by=approval["requested_by"],
        approvers=approval["approvers"],
        notes=approval.get("notes"),
        status=approval["status"],
        approvals=[
            ApprovalEntry(
                approver=a["approver"],
                comments=a.get("comments"),
                approved_at=a["approved_at"],
            )
            for a in approval.get("approvals", [])
        ],
        rejections=[
            RejectionEntry(
                rejector=r["rejector"],
                reason=r["reason"],
                rejected_at=r["rejected_at"],
            )
            for r in approval.get("rejections", [])
        ],
        created_at=approval["created_at"],
        updated_at=approval.get("updated_at"),
        completed_at=approval.get("completed_at"),
    )


# =============================================================================
# Endpoints
# =============================================================================


@router.post(
    "/approvals",
    operation_id="createApprovalRequest",
    summary="Create an approval request",
    status_code=status.HTTP_201_CREATED,
    response_model=ApprovalRequest,
)
async def create_approval_request(
    request: ApprovalRequestCreate,
    storage: Storage,
    user: CurrentUser,
) -> ApprovalRequest:
    """Create a new approval request for a contract.

    This initiates the approval workflow. The specified approvers
    will need to approve before the contract can be activated.
    """
    # Verify contract exists
    contract = await storage.contracts.get(request.contract_id)
    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "NOT_FOUND",
                "message": f"Contract '{request.contract_id}' not found",
            },
        )

    approval = await storage.approvals.create_request(
        contract_id=request.contract_id,
        requested_by=user.id,
        approvers=request.approvers,
        notes=request.notes,
    )

    return _build_approval_response(approval)


@router.get(
    "/approvals/pending",
    operation_id="listPendingApprovals",
    summary="List pending approvals",
    response_model=ApprovalRequestList,
)
async def list_pending_approvals(
    storage: Storage,
    user: CurrentUser,
    contract_id: str | None = Query(default=None, description="Filter by contract ID"),
    my_approvals: bool = Query(
        default=False,
        description="Only show approvals where I'm an approver",
    ),
) -> ApprovalRequestList:
    """List pending approval requests.

    Optionally filter by contract or to show only your pending approvals.
    """
    approver = user.id if my_approvals else None

    approvals = await storage.approvals.list_pending(
        approver=approver,
        contract_id=contract_id,
    )

    return ApprovalRequestList(
        items=[_build_approval_response(a) for a in approvals],
    )


@router.get(
    "/approvals/{request_id}",
    operation_id="getApprovalRequest",
    summary="Get an approval request",
    response_model=ApprovalRequest,
    responses={404: {"description": "Approval request not found"}},
)
async def get_approval_request(
    request_id: str,
    storage: Storage,
    user: CurrentUser,
) -> ApprovalRequest:
    """Get an approval request by ID."""
    approval = await storage.approvals.get_request(request_id)

    if approval is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "NOT_FOUND",
                "message": f"Approval request '{request_id}' not found",
            },
        )

    return _build_approval_response(approval)


@router.post(
    "/approvals/{request_id}/approve",
    operation_id="approve",
    summary="Approve a request",
    response_model=ApprovalRequest,
    responses={
        404: {"description": "Approval request not found"},
        400: {"description": "User not authorized to approve"},
    },
)
async def approve(
    request_id: str,
    request: ApproveRequest,
    storage: Storage,
    service: ContractSvc,
    user: RequireEditor,
) -> ApprovalRequest:
    """Approve an approval request.

    Only users listed in the approvers can approve.
    When all approvers have approved, the contract status is updated to 'active'.
    """
    # Get approval request
    existing = await storage.approvals.get_request(request_id)
    if existing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "NOT_FOUND",
                "message": f"Approval request '{request_id}' not found",
            },
        )

    # Check user is an approver
    if user.id not in existing["approvers"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "NOT_AUTHORIZED",
                "message": "You are not authorized to approve this request",
            },
        )

    # Record approval
    try:
        approval = await storage.approvals.approve(
            request_id=request_id,
            approver=user.id,
            comments=request.comments,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": str(e)},
        )

    # If fully approved, activate the contract
    if approval["status"] == "approved":
        try:
            await service.update_status(
                approval["contract_id"],
                "active",
                user,
            )
        except ValueError:
            pass  # Contract may already be active or in different state

    return _build_approval_response(approval)


@router.post(
    "/approvals/{request_id}/reject",
    operation_id="reject",
    summary="Reject a request",
    response_model=ApprovalRequest,
    responses={
        404: {"description": "Approval request not found"},
        400: {"description": "User not authorized to reject"},
    },
)
async def reject(
    request_id: str,
    request: RejectRequest,
    storage: Storage,
    user: RequireEditor,
) -> ApprovalRequest:
    """Reject an approval request.

    Only users listed in the approvers can reject.
    A single rejection marks the entire request as rejected.
    """
    # Get approval request
    existing = await storage.approvals.get_request(request_id)
    if existing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "NOT_FOUND",
                "message": f"Approval request '{request_id}' not found",
            },
        )

    # Check user is an approver
    if user.id not in existing["approvers"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "NOT_AUTHORIZED",
                "message": "You are not authorized to reject this request",
            },
        )

    # Record rejection
    try:
        approval = await storage.approvals.reject(
            request_id=request_id,
            rejector=user.id,
            reason=request.reason,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": str(e)},
        )

    return _build_approval_response(approval)
