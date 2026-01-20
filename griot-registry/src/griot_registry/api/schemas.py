"""Schema catalog endpoints.

Provides endpoints for searching and browsing schemas across all contracts.
"""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from griot_registry.api.dependencies import Storage
from griot_registry.auth import OptionalUser

router = APIRouter()


# =============================================================================
# Response Models
# =============================================================================


class SchemaCatalogEntry(BaseModel):
    """A schema catalog entry."""

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
    """Response for schema catalog queries."""

    items: list[SchemaCatalogEntry]
    total: int


# =============================================================================
# Endpoints
# =============================================================================


@router.get(
    "/schemas",
    operation_id="findSchemas",
    summary="Find schemas across contracts",
    response_model=SchemaCatalogResponse,
)
async def find_schemas(
    storage: Storage,
    user: OptionalUser,
    name: str | None = Query(default=None, description="Filter by schema name (partial match)"),
    physical_name: str | None = Query(default=None, description="Filter by physical table name"),
    field_name: str | None = Query(default=None, description="Filter by field name"),
    has_pii: bool | None = Query(default=None, description="Filter by PII flag"),
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> SchemaCatalogResponse:
    """Find schemas across all contracts.

    This endpoint searches the schema catalog, which indexes all schemas
    from all contracts for efficient cross-contract lookup.

    Use cases:
    - Find all contracts that define a "customers" schema
    - Find all schemas that contain an "email" field
    - Find all schemas with PII data
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
    "/schemas/contracts/{schema_name}",
    operation_id="getContractsBySchema",
    summary="Get contracts containing a schema",
)
async def get_contracts_by_schema(
    schema_name: str,
    storage: Storage,
    user: OptionalUser,
) -> dict[str, Any]:
    """Get all contract IDs that contain a schema with the given name.

    Returns:
        List of contract IDs that define the specified schema.
    """
    contract_ids = await storage.schema_catalog.get_contracts_by_schema(schema_name)

    return {
        "schema_name": schema_name,
        "contract_ids": contract_ids,
        "count": len(contract_ids),
    }


@router.post(
    "/schemas/rebuild",
    operation_id="rebuildSchemaCatalog",
    summary="Rebuild schema catalog",
)
async def rebuild_catalog(
    storage: Storage,
    user: OptionalUser,  # Should be RequireAdmin in production
) -> dict[str, Any]:
    """Rebuild the entire schema catalog from contracts.

    This operation scans all contracts and rebuilds the schema catalog index.
    Use this if the catalog gets out of sync with the contracts.

    Note: This is an admin operation and may take time for large registries.
    """
    count = await storage.schema_catalog.rebuild_catalog()

    return {
        "status": "completed",
        "schemas_indexed": count,
    }
