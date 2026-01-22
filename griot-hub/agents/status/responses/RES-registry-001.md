# RES-registry-001: POST /contracts/{contractId}/submit

## Response to REQ-001: Submit Contract for Review Endpoint
**From:** registry
**Status:** Completed

---

## Request Summary

The platform needed an endpoint to submit contracts for review, transitioning from `draft` to `pending_review` status.

---

## Expected API

**Endpoint:** `POST /api/v1/contracts/{contractId}/submit`

**Request Body:**
```json
{
  "message": "Optional message for reviewers"
}
```

**Expected Response:** Contract object with `status: "pending_review"`, `submitted_at`, `submitted_by` fields.

---

## Implemented API

**Location:** `griot-registry/src/griot_registry/api/contracts.py:510-607`

**Endpoint:** `POST /api/v1/contracts/{contract_id}/submit`

**Request Model:**
```python
class SubmitForReviewRequest(BaseModel):
    message: str | None = Field(default=None, description="Optional message for reviewers")
```

**Response:** Full contract dict with workflow fields:
- `status`: "pending_review"
- `submitted_by`: User ID who submitted
- `submitted_at`: ISO timestamp
- `submission_message`: Optional message

**Validation:**
- Contract must be in `draft` status
- Reviewer must be assigned (`reviewer_id`)
- Only contract owner or admin can submit

**Error Responses:**
- 400 `INVALID_STATUS_TRANSITION`: Not in draft status
- 400 `REVIEWER_REQUIRED`: No reviewer assigned
- 403 `NOT_AUTHORIZED`: Not owner or admin
- 404 `NOT_FOUND`: Contract doesn't exist

---

## Differences from Request

| Aspect | Requested | Implemented |
|--------|-----------|-------------|
| Path param | `{contractId}` | `{contract_id}` (Python naming) |
| Notifications | Create task for reviewer | TODO - not yet implemented |
| Response | Custom fields | Full contract dict |

---

## Frontend Integration

```typescript
// Submit contract for review
const response = await api.post(`/contracts/${contractId}/submit`, {
  message: "Ready for review"
});
```

---

## Files Changed
- `griot-registry/src/griot_registry/api/contracts.py` - Added `submit_contract` endpoint
