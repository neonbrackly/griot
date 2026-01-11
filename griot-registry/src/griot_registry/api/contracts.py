"""Contract CRUD and versioning endpoints.

Includes breaking change validation (T-304, T-371, T-372) that:
- Detects breaking changes when updating contracts
- Blocks updates with breaking changes by default
- Allows forcing updates with ?allow_breaking=true
"""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from fastapi.responses import JSONResponse, PlainTextResponse

from griot_registry.schemas import (
    BreakingChangeInfo,
    BreakingChangesResponse,
    Contract,
    ContractCreate,
    ContractDiff,
    ContractList,
    ContractUpdate,
    ErrorResponse,
    FieldDefinition,
    VersionList,
)
from griot_registry.storage.base import StorageBackend

router = APIRouter()


# =============================================================================
# Breaking Change Detection Helpers (T-304, T-371)
# =============================================================================
def _contract_to_dict(contract: Contract) -> dict[str, Any]:
    """Convert a registry Contract to a dictionary for griot-core."""
    return {
        "id": contract.id,
        "name": contract.name,
        "description": contract.description,
        "version": contract.version,
        "status": contract.status,
        "fields": [
            {
                "name": f.name,
                "type": f.type,
                "description": f.description,
                "nullable": f.nullable,
                "primary_key": f.primary_key,
                "unique": f.unique,
                "constraints": f.constraints.model_dump(exclude_none=True) if f.constraints else {},
                "metadata": f.metadata.model_dump(exclude_none=True) if f.metadata else {},
            }
            for f in contract.fields
        ],
    }


def _proposed_update_to_dict(
    current: Contract,
    update: ContractUpdate,
) -> dict[str, Any]:
    """Create a dictionary representing the proposed contract state after update."""
    return {
        "id": current.id,
        "name": update.name if update.name else current.name,
        "description": update.description if update.description else current.description,
        "version": "proposed",  # Temporary version for comparison
        "status": current.status,
        "fields": [
            {
                "name": f.name,
                "type": f.type,
                "description": f.description,
                "nullable": f.nullable,
                "primary_key": f.primary_key,
                "unique": f.unique,
                "constraints": f.constraints.model_dump(exclude_none=True) if f.constraints else {},
                "metadata": f.metadata.model_dump(exclude_none=True) if f.metadata else {},
            }
            for f in (update.fields if update.fields else current.fields)
        ],
    }


def detect_breaking_changes_for_update(
    current: Contract,
    update: ContractUpdate,
) -> list[BreakingChangeInfo]:
    """
    Detect breaking changes between current contract and proposed update.

    Uses griot-core's detect_breaking_changes() function (T-301) to identify
    any changes that could break existing data consumers.

    Args:
        current: The current contract version.
        update: The proposed update.

    Returns:
        List of BreakingChangeInfo objects describing breaking changes.
    """
    try:
        from griot_core.contract import detect_breaking_changes, load_contract_from_dict

        # Convert to griot-core models
        current_dict = _contract_to_dict(current)
        proposed_dict = _proposed_update_to_dict(current, update)

        current_model = load_contract_from_dict(current_dict)
        proposed_model = load_contract_from_dict(proposed_dict)

        # Detect breaking changes using griot-core
        breaking_changes = detect_breaking_changes(current_model, proposed_model)

        # Convert to API response format
        return [
            BreakingChangeInfo(
                change_type=bc.change_type.value,
                field=bc.field,
                description=bc.description,
                from_value=bc.from_value,
                to_value=bc.to_value,
                migration_hint=bc.migration_hint,
            )
            for bc in breaking_changes
        ]
    except ImportError:
        # griot-core not available, fall back to basic detection
        return _fallback_breaking_change_detection(current, update)


def _fallback_breaking_change_detection(
    current: Contract,
    update: ContractUpdate,
) -> list[BreakingChangeInfo]:
    """
    Fallback breaking change detection when griot-core is not available.

    Performs basic detection of:
    - Removed fields
    - Type changes
    - Nullable to required changes
    """
    if not update.fields:
        return []

    breaking_changes: list[BreakingChangeInfo] = []
    current_fields = {f.name: f for f in current.fields}
    new_fields = {f.name: f for f in update.fields}

    # Check for removed fields
    for name in current_fields:
        if name not in new_fields:
            breaking_changes.append(
                BreakingChangeInfo(
                    change_type="field_removed",
                    field=name,
                    description=f"Field '{name}' was removed",
                    from_value=current_fields[name].type,
                    to_value=None,
                    migration_hint="Add the field back or migrate consumers",
                )
            )

    # Check for type changes and nullable changes
    for name in current_fields:
        if name not in new_fields:
            continue

        old_f = current_fields[name]
        new_f = new_fields[name]

        if old_f.type != new_f.type:
            breaking_changes.append(
                BreakingChangeInfo(
                    change_type="type_changed_incompatible",
                    field=name,
                    description=f"Type changed from '{old_f.type}' to '{new_f.type}'",
                    from_value=old_f.type,
                    to_value=new_f.type,
                    migration_hint="Use a compatible type or create a new field",
                )
            )

        if old_f.nullable and not new_f.nullable:
            breaking_changes.append(
                BreakingChangeInfo(
                    change_type="nullable_to_required",
                    field=name,
                    description=f"Field '{name}' changed from nullable to required",
                    from_value=True,
                    to_value=False,
                    migration_hint="Keep nullable or ensure all data has values",
                )
            )

    return breaking_changes


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


# =============================================================================
# Schema Version Negotiation Helpers (T-375)
# =============================================================================
SUPPORTED_SCHEMA_VERSIONS = ["v1", "v1.0.0"]
DEFAULT_SCHEMA_VERSION = "v1.0.0"


