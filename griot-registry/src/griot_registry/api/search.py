"""Search endpoint.

Provides full-text search across contracts.
"""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from griot_registry.api.dependencies import ContractSvc, Storage
from griot_registry.auth import OptionalUser

router = APIRouter()


# =============================================================================
# Response Models
# =============================================================================


class SearchHit(BaseModel):
    """A single search result."""

    contract_id: str
    contract_name: str
    version: str | None = None
    status: str | None = None
    score: float = 0.0
    match_type: str | None = Field(
        default=None,
        description="Type of match: name, description, schema, field",
    )
    snippet: str | None = Field(
        default=None,
        description="Text snippet showing the match context",
    )


class SearchResponse(BaseModel):
    """Search results response."""

    query: str
    items: list[SearchHit]
    total: int


# =============================================================================
# Endpoints
# =============================================================================


@router.get(
    "/search",
    operation_id="search",
    summary="Search contracts",
    response_model=SearchResponse,
)
async def search(
    service: ContractSvc,
    user: OptionalUser,
    query: str = Query(..., min_length=1, description="Search query"),
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> SearchResponse:
    """Search across all contracts.

    Performs full-text search across:
    - Contract names
    - Descriptions
    - Schema names
    - Field names and descriptions

    Results are sorted by relevance score.
    """
    results = await service.search(query, limit=limit)

    return SearchResponse(
        query=query,
        items=[
            SearchHit(
                contract_id=r.get("contract_id", ""),
                contract_name=r.get("contract_name", ""),
                version=r.get("version"),
                status=r.get("status"),
                score=r.get("score", 0.0),
                match_type=r.get("match_type"),
                snippet=r.get("snippet"),
            )
            for r in results
        ],
        total=len(results),
    )


@router.get(
    "/search/advanced",
    operation_id="advancedSearch",
    summary="Advanced search",
    response_model=SearchResponse,
)
async def advanced_search(
    storage: Storage,
    user: OptionalUser,
    query: str | None = Query(default=None, description="Text search query"),
    name: str | None = Query(default=None, description="Filter by contract name"),
    status: str | None = Query(default=None, description="Filter by status"),
    schema_name: str | None = Query(default=None, description="Filter by schema name"),
    owner: str | None = Query(default=None, description="Filter by owner/team"),
    has_pii: bool | None = Query(default=None, description="Filter by PII presence"),
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> SearchResponse:
    """Advanced search with multiple filters.

    Combines text search with structured filters for more precise results.
    """
    results: list[dict[str, Any]] = []

    # If we have a text query, use full-text search
    if query:
        results = await storage.contracts.search(query, limit=limit)
    else:
        # Otherwise, list with filters
        contracts, _ = await storage.contracts.list(
            limit=limit,
            status=status,
            schema_name=schema_name,
            owner=owner,
        )
        results = [
            {
                "contract_id": c.id,
                "contract_name": c.name,
                "version": c.version,
                "status": c.status.value,
                "score": 1.0,
            }
            for c in contracts
        ]

    # Apply additional filters if specified
    if name:
        results = [r for r in results if name.lower() in r.get("contract_name", "").lower()]

    if has_pii is not None:
        # Need to check schema catalog for PII
        pii_schemas = await storage.schema_catalog.find_schemas(has_pii=has_pii, limit=1000)
        pii_contract_ids = {s.get("contract_id") for s in pii_schemas}

        if has_pii:
            results = [r for r in results if r.get("contract_id") in pii_contract_ids]
        else:
            results = [r for r in results if r.get("contract_id") not in pii_contract_ids]

    return SearchResponse(
        query=query or "",
        items=[
            SearchHit(
                contract_id=r.get("contract_id", ""),
                contract_name=r.get("contract_name", ""),
                version=r.get("version"),
                status=r.get("status"),
                score=r.get("score", 0.0),
            )
            for r in results[:limit]
        ],
        total=len(results),
    )
