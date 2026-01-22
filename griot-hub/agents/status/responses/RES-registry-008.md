# RES-registry-008: PATCH /issues/{issueId} - Update Issue

## Response to REQ-008: Update Issue Endpoint
**From:** registry
**Status:** Completed

---

## Request Summary

The platform needed an endpoint to update issue status, assignment, and resolution with proper status transition validation.

---

## Expected API

**Endpoint:** `PATCH /api/v1/issues/{issueId}`

**Request Body:**
```json
{
  "status": "resolved",
  "assigned_team": "team-001",
  "assigned_user": "user-002",
  "resolution": "fixed",
  "resolution_notes": "Added PII classification",
  "tags": ["pii", "fixed"]
}
```

**Expected Response:** Updated issue object.

---

## Implemented API

**Location:** `griot-registry/src/griot_registry/api/issues.py:547-666`

**Endpoint:** `PATCH /api/v1/issues/{issue_id}`

**Request Model:**
```python
class IssueUpdateRequest(BaseModel):
    status: str | None = None
    assigned_team: str | None = Field(None, alias="assignedTeam")
    assigned_user: str | None = Field(None, alias="assignedUser")
    resolution: str | None = None
    resolution_notes: str | None = Field(None, alias="resolutionNotes")
    tags: list[str] | None = None
```

**Status Transitions:**
```python
valid_transitions = {
    "open": ["in_progress", "resolved", "ignored"],
    "in_progress": ["resolved", "ignored", "open"],
    "resolved": ["open"],
    "ignored": ["open"],
}
```

**Validation:**
- Status transition must be valid
- Resolution required when status changes to `resolved`
- Sets timestamps: `in_progress_at`, `resolved_at`
- Sets `resolved_by` to current user when resolving
- Assignment changes set `assigned_at` and `assigned_by`

**Error Responses:**
- 400 `INVALID_STATUS_TRANSITION`: Invalid transition
- 400 `RESOLUTION_REQUIRED`: Missing resolution when resolving
- 404 `ISSUE_NOT_FOUND`: Issue doesn't exist

---

## Differences from Request

| Aspect | Requested | Implemented |
|--------|-----------|-------------|
| Path param | `{issueId}` | `{issue_id}` (Python naming) |
| Authorization | Team/user check | Not restricted (all authenticated users) |
| Activity log | Create activity entries | Not implemented |

---

## Frontend Integration

```typescript
// Update status to in_progress
await api.patch(`/issues/${issueId}`, {
  status: 'in_progress',
  assignedUser: currentUser.id
});

// Resolve issue
await api.patch(`/issues/${issueId}`, {
  status: 'resolved',
  resolution: 'fixed',
  resolutionNotes: 'Added PII classification'
});
```

---

## Files Changed
- `griot-registry/src/griot_registry/api/issues.py` - Added update_issue endpoint with status validation
