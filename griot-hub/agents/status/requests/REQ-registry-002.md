# REQ-002: POST /contracts/{contractId}/approve

## Request: Approve Contract Endpoint
**From:** contracts
**To:** registry
**Priority:** High
**Blocking:** Yes

### Description
Need an endpoint to approve a contract. This transitions a contract from `pending_review` to `active` status.

### Context
The contracts frontend (T-CON-003) implements a review workflow where reviewers can approve contracts that have been submitted for review. Approval makes the contract active and usable for data products.

### API Specification

**Endpoint:** `POST /api/v1/contracts/{contractId}/approve`

**Request:**
```json
{
  "comment": "Looks good. Schema is well-defined and PII classifications are correct."
}
```

Note: `comment` is optional.

**Sample Request:**
```bash
curl -X POST https://api.griot.com/api/v1/contracts/customer-analytics-v1/approve \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "comment": "Approved. All quality rules are properly configured."
  }'
```

**Expected Response (200 OK):**
```json
{
  "id": "customer-analytics-v1",
  "name": "Customer Analytics Contract",
  "version": "1.0.0",
  "status": "active",
  "description": "Contract for customer analytics data",
  "reviewer_type": "user",
  "reviewer_id": "user-002",
  "reviewer_name": "Jane Doe",
  "approved_by": "user-002",
  "approved_at": "2026-01-22T14:00:00Z",
  "approval_comment": "Approved. All quality rules are properly configured.",
  "created_at": "2026-01-20T09:00:00Z",
  "updated_at": "2026-01-22T14:00:00Z"
}
```

**Error Response (400):**
```json
{
  "code": "INVALID_STATUS_TRANSITION",
  "message": "Cannot approve contract: contract must be in pending_review status"
}
```

**Error Response (403):**
```json
{
  "code": "NOT_AUTHORIZED",
  "message": "You are not authorized to approve this contract"
}
```

### Business Rules
1. Only contracts in `pending_review` status can be approved
2. Only the assigned reviewer (user or team member) or admin can approve
3. Sets `approved_by`, `approved_at`, and optionally `approval_comment`
4. Creates a notification for the contract owner
5. Contract becomes usable for data products

### Frontend Implementation
Location: `src/app/studio/contracts/[contractId]/page.tsx`
- "Approve" button shown for pending_review contracts (to reviewers/admins)
- Opens a confirmation dialog with optional comment
- Calls mutation on confirm

### Deadline
High priority - needed for T-CON-003 status workflow testing
