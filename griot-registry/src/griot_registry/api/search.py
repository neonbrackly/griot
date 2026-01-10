"""Search endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request

from griot_registry.schemas import SearchResults
from griot_registry.storage.base import StorageBackend

router = APIRouter()


async def get_storage(request: Request) -> StorageBackend:
    """Dependency to get storage backend from app state."""
    return request.app.state.storage


StorageDep = Annotated[StorageBackend, Depends(get_storage)]


@router.get(
    "/search",
    response_model=SearchResults,
    operation_id="searchContracts",
)
async def search_contracts(
    storage: StorageDep,
    q: Annotated[str, Query(description="Search query")],
    field: Annotated[str | None, Query(description="Search in specific field name")] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> SearchResults:
    """Search contracts by name, description, or field names.

    The search looks for matches in:
    - Contract names
    - Contract descriptions
    - Field names
    - Field descriptions

    Use the 'field' parameter to restrict search to a specific field name.
    """
    return await storage.search(
        query=q,
        field_filter=field,
        limit=limit,
        offset=offset,
    )
