# REQ-003: POST /contracts/{contractId}/reject

## Request: Reject Contract / Request Changes Endpoint
**From:** contracts
**To:** registry
**Priority:** High
**Blocking:** Yes

### Description
Need an endpoint to reject a contract and request changes. This transitions a contract from `pending_review` back to `draft` status with feedback.

### Context
The contracts frontend (T-CON-003) implements a review workflow where reviewers can request changes on contracts that have been submitted for review. This sends the contract back to draft status with feedback explaining what needs to be changed.

### API Specification

**Endpoint:** `POST /api/v1/contracts/{contractId}/reject`

**Request:**
```json
{
  "feedback": "Missing PII classification on email field. Please add privacy metadata for all personal data fields."
}
```

Note: `feedback` is **required**.

**Sample Request:**
```bash
curl -X POST https://api.griot.com/api/v1/contracts/customer-analytics-v1/reject \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "feedback": "Please address the following:\n1. Add PII classification to email field\n2. Completeness threshold for phone should be >= 95%\n3. Missing description for customer_id field"
  }'
```

**Expected Response (200 OK):**
```json
{
  "id": "customer-analytics-v1",
  "name": "Customer Analytics Contract",
  "version": "1.0.0",
  "status": "draft",
  "description": "Contract for customer analytics data",
  "reviewer_type": "user",
  "reviewer_id": "user-002",
  "reviewer_name": "Jane Doe",
  "review_feedback": "Please address the following:\n1. Add PII classification to email field\n2. Completeness threshold for phone should be >= 95%\n3. Missing description for customer_id field",
  "rejected_at": "2026-01-22T14:00:00Z",
  "rejected_by": "user-002",
  "created_at": "2026-01-20T09:00:00Z",
  "updated_at": "2026-01-22T14:00:00Z"
}
```

**Error Response (400 - Wrong Status):**
```json
{
  "code": "INVALID_STATUS_TRANSITION",
  "message": "Cannot reject contract: contract must be in pending_review status"
}
```

**Error Response (400 - Missing Feedback):**
```json
{
  "code": "FEEDBACK_REQUIRED",
  "message": "Feedback is required when requesting changes"
}
```

**Error Response (403):**
```json
{
  "code": "NOT_AUTHORIZED",
  "message": "You are not authorized to reject this contract"
}
```

### Business Rules
1. Only contracts in `pending_review` status can be rejected
2. Only the assigned reviewer (user or team member) or admin can reject
3. `feedback` is required - must explain what needs to change
4. Status returns to `draft` so owner can make changes
5. Stores feedback in `review_feedback` field
6. Creates a notification for the contract owner
7. Sets `rejected_at` and `rejected_by` fields

### Frontend Implementation
Location: `src/app/studio/contracts/[contractId]/page.tsx`
- "Request Changes" button shown for pending_review contracts (to reviewers/admins)
- Opens a dialog with required feedback textarea
- Calls mutation on confirm

Location: `src/components/contracts/ReviewDialog.tsx`
- ReviewDialog component for feedback input

### Deadline
High priority - needed for T-CON-003 status workflow testing
