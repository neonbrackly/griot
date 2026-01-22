# RES-registry-002: POST /contracts/{contractId}/approve

## Response to REQ-002: Approve Contract Endpoint
**From:** registry
**Status:** Completed

---

## Request Summary

The platform needed an endpoint to approve contracts, transitioning from `pending_review` to `active` status.

---

## Expected API

**Endpoint:** `POST /api/v1/contracts/{contractId}/approve`

**Request Body:**
```json
{
  "comment": "Optional approval comment"
}
```

**Expected Response:** Contract object with `status: "active"`, `approved_by`, `approved_at`, `approval_comment`.

---

## Implemented API

**Location:** `griot-registry/src/griot_registry/api/contracts.py:610-699`

**Endpoint:** `POST /api/v1/contracts/{contract_id}/approve`

**Request Model:**
```python
class ApproveContractRequest(BaseModel):
    comment: str | None = Field(default=None, description="Optional approval comment")
```

**Response:** Full contract dict with approval fields:
- `status`: "active"
- `approved_by`: User ID who approved
- `approved_at`: ISO timestamp
- `approval_comment`: Optional comment

**Validation:**
- Contract must be in `pending_review` status
- User must be assigned reviewer, team member of reviewing team, or admin

**Error Responses:**
- 400 `INVALID_STATUS_TRANSITION`: Not in pending_review status
- 403 `NOT_AUTHORIZED`: Not reviewer or admin
- 404 `NOT_FOUND`: Contract doesn't exist

---

## Differences from Request

| Aspect | Requested | Implemented |
|--------|-----------|-------------|
| Path param | `{contractId}` | `{contract_id}` (Python naming) |
| Team review | Implicit | Explicit check for team membership |
| Notifications | Create notification for owner | TODO - not yet implemented |

---

## Frontend Integration

```typescript
// Approve contract
const response = await api.post(`/contracts/${contractId}/approve`, {
  comment: "Looks good!"
});
```

---

## Files Changed
- `griot-registry/src/griot_registry/api/contracts.py` - Added `approve_contract` endpoint
