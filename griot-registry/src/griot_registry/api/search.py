"""Search endpoint.

Provides full-text search across contracts, issues, teams, and users.
"""

from __future__ import annotations

import time
from typing import Annotated, Any

from fastapi import APIRouter, HTTPException, Query, Request, status
from pydantic import BaseModel, Field

from griot_registry.api.dependencies import ContractSvc, Storage
from griot_registry.auth import CurrentUser, OptionalUser

router = APIRouter()


# =============================================================================
# Response Models - Global Search (Cmd+K)
# =============================================================================


class SearchHighlight(BaseModel):
    """Highlight for matched text."""

    field: str
    snippet: str


class GlobalSearchItem(BaseModel):
    """A single global search result item."""

    id: str
    type: str
    title: str
    subtitle: str | None = None
    description: str | None = None
    href: str
    icon: str
    status: str | None = None
    metadata: dict[str, Any] = {}
    score: float = 0.0
    highlights: list[SearchHighlight] = []


class SearchCategory(BaseModel):
    """Search results for a specific entity type."""

    items: list[GlobalSearchItem]
    total: int
    has_more: bool = Field(False, alias="hasMore")

    model_config = {"populate_by_name": True}


class QuickAction(BaseModel):
    """Quick action suggestion in search."""

    id: str
    title: str
    subtitle: str
    href: str
    icon: str
    keywords: list[str] = []


class GlobalSearchResponse(BaseModel):
    """Response for global search (Cmd+K)."""

    query: str
    results: dict[str, SearchCategory]
    quick_actions: list[QuickAction] = Field(default_factory=list, alias="quickActions")
    total_results: int = Field(0, alias="totalResults")
    search_time_ms: int = Field(0, alias="searchTimeMs")

    model_config = {"populate_by_name": True}


# =============================================================================
# Response Models - Legacy Contract Search
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
# Helper Functions
# =============================================================================


def _highlight_text(text: str, query: str) -> str:
    """Wrap query terms with <mark> tags for highlighting."""
    if not text or not query:
        return text
    query_lower = query.lower()
    text_lower = text.lower()
    if query_lower in text_lower:
        start = text_lower.index(query_lower)
        end = start + len(query)
        return f"{text[:start]}<mark>{text[start:end]}</mark>{text[end:]}"
    return text


def _calculate_score(text: str, query: str, weight: float = 1.0) -> float:
    """Calculate relevance score for a match."""
    if not text or not query:
        return 0.0
    text_lower = text.lower()
    query_lower = query.lower()

    if query_lower == text_lower:
        return 1.0 * weight  # Exact match
    elif text_lower.startswith(query_lower):
        return 0.9 * weight  # Prefix match
    elif query_lower in text_lower:
        return 0.7 * weight  # Contains match
    return 0.0


# =============================================================================
# Endpoints - Global Search (Cmd+K)
# =============================================================================


