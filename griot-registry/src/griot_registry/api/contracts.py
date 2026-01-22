"""Contract CRUD and versioning endpoints."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated, Any

from fastapi import APIRouter, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from griot_core import Contract, load_contract_from_dict, lint_contract

from griot_registry.api.dependencies import ContractSvc, Storage
from griot_registry.auth import CurrentUser, OptionalUser, RequireEditor, User

router = APIRouter()


# =============================================================================
# Schema Hydration Helper
# =============================================================================


async def _hydrate_schemas(
    contract_dict: dict[str, Any],
    storage: Storage,
) -> dict[str, Any]:
    """Hydrate schema refs in a contract with actual schema data.

    When a contract has schemaRefs, this function fetches the actual schemas
    from the schema repository and populates the 'schema' field.

    Args:
        contract_dict: Contract data as dictionary
        storage: Storage backend for fetching schemas

    Returns:
        Contract dict with hydrated schemas
    """
    schema_refs = contract_dict.get("schemaRefs") or contract_dict.get("schema_refs")
    if not schema_refs:
        return contract_dict

    hydrated_schemas = []
    for ref in schema_refs:
        schema_id = ref.get("schemaId") or ref.get("schema_id")
        version = ref.get("version")

        if not schema_id:
            continue

        # Fetch the schema
        if version:
            schema = await storage.schemas.get_version(schema_id, version)
        else:
            schema = await storage.schemas.get(schema_id)

        if schema:
            # Convert to ODCS format for embedding in contract
            schema_entry = {
                "id": schema.get("id"),
                "name": schema.get("name"),
                "physicalName": schema.get("physical_name") or schema.get("physicalName"),
                "logicalType": schema.get("logical_type") or schema.get("logicalType", "object"),
                "physicalType": schema.get("physical_type") or schema.get("physicalType", "table"),
                "description": schema.get("description"),
                "businessName": schema.get("business_name") or schema.get("businessName"),
                "tags": schema.get("tags", []),
                "authoritativeDefinitions": schema.get("authoritative_definitions") or schema.get("authoritativeDefinitions", []),
                "quality": schema.get("quality", []),
                "properties": schema.get("properties", []),
                # Add ref metadata
                "_ref": {
                    "schemaId": schema_id,
                    "version": version or schema.get("version"),
                    "resolvedAt": datetime.now(timezone.utc).isoformat(),
                },
            }
            hydrated_schemas.append(schema_entry)

    # Replace or add to existing schemas
    if hydrated_schemas:
        contract_dict["schema"] = hydrated_schemas
        # Also keep the refs for reference
        contract_dict["schemaRefs"] = schema_refs

    return contract_dict


# =============================================================================
# Request/Response Models
# =============================================================================


class ContractCreateRequest(BaseModel):
    """Request body for creating a contract."""

    # The full contract data in ODCS format
    # We accept the raw dict and parse it with griot-core
    model_config = {"extra": "allow"}


class ContractUpdateRequest(BaseModel):
    """Request body for updating a contract."""

    change_type: str = Field(
        default="minor",
        description="Type of change: patch, minor, major",
    )
    change_notes: str | None = Field(
        default=None,
        description="Notes describing the changes",
    )

    model_config = {"extra": "allow"}


class ContractListResponse(BaseModel):
    """Response for listing contracts."""

    items: list[dict[str, Any]]
    total: int
    limit: int
    offset: int


class VersionSummary(BaseModel):
    """Summary of a contract version."""

    contract_id: str
    version: str
    change_type: str | None = None
    change_notes: str | None = None
    is_breaking: bool = False
    created_at: str | None = None
    created_by: str | None = None


class VersionListResponse(BaseModel):
    """Response for listing versions."""

    items: list[VersionSummary]
    total: int


class BreakingChangeInfo(BaseModel):
    """Information about a breaking change."""

    change_type: str
    field: str | None
    description: str
    from_value: Any = None
    to_value: Any = None
    migration_hint: str | None = None


class BreakingChangesResponse(BaseModel):
    """Response when breaking changes are detected."""

    code: str = "BREAKING_CHANGES_DETECTED"
    message: str
    breaking_changes: list[BreakingChangeInfo]
    allow_breaking_hint: str = "Add ?allow_breaking=true to force the update"


class ValidationIssue(BaseModel):
    """A validation issue."""

    code: str
    field: str | None
    message: str
    severity: str
    suggestion: str | None = None


class ValidationResponse(BaseModel):
    """Validation result response."""

    is_valid: bool
    has_errors: bool
    has_warnings: bool
    error_count: int
    warning_count: int
    issues: list[ValidationIssue]


class StatusUpdateRequest(BaseModel):
    """Request to update contract status."""

    status: str = Field(..., description="New status: draft, active, deprecated, retired")


class SubmitForReviewRequest(BaseModel):
    """Request to submit contract for review."""

    message: str | None = Field(
        default=None,
        description="Optional message for reviewers",
    )


class ApproveContractRequest(BaseModel):
    """Request to approve a contract."""

    comment: str | None = Field(
        default=None,
        description="Optional approval comment",
    )


class RejectContractRequest(BaseModel):
    """Request to reject/request changes on a contract."""

    feedback: str = Field(
        ...,
        min_length=1,
        description="Required feedback explaining what needs to change",
    )


class DeprecateContractRequest(BaseModel):
    """Request to deprecate a contract."""

    reason: str = Field(
        ...,
        min_length=1,
        description="Required reason for deprecation",
    )
    replacement_contract_id: str | None = Field(
        default=None,
        alias="replacementContractId",
        description="ID of replacement contract (if any)",
    )

    model_config = {"populate_by_name": True}


class AssignReviewerRequest(BaseModel):
    """Request to assign a reviewer to a contract."""

    reviewer_type: str = Field(
        ...,
        alias="reviewerType",
        description="Type: 'user' or 'team'",
    )
    reviewer_id: str = Field(
        ...,
        alias="reviewerId",
        description="ID of user or team to assign",
    )

    model_config = {"populate_by_name": True}


# =============================================================================
# Contract CRUD Endpoints
# =============================================================================


@router.get(
    "/contracts",
    operation_id="listContracts",
    summary="List contracts",
    response_model=ContractListResponse,
)
async def list_contracts(
    request: Request,
    service: ContractSvc,
    user: OptionalUser,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    status: str | None = Query(default=None, description="Filter by status"),
    schema_name: str | None = Query(default=None, description="Filter by schema name"),
    owner: str | None = Query(default=None, description="Filter by owner/team"),
    hydrate_schemas: bool = Query(
        default=False,
        alias="hydrateSchemas",
        description="Whether to fetch full schema data for schemaRefs (slower)",
    ),
) -> ContractListResponse:
    """List all contracts with optional filtering.

    Supports pagination and filtering by status, schema name, or owner.

    Set hydrateSchemas=true to resolve schemaRefs to full schema data.
    Note: This is slower as it requires additional queries per contract.
    """
    contracts, total = await service.list_contracts(
        limit=limit,
        offset=offset,
        status=status,
        schema_name=schema_name,
        owner=owner,
    )

    items = [c.to_dict() for c in contracts]

    # Optionally hydrate schemas
    if hydrate_schemas:
        storage = request.app.state.storage
        items = [await _hydrate_schemas(item, storage) for item in items]

    return ContractListResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post(
    "/contracts",
    operation_id="createContract",
    summary="Create a contract",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Contract created successfully"},
        400: {"description": "Invalid contract data"},
        409: {"description": "Contract already exists"},
        422: {"description": "Validation failed"},
    },
)
async def create_contract(
    request: Request,
    request_data: dict[str, Any],
    service: ContractSvc,
    user: RequireEditor,
) -> dict[str, Any]:
    """Create a new contract.

    The contract will be created with the provided version (or 1.0.0 if not specified)
    and status 'draft'.

    The request body should be a valid ODCS contract in JSON format.
    Optionally include schemaRefs to reference standalone schemas.
    """
    # Extract schemaRefs before parsing (griot-core doesn't support schemaRefs)
    schema_refs = request_data.pop("schemaRefs", None) or request_data.pop("schema_refs", None)

    try:
        # Parse the contract using griot-core
        contract = load_contract_from_dict(request_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_CONTRACT", "message": f"Failed to parse contract: {e}"},
        )

    # Create via service (handles validation)
    result = await service.create_contract(contract, user, schema_refs=schema_refs)

    if not result.success:
        # Check if validation failed
        if result.validation and not result.validation.is_valid:
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={
                    "code": "VALIDATION_FAILED",
                    "message": "Contract validation failed",
                    "validation": result.validation.to_dict(),
                },
            )

        # Contract already exists
        if "already exists" in (result.error or ""):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"code": "CONFLICT", "message": result.error},
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "CREATE_FAILED", "message": result.error},
        )

    # Include schemaRefs in response if they were provided
    response = result.contract.to_dict()
    if schema_refs:
        response["schemaRefs"] = schema_refs

    return response


@router.get(
    "/contracts/{contract_id}",
    operation_id="getContract",
    summary="Get a contract",
    responses={
        404: {"description": "Contract not found"},
    },
)
async def get_contract(
    contract_id: str,
    request: Request,
    service: ContractSvc,
    user: OptionalUser,
    version: str | None = Query(default=None, description="Specific version to retrieve"),
    hydrate_schemas: bool = Query(
        default=True,
        alias="hydrateSchemas",
        description="Whether to fetch full schema data for schemaRefs",
    ),
) -> dict[str, Any]:
    """Get a contract by ID.

    Optionally specify a version to retrieve a specific version.
    Defaults to the latest version.

    When a contract uses schemaRefs (references to standalone schemas),
    the full schema data is fetched and included unless hydrateSchemas=false.
    """
    contract = await service.get_contract(contract_id, version)

    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "NOT_FOUND",
                "message": f"Contract '{contract_id}' not found"
                + (f" (version {version})" if version else ""),
            },
        )

    contract_dict = contract.to_dict()

    # Fetch schemaRefs from storage (griot-core Contract doesn't store these)
    storage = request.app.state.storage
    raw_doc = await storage.contracts._contracts.find_one({"id": contract_id})
    if raw_doc and "schemaRefs" in raw_doc:
        contract_dict["schemaRefs"] = raw_doc["schemaRefs"]

    # Hydrate schemas if requested and schemaRefs exist
    if hydrate_schemas:
        contract_dict = await _hydrate_schemas(contract_dict, storage)

    return contract_dict


@router.put(
    "/contracts/{contract_id}",
    operation_id="updateContract",
    summary="Update a contract",
    responses={
        400: {"description": "Invalid update data"},
        404: {"description": "Contract not found"},
        409: {"model": BreakingChangesResponse, "description": "Breaking changes detected"},
        422: {"description": "Validation failed"},
    },
)
async def update_contract(
    contract_id: str,
    request_data: dict[str, Any],
    service: ContractSvc,
    user: RequireEditor,
    allow_breaking: Annotated[
        bool,
        Query(description="Allow updates with breaking changes"),
    ] = False,
) -> dict[str, Any]:
    """Update a contract, creating a new version.

    The version number is automatically incremented based on change_type:
    - patch: 1.0.0 -> 1.0.1
    - minor: 1.0.0 -> 1.1.0
    - major: 1.0.0 -> 2.0.0

    Breaking changes are automatically detected and blocked by default.
    Use ?allow_breaking=true to force updates with breaking changes.
    """
    # Extract change metadata
    change_type = request_data.pop("change_type", "minor")
    change_notes = request_data.pop("change_notes", None)

    try:
        # Parse the contract using griot-core
        contract = load_contract_from_dict(request_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_CONTRACT", "message": f"Failed to parse contract: {e}"},
        )

    # Ensure contract ID matches
    if contract.id != contract_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "ID_MISMATCH",
                "message": f"Contract ID in body '{contract.id}' doesn't match URL '{contract_id}'",
            },
        )

    # Update via service
    try:
        result = await service.update_contract(
            contract_id=contract_id,
            updated_contract=contract,
            change_type=change_type,
            change_notes=change_notes,
            allow_breaking=allow_breaking,
            user=user,
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "UPDATE_ERROR", "message": f"Error during update: {e}"},
        )

    if not result.success:
        # Breaking changes blocked
        if result.blocked_by_breaking:
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content=BreakingChangesResponse(
                    message=f"Update contains {len(result.breaking_changes)} breaking change(s)",
                    breaking_changes=[
                        BreakingChangeInfo(
                            change_type=bc.change_type,
                            field=bc.field,
                            description=bc.description,
                            from_value=bc.from_value,
                            to_value=bc.to_value,
                            migration_hint=bc.migration_hint,
                        )
                        for bc in result.breaking_changes
                    ],
                ).model_dump(),
            )

        # Validation failed
        if result.validation and not result.validation.is_valid:
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={
                    "code": "VALIDATION_FAILED",
                    "message": "Contract validation failed",
                    "validation": result.validation.to_dict(),
                },
            )

        # Not found
        if "not found" in (result.error or "").lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "NOT_FOUND", "message": result.error},
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "UPDATE_FAILED", "message": result.error},
        )

    return result.contract.to_dict()


@router.patch(
    "/contracts/{contract_id}/status",
    operation_id="updateContractStatus",
    summary="Update contract status",
    responses={
        400: {"description": "Invalid status transition"},
        404: {"description": "Contract not found"},
    },
)
async def update_contract_status(
    contract_id: str,
    request: StatusUpdateRequest,
    service: ContractSvc,
    user: RequireEditor,
) -> dict[str, Any]:
    """Update the status of a contract.

    Valid status transitions:
    - draft -> active, deprecated
    - active -> deprecated
    - deprecated -> retired
    """
    try:
        contract = await service.update_status(contract_id, request.status, user)
        return contract.to_dict()
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "NOT_FOUND", "message": error_msg},
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_TRANSITION", "message": error_msg},
        )


@router.delete(
    "/contracts/{contract_id}",
    operation_id="deprecateContract",
    summary="Deprecate a contract",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {"description": "Contract not found"},
    },
)
async def deprecate_contract(
    contract_id: str,
    service: ContractSvc,
    user: RequireEditor,
) -> None:
    """Deprecate a contract.

    This marks the contract as deprecated but does not delete it.
    Deprecated contracts remain accessible but should not be used for new data.
    """
    success = await service.deprecate_contract(contract_id, user)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": f"Contract '{contract_id}' not found"},
        )


# =============================================================================
# Workflow Endpoints (submit, approve, reject, deprecate)
# =============================================================================


def _utc_now() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(timezone.utc)


@router.post(
    "/contracts/{contract_id}/submit",
    operation_id="submitContract",
    summary="Submit contract for review",
    responses={
        200: {"description": "Contract submitted successfully"},
        400: {"description": "Invalid status transition or missing reviewer"},
        403: {"description": "Not authorized to submit"},
        404: {"description": "Contract not found"},
    },
)
async def submit_contract(
    contract_id: str,
    request: Request,
    body: SubmitForReviewRequest,
    service: ContractSvc,
    user: CurrentUser,
) -> dict[str, Any]:
    """Submit a contract for review.

    Only contracts in 'draft' status can be submitted.
    A reviewer must be assigned before submission.
    """
    storage = request.app.state.storage

    # Get contract
    contract = await service.get_contract(contract_id)
    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": f"Contract '{contract_id}' not found"},
        )

    contract_dict = contract.to_dict()

    # Check status
    current_status = contract_dict.get("status", "draft")
    if current_status != "draft":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_STATUS_TRANSITION",
                "message": f"Cannot submit contract: contract must be in draft status (current: {current_status})",
            },
        )

    # Check reviewer is assigned
    if not contract_dict.get("reviewer_id"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "REVIEWER_REQUIRED",
                "message": "Cannot submit contract: no reviewer assigned",
            },
        )

    # Check ownership (only owner can submit)
    owner_id = contract_dict.get("created_by") or contract_dict.get("owner")
    is_admin = any(r.value == "admin" for r in user.roles)
    if owner_id != user.id and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "NOT_AUTHORIZED",
                "message": "Only the contract owner can submit for review",
            },
        )

    # Update contract
    now = _utc_now()
    updated = await storage.contracts.update_status(
        contract_id,
        "pending_review",
        updated_by=user.id,
    )

    # Add workflow fields
    await storage.contracts.update(
        contract_id,
        Contract.from_dict({
            **updated.to_dict(),
            "submitted_by": user.id,
            "submitted_at": now.isoformat(),
            "submission_message": body.message,
        }),
    )

    # TODO: Create notification for reviewer

    result = await service.get_contract(contract_id)
    return result.to_dict()


@router.post(
    "/contracts/{contract_id}/approve",
    operation_id="approveContract",
    summary="Approve a contract",
    responses={
        200: {"description": "Contract approved successfully"},
        400: {"description": "Invalid status transition"},
        403: {"description": "Not authorized to approve"},
        404: {"description": "Contract not found"},
    },
)
async def approve_contract(
    contract_id: str,
    request: Request,
    body: ApproveContractRequest,
    service: ContractSvc,
    user: CurrentUser,
) -> dict[str, Any]:
    """Approve a contract.

    Only contracts in 'pending_review' status can be approved.
    Only the assigned reviewer or an admin can approve.
    """
    storage = request.app.state.storage

    # Get contract
    contract = await service.get_contract(contract_id)
    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": f"Contract '{contract_id}' not found"},
        )

    contract_dict = contract.to_dict()

    # Check status
    current_status = contract_dict.get("status", "draft")
    if current_status != "pending_review":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_STATUS_TRANSITION",
                "message": f"Cannot approve contract: contract must be in pending_review status (current: {current_status})",
            },
        )

    # Check authorization (reviewer or admin)
    is_admin = any(r.value == "admin" for r in user.roles)
    reviewer_id = contract_dict.get("reviewer_id")
    is_reviewer = reviewer_id == user.id

    # Check team membership if reviewer is a team
    reviewer_type = contract_dict.get("reviewer_type", "user")
    if reviewer_type == "team" and reviewer_id:
        team = await storage.teams.get(reviewer_id)
        if team:
            is_reviewer = any(m.get("user_id") == user.id for m in team.get("members", []))

    if not is_reviewer and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "NOT_AUTHORIZED",
                "message": "You are not authorized to approve this contract",
            },
        )

    # Update contract
    now = _utc_now()
    updated = await storage.contracts.update_status(
        contract_id,
        "active",
        updated_by=user.id,
    )

    # Add approval fields
    await storage.contracts.update(
        contract_id,
        Contract.from_dict({
            **updated.to_dict(),
            "approved_by": user.id,
            "approved_at": now.isoformat(),
            "approval_comment": body.comment,
        }),
    )

    # TODO: Create notification for owner

    result = await service.get_contract(contract_id)
    return result.to_dict()


@router.post(
    "/contracts/{contract_id}/reject",
    operation_id="rejectContract",
    summary="Reject a contract (request changes)",
    responses={
        200: {"description": "Contract rejected successfully"},
        400: {"description": "Invalid status transition or missing feedback"},
        403: {"description": "Not authorized to reject"},
        404: {"description": "Contract not found"},
    },
)
async def reject_contract(
    contract_id: str,
    request: Request,
    body: RejectContractRequest,
    service: ContractSvc,
    user: CurrentUser,
) -> dict[str, Any]:
    """Reject a contract and request changes.

    Only contracts in 'pending_review' status can be rejected.
    Feedback is required to explain what needs to change.
    Contract returns to 'draft' status.
    """
    storage = request.app.state.storage

    # Get contract
    contract = await service.get_contract(contract_id)
    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": f"Contract '{contract_id}' not found"},
        )

    contract_dict = contract.to_dict()

    # Check status
    current_status = contract_dict.get("status", "draft")
    if current_status != "pending_review":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_STATUS_TRANSITION",
                "message": f"Cannot reject contract: contract must be in pending_review status (current: {current_status})",
            },
        )

    # Check authorization (reviewer or admin)
    is_admin = any(r.value == "admin" for r in user.roles)
    reviewer_id = contract_dict.get("reviewer_id")
    is_reviewer = reviewer_id == user.id

    # Check team membership if reviewer is a team
    reviewer_type = contract_dict.get("reviewer_type", "user")
    if reviewer_type == "team" and reviewer_id:
        team = await storage.teams.get(reviewer_id)
        if team:
            is_reviewer = any(m.get("user_id") == user.id for m in team.get("members", []))

    if not is_reviewer and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "NOT_AUTHORIZED",
                "message": "You are not authorized to reject this contract",
            },
        )

    # Update contract
    now = _utc_now()
    updated = await storage.contracts.update_status(
        contract_id,
        "draft",
        updated_by=user.id,
    )

    # Add rejection fields
    await storage.contracts.update(
        contract_id,
        Contract.from_dict({
            **updated.to_dict(),
            "rejected_by": user.id,
            "rejected_at": now.isoformat(),
            "review_feedback": body.feedback,
        }),
    )

    # TODO: Create notification for owner

    result = await service.get_contract(contract_id)
    return result.to_dict()


@router.post(
    "/contracts/{contract_id}/deprecate",
    operation_id="deprecateContractWithReason",
    summary="Deprecate a contract with reason",
    responses={
        200: {"description": "Contract deprecated successfully"},
        400: {"description": "Invalid status transition or replacement contract"},
        403: {"description": "Not authorized to deprecate"},
        404: {"description": "Contract not found"},
    },
)
async def deprecate_contract_with_reason(
    contract_id: str,
    request: Request,
    body: DeprecateContractRequest,
    service: ContractSvc,
    user: CurrentUser,
) -> dict[str, Any]:
    """Deprecate a contract with a reason.

    Only contracts in 'active' status can be deprecated.
    A reason is required.
    If a replacement contract is specified, it must exist and be active.
    """
    storage = request.app.state.storage

    # Get contract
    contract = await service.get_contract(contract_id)
    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": f"Contract '{contract_id}' not found"},
        )

    contract_dict = contract.to_dict()

    # Check status
    current_status = contract_dict.get("status", "draft")
    if current_status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_STATUS_TRANSITION",
                "message": f"Cannot deprecate contract: contract must be in active status (current: {current_status})",
            },
        )

    # Check ownership (only owner or admin can deprecate)
    owner_id = contract_dict.get("created_by") or contract_dict.get("owner")
    is_admin = any(r.value == "admin" for r in user.roles)
    if owner_id != user.id and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "NOT_AUTHORIZED",
                "message": "You are not authorized to deprecate this contract",
            },
        )

    # Validate replacement contract if provided
    if body.replacement_contract_id:
        replacement = await service.get_contract(body.replacement_contract_id)
        if replacement is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "INVALID_REPLACEMENT",
                    "message": f"Replacement contract '{body.replacement_contract_id}' not found",
                },
            )
        replacement_status = replacement.to_dict().get("status", "draft")
        if replacement_status != "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "INVALID_REPLACEMENT",
                    "message": "Replacement contract must be active",
                },
            )

    # Update contract
    now = _utc_now()
    await storage.contracts.update_status(
        contract_id,
        "deprecated",
        updated_by=user.id,
    )

    # Add deprecation metadata (doesn't create a new version)
    await storage.contracts.update_metadata(
        contract_id,
        {
            "deprecated_by": user.id,
            "deprecated_at": now.isoformat(),
            "deprecation_reason": body.reason,
            "replacement_contract_id": body.replacement_contract_id,
        },
        updated_by=user.id,
    )

    result = await service.get_contract(contract_id)
    return result.to_dict()


@router.post(
    "/contracts/{contract_id}/reviewer",
    operation_id="assignReviewer",
    summary="Assign a reviewer to a contract",
    responses={
        200: {"description": "Reviewer assigned successfully"},
        400: {"description": "Invalid reviewer"},
        403: {"description": "Not authorized to assign reviewer"},
        404: {"description": "Contract not found"},
    },
)
async def assign_reviewer(
    contract_id: str,
    request: Request,
    body: AssignReviewerRequest,
    service: ContractSvc,
    user: CurrentUser,
) -> dict[str, Any]:
    """Assign a reviewer (user or team) to a contract.

    Only the contract owner or an admin can assign a reviewer.
    """
    storage = request.app.state.storage

    # Get contract
    contract = await service.get_contract(contract_id)
    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": f"Contract '{contract_id}' not found"},
        )

    contract_dict = contract.to_dict()

    # Check ownership (only owner or admin can assign reviewer)
    owner_id = contract_dict.get("created_by") or contract_dict.get("owner")
    is_admin = any(r.value == "admin" for r in user.roles)
    if owner_id != user.id and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "NOT_AUTHORIZED",
                "message": "Only the contract owner can assign a reviewer",
            },
        )

    # Validate reviewer
    reviewer_name = None
    if body.reviewer_type == "user":
        reviewer = await storage.users.get(body.reviewer_id)
        if not reviewer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "INVALID_REVIEWER",
                    "message": f"User '{body.reviewer_id}' not found",
                },
            )
        reviewer_name = reviewer.get("name")
    elif body.reviewer_type == "team":
        reviewer = await storage.teams.get(body.reviewer_id)
        if not reviewer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "INVALID_REVIEWER",
                    "message": f"Team '{body.reviewer_id}' not found",
                },
            )
        reviewer_name = reviewer.get("name")
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_REVIEWER_TYPE",
                "message": "reviewer_type must be 'user' or 'team'",
            },
        )

    # Update contract metadata (doesn't create a new version)
    await storage.contracts.update_metadata(
        contract_id,
        {
            "reviewer_type": body.reviewer_type,
            "reviewer_id": body.reviewer_id,
            "reviewer_name": reviewer_name,
        },
        updated_by=user.id,
    )

    result = await service.get_contract(contract_id)
    return result.to_dict()


# =============================================================================
# Version Endpoints
# =============================================================================


@router.get(
    "/contracts/{contract_id}/versions",
    operation_id="listVersions",
    summary="List contract versions",
    response_model=VersionListResponse,
    responses={
        404: {"description": "Contract not found"},
    },
)
async def list_versions(
    contract_id: str,
    storage: Storage,
    user: OptionalUser,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> VersionListResponse:
    """List all versions of a contract."""
    # Check contract exists
    if not await storage.contracts.exists(contract_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": f"Contract '{contract_id}' not found"},
        )

    versions, total = await storage.contracts.list_versions(
        contract_id,
        limit=limit,
        offset=offset,
    )

    return VersionListResponse(
        items=[
            VersionSummary(
                contract_id=contract_id,
                version=v.get("version", ""),
                change_type=v.get("change_type"),
                change_notes=v.get("change_notes"),
                is_breaking=v.get("is_breaking", False),
                created_at=v.get("created_at").isoformat() if v.get("created_at") else None,
                created_by=v.get("created_by"),
            )
            for v in versions
        ],
        total=total,
    )


@router.get(
    "/contracts/{contract_id}/versions/{version}",
    operation_id="getVersion",
    summary="Get a specific version",
    responses={
        404: {"description": "Contract or version not found"},
    },
)
async def get_version(
    contract_id: str,
    version: str,
    service: ContractSvc,
    user: OptionalUser,
) -> dict[str, Any]:
    """Get a specific version of a contract."""
    contract = await service.get_contract(contract_id, version)

    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "NOT_FOUND",
                "message": f"Contract '{contract_id}' version '{version}' not found",
            },
        )

    return contract.to_dict()


# =============================================================================
# Validation Endpoint
# =============================================================================


@router.post(
    "/contracts/validate",
    operation_id="validateContract",
    summary="Validate a contract without storing",
    response_model=ValidationResponse,
)
async def validate_contract(
    request_data: dict[str, Any],
    service: ContractSvc,
    user: OptionalUser,
) -> ValidationResponse:
    """Validate a contract without storing it.

    Useful for checking if a contract is valid before creating or updating.
    """
    try:
        contract = load_contract_from_dict(request_data)
    except Exception as e:
        return ValidationResponse(
            is_valid=False,
            has_errors=True,
            has_warnings=False,
            error_count=1,
            warning_count=0,
            issues=[
                ValidationIssue(
                    code="PARSE_ERROR",
                    field=None,
                    message=f"Failed to parse contract: {e}",
                    severity="error",
                )
            ],
        )

    result = service.validation_service.validate(contract)

    return ValidationResponse(
        is_valid=result.is_valid,
        has_errors=result.has_errors,
        has_warnings=result.has_warnings,
        error_count=sum(1 for i in result.lint_issues if i.severity.value == "error"),
        warning_count=sum(1 for i in result.lint_issues if i.severity.value == "warning"),
        issues=[
            ValidationIssue(
                code=i.code,
                field=i.field,
                message=i.message,
                severity=i.severity.value,
                suggestion=i.suggestion,
            )
            for i in result.lint_issues
        ],
    )
