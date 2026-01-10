"""Approval chain endpoints for contract governance (FR-REG-008)."""

from datetime import datetime, timezone
from typing import Annotated, Literal
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, Field

from griot_registry.schemas import ErrorResponse
from griot_registry.storage.base import StorageBackend

router = APIRouter()


# =============================================================================
# Schemas
# =============================================================================
class ApprovalRequest(BaseModel):
    """Request to create an approval."""

    contract_id: str
    version: str
    approver: str = Field(..., description="User ID or email of the approver")
    role: Literal["owner", "data_steward", "compliance", "security"] = Field(
        ..., description="Role of the approver in the chain"
    )
    comments: str | None = None


class ApprovalDecision(BaseModel):
    """Approval decision from a reviewer."""

    decision: Literal["approve", "reject", "request_changes"]
    comments: str | None = None


class Approval(BaseModel):
    """An approval record."""

    id: UUID
    contract_id: str
    version: str
    approver: str
    role: str
    status: Literal["pending", "approved", "rejected", "changes_requested"]
    comments: str | None = None
    decision_comments: str | None = None
    requested_at: datetime
    decided_at: datetime | None = None


class ApprovalChain(BaseModel):
    """The full approval chain for a contract version."""

    contract_id: str
    version: str
    status: Literal["pending", "approved", "rejected", "draft"]
    required_approvals: list[str]  # Roles required
    approvals: list[Approval]
    created_at: datetime
    completed_at: datetime | None = None


class ApprovalChainCreate(BaseModel):
    """Request to create an approval chain."""

    contract_id: str
    version: str
    required_roles: list[str] = Field(
        default=["owner", "data_steward"],
        description="Roles required to approve this contract",
    )


class ApprovalChainList(BaseModel):
    """List of approval chains."""

    items: list[ApprovalChain]
    total: int


# =============================================================================
# In-memory storage (would be moved to storage backend in production)
# =============================================================================
_approval_chains: dict[str, ApprovalChain] = {}
_approvals: dict[str, Approval] = {}


def _get_chain_key(contract_id: str, version: str) -> str:
    """Generate a key for the approval chain."""
    return f"{contract_id}:{version}"


# =============================================================================
# Dependencies
# =============================================================================
async def get_storage(request: Request) -> StorageBackend:
    """Dependency to get storage backend from app state."""
    return request.app.state.storage


StorageDep = Annotated[StorageBackend, Depends(get_storage)]


# =============================================================================
# Endpoints
# =============================================================================
@router.post(
    "/contracts/{contract_id}/versions/{version}/approval-chain",
    response_model=ApprovalChain,
    status_code=status.HTTP_201_CREATED,
    operation_id="createApprovalChain",
    responses={
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse, "description": "Approval chain already exists"},
    },
)
async def create_approval_chain(
    storage: StorageDep,
    contract_id: str,
    version: str,
    chain_request: ApprovalChainCreate,
) -> ApprovalChain:
    """Create an approval chain for a contract version.

    This initiates the approval process for a contract. The contract must
    exist and the specified version must be valid.

    Required approvers are determined by the required_roles parameter.
    Common roles include:
    - owner: Contract owner/author
    - data_steward: Data governance team
    - compliance: Compliance/legal team
    - security: Security team
    """
    # Verify contract exists
    contract = await storage.get_contract(contract_id, version=version)
    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "NOT_FOUND",
                "message": f"Contract '{contract_id}' version '{version}' not found",
            },
        )

    # Check if chain already exists
    chain_key = _get_chain_key(contract_id, version)
    if chain_key in _approval_chains:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "CONFLICT",
                "message": f"Approval chain already exists for '{contract_id}' v{version}",
            },
        )

    now = datetime.now(timezone.utc)
    chain = ApprovalChain(
        contract_id=contract_id,
        version=version,
        status="pending",
        required_approvals=chain_request.required_roles,
        approvals=[],
        created_at=now,
        completed_at=None,
    )

    _approval_chains[chain_key] = chain
    return chain


@router.get(
    "/contracts/{contract_id}/versions/{version}/approval-chain",
    response_model=ApprovalChain,
    operation_id="getApprovalChain",
    responses={404: {"model": ErrorResponse}},
)
async def get_approval_chain(
    storage: StorageDep,
    contract_id: str,
    version: str,
) -> ApprovalChain:
    """Get the approval chain for a contract version."""
    chain_key = _get_chain_key(contract_id, version)

    if chain_key not in _approval_chains:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "NOT_FOUND",
                "message": f"No approval chain for '{contract_id}' v{version}",
            },
        )

    return _approval_chains[chain_key]


