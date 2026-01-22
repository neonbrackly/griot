"""Schema management endpoints.

Provides endpoints for standalone schema CRUD, versioning, and lifecycle management.
Schemas are first-class entities that can be referenced by contracts.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Annotated, Any

from fastapi import APIRouter, HTTPException, Query, Request, status
from pydantic import BaseModel, Field, field_validator

from griot_registry.api.dependencies import Storage
from griot_registry.auth import CurrentUser

router = APIRouter()


# =============================================================================
# Helper Functions
# =============================================================================


def _utc_now() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(timezone.utc)


def _parse_version(version: str) -> tuple[int, int, int]:
    """Parse semantic version string into tuple."""
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)$", version)
    if not match:
        raise ValueError(f"Invalid version format: {version}")
    return int(match.group(1)), int(match.group(2)), int(match.group(3))


def _increment_version(version: str, change_type: str) -> str:
    """Increment version based on change type."""
    major, minor, patch = _parse_version(version)
    if change_type == "major":
        return f"{major + 1}.0.0"
    elif change_type == "minor":
        return f"{major}.{minor + 1}.0"
    else:  # patch
        return f"{major}.{minor}.{patch + 1}"


def _detect_breaking_changes(
    old_properties: list[dict[str, Any]],
    new_properties: list[dict[str, Any]],
) -> list[dict[str, str]]:
    """Detect breaking changes between two property lists."""
    breaking_changes = []

    old_props = {p.get("name"): p for p in old_properties}
    new_props = {p.get("name"): p for p in new_properties}

    # Check for removed columns
    for name in old_props:
        if name not in new_props:
            breaking_changes.append({
                "type": "column_removed",
                "column": name,
                "description": f"Column '{name}' was removed",
            })

    # Check for type changes and other breaking modifications
    for name, new_prop in new_props.items():
        if name in old_props:
            old_prop = old_props[name]

            # Type change
            old_type = old_prop.get("logicalType") or old_prop.get("logical_type", "string")
            new_type = new_prop.get("logicalType") or new_prop.get("logical_type", "string")
            if old_type != new_type:
                breaking_changes.append({
                    "type": "type_changed",
                    "column": name,
                    "description": f"Column '{name}' type changed from '{old_type}' to '{new_type}'",
                })

            # Nullable to required
            old_nullable = old_prop.get("nullable", True)
            new_nullable = new_prop.get("nullable", True)
            if old_nullable and not new_nullable:
                breaking_changes.append({
                    "type": "nullable_to_required",
                    "column": name,
                    "description": f"Column '{name}' changed from nullable to required",
                })

    return breaking_changes


def _detect_pii_changes(
    old_properties: list[dict[str, Any]],
    new_properties: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Detect PII classification changes."""
    pii_changes = []

    old_props = {p.get("name"): p for p in old_properties}
    new_props = {p.get("name"): p for p in new_properties}

    for name, new_prop in new_props.items():
        if name in old_props:
            old_prop = old_props[name]

            # Get PII classification from customProperties.privacy
            old_custom = old_prop.get("customProperties") or old_prop.get("custom_properties") or {}
            new_custom = new_prop.get("customProperties") or new_prop.get("custom_properties") or {}

            old_privacy = old_custom.get("privacy", {})
            new_privacy = new_custom.get("privacy", {})

            # Handle list format for privacy
            if isinstance(old_privacy, list):
                old_pii = any(p.get("value") for p in old_privacy if p.get("name") == "is_pii")
            else:
                old_pii = old_privacy.get("is_pii", False)

            if isinstance(new_privacy, list):
                new_pii = any(p.get("value") for p in new_privacy if p.get("name") == "is_pii")
            else:
                new_pii = new_privacy.get("is_pii", False)

            if old_pii != new_pii:
                pii_changes.append({
                    "column": name,
                    "old_is_pii": old_pii,
                    "new_is_pii": new_pii,
                    "description": f"Column '{name}' PII classification changed from {old_pii} to {new_pii}",
                })

    return pii_changes


# =============================================================================
# Request/Response Models
# =============================================================================


