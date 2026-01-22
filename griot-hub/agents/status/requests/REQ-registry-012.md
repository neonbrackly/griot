# REQ-012: GET /search - Global Search Endpoint

## Request: Global Search Endpoint
**From:** platform
**To:** registry
**Priority:** High
**Blocking:** Yes

### Description
Need a unified search endpoint that searches across all entity types (contracts, assets, issues, teams, users) and returns grouped, ranked results. This powers the Cmd+K global search modal.

### Context
The platform frontend (Global Search - Cmd+K) provides:
1. Keyboard shortcut (Cmd+K / Ctrl+K) to open search modal
2. Instant search results as user types
3. Results grouped by type (Contracts, Assets, Issues, Teams)
4. Keyboard navigation (arrow keys to navigate, Enter to select)
5. Recent searches history
6. Quick actions (e.g., "Create new contract")

### API Specification

**Endpoint:** `GET /api/v1/search`

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| q | string | Yes | Search query (minimum 2 characters) |
| types | string | No | Comma-separated types to search: `contracts,assets,issues,teams,users` (default: all) |
| limit | integer | No | Max results per type (default: 5, max: 20) |
| include_archived | boolean | No | Include archived/deprecated items (default: false) |

**Sample Request:**
```bash
curl -X GET "https://api.griot.com/api/v1/search?q=customer&types=contracts,assets,issues&limit=5" \
  -H "Authorization: Bearer <token>"
```

**Expected Response (200 OK):**
```json
{
  "query": "customer",
  "results": {
    "contracts": {
      "items": [
        {
          "id": "customer-analytics-v1",
          "type": "contract",
          "title": "Customer Analytics Contract",
          "subtitle": "v1.2.0 | Active | Analytics Domain",
          "description": "Contract for customer analytics data pipeline",
          "href": "/studio/contracts/customer-analytics-v1",
          "icon": "file-text",
          "status": "active",
          "metadata": {
            "version": "1.2.0",
            "domain": "analytics",
            "owner_team": "Data Engineering"
          },
          "score": 0.95,
          "highlights": [
            {
              "field": "name",
              "snippet": "<mark>Customer</mark> Analytics Contract"
            }
          ]
        },
        {
          "id": "customer-orders-v1",
          "type": "contract",
          "title": "Customer Orders Contract",
          "subtitle": "v1.0.0 | Draft | Sales Domain",
          "description": "Contract for customer order data",
          "href": "/studio/contracts/customer-orders-v1",
          "icon": "file-text",
          "status": "draft",
          "metadata": {
            "version": "1.0.0",
            "domain": "sales",
            "owner_team": "Data Engineering"
          },
          "score": 0.88,
          "highlights": [
            {
              "field": "name",
              "snippet": "<mark>Customer</mark> Orders Contract"
            }
          ]
        }
      ],
      "total": 3,
      "has_more": false
    },
    "assets": {
      "items": [
        {
          "id": "asset-customers",
          "type": "asset",
          "title": "Customers Table",
          "subtitle": "PostgreSQL | analytics_db.public.customers",
          "description": "Master customer dimension table",
          "href": "/studio/assets/asset-customers",
          "icon": "database",
          "status": "active",
          "metadata": {
            "connection": "analytics_db",
            "schema": "public",
            "table": "customers"
          },
          "score": 0.92,
          "highlights": [
            {
              "field": "name",
              "snippet": "<mark>Customers</mark> Table"
            }
          ]
        }
      ],
      "total": 1,
      "has_more": false
    },
    "issues": {
      "items": [
        {
          "id": "issue-001",
          "type": "issue",
          "title": "PII Exposure in Customer Email",
          "subtitle": "Critical | Open | Customer Analytics Contract",
          "description": "The email field lacks PII classification",
          "href": "/studio/issues/issue-001",
          "icon": "alert-triangle",
          "status": "open",
          "metadata": {
            "severity": "critical",
            "category": "pii_exposure",
            "contract_id": "customer-analytics-v1"
          },
          "score": 0.85,
          "highlights": [
            {
              "field": "title",
              "snippet": "PII Exposure in <mark>Customer</mark> Email"
            }
          ]
        }
      ],
      "total": 2,
      "has_more": true
    },
    "teams": {
      "items": [
        {
          "id": "team-customer-success",
          "type": "team",
          "title": "Customer Success Team",
          "subtitle": "8 members | CRM Domain",
          "description": "Team responsible for customer-facing data",
          "href": "/admin/teams/team-customer-success",
          "icon": "users",
          "status": "active",
          "metadata": {
            "member_count": 8,
            "domains": ["crm", "support"]
          },
          "score": 0.90,
          "highlights": [
            {
              "field": "name",
              "snippet": "<mark>Customer</mark> Success Team"
            }
          ]
        }
      ],
      "total": 1,
      "has_more": false
    },
    "users": {
      "items": [],
      "total": 0,
      "has_more": false
    }
  },
  "quick_actions": [
    {
      "id": "create-contract",
      "title": "Create new contract",
      "subtitle": "Start with a blank contract",
      "href": "/studio/contracts/new/wizard",
      "icon": "plus",
      "keywords": ["new", "create", "add"]
    }
  ],
  "total_results": 7,
  "search_time_ms": 45
}
```

**Error Response (400 - Query Too Short):**
```json
{
  "code": "QUERY_TOO_SHORT",
  "message": "Search query must be at least 2 characters"
}
```

**Error Response (401):**
```json
{
  "code": "UNAUTHORIZED",
  "message": "Authentication required"
}
```

### Search Behavior
| Field Searched | Weight | Description |
|----------------|--------|-------------|
| name/title | High | Primary identifier |
| description | Medium | Detailed text |
| tags | Medium | Categorization |
| domain | Medium | Business domain |
| table/field names | Low | Schema elements |
| owner/author | Low | Attribution |

### Business Rules
1. Minimum 2 characters required to search
2. Results are ranked by relevance score
3. User permissions filter results (only show accessible items)
4. Archived/deprecated items excluded by default
5. Response time should be < 200ms for good UX
6. Highlights use `<mark>` tags for matched text
7. Quick actions are context-aware based on user permissions

### Frontend Implementation
Location: `src/components/layout/GlobalSearch.tsx`
- Opens on Cmd+K / Ctrl+K keyboard shortcut
- Debounced search (300ms delay)
- Arrow keys navigate results
- Enter selects and navigates
- Escape closes modal
- Recent searches stored in localStorage

### Deadline
High priority - core navigation feature
