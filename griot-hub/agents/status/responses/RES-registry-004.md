# RES-registry-004: POST /contracts/{contractId}/deprecate

## Response to REQ-004: Deprecate Contract Endpoint
**From:** registry
**Status:** Completed

---

## Request Summary

The platform needed an endpoint to deprecate active contracts with a reason and optional replacement contract reference.

---

## Expected API

**Endpoint:** `POST /api/v1/contracts/{contractId}/deprecate`

**Request Body:**
```json
{
  "reason": "Required reason for deprecation",
  "replacement_contract_id": "optional-replacement-id"
}
```

**Expected Response:** Contract object with `status: "deprecated"`, `deprecation_reason`, `deprecated_by`, `deprecated_at`.

---

## Implemented API

**Location:** `griot-registry/src/griot_registry/api/contracts.py:795-899`

**Endpoint:** `POST /api/v1/contracts/{contract_id}/deprecate`

**Request Model:**
```python
class DeprecateContractRequest(BaseModel):
    reason: str = Field(..., min_length=1, description="Required reason for deprecation")
    replacement_contract_id: str | None = Field(
        default=None,
        alias="replacementContractId",
        description="ID of replacement contract (if any)"
    )

    model_config = {"populate_by_name": True}
```

**Response:** Full contract dict with deprecation fields:
- `status`: "deprecated"
- `deprecated_by`: User ID who deprecated
- `deprecated_at`: ISO timestamp
- `deprecation_reason`: Required reason text
- `replacement_contract_id`: Optional replacement reference

**Validation:**
- Contract must be in `active` status
- `reason` is required (min length 1)
- Only contract owner or admin can deprecate
- If `replacement_contract_id` provided, it must exist and be active

**Error Responses:**
- 400 `INVALID_STATUS_TRANSITION`: Not in active status
- 400 `INVALID_REPLACEMENT`: Replacement contract not found or not active
- 403 `NOT_AUTHORIZED`: Not owner or admin
- 404 `NOT_FOUND`: Contract doesn't exist

---

## Differences from Request

| Aspect | Requested | Implemented |
|--------|-----------|-------------|
| Path param | `{contractId}` | `{contract_id}` (Python naming) |
| Field alias | `replacement_contract_id` | Accepts both `replacement_contract_id` and `replacementContractId` |
| Replacement validation | Must be active | Validates existence AND active status |

---

## Frontend Integration

```typescript
// Deprecate contract
const response = await api.post(`/contracts/${contractId}/deprecate`, {
  reason: "Superseded by v2 with improved schema",
  replacementContractId: "customer-analytics-v2"
});
```

---

## Files Changed
- `griot-registry/src/griot_registry/api/contracts.py` - Added `deprecate_contract_with_reason` endpoint