class PropertyCreate(BaseModel):
    """Property (column) definition for schema creation."""

    name: str = Field(..., min_length=1, description="Column name")
    id: str | None = Field(None, description="Optional unique ID for the property")
    logical_type: str = Field("string", alias="logicalType", description="Logical data type")
    physical_type: str | None = Field(None, alias="physicalType", description="Physical database type")
    description: str | None = None
    primary_key: bool = Field(False, alias="primaryKey")
    primary_key_position: int | None = Field(None, alias="primaryKeyPosition")
    partitioned: bool = False
    partition_key_position: int | None = Field(None, alias="partitionKeyPosition")
    required: bool = False
    unique: bool = False
    nullable: bool = True
    critical_data_element: bool = Field(False, alias="criticalDataElement")
    relationships: list[dict[str, Any]] = []
    tags: list[str] = []
    custom_properties: dict[str, Any] = Field(default_factory=dict, alias="customProperties")
    authoritative_definitions: list[dict[str, Any]] = Field(default_factory=list, alias="authoritativeDefinitions")
    quality: list[dict[str, Any]] = []

    model_config = {"populate_by_name": True}


class SchemaCreateRequest(BaseModel):
    """Request body for creating a schema."""

    name: str = Field(..., min_length=1, description="Schema name")
    physical_name: str | None = Field(None, alias="physicalName", description="Physical table name")
    logical_type: str = Field("object", alias="logicalType")
    physical_type: str | None = Field("table", alias="physicalType")
    description: str | None = None
    business_name: str | None = Field(None, alias="businessName")
    domain: str | None = None
    tags: list[str] = []
    authoritative_definitions: list[dict[str, Any]] = Field(default_factory=list, alias="authoritativeDefinitions")
    quality: list[dict[str, Any]] = []
    properties: list[PropertyCreate] = Field(..., min_length=1, description="Column definitions")
    owner_team_id: str | None = Field(None, alias="ownerTeamId", description="Team that owns this schema")

    model_config = {"populate_by_name": True}

    @field_validator("properties")
    @classmethod
    def validate_properties(cls, v: list[PropertyCreate]) -> list[PropertyCreate]:
        """Ensure at least one property is defined."""
        if not v:
            raise ValueError("Schema must have at least one property")
        return v


class SchemaUpdateRequest(BaseModel):
    """Request body for updating a schema."""

    name: str | None = None
    physical_name: str | None = Field(None, alias="physicalName")
    description: str | None = None
    business_name: str | None = Field(None, alias="businessName")
    domain: str | None = None
    tags: list[str] | None = None
    authoritative_definitions: list[dict[str, Any]] | None = Field(None, alias="authoritativeDefinitions")
    quality: list[dict[str, Any]] | None = None
    properties: list[PropertyCreate] | None = None
    force_breaking: bool = Field(False, alias="forceBreaking", description="Force breaking changes (admin only)")

    model_config = {"populate_by_name": True}


class SchemaProperty(BaseModel):
    """Property (column) in schema response."""

    id: str | None = None
    name: str
    logical_type: str = Field(..., alias="logicalType")
    physical_type: str | None = Field(None, alias="physicalType")
    description: str | None = None
    primary_key: bool = Field(False, alias="primaryKey")
    primary_key_position: int | None = Field(None, alias="primaryKeyPosition")
    partitioned: bool = False
    partition_key_position: int | None = Field(None, alias="partitionKeyPosition")
    required: bool = False
    unique: bool = False
    nullable: bool = True
    critical_data_element: bool = Field(False, alias="criticalDataElement")
    relationships: list[dict[str, Any]] = []
    tags: list[str] = []
    custom_properties: dict[str, Any] = Field(default_factory=dict, alias="customProperties")
    authoritative_definitions: list[dict[str, Any]] = Field(default_factory=list, alias="authoritativeDefinitions")
    quality: list[dict[str, Any]] = []

    model_config = {"populate_by_name": True}


class SchemaResponse(BaseModel):
    """Schema response model."""

    id: str
    name: str
    physical_name: str | None = Field(None, alias="physicalName")
    logical_type: str = Field(..., alias="logicalType")
    physical_type: str | None = Field(None, alias="physicalType")
    description: str | None = None
    business_name: str | None = Field(None, alias="businessName")
    domain: str | None = None
    tags: list[str] = []
    authoritative_definitions: list[dict[str, Any]] = Field(default_factory=list, alias="authoritativeDefinitions")
    quality: list[dict[str, Any]] = []
    properties: list[SchemaProperty] = []

    # Versioning
    version: str
    status: str

    # Ownership
    owner_id: str = Field(..., alias="ownerId")
    owner_team_id: str | None = Field(None, alias="ownerTeamId")

    # Source tracking
    source: str
    connection_id: str | None = Field(None, alias="connectionId")

    # Computed
    property_count: int = Field(0, alias="propertyCount")
    has_pii: bool = Field(False, alias="hasPii")

    # Audit
    created_at: datetime = Field(..., alias="createdAt")
    created_by: str = Field(..., alias="createdBy")
    updated_at: datetime | None = Field(None, alias="updatedAt")
    updated_by: str | None = Field(None, alias="updatedBy")

    model_config = {"populate_by_name": True}


