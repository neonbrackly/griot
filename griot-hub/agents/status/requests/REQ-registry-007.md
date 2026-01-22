# REQ-007: GET /issues/{issueId} - Get Issue Detail

## Request: Get Issue Detail Endpoint
**From:** platform
**To:** registry
**Priority:** High
**Blocking:** Yes

### Description
Need an endpoint to retrieve full details of a single issue, including its history, related contract information, and resolution timeline.

### Context
The platform frontend (Issue Detail page) displays:
1. Full issue information with severity badge
2. Contract and field attribution
3. Detection details and timeline
4. Assignment information (team/user)
5. Resolution form for updating status
6. Activity/comment history

### API Specification

**Endpoint:** `GET /api/v1/issues/{issueId}`

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| issueId | string | Yes | Unique issue identifier |

**Sample Request:**
```bash
curl -X GET "https://api.griot.com/api/v1/issues/issue-001" \
  -H "Authorization: Bearer <token>"
```

**Expected Response (200 OK):**
```json
{
  "id": "issue-001",
  "title": "PII Exposure Detected in Customer Email Field",
  "description": "The email field in customers table lacks proper PII classification and encryption requirements. This field contains personally identifiable information that should be classified as 'direct-identifier' and require encryption at rest.",
  "severity": "critical",
  "category": "pii_exposure",
  "status": "open",

  "contract": {
    "id": "customer-analytics-v1",
    "name": "Customer Analytics Contract",
    "version": "1.2.0",
    "status": "active",
    "owner_team": "team-001",
    "owner_team_name": "Data Engineering"
  },

  "location": {
    "table": "customers",
    "field": "email",
    "physical_table": "dim_customers",
    "physical_column": "email_address"
  },

  "quality_rule": {
    "id": "qr-pii-001",
    "name": "PII Classification Required",
    "type": "validity",
    "threshold": 100,
    "actual_value": 0,
    "last_run_at": "2026-01-22T08:30:00Z"
  },

  "assignment": {
    "team_id": "team-001",
    "team_name": "Data Engineering",
    "user_id": null,
    "user_name": null,
    "assigned_at": "2026-01-22T09:00:00Z",
    "assigned_by": "user-001"
  },

  "timeline": {
    "detected_at": "2026-01-22T08:30:00Z",
    "acknowledged_at": null,
    "in_progress_at": null,
    "resolved_at": null,
    "resolution": null,
    "resolution_notes": null,
    "resolved_by": null
  },

  "activity": [
    {
      "id": "activity-001",
      "type": "issue_created",
      "description": "Issue detected by automated quality check",
      "actor_id": "system",
      "actor_name": "System",
      "created_at": "2026-01-22T08:30:00Z"
    },
    {
      "id": "activity-002",
      "type": "issue_assigned",
      "description": "Assigned to Data Engineering team",
      "actor_id": "user-001",
      "actor_name": "Brackly Murunga",
      "created_at": "2026-01-22T09:00:00Z"
    }
  ],

  "comments": [
    {
      "id": "comment-001",
      "content": "Investigating the source system to determine PII classification requirements.",
      "author_id": "user-002",
      "author_name": "Jane Doe",
      "author_avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=jane",
      "created_at": "2026-01-22T10:15:00Z"
    }
  ],

  "metadata": {
    "run_id": "run-20260122-001",
    "source_system": "automated_quality_check",
    "tags": ["pii", "compliance", "urgent"]
  },

  "created_at": "2026-01-22T08:30:00Z",
  "updated_at": "2026-01-22T10:15:00Z"
}
```

**Error Response (404):**
```json
{
  "code": "ISSUE_NOT_FOUND",
  "message": "Issue with ID 'issue-001' not found"
}
```

### Business Rules
1. All authenticated users can view issue details
2. Activity timeline should be returned in chronological order
3. Comments should be included with author information
4. Related contract and quality rule information should be embedded
5. Location should include both logical and physical names

### Frontend Implementation
Location: `src/app/studio/issues/[issueId]/page.tsx`
- Issue header with severity badge and status
- Description and detection details
- Contract link (navigates to contract detail)
- Assignment section with team/user
- Resolution form for status updates
- Activity timeline
- Comments section

### Deadline
High priority - needed for issue management workflow
