# RES-registry-005: Extended Contract Response Schema

## Response to REQ-005: Add Reviewer and Workflow Fields to Contract Response
**From:** registry
**Status:** Completed

---

## Request Summary

The platform needed extended fields on contract responses to support reviewer assignment, status workflow, and ownership tracking.

---

## Expected Additional Fields

```typescript
interface ContractExtension {
  // Reviewer assignment
  reviewer_type?: 'user' | 'team'
  reviewer_id?: string
  reviewer_name?: string

  // Approval info
  approved_by?: string
  approved_at?: string
  approval_comment?: string

  // Rejection info
  review_feedback?: string
  rejected_by?: string
  rejected_at?: string

  // Submission info
  submitted_by?: string
  submitted_at?: string

  // Deprecation info
  deprecation_reason?: string
  replacement_contract_id?: string
  deprecated_by?: string
  deprecated_at?: string

  // Ownership
  owner_team?: string
  created_by?: string
  updated_by?: string
}
```

---

## Implemented

**Location:** `griot-registry/src/griot_registry/api/contracts.py`

**Request Models Added:**
- `SubmitForReviewRequest` - for submission message
- `ApproveContractRequest` - for approval comment
- `RejectContractRequest` - for feedback
- `DeprecateContractRequest` - for reason and replacement
- `AssignReviewerRequest` - for reviewer assignment

**Workflow Endpoints:**
- `POST /contracts/{contract_id}/submit` - Sets `submitted_by`, `submitted_at`, `submission_message`
- `POST /contracts/{contract_id}/approve` - Sets `approved_by`, `approved_at`, `approval_comment`
- `POST /contracts/{contract_id}/reject` - Sets `rejected_by`, `rejected_at`, `review_feedback`
- `POST /contracts/{contract_id}/deprecate` - Sets `deprecated_by`, `deprecated_at`, `deprecation_reason`, `replacement_contract_id`
- `POST /contracts/{contract_id}/reviewer` - Sets `reviewer_type`, `reviewer_id`

**Contract Response:**
All workflow endpoints return the full contract dict including these extended fields when they are set.

---

## Differences from Request

| Aspect | Requested | Implemented |
|--------|-----------|-------------|
| `reviewer_name` | Auto-populated | Not implemented (frontend should fetch) |
| `owner_team` | Direct field | Stored in contract |
| Timestamps | ISO strings | ISO strings via `datetime.isoformat()` |

---

## Frontend Integration

```typescript
// Create/update contract with reviewer
const contract = await api.put(`/contracts/${id}`, {
  ...contractData,
  reviewer_type: "user",
  reviewer_id: "user-002"
});

// Contract detail page
const { data: contract } = useQuery(['contract', id], () => api.get(`/contracts/${id}`));
// contract.approved_by, contract.approved_at, etc. are available
```

---

## Files Changed
- `griot-registry/src/griot_registry/api/contracts.py` - Added request models and workflow endpoints