class SchemaListItem(BaseModel):
    """Schema item in list response."""

    id: str
    name: str
    physical_name: str | None = Field(None, alias="physicalName")
    description: str | None = None
    domain: str | None = None
    version: str
    status: str
    source: str
    property_count: int = Field(0, alias="propertyCount")
    has_pii: bool = Field(False, alias="hasPii")
    owner_id: str = Field(..., alias="ownerId")
    owner_team_id: str | None = Field(None, alias="ownerTeamId")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime | None = Field(None, alias="updatedAt")

    model_config = {"populate_by_name": True}


class SchemaListResponse(BaseModel):
    """Response for listing schemas."""

    items: list[SchemaListItem]
    total: int
    limit: int
    offset: int


class VersionHistoryItem(BaseModel):
    """Version history entry."""

    version: str
    change_type: str = Field(..., alias="changeType")
    change_notes: str | None = Field(None, alias="changeNotes")
    created_at: datetime = Field(..., alias="createdAt")
    created_by: str = Field(..., alias="createdBy")
    is_current: bool = Field(False, alias="isCurrent")

    model_config = {"populate_by_name": True}


class VersionHistoryResponse(BaseModel):
    """Response for version history."""

    schema_id: str = Field(..., alias="schemaId")
    current_version: str = Field(..., alias="currentVersion")
    versions: list[VersionHistoryItem]
    total: int

    model_config = {"populate_by_name": True}


class BreakingChangeInfo(BaseModel):
    """Information about a breaking change."""

    type: str
    column: str
    description: str


class BreakingChangesResponse(BaseModel):
    """Response when breaking changes are detected."""

    code: str = "BREAKING_CHANGES_DETECTED"
    message: str
    breaking_changes: list[BreakingChangeInfo] = Field(..., alias="breakingChanges")
    affected_contracts: list[dict[str, str]] = Field(..., alias="affectedContracts")
    suggestions: list[str] = []

    model_config = {"populate_by_name": True}


class PublishRequest(BaseModel):
    """Request to publish a draft schema."""

    pass  # No body required


class DeprecateRequest(BaseModel):
    """Request to deprecate a schema."""

    reason: str = Field(..., min_length=1, description="Reason for deprecation")
    replacement_schema_id: str | None = Field(None, alias="replacementSchemaId")

    model_config = {"populate_by_name": True}


class CloneRequest(BaseModel):
    """Request to clone a schema as a new version."""

    change_notes: str = Field(..., min_length=1, alias="changeNotes", description="Notes describing the changes")

    model_config = {"populate_by_name": True}


# =============================================================================
# Helper to convert storage dict to response
# =============================================================================


def _schema_to_response(schema: dict[str, Any]) -> SchemaResponse:
    """Convert storage schema dict to response model."""
    properties = schema.get("properties", [])

    # Check for PII
    has_pii = False
    for prop in properties:
        custom = prop.get("customProperties") or prop.get("custom_properties") or {}
        privacy = custom.get("privacy", {})
        if isinstance(privacy, list):
            has_pii = any(p.get("value") for p in privacy if p.get("name") == "is_pii")
        else:
            has_pii = privacy.get("is_pii", False)
        if has_pii:
            break

    return SchemaResponse(
        id=schema["id"],
        name=schema.get("name", ""),
        physical_name=schema.get("physical_name") or schema.get("physicalName"),
        logical_type=schema.get("logical_type") or schema.get("logicalType", "object"),
        physical_type=schema.get("physical_type") or schema.get("physicalType"),
        description=schema.get("description"),
        business_name=schema.get("business_name") or schema.get("businessName"),
        domain=schema.get("domain"),
        tags=schema.get("tags", []),
        authoritative_definitions=schema.get("authoritative_definitions") or schema.get("authoritativeDefinitions", []),
        quality=schema.get("quality", []),
        properties=[
            SchemaProperty(
                id=p.get("id"),
                name=p.get("name", ""),
                logical_type=p.get("logicalType") or p.get("logical_type", "string"),
                physical_type=p.get("physicalType") or p.get("physical_type"),
                description=p.get("description"),
                primary_key=p.get("primaryKey") or p.get("primary_key", False),
                primary_key_position=p.get("primaryKeyPosition") or p.get("primary_key_position"),
                partitioned=p.get("partitioned", False),
                partition_key_position=p.get("partitionKeyPosition") or p.get("partition_key_position"),
                required=p.get("required", False),
                unique=p.get("unique", False),
                nullable=p.get("nullable", True),
                critical_data_element=p.get("criticalDataElement") or p.get("critical_data_element", False),
                relationships=p.get("relationships", []),
                tags=p.get("tags", []),
                custom_properties=p.get("customProperties") or p.get("custom_properties", {}),
                authoritative_definitions=p.get("authoritativeDefinitions") or p.get("authoritative_definitions", []),
                quality=p.get("quality", []),
            )
            for p in properties
        ],
        version=schema.get("version", "1.0.0"),
        status=schema.get("status", "draft"),
        owner_id=schema.get("owner_id", ""),
        owner_team_id=schema.get("owner_team_id"),
        source=schema.get("source", "manual"),
        connection_id=schema.get("connection_id"),
        property_count=len(properties),
        has_pii=has_pii,
        created_at=schema.get("created_at", _utc_now()),
        created_by=schema.get("created_by", ""),
        updated_at=schema.get("updated_at"),
        updated_by=schema.get("updated_by"),
    )