@router.post(
    "/contracts/{contract_id}/versions/{version}/approvals",
    response_model=Approval,
    status_code=status.HTTP_201_CREATED,
    operation_id="requestApproval",
    responses={
        404: {"model": ErrorResponse},
        400: {"model": ErrorResponse},
    },
)
async def request_approval(
    storage: StorageDep,
    contract_id: str,
    version: str,
    request: ApprovalRequest,
) -> Approval:
    """Request approval from a specific approver.

    Adds a pending approval request to the chain for the specified approver
    and role.
    """
    chain_key = _get_chain_key(contract_id, version)

    if chain_key not in _approval_chains:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "NOT_FOUND",
                "message": f"No approval chain for '{contract_id}' v{version}. Create one first.",
            },
        )

    chain = _approval_chains[chain_key]

    # Check if role is required
    if request.role not in chain.required_approvals:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_ROLE",
                "message": f"Role '{request.role}' is not in the required approvals list",
            },
        )

    # Check if this role already has an approval
    existing = [a for a in chain.approvals if a.role == request.role and a.status == "pending"]
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "DUPLICATE_REQUEST",
                "message": f"Pending approval already exists for role '{request.role}'",
            },
        )

    now = datetime.now(timezone.utc)
    approval = Approval(
        id=uuid4(),
        contract_id=contract_id,
        version=version,
        approver=request.approver,
        role=request.role,
        status="pending",
        comments=request.comments,
        requested_at=now,
    )

    chain.approvals.append(approval)
    _approvals[str(approval.id)] = approval

    return approval


@router.post(
    "/approvals/{approval_id}/decision",
    response_model=Approval,
    operation_id="submitApprovalDecision",
    responses={
        404: {"model": ErrorResponse},
        400: {"model": ErrorResponse},
    },
)
async def submit_approval_decision(
    approval_id: str,
    decision: ApprovalDecision,
) -> Approval:
    """Submit a decision for a pending approval.

    Approvers can:
    - approve: Approve the contract version
    - reject: Reject the contract version
    - request_changes: Request changes before approval
    """
    if approval_id not in _approvals:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Approval not found"},
        )

    approval = _approvals[approval_id]

    if approval.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "ALREADY_DECIDED",
                "message": f"Approval already has status: {approval.status}",
            },
        )

    now = datetime.now(timezone.utc)

    # Update approval
    if decision.decision == "approve":
        approval.status = "approved"
    elif decision.decision == "reject":
        approval.status = "rejected"
    else:
        approval.status = "changes_requested"

    approval.decision_comments = decision.comments
    approval.decided_at = now

    # Update chain status
    chain_key = _get_chain_key(approval.contract_id, approval.version)
    if chain_key in _approval_chains:
        chain = _approval_chains[chain_key]
        _update_chain_status(chain)

    return approval


@router.get(
    "/approvals",
    response_model=ApprovalChainList,
    operation_id="listApprovalChains",
)
async def list_approval_chains(
    contract_id: str | None = None,
    status: Literal["pending", "approved", "rejected", "draft"] | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> ApprovalChainList:
    """List approval chains with optional filtering."""
    chains = list(_approval_chains.values())

    # Filter
    if contract_id:
        chains = [c for c in chains if c.contract_id == contract_id]
    if status:
        chains = [c for c in chains if c.status == status]

    # Sort by created_at descending
    chains.sort(key=lambda c: c.created_at, reverse=True)

    total = len(chains)
    items = chains[offset : offset + limit]

    return ApprovalChainList(items=items, total=total)


@router.get(
    "/contracts/{contract_id}/approval-status",
    operation_id="getContractApprovalStatus",
    responses={404: {"model": ErrorResponse}},
)
async def get_contract_approval_status(
    storage: StorageDep,
    contract_id: str,
) -> dict:
    """Get approval status summary for all versions of a contract."""
    # Verify contract exists
    contract = await storage.get_contract(contract_id)
    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": f"Contract '{contract_id}' not found"},
        )

    # Get all chains for this contract
    chains = [c for c in _approval_chains.values() if c.contract_id == contract_id]

    versions_status = {}
    for chain in chains:
        versions_status[chain.version] = {
            "status": chain.status,
            "required": chain.required_approvals,
            "approved_by": [
                a.role for a in chain.approvals if a.status == "approved"
            ],
            "pending": [
                a.role for a in chain.approvals if a.status == "pending"
            ],
        }

    return {
        "contract_id": contract_id,
        "latest_version": contract.version,
        "versions": versions_status,
    }


# =============================================================================
# Helper functions
# =============================================================================
def _update_chain_status(chain: ApprovalChain) -> None:
    """Update the overall chain status based on individual approvals."""
    approved_roles = {a.role for a in chain.approvals if a.status == "approved"}
    rejected = any(a.status == "rejected" for a in chain.approvals)
    changes_requested = any(a.status == "changes_requested" for a in chain.approvals)

    if rejected:
        chain.status = "rejected"
        chain.completed_at = datetime.now(timezone.utc)
    elif changes_requested:
        chain.status = "pending"  # Stay pending until changes addressed
    elif approved_roles.issuperset(set(chain.required_approvals)):
        chain.status = "approved"
        chain.completed_at = datetime.now(timezone.utc)
    else:
        chain.status = "pending"
