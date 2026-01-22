# REQ-006: GET /issues - List Issues with Filtering

## Request: List Issues Endpoint
**From:** platform
**To:** registry
**Priority:** High
**Blocking:** Yes

### Description
Need an endpoint to list data quality issues with filtering, pagination, and sorting capabilities. Issues are detected when contracts violate quality rules, experience schema drift, or breach SLAs.

### Context
The platform frontend (Issues Management) implements:
1. Issues list page with severity-based tabs (All, Critical, Warning, Info, Resolved)
2. Filtering by category, contract, assigned team, and date range
3. Search by issue title and contract name
4. Export to CSV functionality
5. Real-time issue counts per severity level

Currently using MSW mocks. Need real API endpoints for production.

### API Specification

**Endpoint:** `GET /api/v1/issues`

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| page | integer | No | Page number (default: 1) |
| limit | integer | No | Items per page (default: 20, max: 100) |
| severity | string | No | Filter by severity: `critical`, `warning`, `info` |
| status | string | No | Filter by status: `open`, `in_progress`, `resolved`, `ignored` |
| category | string | No | Filter by category: `pii_exposure`, `schema_drift`, `sla_breach`, `quality_failure`, `other` |
| contract_id | string | No | Filter by specific contract |
| assigned_team | string | No | Filter by assigned team ID |
| assigned_user | string | No | Filter by assigned user ID |
| search | string | No | Search in title, description, contract name |
| detected_after | string | No | ISO date - issues detected after this date |
| detected_before | string | No | ISO date - issues detected before this date |
| sort_by | string | No | Sort field: `detected_at`, `severity`, `status` (default: `detected_at`) |
| sort_order | string | No | Sort order: `asc`, `desc` (default: `desc`) |

**Sample Request:**
```bash
curl -X GET "https://api.griot.com/api/v1/issues?severity=critical&status=open&limit=20" \
  -H "Authorization: Bearer <token>"
```

**Expected Response (200 OK):**
```json
{
  "items": [
    {
      "id": "issue-001",
      "title": "PII Exposure Detected in Customer Email Field",
      "description": "The email field in customers table lacks proper PII classification and encryption requirements.",
      "severity": "critical",
      "category": "pii_exposure",
      "status": "open",
      "contract_id": "customer-analytics-v1",
      "contract_name": "Customer Analytics Contract",
      "contract_version": "1.2.0",
      "table": "customers",
      "field": "email",
      "quality_rule_id": "qr-pii-001",
      "assigned_team": "team-001",
      "assigned_team_name": "Data Engineering",
      "assigned_user": null,
      "assigned_user_name": null,
      "detected_at": "2026-01-22T08:30:00Z",
      "acknowledged_at": null,
      "resolved_at": null,
      "resolution": null,
      "created_at": "2026-01-22T08:30:00Z",
      "updated_at": "2026-01-22T08:30:00Z"
    },
    {
      "id": "issue-002",
      "title": "Schema Drift: New Column Added Without Contract Update",
      "description": "Column 'loyalty_tier' was added to the source table but not reflected in the contract schema.",
      "severity": "warning",
      "category": "schema_drift",
      "status": "in_progress",
      "contract_id": "customer-analytics-v1",
      "contract_name": "Customer Analytics Contract",
      "contract_version": "1.2.0",
      "table": "customers",
      "field": null,
      "quality_rule_id": null,
      "assigned_team": "team-001",
      "assigned_team_name": "Data Engineering",
      "assigned_user": "user-002",
      "assigned_user_name": "Jane Doe",
      "detected_at": "2026-01-21T14:00:00Z",
      "acknowledged_at": "2026-01-21T15:30:00Z",
      "resolved_at": null,
      "resolution": null,
      "created_at": "2026-01-21T14:00:00Z",
      "updated_at": "2026-01-21T15:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 47,
    "total_pages": 3
  },
  "summary": {
    "critical": 5,
    "warning": 18,
    "info": 24,
    "open": 23,
    "in_progress": 12,
    "resolved": 10,
    "ignored": 2
  }
}
```

**Error Response (401):**
```json
{
  "code": "UNAUTHORIZED",
  "message": "Authentication required"
}
```

### Business Rules
1. All authenticated users can view issues
2. Summary counts should be returned for quick tab display
3. Results should be sorted by detection date (newest first) by default
4. Critical issues should be prominently displayed
5. Resolved issues should still be queryable for audit purposes

### Frontend Implementation
Location: `src/app/studio/issues/page.tsx`
- Severity tabs with counts from summary
- Search input for filtering
- Category and team filter dropdowns
- DataTable with sortable columns
- Export to CSV button

### Deadline
High priority - core platform functionality