def _schema_to_list_item(schema: dict[str, Any]) -> SchemaListItem:
    """Convert storage schema dict to list item."""
    properties = schema.get("properties", [])

    has_pii = False
    for prop in properties:
        custom = prop.get("customProperties") or prop.get("custom_properties") or {}
        privacy = custom.get("privacy", {})
        if isinstance(privacy, list):
            has_pii = any(p.get("value") for p in privacy if p.get("name") == "is_pii")
        else:
            has_pii = privacy.get("is_pii", False)
        if has_pii:
            break

    return SchemaListItem(
        id=schema["id"],
        name=schema.get("name", ""),
        physical_name=schema.get("physical_name") or schema.get("physicalName"),
        description=schema.get("description"),
        domain=schema.get("domain"),
        version=schema.get("version", "1.0.0"),
        status=schema.get("status", "draft"),
        source=schema.get("source", "manual"),
        property_count=len(properties),
        has_pii=has_pii,
        owner_id=schema.get("owner_id", ""),
        owner_team_id=schema.get("owner_team_id"),
        created_at=schema.get("created_at", _utc_now()),
        updated_at=schema.get("updated_at"),
    )


# =============================================================================
# Authorization Helpers
# =============================================================================


async def _check_schema_access(
    storage: Storage,
    schema: dict[str, Any],
    user: CurrentUser,
    action: str = "edit",
) -> None:
    """Check if user can edit/delete a schema."""
    owner_id = schema.get("owner_id")
    owner_team_id = schema.get("owner_team_id")

    # Check if user is owner
    if owner_id == user.id:
        return

    # Check if user is admin
    is_admin = any(r.value == "admin" for r in user.roles)
    if is_admin:
        return

    # Check if user is member of owner team
    if owner_team_id:
        team = await storage.teams.get(owner_team_id)
        if team:
            members = team.get("members", [])
            if any(m.get("user_id") == user.id for m in members):
                return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={
            "code": "NOT_AUTHORIZED",
            "message": f"You are not authorized to {action} this schema. Only the owner or team members can {action}.",
        },
    )


# =============================================================================
# Schema CRUD Endpoints
# =============================================================================


