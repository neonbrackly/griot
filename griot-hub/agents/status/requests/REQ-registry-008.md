# REQ-008: PATCH /issues/{issueId} - Update Issue

## Request: Update Issue Endpoint
**From:** platform
**To:** registry
**Priority:** High
**Blocking:** Yes

### Description
Need an endpoint to update issue status, assignment, and add resolution notes. This is the primary endpoint for managing the issue lifecycle from detection to resolution.

### Context
The platform frontend (Issue Detail page) allows users to:
1. Change issue status (open -> in_progress -> resolved/ignored)
2. Assign/reassign to a team or specific user
3. Add resolution notes when resolving
4. Acknowledge critical issues

### API Specification

**Endpoint:** `PATCH /api/v1/issues/{issueId}`

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| issueId | string | Yes | Unique issue identifier |

**Request Body:**
```json
{
  "status": "resolved",
  "assigned_team": "team-001",
  "assigned_user": "user-002",
  "resolution": "fixed",
  "resolution_notes": "Added PII classification 'direct-identifier' to the email field. Updated contract schema and re-validated.",
  "tags": ["pii", "compliance", "fixed"]
}
```

Note: All fields are optional. Only include fields being updated.

**Field Descriptions:**
| Field | Type | Description |
|-------|------|-------------|
| status | string | New status: `open`, `in_progress`, `resolved`, `ignored` |
| assigned_team | string | Team ID to assign the issue to |
| assigned_user | string | User ID to assign the issue to (within assigned team) |
| resolution | string | Resolution type: `fixed`, `wont_fix`, `false_positive`, `deferred` |
| resolution_notes | string | Explanation of how the issue was resolved |
| tags | array | Updated tags for categorization |

**Sample Request - Mark In Progress:**
```bash
curl -X PATCH "https://api.griot.com/api/v1/issues/issue-001" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_progress",
    "assigned_user": "user-002"
  }'
```

**Sample Request - Resolve Issue:**
```bash
curl -X PATCH "https://api.griot.com/api/v1/issues/issue-001" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "resolved",
    "resolution": "fixed",
    "resolution_notes": "Added PII classification to the email field in contract schema."
  }'
```

**Expected Response (200 OK):**
```json
{
  "id": "issue-001",
  "title": "PII Exposure Detected in Customer Email Field",
  "description": "The email field in customers table lacks proper PII classification and encryption requirements.",
  "severity": "critical",
  "category": "pii_exposure",
  "status": "resolved",
  "contract_id": "customer-analytics-v1",
  "contract_name": "Customer Analytics Contract",
  "contract_version": "1.2.0",
  "table": "customers",
  "field": "email",
  "assigned_team": "team-001",
  "assigned_team_name": "Data Engineering",
  "assigned_user": "user-002",
  "assigned_user_name": "Jane Doe",
  "detected_at": "2026-01-22T08:30:00Z",
  "acknowledged_at": "2026-01-22T09:00:00Z",
  "resolved_at": "2026-01-22T14:30:00Z",
  "resolution": "fixed",
  "resolution_notes": "Added PII classification to the email field in contract schema.",
  "resolved_by": "user-002",
  "tags": ["pii", "compliance", "fixed"],
  "created_at": "2026-01-22T08:30:00Z",
  "updated_at": "2026-01-22T14:30:00Z"
}
```

**Error Response (400 - Invalid Transition):**
```json
{
  "code": "INVALID_STATUS_TRANSITION",
  "message": "Cannot transition from 'resolved' to 'open'. Resolved issues must be reopened explicitly."
}
```

**Error Response (400 - Resolution Required):**
```json
{
  "code": "RESOLUTION_REQUIRED",
  "message": "Resolution notes are required when marking an issue as resolved"
}
```

**Error Response (403):**
```json
{
  "code": "NOT_AUTHORIZED",
  "message": "You are not authorized to update this issue"
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
1. Only assigned team members, assigned user, or admins can update an issue
2. Resolution notes are required when status changes to `resolved`
3. Status transitions follow this flow:
   - `open` -> `in_progress`, `resolved`, `ignored`
   - `in_progress` -> `resolved`, `ignored`, `open` (re-open)
   - `resolved` -> `open` (re-open only)
   - `ignored` -> `open` (re-open only)
4. When status changes to `resolved`:
   - Set `resolved_at` to current timestamp
   - Set `resolved_by` to current user
   - Require `resolution` type
5. When status changes to `in_progress`:
   - Set `in_progress_at` if not already set
6. Assignment changes create activity log entries
7. Status changes trigger notifications to relevant users

### Frontend Implementation
Location: `src/app/studio/issues/[issueId]/page.tsx`
- Status dropdown with allowed transitions
- Assignment selectors (team dropdown, user dropdown)
- Resolution form (shown when resolving):
  - Resolution type radio buttons
  - Resolution notes textarea
  - Submit button
- Activity timeline updates on status change

### Deadline
High priority - needed for issue management workflow
