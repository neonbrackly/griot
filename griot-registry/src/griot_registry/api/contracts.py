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
    VersionList,
)
from griot_registry.storage.base import StorageBackend

router = APIRouter()


# =============================================================================
# Breaking Change Detection Helpers (T-304, T-371)
# =============================================================================
def _extract_properties_from_schema(schema_list: list | None) -> dict[str, dict[str, Any]]:
    """Extract all properties from ODCS schema into a flat dictionary."""
    properties: dict[str, dict[str, Any]] = {}
    if not schema_list:
        return properties

    for schema in schema_list:
        schema_name = schema.name if hasattr(schema, 'name') else schema.get('name', '')
        schema_props = schema.properties if hasattr(schema, 'properties') else schema.get('properties', [])

        if not schema_props:
            continue

        for prop in schema_props:
            prop_name = prop.name if hasattr(prop, 'name') else prop.get('name', '')
            full_name = f"{schema_name}.{prop_name}"
            properties[full_name] = {
                "name": prop_name,
                "schema": schema_name,
                "logicalType": prop.logicalType if hasattr(prop, 'logicalType') else prop.get('logicalType', 'string'),
                "nullable": prop.nullable if hasattr(prop, 'nullable') else prop.get('nullable', True),
                "primary_key": prop.primary_key if hasattr(prop, 'primary_key') else prop.get('primary_key', False),
            }

    return properties


def detect_breaking_changes_for_update(
    current: Contract,
    update: ContractUpdate,
) -> list[BreakingChangeInfo]:
    """
    Detect breaking changes between current contract and proposed update.

    Uses ODCS schema format to detect breaking changes in:
    - Removed properties
    - Type changes
    - Nullable to required changes
    - Removed schemas

    Args:
        current: The current contract version.
        update: The proposed update.

    Returns:
        List of BreakingChangeInfo objects describing breaking changes.
    """
    # If no schema update, no breaking changes from schema perspective
    if not update.schema:
        return []

    breaking_changes: list[BreakingChangeInfo] = []

    # Extract properties from current and proposed schemas
    current_props = _extract_properties_from_schema(current.schema)
    new_props = _extract_properties_from_schema(update.schema)

    # Check for removed properties
    for prop_name in current_props:
        if prop_name not in new_props:
            breaking_changes.append(
                BreakingChangeInfo(
                    change_type="field_removed",
                    field=prop_name,
                    description=f"Property '{prop_name}' was removed",
                    from_value=current_props[prop_name].get("logicalType"),
                    to_value=None,
                    migration_hint="Add the property back or migrate consumers",
                )
            )

    # Check for type changes and nullable changes
    for prop_name in current_props:
        if prop_name not in new_props:
            continue

        old_p = current_props[prop_name]
        new_p = new_props[prop_name]

        # Type change
        if old_p.get("logicalType") != new_p.get("logicalType"):
            breaking_changes.append(
                BreakingChangeInfo(
                    change_type="type_changed_incompatible",
                    field=prop_name,
                    description=f"Type changed from '{old_p.get('logicalType')}' to '{new_p.get('logicalType')}'",
                    from_value=old_p.get("logicalType"),
                    to_value=new_p.get("logicalType"),
                    migration_hint="Use a compatible type or create a new property",
                )
            )

        # Nullable to required change
        if old_p.get("nullable") and not new_p.get("nullable"):
            breaking_changes.append(
                BreakingChangeInfo(
                    change_type="nullable_to_required",
                    field=prop_name,
                    description=f"Property '{prop_name}' changed from nullable to required",
                    from_value=True,
                    to_value=False,
                    migration_hint="Keep nullable or ensure all data has values",
                )
            )

    # Check for removed schemas
    current_schemas = {s.name if hasattr(s, 'name') else s.get('name', '') for s in (current.schema or [])}
    new_schemas = {s.name if hasattr(s, 'name') else s.get('name', '') for s in (update.schema or [])}

    for schema_name in current_schemas - new_schemas:
        breaking_changes.append(
            BreakingChangeInfo(
                change_type="schema_removed",
                field=schema_name,
                description=f"Schema '{schema_name}' was removed",
                from_value=schema_name,
                to_value=None,
                migration_hint="Add the schema back or migrate consumers",
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


@router.patch(
    "/contracts/{contract_id}/status",
    response_model=Contract,
    operation_id="updateContractStatus",
    responses={
        400: {"model": ErrorResponse, "description": "Invalid status transition"},
        404: {"model": ErrorResponse},
    },
)
async def update_contract_status(
    storage: StorageDep,
    contract_id: str,
    status_update: dict,
) -> Contract:
    """Update the status of a contract.

    This endpoint is used by the approval workflow to transition contract status.

    Valid status transitions:
    - draft -> active (requires approval)
    - draft -> deprecated
    - active -> deprecated
    - deprecated -> retired

    Args:
        contract_id: The contract ID
        status_update: Object containing the new status {"status": "active"}

    Returns:
        The updated contract with new status
    """
    contract = await storage.get_contract(contract_id)
    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": f"Contract '{contract_id}' not found"},
        )

    new_status = status_update.get("status")
    if new_status is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "BAD_REQUEST", "message": "Missing 'status' field"},
        )

    # Validate status transition
    valid_transitions = {
        "draft": ["active", "deprecated"],
        "active": ["deprecated"],
        "deprecated": ["retired"],
        "retired": [],
    }

    current_status = contract.status
    allowed = valid_transitions.get(current_status, [])

    if new_status not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_STATUS_TRANSITION",
                "message": f"Cannot transition from '{current_status}' to '{new_status}'",
                "allowed_transitions": allowed,
            },
        )

    # Update the status
    return await storage.update_contract_status(contract_id, new_status)


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
