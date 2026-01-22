# REQ-004: POST /contracts/{contractId}/deprecate

## Request: Deprecate Contract Endpoint
**From:** contracts
**To:** registry
**Priority:** High
**Blocking:** Yes

### Description
Need an endpoint to deprecate an active contract. This transitions a contract from `active` to `deprecated` status.

### Context
The contracts frontend (T-CON-003) implements a lifecycle workflow where active contracts can be deprecated when they are no longer recommended for use. Deprecated contracts remain readable but should not be used for new data products.

### API Specification

**Endpoint:** `POST /api/v1/contracts/{contractId}/deprecate`

**Request:**
```json
{
  "reason": "Replaced by v2 contract with updated schema and improved quality rules.",
  "replacement_contract_id": "customer-analytics-v2"
}
```

Note: `reason` is **required**, `replacement_contract_id` is optional.

**Sample Request:**
```bash
curl -X POST https://api.griot.com/api/v1/contracts/customer-analytics-v1/deprecate \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "reason": "This contract version has been superseded by v2 which includes GDPR compliance fields and updated PII classifications.",
    "replacement_contract_id": "customer-analytics-v2"
  }'
```

**Expected Response (200 OK):**
```json
{
  "id": "customer-analytics-v1",
  "name": "Customer Analytics Contract",
  "version": "1.0.0",
  "status": "deprecated",
  "description": "Contract for customer analytics data",
  "deprecation_reason": "This contract version has been superseded by v2 which includes GDPR compliance fields and updated PII classifications.",
  "replacement_contract_id": "customer-analytics-v2",
  "deprecated_at": "2026-01-22T16:00:00Z",
  "deprecated_by": "user-001",
  "created_at": "2026-01-20T09:00:00Z",
  "updated_at": "2026-01-22T16:00:00Z"
}
```

**Error Response (400 - Wrong Status):**
```json
{
  "code": "INVALID_STATUS_TRANSITION",
  "message": "Cannot deprecate contract: contract must be in active status"
}
```

**Error Response (400 - Missing Reason):**
```json
{
  "code": "REASON_REQUIRED",
  "message": "A reason is required for deprecation"
}
```

**Error Response (400 - Invalid Replacement):**
```json
{
  "code": "INVALID_REPLACEMENT",
  "message": "Replacement contract does not exist or is not active"
}
```

**Error Response (403):**
```json
{
  "code": "NOT_AUTHORIZED",
  "message": "You are not authorized to deprecate this contract"
}
```

### Business Rules
1. Only contracts in `active` status can be deprecated
2. Only the contract owner or admin can deprecate
3. `reason` is required - must explain why deprecating
4. If `replacement_contract_id` is provided, it must reference a valid active contract
5. Deprecated contracts remain readable but show deprecation warning
6. Data products using deprecated contracts should show a warning
7. Sets `deprecated_at`, `deprecated_by`, and `deprecation_reason` fields

### Frontend Implementation
Location: `src/app/studio/contracts/[contractId]/page.tsx`
- "Deprecate" button shown for active contracts (to owners/admins)
- Opens a dialog with required reason textarea and optional replacement contract selector
- Calls mutation on confirm

Location: `src/components/contracts/ReviewDialog.tsx`
- ReviewDialog component for deprecation reason input

### Deadline
High priority - needed for T-CON-003 status workflow testing
