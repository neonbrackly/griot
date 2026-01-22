# REQ-001: POST /contracts/{contractId}/submit

## Request: Submit Contract for Review Endpoint
**From:** contracts
**To:** registry
**Priority:** High
**Blocking:** Yes

### Description
Need an endpoint to submit a contract for review. This transitions a contract from `draft` to `pending_review` status.

### Context
The contracts frontend (T-CON-003) implements a status workflow where:
1. Users create contracts in `draft` status
2. Users submit for review when ready
3. Reviewers approve or request changes
4. Active contracts can be deprecated

Currently, the frontend uses `PUT /contracts/{id}` with status change, but a dedicated endpoint provides better control and validation.

### API Specification

**Endpoint:** `POST /api/v1/contracts/{contractId}/submit`

**Request:**
```json
{
  "message": "Ready for your review. Key changes in schema section."
}
```

Note: `message` is optional.

**Sample Request:**
```bash
curl -X POST https://api.griot.com/api/v1/contracts/customer-analytics-v1/submit \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Please review the new PII classifications on the email and phone fields."
  }'
```

**Expected Response (200 OK):**
```json
{
  "id": "customer-analytics-v1",
  "name": "Customer Analytics Contract",
  "version": "1.0.0",
  "status": "pending_review",
  "description": "Contract for customer analytics data",
  "reviewer_type": "user",
  "reviewer_id": "user-002",
  "reviewer_name": "Jane Doe",
  "submitted_at": "2026-01-22T10:30:00Z",
  "submitted_by": "user-001",
  "created_at": "2026-01-20T09:00:00Z",
  "updated_at": "2026-01-22T10:30:00Z"
}
```

**Error Response (400):**
```json
{
  "code": "INVALID_STATUS_TRANSITION",
  "message": "Cannot submit contract: contract must be in draft status"
}
```

**Error Response (400 - No Reviewer):**
```json
{
  "code": "REVIEWER_REQUIRED",
  "message": "Cannot submit contract: no reviewer assigned"
}
```

### Business Rules
1. Only contracts in `draft` status can be submitted
2. Contract must have a reviewer assigned (`reviewer_id`)
3. Only the contract owner can submit
4. Creates a notification/task for the assigned reviewer
5. Sets `submitted_at` and `submitted_by` fields

### Frontend Implementation
Location: `src/app/studio/contracts/[contractId]/page.tsx`
- "Submit for Review" button shown for draft contracts
- Opens a dialog for optional message
- Calls mutation on confirm

### Deadline
High priority - needed for T-CON-003 status workflow testing
