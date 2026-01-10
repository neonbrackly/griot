"""Approval chain endpoints for contract governance (FR-REG-008)."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

router = APIRouter()


class ApprovalStatus(str, Enum):
    """Status of an approval request."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class ApprovalDecisionType(str, Enum):
    """Type of approval decision."""

    APPROVE = "approve"
    REJECT = "reject"


class ApproverInfo(BaseModel):
    """Information about an approver."""

    user_id: str
    email: str
    name: str | None = None
    role: str | None = None


class Approval(BaseModel):
    """A single approval in the chain."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    approver: ApproverInfo
    status: ApprovalStatus = ApprovalStatus.PENDING
    decision_at: datetime | None = None
    comment: str | None = None
    order: int = 0


class ApprovalChain(BaseModel):
    """An approval chain for a contract version."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    contract_id: str
    contract_version: str
    approvals: list[Approval]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str
    status: ApprovalStatus = ApprovalStatus.PENDING
    completed_at: datetime | None = None

    @property
    def current_approval(self) -> Approval | None:
        """Get the current pending approval."""
        for approval in sorted(self.approvals, key=lambda a: a.order):
            if approval.status == ApprovalStatus.PENDING:
                return approval
        return None

    @property
    def is_complete(self) -> bool:
        """Check if approval chain is complete."""
        return all(a.status == ApprovalStatus.APPROVED for a in self.approvals)

    @property
    def is_rejected(self) -> bool:
        """Check if any approval was rejected."""
        return any(a.status == ApprovalStatus.REJECTED for a in self.approvals)


class ApprovalChainCreate(BaseModel):
    """Request to create an approval chain."""

    approvers: list[ApproverInfo]
    require_all: bool = True
    notify: bool = True


class ApprovalDecision(BaseModel):
    """A decision on an approval."""

    decision: ApprovalDecisionType
    comment: str | None = None


class ApprovalChainStatus(BaseModel):
    """Status summary of an approval chain."""

    chain_id: str
    contract_id: str
    contract_version: str
    status: ApprovalStatus
    total_approvers: int
    approved_count: int
    pending_count: int
    rejected_count: int
    current_approver: ApproverInfo | None
    created_at: datetime
    completed_at: datetime | None


# In-memory storage for approval chains (would be in database in production)
_approval_chains: dict[str, ApprovalChain] = {}
_approval_to_chain: dict[str, str] = {}


def _get_chain_key(contract_id: str, version: str) -> str:
    """Generate key for contract version approval chain."""
    return f"{contract_id}@{version}"


@router.post(
    "/contracts/{contract_id}/versions/{version}/approval-chain",
    response_model=ApprovalChain,
    status_code=status.HTTP_201_CREATED,
    summary="Create approval chain",
    description="Create an approval chain for a contract version.",
)
async def create_approval_chain(
    contract_id: str,
    version: str,
    request: ApprovalChainCreate,
) -> ApprovalChain:
    """Create an approval chain for a contract version.

    This implements FR-REG-008: Approval workflow for contract changes.
    """
    chain_key = _get_chain_key(contract_id, version)

    # Check if chain already exists
    if chain_key in _approval_chains:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "CHAIN_EXISTS",
                "message": f"Approval chain already exists for {contract_id}@{version}",
            },
        )

    # Create approvals from approvers
    approvals = [
        Approval(
            approver=approver,
            order=i,
        )
        for i, approver in enumerate(request.approvers)
    ]

    # Create chain
    chain = ApprovalChain(
        contract_id=contract_id,
        contract_version=version,
        approvals=approvals,
        created_by="system",  # Would come from auth context
    )

    # Store chain
    _approval_chains[chain_key] = chain

    # Map approval IDs to chain
    for approval in approvals:
        _approval_to_chain[approval.id] = chain_key

    return chain


@router.get(
    "/contracts/{contract_id}/versions/{version}/approval-chain",
    response_model=ApprovalChain,
    summary="Get approval chain",
    description="Get the approval chain for a contract version.",
)
async def get_approval_chain(
    contract_id: str,
    version: str,
) -> ApprovalChain:
    """Get the approval chain for a contract version."""
    chain_key = _get_chain_key(contract_id, version)

    if chain_key not in _approval_chains:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "CHAIN_NOT_FOUND",
                "message": f"No approval chain found for {contract_id}@{version}",
            },
        )

    return _approval_chains[chain_key]


