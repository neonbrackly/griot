"""Contract CRUD and versioning endpoints."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from griot_core import Contract, load_contract_from_dict, lint_contract

from griot_registry.api.dependencies import ContractSvc, Storage
from griot_registry.auth import CurrentUser, OptionalUser, RequireEditor

router = APIRouter()


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
    service: ContractSvc,
    user: OptionalUser,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    status: str | None = Query(default=None, description="Filter by status"),
    schema_name: str | None = Query(default=None, description="Filter by schema name"),
    owner: str | None = Query(default=None, description="Filter by owner/team"),
) -> ContractListResponse:
    """List all contracts with optional filtering.

    Supports pagination and filtering by status, schema name, or owner.
    """
    contracts, total = await service.list_contracts(
        limit=limit,
        offset=offset,
        status=status,
        schema_name=schema_name,
        owner=owner,
    )

    return ContractListResponse(
        items=[c.to_dict() for c in contracts],
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
    request_data: dict[str, Any],
    service: ContractSvc,
    user: RequireEditor,
) -> dict[str, Any]:
    """Create a new contract.

    The contract will be created with the provided version (or 1.0.0 if not specified)
    and status 'draft'.

    The request body should be a valid ODCS contract in JSON format.
    """
    try:
        # Parse the contract using griot-core
        contract = load_contract_from_dict(request_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_CONTRACT", "message": f"Failed to parse contract: {e}"},
        )

    # Create via service (handles validation)
    result = await service.create_contract(contract, user)

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

    return result.contract.to_dict()


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
    service: ContractSvc,
    user: OptionalUser,
    version: str | None = Query(default=None, description="Specific version to retrieve"),
) -> dict[str, Any]:
    """Get a contract by ID.

    Optionally specify a version to retrieve a specific version.
    Defaults to the latest version.
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

    return contract.to_dict()


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
