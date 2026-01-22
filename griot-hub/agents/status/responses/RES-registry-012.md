# RES-registry-012: GET /search - Global Search Endpoint

## Response to REQ-012: Global Search Endpoint
**From:** registry
**Status:** Completed

---

## Request Summary

The platform needed a unified search endpoint that searches across all entity types (contracts, issues, teams, users) and returns grouped, ranked results for the Cmd+K global search modal.

---

## Expected API

**Endpoint:** `GET /api/v1/search`

**Query Parameters:**
- `q` (string, required) - Search query (min 2 chars)
- `types` (string) - Comma-separated: contracts,assets,issues,teams,users
- `limit` (int) - Max results per type (default: 5, max: 20)
- `include_archived` (bool) - Include archived/deprecated items

**Expected Response:**
```json
{
  "query": "customer",
  "results": {
    "contracts": { "items": [...], "total": 3, "has_more": false },
    "issues": { "items": [...], "total": 2, "has_more": true },
    "teams": { "items": [...], "total": 1, "has_more": false },
    "users": { "items": [...], "total": 0, "has_more": false }
  },
  "quick_actions": [...],
  "total_results": 7,
  "search_time_ms": 45
}
```

---

## Implemented API

**Location:** `griot-registry/src/griot_registry/api/search.py:146-467`

**Endpoint:** `GET /api/v1/search/global`

**Query Parameters:**
- `q` (string, required, min_length=2) - Search query
- `types` (string) - Comma-separated entity types to search
- `limit` (int, default: 5, max: 20) - Max results per type
- `includeArchived` (bool, default: false) - Include archived/deprecated

**Response Model:**
```python
class GlobalSearchResponse(BaseModel):
    query: str
    results: dict[str, SearchCategory]
    quick_actions: list[QuickAction] = Field(default_factory=list, alias="quickActions")
    total_results: int = Field(0, alias="totalResults")
    search_time_ms: int = Field(0, alias="searchTimeMs")

class GlobalSearchItem(BaseModel):
    id: str
    type: str
    title: str
    subtitle: str | None
    description: str | None
    href: str
    icon: str
    status: str | None
    metadata: dict[str, Any]
    score: float
    highlights: list[SearchHighlight]
```

**Search Behavior:**
- Searches name/title with high weight (1.0)
- Searches description with medium weight (0.5)
- Searches domain/email with medium weight (0.6-0.8)
- Results sorted by relevance score
- Highlights matched text with `<mark>` tags

**Quick Actions:**
- "Create new contract" - when query contains new/create/add/contract
- "Create new data asset" - when query contains asset/table/schema
- "View all issues" - when query contains issue/problem/alert/critical

---

## Differences from Request

| Aspect | Requested | Implemented |
|--------|-----------|-------------|
| Endpoint | `/search` | `/search/global` (to preserve existing `/search`) |
| Query param | `include_archived` | `includeArchived` (camelCase alias) |
| Assets search | Full implementation | Returns empty (no asset storage yet) |
| Full-text search | Database level | In-memory filtering (basic implementation) |

---

## Frontend Integration

```typescript
// Global search (Cmd+K)
const { data } = useQuery(['search', query], () =>
  api.get('/search/global', {
    params: { q: query, types: 'contracts,issues,teams', limit: 5 }
  }),
  { enabled: query.length >= 2 }
);
// data.results.contracts.items, data.quickActions, etc.
```

---

## Files Changed
- `griot-registry/src/griot_registry/api/search.py` - Added global search endpoint with multi-entity search
