# RES-registry-003: POST /contracts/{contractId}/reject

## Response to REQ-003: Reject Contract / Request Changes Endpoint
**From:** registry
**Status:** Completed

---

## Request Summary

The platform needed an endpoint to reject contracts and request changes, transitioning from `pending_review` back to `draft` status with feedback.

---

## Expected API

**Endpoint:** `POST /api/v1/contracts/{contractId}/reject`

**Request Body:**
```json
{
  "feedback": "Required feedback explaining what needs to change"
}
```

**Expected Response:** Contract object with `status: "draft"`, `review_feedback`, `rejected_by`, `rejected_at`.

---

## Implemented API

**Location:** `griot-registry/src/griot_registry/api/contracts.py:702-792`

**Endpoint:** `POST /api/v1/contracts/{contract_id}/reject`

**Request Model:**
```python
class RejectContractRequest(BaseModel):
    feedback: str = Field(..., min_length=1, description="Required feedback explaining what needs to change")
```

**Response:** Full contract dict with rejection fields:
- `status`: "draft"
- `rejected_by`: User ID who rejected
- `rejected_at`: ISO timestamp
- `review_feedback`: Required feedback text

**Validation:**
- Contract must be in `pending_review` status
- `feedback` is required (min length 1)
- User must be assigned reviewer, team member of reviewing team, or admin

**Error Responses:**
- 400 `INVALID_STATUS_TRANSITION`: Not in pending_review status
- 400 `FEEDBACK_REQUIRED`: Missing feedback (handled by Pydantic)
- 403 `NOT_AUTHORIZED`: Not reviewer or admin
- 404 `NOT_FOUND`: Contract doesn't exist

---

## Differences from Request

| Aspect | Requested | Implemented |
|--------|-----------|-------------|
| Path param | `{contractId}` | `{contract_id}` (Python naming) |
| Feedback validation | Required field | Required with min_length=1 |
| Notifications | Create notification for owner | TODO - not yet implemented |

---

## Frontend Integration

```typescript
// Reject contract with feedback
const response = await api.post(`/contracts/${contractId}/reject`, {
  feedback: "Please add PII classifications to all personal data fields."
});
```

---

## Files Changed
- `griot-registry/src/griot_registry/api/contracts.py` - Added `reject_contract` endpoint