@router.get(
    "/search/global",
    operation_id="globalSearch",
    summary="Global search across all entities",
    response_model=GlobalSearchResponse,
)
async def global_search(
    request: Request,
    storage: Storage,
    user: CurrentUser,
    q: str = Query(..., min_length=2, description="Search query (minimum 2 characters)"),
    types: str | None = Query(
        default=None,
        description="Comma-separated types to search: contracts,assets,issues,teams,users",
    ),
    limit: Annotated[int, Query(ge=1, le=20)] = 5,
    include_archived: bool = Query(default=False, alias="includeArchived", description="Include archived/deprecated items"),
) -> GlobalSearchResponse:
    """Global search across all entity types.

    Powers the Cmd+K global search modal. Searches across:
    - Contracts (by name, description, domain)
    - Issues (by title, description, contract name)
    - Teams (by name, description)
    - Users (by name, email)

    Results are grouped by type and ranked by relevance score.
    """
    start_time = time.time()
    query_lower = q.lower()

    # Parse types to search
    search_types = {"contracts", "assets", "issues", "teams", "users"}
    if types:
        search_types = {t.strip().lower() for t in types.split(",")}

    results: dict[str, SearchCategory] = {}
    total_results = 0

    # Search contracts
    if "contracts" in search_types:
        contract_items: list[GlobalSearchItem] = []
        try:
            contracts, total_contracts = await storage.contracts.list(limit=100)
            for contract in contracts:
                contract_dict = contract.to_dict() if hasattr(contract, "to_dict") else contract
                name = contract_dict.get("name", "")
                description = contract_dict.get("description", "")
                domain = contract_dict.get("domain", "")
                status_val = contract_dict.get("status", "draft")

                # Skip deprecated if not including archived
                if not include_archived and status_val == "deprecated":
                    continue

                # Calculate score
                score = max(
                    _calculate_score(name, q, 1.0),
                    _calculate_score(description, q, 0.5),
                    _calculate_score(domain, q, 0.6),
                )

                if score > 0:
                    highlights = []
                    if _calculate_score(name, q) > 0:
                        highlights.append(SearchHighlight(
                            field="name",
                            snippet=_highlight_text(name, q),
                        ))

                    contract_items.append(GlobalSearchItem(
                        id=contract_dict.get("id", ""),
                        type="contract",
                        title=name,
                        subtitle=f"v{contract_dict.get('version', '1.0.0')} | {status_val.title()} | {domain.title() if domain else 'No Domain'}",
                        description=description[:100] if description else None,
                        href=f"/studio/contracts/{contract_dict.get('id', '')}",
                        icon="file-text",
                        status=status_val,
                        metadata={
                            "version": contract_dict.get("version", "1.0.0"),
                            "domain": domain,
                            "owner_team": contract_dict.get("owner_team"),
                        },
                        score=score,
                        highlights=highlights,
                    ))
        except Exception:
            pass

        # Sort by score and limit
        contract_items.sort(key=lambda x: x.score, reverse=True)
        total_contracts_found = len(contract_items)
        contract_items = contract_items[:limit]
        results["contracts"] = SearchCategory(
            items=contract_items,
            total=total_contracts_found,
            has_more=total_contracts_found > limit,
        )
        total_results += total_contracts_found

    # Search issues
    if "issues" in search_types:
        issue_items: list[GlobalSearchItem] = []
        try:
            issues, _ = await storage.issues.list(limit=100)
            for issue in issues:
                title = issue.get("title", "")
                description = issue.get("description", "")
                contract_name = issue.get("contract_name", "")
                status_val = issue.get("status", "open")

                # Skip resolved if not including archived
                if not include_archived and status_val in ("resolved", "ignored"):
                    continue

                score = max(
                    _calculate_score(title, q, 1.0),
                    _calculate_score(description, q, 0.5),
                    _calculate_score(contract_name, q, 0.6),
                )

                if score > 0:
                    highlights = []
                    if _calculate_score(title, q) > 0:
                        highlights.append(SearchHighlight(
                            field="title",
                            snippet=_highlight_text(title, q),
                        ))

                    severity = issue.get("severity", "warning")
                    issue_items.append(GlobalSearchItem(
                        id=issue.get("id", ""),
                        type="issue",
                        title=title,
                        subtitle=f"{severity.title()} | {status_val.title()} | {contract_name or 'No Contract'}",
                        description=description[:100] if description else None,
                        href=f"/studio/issues/{issue.get('id', '')}",
                        icon="alert-triangle",
                        status=status_val,
                        metadata={
                            "severity": severity,
                            "category": issue.get("category"),
                            "contract_id": issue.get("contract_id"),
                        },
                        score=score,
                        highlights=highlights,
                    ))
        except Exception:
            pass

        issue_items.sort(key=lambda x: x.score, reverse=True)
        total_issues_found = len(issue_items)
        issue_items = issue_items[:limit]
        results["issues"] = SearchCategory(
            items=issue_items,
            total=total_issues_found,
            has_more=total_issues_found > limit,
        )
        total_results += total_issues_found

    # Search teams
    if "teams" in search_types:
        team_items: list[GlobalSearchItem] = []
        try:
            teams, _ = await storage.teams.list(limit=100)
            for team in teams:
                name = team.get("name", "")
                description = team.get("description", "")

                score = max(
                    _calculate_score(name, q, 1.0),
                    _calculate_score(description, q, 0.5),
                )

                if score > 0:
                    highlights = []
                    if _calculate_score(name, q) > 0:
                        highlights.append(SearchHighlight(
                            field="name",
                            snippet=_highlight_text(name, q),
                        ))

                    member_count = len(team.get("members", []))
                    domains = team.get("domains", [])
                    team_items.append(GlobalSearchItem(
                        id=team.get("id", ""),
                        type="team",
                        title=name,
                        subtitle=f"{member_count} members | {', '.join(domains[:2]) if domains else 'No domains'}",
                        description=description[:100] if description else None,
                        href=f"/admin/teams/{team.get('id', '')}",
                        icon="users",
                        status="active",
                        metadata={
                            "member_count": member_count,
                            "domains": domains,
                        },
                        score=score,
                        highlights=highlights,
                    ))
        except Exception:
            pass

        team_items.sort(key=lambda x: x.score, reverse=True)
        total_teams_found = len(team_items)
        team_items = team_items[:limit]
        results["teams"] = SearchCategory(
            items=team_items,
            total=total_teams_found,
            has_more=total_teams_found > limit,
        )
        total_results += total_teams_found

    # Search users
    if "users" in search_types:
        user_items: list[GlobalSearchItem] = []
        try:
            users, _ = await storage.users.list(limit=100)
            for u in users:
                name = u.get("name", "")
                email = u.get("email", "")
                status_val = u.get("status", "active")

                # Skip inactive if not including archived
                if not include_archived and status_val == "inactive":
                    continue

                score = max(
                    _calculate_score(name, q, 1.0),
                    _calculate_score(email, q, 0.8),
                )

                if score > 0:
                    highlights = []
                    if _calculate_score(name, q) > 0:
                        highlights.append(SearchHighlight(
                            field="name",
                            snippet=_highlight_text(name, q),
                        ))

                    role = u.get("role", "Viewer")
                    user_items.append(GlobalSearchItem(
                        id=u.get("id", ""),
                        type="user",
                        title=name,
                        subtitle=f"{role} | {email}",
                        description=None,
                        href=f"/admin/users/{u.get('id', '')}",
                        icon="user",
                        status=status_val,
                        metadata={
                            "email": email,
                            "role": role,
                        },
                        score=score,
                        highlights=highlights,
                    ))
        except Exception:
            pass

        user_items.sort(key=lambda x: x.score, reverse=True)
        total_users_found = len(user_items)
        user_items = user_items[:limit]
        results["users"] = SearchCategory(
            items=user_items,
            total=total_users_found,
            has_more=total_users_found > limit,
        )
        total_results += total_users_found

    # Add quick actions based on query and user permissions
    quick_actions: list[QuickAction] = []
    quick_action_keywords = q.lower().split()

    # Create contract action
    if any(kw in ["new", "create", "add", "contract"] for kw in quick_action_keywords):
        quick_actions.append(QuickAction(
            id="create-contract",
            title="Create new contract",
            subtitle="Start with a blank contract",
            href="/studio/contracts/new/wizard",
            icon="plus",
            keywords=["new", "create", "add", "contract"],
        ))

    # Create asset action
    if any(kw in ["new", "create", "add", "asset", "table", "schema"] for kw in quick_action_keywords):
        quick_actions.append(QuickAction(
            id="create-asset",
            title="Create new data asset",
            subtitle="Define a new schema or table",
            href="/studio/assets/new",
            icon="database",
            keywords=["new", "create", "add", "asset", "table", "schema"],
        ))

    # View issues action
    if any(kw in ["issue", "problem", "alert", "critical"] for kw in quick_action_keywords):
        quick_actions.append(QuickAction(
            id="view-issues",
            title="View all issues",
            subtitle="Browse data quality issues",
            href="/studio/issues",
            icon="alert-triangle",
            keywords=["issue", "problem", "alert", "critical"],
        ))

    elapsed_ms = int((time.time() - start_time) * 1000)

    return GlobalSearchResponse(
        query=q,
        results=results,
        quick_actions=quick_actions,
        total_results=total_results,
        search_time_ms=elapsed_ms,
    )


# =============================================================================
# Endpoints - Legacy Contract Search
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