@router.get(
    "/contracts/{contract_id}/versions/{version}/approval-status",
    response_model=ApprovalChainStatus,
    summary="Get approval status",
    description="Get a summary of the approval chain status.",
)
async def get_approval_status(
    contract_id: str,
    version: str,
) -> ApprovalChainStatus:
    """Get approval chain status summary."""
    chain_key = _get_chain_key(contract_id, version)

    if chain_key not in _approval_chains:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "CHAIN_NOT_FOUND",
                "message": f"No approval chain found for {contract_id}@{version}",
            },
        )

    chain = _approval_chains[chain_key]
    current = chain.current_approval

    return ApprovalChainStatus(
        chain_id=chain.id,
        contract_id=chain.contract_id,
        contract_version=chain.contract_version,
        status=chain.status,
        total_approvers=len(chain.approvals),
        approved_count=sum(1 for a in chain.approvals if a.status == ApprovalStatus.APPROVED),
        pending_count=sum(1 for a in chain.approvals if a.status == ApprovalStatus.PENDING),
        rejected_count=sum(1 for a in chain.approvals if a.status == ApprovalStatus.REJECTED),
        current_approver=current.approver if current else None,
        created_at=chain.created_at,
        completed_at=chain.completed_at,
    )


@router.get(
    "/approvals/{approval_id}",
    response_model=Approval,
    summary="Get approval",
    description="Get a specific approval by ID.",
)
async def get_approval(approval_id: str) -> Approval:
    """Get a specific approval."""
    if approval_id not in _approval_to_chain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "APPROVAL_NOT_FOUND",
                "message": f"Approval not found: {approval_id}",
            },
        )

    chain_key = _approval_to_chain[approval_id]
    chain = _approval_chains[chain_key]

    for approval in chain.approvals:
        if approval.id == approval_id:
            return approval

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "code": "APPROVAL_NOT_FOUND",
            "message": f"Approval not found: {approval_id}",
        },
    )


@router.post(
    "/approvals/{approval_id}/decision",
    response_model=Approval,
    summary="Submit approval decision",
    description="Submit a decision (approve/reject) for an approval.",
)
async def submit_approval_decision(
    approval_id: str,
    decision: ApprovalDecision,
) -> Approval:
    """Submit an approval decision.

    This implements the approval workflow where approvers can
    approve or reject contract changes in sequence.
    """
    if approval_id not in _approval_to_chain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "APPROVAL_NOT_FOUND",
                "message": f"Approval not found: {approval_id}",
            },
        )

    chain_key = _approval_to_chain[approval_id]
    chain = _approval_chains[chain_key]

    # Find the approval
    approval = None
    for a in chain.approvals:
        if a.id == approval_id:
            approval = a
            break

    if not approval:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "APPROVAL_NOT_FOUND",
                "message": f"Approval not found: {approval_id}",
            },
        )

    # Check if approval is pending
    if approval.status != ApprovalStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "ALREADY_DECIDED",
                "message": f"Approval already has status: {approval.status}",
            },
        )

    # Check if it's this approver's turn (sequential approval)
    current = chain.current_approval
    if current and current.id != approval_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "NOT_YOUR_TURN",
                "message": "It is not your turn to approve. Wait for previous approvers.",
            },
        )

    # Update approval
    now = datetime.now(timezone.utc)
    approval.decision_at = now
    approval.comment = decision.comment

    if decision.decision == ApprovalDecisionType.APPROVE:
        approval.status = ApprovalStatus.APPROVED
    else:
        approval.status = ApprovalStatus.REJECTED
        # Reject the entire chain
        chain.status = ApprovalStatus.REJECTED
        chain.completed_at = now

    # Check if chain is complete
    if chain.is_complete:
        chain.status = ApprovalStatus.APPROVED
        chain.completed_at = now

    return approval


@router.delete(
    "/contracts/{contract_id}/versions/{version}/approval-chain",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cancel approval chain",
    description="Cancel an approval chain.",
)
async def cancel_approval_chain(
    contract_id: str,
    version: str,
) -> None:
    """Cancel an approval chain."""
    chain_key = _get_chain_key(contract_id, version)

    if chain_key not in _approval_chains:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "CHAIN_NOT_FOUND",
                "message": f"No approval chain found for {contract_id}@{version}",
            },
        )

    chain = _approval_chains[chain_key]

    # Mark as cancelled
    chain.status = ApprovalStatus.CANCELLED
    chain.completed_at = datetime.now(timezone.utc)

    # Cancel all pending approvals
    for approval in chain.approvals:
        if approval.status == ApprovalStatus.PENDING:
            approval.status = ApprovalStatus.CANCELLED


@router.get(
    "/approvals/pending",
    response_model=list[Approval],
    summary="List pending approvals",
    description="List all pending approvals for the current user.",
)
async def list_pending_approvals(
    user_id: str | None = None,
    email: str | None = None,
) -> list[Approval]:
    """List pending approvals, optionally filtered by user."""
    pending = []

    for chain in _approval_chains.values():
        if chain.status != ApprovalStatus.PENDING:
            continue

        current = chain.current_approval
        if not current:
            continue

        # Filter by user if specified
        if user_id and current.approver.user_id != user_id:
            continue
        if email and current.approver.email != email:
            continue

        pending.append(current)

    return pending