@router.post(
    "/schemas",
    operation_id="createSchema",
    summary="Create a new schema",
    response_model=SchemaResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_schema(
    request: Request,
    storage: Storage,
    user: CurrentUser,
    body: SchemaCreateRequest,
) -> SchemaResponse:
    """Create a new standalone schema.

    The schema is created in 'draft' status. Use POST /schemas/{id}/publish
    to make it available for contracts.

    Ownership is set to the creating user by default. A team can also be
    specified as owner.
    """
    import uuid

    now = _utc_now()
    schema_id = f"sch-{uuid.uuid4().hex[:12]}"

    # Convert properties to storage format
    properties = []
    for prop in body.properties:
        prop_dict = prop.model_dump(by_alias=True, exclude_none=True)
        if not prop_dict.get("id"):
            prop_dict["id"] = f"prop-{uuid.uuid4().hex[:8]}"
        properties.append(prop_dict)

    schema_doc = {
        "id": schema_id,
        "name": body.name,
        "physical_name": body.physical_name,
        "logical_type": body.logical_type,
        "physical_type": body.physical_type,
        "description": body.description,
        "business_name": body.business_name,
        "domain": body.domain,
        "tags": body.tags,
        "authoritative_definitions": body.authoritative_definitions,
        "quality": body.quality,
        "properties": properties,
        # Versioning
        "version": "1.0.0",
        "status": "draft",
        "version_history": [
            {
                "version": "1.0.0",
                "change_type": "initial",
                "change_notes": "Initial version",
                "created_at": now.isoformat(),
                "created_by": user.id,
                "snapshot": None,  # Will be set on publish
            }
        ],
        # Ownership
        "owner_id": user.id,
        "owner_team_id": body.owner_team_id,
        # Source
        "source": "manual",
        "connection_id": None,
        # Audit
        "created_at": now,
        "created_by": user.id,
        "updated_at": now,
        "updated_by": user.id,
    }

    created = await storage.schemas.create(schema_doc)
    return _schema_to_response(created)


@router.get(
    "/schemas",
    operation_id="listSchemas",
    summary="List schemas",
    response_model=SchemaListResponse,
)
async def list_schemas(
    storage: Storage,
    user: CurrentUser,
    search: str | None = Query(None, description="Search by name or description"),
    domain: str | None = Query(None, description="Filter by domain"),
    source: str | None = Query(None, description="Filter by source: manual, connection"),
    status_filter: str | None = Query(None, alias="status", description="Filter by status: draft, active, deprecated"),
    owner_id: str | None = Query(None, alias="ownerId", description="Filter by owner user ID"),
    owner_team_id: str | None = Query(None, alias="ownerTeamId", description="Filter by owner team ID"),
    active_only: bool = Query(False, alias="activeOnly", description="Only return active schemas"),
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> SchemaListResponse:
    """List schemas with filtering and pagination.

    Use `activeOnly=true` for contract creation to only show schemas
    that are available for use.
    """
    if active_only:
        status_filter = "active"

    schemas, total = await storage.schemas.list(
        search=search,
        domain=domain,
        source=source,
        status=status_filter,
        owner_id=owner_id,
        owner_team_id=owner_team_id,
        limit=limit,
        offset=offset,
    )

    return SchemaListResponse(
        items=[_schema_to_list_item(s) for s in schemas],
        total=total,
        limit=limit,
        offset=offset,
    )


# =============================================================================
# Legacy Schema Catalog Endpoints (MUST be before {schema_id} routes!)
# =============================================================================


class SchemaCatalogEntry(BaseModel):
    """A schema catalog entry (legacy)."""

    schema_id: str
    name: str
    physical_name: str | None = None
    logical_type: str = "object"
    physical_type: str = "table"
    description: str | None = None
    business_name: str | None = None
    contract_id: str
    contract_name: str
    contract_version: str
    contract_status: str
    field_names: list[str] = Field(default_factory=list)
    field_count: int = 0
    has_pii: bool = False
    primary_key_field: str | None = None


class SchemaCatalogResponse(BaseModel):
    """Response for schema catalog queries (legacy)."""

    items: list[SchemaCatalogEntry]
    total: int


@router.get(
    "/schemas/catalog",
    operation_id="findSchemasInContracts",
    summary="Find schemas across contracts (legacy catalog)",
    response_model=SchemaCatalogResponse,
)
async def find_schemas_in_contracts(
    storage: Storage,
    user: CurrentUser,
    name: str | None = Query(None, description="Filter by schema name"),
    physical_name: str | None = Query(None, description="Filter by physical table name"),
    field_name: str | None = Query(None, description="Filter by field name"),
    has_pii: bool | None = Query(None, description="Filter by PII flag"),
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> SchemaCatalogResponse:
    """Find schemas across all contracts (legacy catalog view).

    This searches the schema catalog which indexes schemas embedded in contracts.
    For standalone schemas, use GET /schemas instead.
    """
    entries = await storage.schema_catalog.find_schemas(
        name=name,
        physical_name=physical_name,
        field_name=field_name,
        has_pii=has_pii,
        limit=limit,
    )

    return SchemaCatalogResponse(
        items=[
            SchemaCatalogEntry(
                schema_id=e.get("schema_id", ""),
                name=e.get("name", ""),
                physical_name=e.get("physical_name"),
                logical_type=e.get("logical_type", "object"),
                physical_type=e.get("physical_type", "table"),
                description=e.get("description"),
                business_name=e.get("business_name"),
                contract_id=e.get("contract_id", ""),
                contract_name=e.get("contract_name", ""),
                contract_version=e.get("contract_version", ""),
                contract_status=e.get("contract_status", ""),
                field_names=e.get("field_names", []),
                field_count=e.get("field_count", 0),
                has_pii=e.get("has_pii", False),
                primary_key_field=e.get("primary_key_field"),
            )
            for e in entries
        ],
        total=len(entries),
    )


@router.get(
    "/schemas/catalog/contracts/{schema_name}",
    operation_id="getContractsBySchemaName",
    summary="Get contracts containing a schema (legacy)",
)
async def get_contracts_by_schema_name(
    schema_name: str,
    storage: Storage,
    user: CurrentUser,
) -> dict[str, Any]:
    """Get all contracts that contain a schema with the given name."""
    contract_ids = await storage.schema_catalog.get_contracts_by_schema(schema_name)

    return {
        "schema_name": schema_name,
        "contract_ids": contract_ids,
        "count": len(contract_ids),
    }


# =============================================================================
# Schema CRUD Endpoints (individual schema operations)
# =============================================================================


@router.get(
    "/schemas/{schema_id}",
    operation_id="getSchema",
    summary="Get schema by ID",
    response_model=SchemaResponse,
)
async def get_schema(
    schema_id: str,
    storage: Storage,
    user: CurrentUser,
    version: str | None = Query(None, description="Specific version to retrieve"),
) -> SchemaResponse:
    """Get a schema by ID.

    Optionally specify a version to retrieve a specific version.
    """
    if version:
        schema = await storage.schemas.get_version(schema_id, version)
    else:
        schema = await storage.schemas.get(schema_id)

    if not schema:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "SCHEMA_NOT_FOUND",
                "message": f"Schema '{schema_id}' not found",
            },
        )

    return _schema_to_response(schema)


@router.put(
    "/schemas/{schema_id}",
    operation_id="updateSchema",
    summary="Update a schema",
    response_model=SchemaResponse,
)
async def update_schema(
    schema_id: str,
    request: Request,
    storage: Storage,
    user: CurrentUser,
    body: SchemaUpdateRequest,
) -> SchemaResponse:
    """Update a schema.

    Breaking changes (removing columns, changing types) are blocked
    for active schemas unless forceBreaking=true (admin only).

    For active schemas with breaking changes, the recommended workflow is:
    1. Clone the schema to create a new version
    2. Make changes to the new version
    3. Update contracts to reference the new version
    4. Deprecate the old version
    """
    schema = await storage.schemas.get(schema_id)
    if not schema:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "SCHEMA_NOT_FOUND", "message": f"Schema '{schema_id}' not found"},
        )

    # Check authorization
    await _check_schema_access(storage, schema, user, "edit")

    # Cannot edit deprecated schemas
    if schema.get("status") == "deprecated":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "SCHEMA_DEPRECATED",
                "message": "Cannot edit deprecated schemas. Clone to create a new version.",
            },
        )

    # Build updates
    updates: dict[str, Any] = {"updated_at": _utc_now(), "updated_by": user.id}

    if body.name is not None:
        updates["name"] = body.name
    if body.physical_name is not None:
        updates["physical_name"] = body.physical_name
    if body.description is not None:
        updates["description"] = body.description
    if body.business_name is not None:
        updates["business_name"] = body.business_name
    if body.domain is not None:
        updates["domain"] = body.domain
    if body.tags is not None:
        updates["tags"] = body.tags
    if body.authoritative_definitions is not None:
        updates["authoritative_definitions"] = body.authoritative_definitions
    if body.quality is not None:
        updates["quality"] = body.quality

    # Handle property changes for active schemas
    if body.properties is not None and schema.get("status") == "active":
        old_properties = schema.get("properties", [])
        new_properties = [p.model_dump(by_alias=True, exclude_none=True) for p in body.properties]

        # Detect breaking changes
        breaking_changes = _detect_breaking_changes(old_properties, new_properties)

        if breaking_changes and not body.force_breaking:
            # Get affected contracts
            affected = await storage.schemas.get_contracts_using_schema(schema_id)

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "BREAKING_CHANGES_DETECTED",
                    "message": "Breaking changes detected. Use forceBreaking=true or clone the schema.",
                    "breakingChanges": breaking_changes,
                    "affectedContracts": [{"id": c.get("id"), "name": c.get("name")} for c in affected],
                    "suggestions": [
                        f"Clone schema to create new version: POST /schemas/{schema_id}/clone",
                        "Use forceBreaking=true to force update (admin only)",
                    ],
                },
            )

        if body.force_breaking:
            # Only admin can force breaking changes
            is_admin = any(r.value == "admin" for r in user.roles)
            if not is_admin:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={"code": "ADMIN_REQUIRED", "message": "Only admins can force breaking changes"},
                )

        # Detect PII changes and notify
        pii_changes = _detect_pii_changes(old_properties, new_properties)
        if pii_changes:
            # Get affected contracts and notify owners
            affected = await storage.schemas.get_contracts_using_schema(schema_id)
            for contract in affected:
                contract_owner = contract.get("created_by") or contract.get("owner_id")
                if contract_owner:
                    await storage.notifications.create({
                        "user_id": contract_owner,
                        "type": "schema_pii_changed",
                        "title": f"PII classification changed in schema '{schema.get('name')}'",
                        "description": f"Schema used by contract '{contract.get('name')}' has updated PII classifications. Please review.",
                        "href": f"/studio/schemas/{schema_id}",
                        "metadata": {
                            "schema_id": schema_id,
                            "contract_id": contract.get("id"),
                            "pii_changes": pii_changes,
                        },
                    })

        updates["properties"] = new_properties

    elif body.properties is not None:
        # Draft schema - allow all changes
        updates["properties"] = [p.model_dump(by_alias=True, exclude_none=True) for p in body.properties]

    updated = await storage.schemas.update(schema_id, updates, user.id)
    return _schema_to_response(updated)


