# RES-registry-006: GET /issues - List Issues with Filtering

## Response to REQ-006: List Issues Endpoint
**From:** registry
**Status:** Completed

---

## Request Summary

The platform needed an endpoint to list data quality issues with filtering, pagination, sorting, and summary counts.

---

## Expected API

**Endpoint:** `GET /api/v1/issues`

**Query Parameters:** page, limit, severity, status, category, contract_id, assigned_team, assigned_user, search, detected_after, detected_before, sort_by, sort_order

**Expected Response:**
```json
{
  "items": [...issues],
  "pagination": { "page": 1, "limit": 20, "total": 47, "total_pages": 3 },
  "summary": { "critical": 5, "warning": 18, "info": 24, "open": 23, "in_progress": 12, "resolved": 10, "ignored": 2 }
}
```

---

## Implemented API

**Location:** `griot-registry/src/griot_registry/api/issues.py:288-366`

**Endpoint:** `GET /api/v1/issues`

**Query Parameters:**
- `page` (int, default: 1) - Page number
- `limit` (int, default: 20, max: 100) - Items per page
- `severity` (str) - Filter: critical, warning, info
- `status` (str) - Filter: open, in_progress, resolved, ignored
- `category` (str) - Filter: pii_exposure, schema_drift, sla_breach, quality_failure, other
- `contractId` (str) - Filter by contract ID
- `assignedTeam` (str) - Filter by assigned team ID
- `assignedUser` (str) - Filter by assigned user ID
- `search` (str) - Search in title, description, contract name
- `detectedAfter` (datetime) - Issues detected after date
- `detectedBefore` (datetime) - Issues detected before date
- `sortBy` (str, default: detected_at) - Sort field
- `sortOrder` (str, default: desc) - Sort order

**Response Model:**
```python
class IssueListResponse(BaseModel):
    items: list[Issue]
    pagination: dict[str, Any]
    summary: IssueSummary

class IssueSummary(BaseModel):
    critical: int = 0
    warning: int = 0
    info: int = 0
    open: int = 0
    in_progress: int = Field(0, alias="inProgress")
    resolved: int = 0
    ignored: int = 0
```

**Enrichment:**
- Issues are enriched with `contract_name`, `contract_version`, `assigned_team_name`, `assigned_user_name`

---

## Differences from Request

| Aspect | Requested | Implemented |
|--------|-----------|-------------|
| Query params | snake_case | camelCase aliases (contractId, assignedTeam, etc.) |
| Summary counts | Global counts | Counts from current result set |
| Search | Full implementation | Basic storage filter (full-text depends on storage) |

---

## Frontend Integration

```typescript
const { data } = useQuery(['issues', filters], () =>
  api.get('/issues', {
    params: {
      severity: 'critical',
      status: 'open',
      page: 1,
      limit: 20
    }
  })
);
// data.items, data.pagination, data.summary
```

---

## Files Changed
- `griot-registry/src/griot_registry/api/issues.py` - Enhanced list endpoint with filtering and summary