def parse_accept_header(accept: str) -> tuple[str, str]:
    """
    Parse Accept header for schema version negotiation (T-375).

    Supports:
    - application/json (default JSON response)
    - application/x-yaml (YAML response)
    - application/vnd.griot.v1+json (versioned JSON)
    - application/vnd.griot.v1+yaml (versioned YAML)
    - application/vnd.griot.v1.0.0+yaml (full version)

    Returns:
        Tuple of (schema_version, format)
    """
    schema_version = DEFAULT_SCHEMA_VERSION
    response_format = "json"

    if "application/x-yaml" in accept:
        response_format = "yaml"
    elif "application/vnd.griot" in accept:
        # Parse versioned media type: application/vnd.griot.v1+yaml
        import re
        match = re.search(r"application/vnd\.griot\.(v[\d.]+)\+(\w+)", accept)
        if match:
            requested_version = match.group(1)
            requested_format = match.group(2)

            # Normalize version
            if requested_version in SUPPORTED_SCHEMA_VERSIONS:
                schema_version = requested_version
            elif requested_version.startswith("v") and requested_version[1:] in ["1", "1.0", "1.0.0"]:
                schema_version = "v1.0.0"

            response_format = requested_format if requested_format in ["json", "yaml"] else "json"

    return schema_version, response_format


@router.get(
    "/contracts/{contract_id}",
    response_model=Contract,
    operation_id="getContract",
    responses={
        404: {"model": ErrorResponse},
        406: {"model": ErrorResponse, "description": "Unsupported schema version"},
    },
)
async def get_contract(
    storage: StorageDep,
    contract_id: str,
    version: str | None = None,
    request: Request = None,
) -> Contract | Response:
    """Get a contract by ID (T-375 enhanced with schema version negotiation).

    Optionally specify a version to retrieve a specific version.
    Defaults to the latest version.

    Schema Version Negotiation (T-375):
    Use the Accept header to request specific schema versions and formats:
    - application/json (default): JSON with current schema
    - application/x-yaml: YAML with current schema
    - application/vnd.griot.v1+json: JSON with ODCS v1 schema
    - application/vnd.griot.v1+yaml: YAML with ODCS v1 schema

    The X-Griot-Schema-Version response header indicates the schema version used.
    """
    contract = await storage.get_contract(contract_id, version=version)
    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": f"Contract '{contract_id}' not found"},
        )

    # T-375: Schema version negotiation
    accept_header = request.headers.get("accept", "") if request else ""
    schema_version, response_format = parse_accept_header(accept_header)

    # Validate schema version
    normalized_version = schema_version.replace("v", "") if schema_version.startswith("v") else schema_version
    if normalized_version not in ["1", "1.0", "1.0.0"]:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail={
                "code": "UNSUPPORTED_SCHEMA_VERSION",
                "message": f"Schema version '{schema_version}' is not supported",
                "supported_versions": SUPPORTED_SCHEMA_VERSIONS,
            },
        )

    # Build response with schema version header
    headers = {"X-Griot-Schema-Version": schema_version}

    if response_format == "yaml":
        yaml_content = await storage.get_contract_yaml(contract_id, version=version)
        return PlainTextResponse(
            content=yaml_content,
            media_type=f"application/vnd.griot.{schema_version}+yaml",
            headers=headers,
        )

    # JSON response
    return JSONResponse(
        content=contract.model_dump(mode="json", exclude_none=True),
        headers=headers,
    )


@router.put(
    "/contracts/{contract_id}",
    response_model=Contract,
    operation_id="updateContract",
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        409: {"model": BreakingChangesResponse, "description": "Breaking changes detected"},
    },
)
async def update_contract(
    storage: StorageDep,
    contract_id: str,
    update: ContractUpdate,
    allow_breaking: Annotated[
        bool,
        Query(
            description="Set to true to allow updates with breaking changes. "
            "Required when the update contains breaking changes.",
        ),
    ] = False,
) -> Contract | JSONResponse:
    """Update a contract, creating a new version (T-304, T-371, T-372).

    The version number is automatically incremented based on change_type:
    - patch: 1.0.0 -> 1.0.1
    - minor: 1.0.0 -> 1.1.0
    - major: 1.0.0 -> 2.0.0

    Breaking Change Validation:
    - Automatically detects breaking changes (field removal, type changes, etc.)
    - Blocks updates with breaking changes by default
    - Use ?allow_breaking=true to force updates with breaking changes
    - Breaking changes are tracked in version history (T-373)

    Breaking change types detected:
    - field_removed: An existing field was removed
    - type_changed_incompatible: Field type changed incompatibly
    - nullable_to_required: Nullable field became required
    - enum_values_removed: Enum constraint values were removed
    - constraint_tightened: Constraints became more restrictive
    - pattern_changed: Regex pattern was modified
    - primary_key_changed: Primary key field changed
    - required_field_added: Required field added without default
    """
    contract = await storage.get_contract(contract_id)
    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": f"Contract '{contract_id}' not found"},
        )

    # T-304/T-371: Detect breaking changes
    breaking_changes = detect_breaking_changes_for_update(contract, update)

    # T-372: Block if breaking changes and allow_breaking is False
    if breaking_changes and not allow_breaking:
        response = BreakingChangesResponse(
            breaking_changes=breaking_changes,
            message=f"Update contains {len(breaking_changes)} breaking change(s) that require explicit acknowledgment",
        )
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=response.model_dump(),
        )

    # T-373: Pass breaking change info to storage for history tracking
    # If there are breaking changes and allow_breaking=True, mark as breaking version
    is_breaking_update = len(breaking_changes) > 0

    return await storage.update_contract(
        contract_id,
        update,
        is_breaking=is_breaking_update,
        breaking_changes=[bc.model_dump() for bc in breaking_changes] if is_breaking_update else None,
    )


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