@router.delete(
    "/schemas/{schema_id}",
    operation_id="deleteSchema",
    summary="Delete a schema",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_schema(
    schema_id: str,
    storage: Storage,
    user: CurrentUser,
) -> None:
    """Delete a schema.

    Only schemas not referenced by any contracts can be deleted.
    Only the owner or team members can delete a schema.
    """
    schema = await storage.schemas.get(schema_id)
    if not schema:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "SCHEMA_NOT_FOUND", "message": f"Schema '{schema_id}' not found"},
        )

    # Check authorization
    await _check_schema_access(storage, schema, user, "delete")

    # Check if schema is in use
    can_delete, dependent_contracts = await storage.schemas.can_delete(schema_id)
    if not can_delete:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "SCHEMA_IN_USE",
                "message": f"Cannot delete schema. It is used by {len(dependent_contracts)} contracts.",
                "dependentContracts": [{"id": c.get("id"), "name": c.get("name")} for c in dependent_contracts],
            },
        )

    await storage.schemas.delete(schema_id)


# =============================================================================
# Schema Lifecycle Endpoints
# =============================================================================


@router.post(
    "/schemas/{schema_id}/publish",
    operation_id="publishSchema",
    summary="Publish a draft schema",
    response_model=SchemaResponse,
)
async def publish_schema(
    schema_id: str,
    storage: Storage,
    user: CurrentUser,
) -> SchemaResponse:
    """Publish a draft schema to make it active.

    Only schemas in 'draft' status can be published.
    Publishing makes the schema available for contracts to reference.
    """
    schema = await storage.schemas.get(schema_id)
    if not schema:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "SCHEMA_NOT_FOUND", "message": f"Schema '{schema_id}' not found"},
        )

    # Check authorization
    await _check_schema_access(storage, schema, user, "publish")

    if schema.get("status") != "draft":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_STATUS",
                "message": f"Cannot publish schema: must be in draft status (current: {schema.get('status')})",
            },
        )

    updated = await storage.schemas.update_status(schema_id, "active", user.id)
    return _schema_to_response(updated)


