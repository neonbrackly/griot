"""Contract CRUD and versioning endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from fastapi.responses import PlainTextResponse

from griot_registry.schemas import (
    Contract,
    ContractCreate,
    ContractDiff,
    ContractList,
    ContractUpdate,
    ErrorResponse,
    VersionList,
)
from griot_registry.storage.base import StorageBackend

router = APIRouter()


async def get_storage(request: Request) -> StorageBackend:
    """Dependency to get storage backend from app state."""
    return request.app.state.storage


StorageDep = Annotated[StorageBackend, Depends(get_storage)]


# =============================================================================
# Contract CRUD
# =============================================================================
@router.get(
    "/contracts",
    response_model=ContractList,
    operation_id="listContracts",
)
async def list_contracts(
    storage: StorageDep,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    status: str | None = None,
    owner: str | None = None,
) -> ContractList:
    """List all contracts with optional filtering."""
    return await storage.list_contracts(
        limit=limit,
        offset=offset,
        status=status,
        owner=owner,
    )


@router.post(
    "/contracts",
    response_model=Contract,
    status_code=status.HTTP_201_CREATED,
    operation_id="createContract",
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        409: {"model": ErrorResponse, "description": "Contract ID already exists"},
    },
)
async def create_contract(
    storage: StorageDep,
    contract: ContractCreate,
) -> Contract:
    """Create a new contract.

    The contract will be created with version 1.0.0 and status 'draft'.
    """
    # Check if contract already exists
    existing = await storage.get_contract(contract.id)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "CONFLICT", "message": f"Contract '{contract.id}' already exists"},
        )

    return await storage.create_contract(contract)


@router.get(
    "/contracts/{contract_id}",
    response_model=Contract,
    operation_id="getContract",
    responses={404: {"model": ErrorResponse}},
)
async def get_contract(
    storage: StorageDep,
    contract_id: str,
    version: str | None = None,
    request: Request = None,
) -> Contract | Response:
    """Get a contract by ID.

    Optionally specify a version to retrieve a specific version.
    Defaults to the latest version.

    Supports content negotiation:
    - application/json (default): Returns JSON
    - application/x-yaml: Returns YAML
    """
    contract = await storage.get_contract(contract_id, version=version)
    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": f"Contract '{contract_id}' not found"},
        )

    # Content negotiation for YAML response
    if request and "application/x-yaml" in request.headers.get("accept", ""):
        yaml_content = await storage.get_contract_yaml(contract_id, version=version)
        return PlainTextResponse(content=yaml_content, media_type="application/x-yaml")

    return contract


@router.put(
    "/contracts/{contract_id}",
    response_model=Contract,
    operation_id="updateContract",
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
)
async def update_contract(
    storage: StorageDep,
    contract_id: str,
    update: ContractUpdate,
) -> Contract:
    """Update a contract, creating a new version.

    The version number is automatically incremented based on change_type:
    - patch: 1.0.0 -> 1.0.1
    - minor: 1.0.0 -> 1.1.0
    - major: 1.0.0 -> 2.0.0
    """
    contract = await storage.get_contract(contract_id)
    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": f"Contract '{contract_id}' not found"},
        )

    return await storage.update_contract(contract_id, update)


@router.delete(
    "/contracts/{contract_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="deprecateContract",
    responses={404: {"model": ErrorResponse}},
)
async def deprecate_contract(
    storage: StorageDep,
    contract_id: str,
) -> None:
    """Deprecate a contract.

    This marks the contract as deprecated but does not delete it.
    Deprecated contracts remain accessible but should not be used for new data.
    """
    contract = await storage.get_contract(contract_id)
    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": f"Contract '{contract_id}' not found"},
        )

    await storage.deprecate_contract(contract_id)


# =============================================================================
# Versions
# =============================================================================
@router.get(
    "/contracts/{contract_id}/versions",
    response_model=VersionList,
    operation_id="listVersions",
    responses={404: {"model": ErrorResponse}},
)
async def list_versions(
    storage: StorageDep,
    contract_id: str,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> VersionList:
    """List all versions of a contract."""
    contract = await storage.get_contract(contract_id)
    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": f"Contract '{contract_id}' not found"},
        )

    return await storage.list_versions(contract_id, limit=limit, offset=offset)


@router.get(
    "/contracts/{contract_id}/versions/{version}",
    response_model=Contract,
    operation_id="getVersion",
    responses={404: {"model": ErrorResponse}},
)
async def get_version(
    storage: StorageDep,
    contract_id: str,
    version: str,
) -> Contract:
    """Get a specific version of a contract."""
    contract = await storage.get_contract(contract_id, version=version)
    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "NOT_FOUND",
                "message": f"Contract '{contract_id}' version '{version}' not found",
            },
        )

    return contract


@router.get(
    "/contracts/{contract_id}/diff",
    response_model=ContractDiff,
    operation_id="diffVersions",
    responses={404: {"model": ErrorResponse}},
)
async def diff_versions(
    storage: StorageDep,
    contract_id: str,
    from_version: Annotated[str, Query(alias="from")],
    to_version: Annotated[str, Query(alias="to")],
) -> ContractDiff:
    """Compare two versions of a contract.

    Returns the differences between the versions including:
    - Added/removed fields
    - Type changes
    - Constraint changes
    - Whether changes are breaking
    """
    # Verify contract exists
    contract = await storage.get_contract(contract_id)
    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": f"Contract '{contract_id}' not found"},
        )

    # Get both versions
    from_contract = await storage.get_contract(contract_id, version=from_version)
    if from_contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": f"Version '{from_version}' not found"},
        )

    to_contract = await storage.get_contract(contract_id, version=to_version)
    if to_contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": f"Version '{to_version}' not found"},
        )

    return await storage.diff_contracts(from_contract, to_contract)