@router.post(
    "/schemas/{schema_id}/deprecate",
    operation_id="deprecateSchema",
    summary="Deprecate a schema",
    response_model=SchemaResponse,
)
async def deprecate_schema(
    schema_id: str,
    storage: Storage,
    user: CurrentUser,
    body: DeprecateRequest,
) -> SchemaResponse:
    """Deprecate an active schema.

    Deprecation notifies all contract owners using this schema.
    Contracts can still use deprecated schemas but are encouraged to migrate.
    """
    schema = await storage.schemas.get(schema_id)
    if not schema:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "SCHEMA_NOT_FOUND", "message": f"Schema '{schema_id}' not found"},
        )

    # Check authorization
    await _check_schema_access(storage, schema, user, "deprecate")

    if schema.get("status") != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_STATUS",
                "message": f"Cannot deprecate schema: must be in active status (current: {schema.get('status')})",
            },
        )

    # Update status
    updates = {
        "status": "deprecated",
        "deprecation_reason": body.reason,
        "replacement_schema_id": body.replacement_schema_id,
        "deprecated_at": _utc_now(),
        "deprecated_by": user.id,
    }

    updated = await storage.schemas.update(schema_id, updates, user.id)

    # Notify all contract owners
    affected = await storage.schemas.get_contracts_using_schema(schema_id)
    for contract in affected:
        contract_owner = contract.get("created_by") or contract.get("owner_id")
        if contract_owner:
            replacement_msg = ""
            if body.replacement_schema_id:
                replacement_msg = f" Replacement schema: {body.replacement_schema_id}"

            await storage.notifications.create({
                "user_id": contract_owner,
                "type": "schema_deprecated",
                "title": f"Schema '{schema.get('name')}' has been deprecated",
                "description": f"Schema used by contract '{contract.get('name')}' has been deprecated. Reason: {body.reason}.{replacement_msg} Please update your contract.",
                "href": f"/studio/contracts/{contract.get('id')}",
                "metadata": {
                    "schema_id": schema_id,
                    "contract_id": contract.get("id"),
                    "reason": body.reason,
                    "replacement_schema_id": body.replacement_schema_id,
                },
            })

    return _schema_to_response(updated)


@router.post(
    "/schemas/{schema_id}/clone",
    operation_id="cloneSchema",
    summary="Clone schema as new version",
    response_model=SchemaResponse,
    status_code=status.HTTP_201_CREATED,
)
async def clone_schema(
    schema_id: str,
    storage: Storage,
    user: CurrentUser,
    body: CloneRequest,
) -> SchemaResponse:
    """Clone a schema to create a new version.

    This is the recommended way to make breaking changes:
    1. Clone the schema
    2. Edit the new version
    3. Publish the new version
    4. Update contracts to use the new version
    5. Deprecate the old version
    """
    schema = await storage.schemas.get(schema_id)
    if not schema:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "SCHEMA_NOT_FOUND", "message": f"Schema '{schema_id}' not found"},
        )

    # Check authorization
    await _check_schema_access(storage, schema, user, "clone")

    import uuid

    now = _utc_now()
    new_schema_id = f"sch-{uuid.uuid4().hex[:12]}"
    current_version = schema.get("version", "1.0.0")
    new_version = _increment_version(current_version, "minor")

    # Create new schema as draft
    new_schema = {
        **schema,
        "id": new_schema_id,
        "version": new_version,
        "status": "draft",
        "version_history": [
            {
                "version": new_version,
                "change_type": "clone",
                "change_notes": body.change_notes,
                "created_at": now.isoformat(),
                "created_by": user.id,
                "cloned_from": {
                    "schema_id": schema_id,
                    "version": current_version,
                },
            }
        ],
        "cloned_from_schema_id": schema_id,
        "cloned_from_version": current_version,
        "created_at": now,
        "created_by": user.id,
        "updated_at": now,
        "updated_by": user.id,
    }

    # Remove deprecated fields
    new_schema.pop("deprecated_at", None)
    new_schema.pop("deprecated_by", None)
    new_schema.pop("deprecation_reason", None)
    new_schema.pop("replacement_schema_id", None)

    created = await storage.schemas.create(new_schema)
    return _schema_to_response(created)


# =============================================================================
# Version History Endpoints
# =============================================================================


@router.get(
    "/schemas/{schema_id}/versions",
    operation_id="listSchemaVersions",
    summary="List schema version history",
    response_model=VersionHistoryResponse,
)
async def list_schema_versions(
    schema_id: str,
    storage: Storage,
    user: CurrentUser,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> VersionHistoryResponse:
    """List version history for a schema."""
    schema = await storage.schemas.get(schema_id)
    if not schema:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "SCHEMA_NOT_FOUND", "message": f"Schema '{schema_id}' not found"},
        )

    versions, total = await storage.schemas.list_versions(schema_id, limit, offset)
    current_version = schema.get("version", "1.0.0")

    return VersionHistoryResponse(
        schema_id=schema_id,
        current_version=current_version,
        versions=[
            VersionHistoryItem(
                version=v.get("version", ""),
                change_type=v.get("change_type", "unknown"),
                change_notes=v.get("change_notes"),
                created_at=v.get("created_at", _utc_now()),
                created_by=v.get("created_by", ""),
                is_current=v.get("version") == current_version,
            )
            for v in versions
        ],
        total=total,
    )
