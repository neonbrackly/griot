# REQ-005: Extended Contract Response Schema

## Request: Add Reviewer and Workflow Fields to Contract Response
**From:** contracts
**To:** registry
**Priority:** High
**Blocking:** Yes

### Description
The Contract response from `GET /contracts/{id}` and `PUT /contracts/{id}` needs additional fields to support the reviewer assignment (T-CON-002) and status workflow (T-CON-003) features.

### Context
The contracts frontend implements:
1. Reviewer assignment in the creation wizard (T-CON-002)
2. Status workflow with submit, approve, reject, deprecate actions (T-CON-003)
3. Enhanced detail page showing ownership and governance (T-CON-004)

These features require additional fields on the Contract response that are not currently returned by the registry API.

### Required Additional Fields

Add these fields to the Contract schema:

```typescript
interface ContractExtension {
  // Reviewer assignment (T-CON-002)
  reviewer_type?: 'user' | 'team'      // Type of reviewer
  reviewer_id?: string                  // ID of assigned reviewer
  reviewer_name?: string                // Display name (populated from user/team)

  // Approval info (T-CON-003)
  approved_by?: string                  // User ID who approved
  approved_at?: string                  // ISO timestamp of approval
  approval_comment?: string             // Optional approval comment

  // Rejection info (T-CON-003)
  review_feedback?: string              // Feedback when rejected
  rejected_by?: string                  // User ID who rejected
  rejected_at?: string                  // ISO timestamp of rejection

  // Submission info (T-CON-003)
  submitted_by?: string                 // User ID who submitted for review
  submitted_at?: string                 // ISO timestamp of submission

  // Deprecation info (T-CON-003)
  deprecation_reason?: string           // Reason for deprecation
  replacement_contract_id?: string      // ID of replacement contract
  deprecated_by?: string                // User ID who deprecated
  deprecated_at?: string                // ISO timestamp of deprecation

  // Ownership (T-CON-004)
  owner_team?: string                   // Team that owns the contract
  created_by?: string                   // User ID who created
  updated_by?: string                   // User ID who last updated
}
```

### Sample Extended Contract Response

**GET /api/v1/contracts/customer-analytics-v1**

```json
{
  "id": "customer-analytics-v1",
  "name": "Customer Analytics Contract",
  "version": "1.2.0",
  "status": "active",
  "description": "Contract for customer analytics data",
  "domain": "analytics",

  "schema": [
    {
      "name": "customers",
      "physicalName": "dim_customers",
      "description": "Customer dimension table",
      "properties": [
        {
          "name": "customer_id",
          "logicalType": "string",
          "physicalType": "VARCHAR(50)",
          "required": true,
          "primaryKey": true,
          "description": "Unique customer identifier"
        },
        {
          "name": "email",
          "logicalType": "string",
          "required": true,
          "piiClassification": "direct-identifier",
          "description": "Customer email address"
        }
      ]
    }
  ],

  "qualityRules": [
    {
      "id": "qr-001",
      "name": "Email completeness",
      "type": "completeness",
      "table": "customers",
      "field": "email",
      "threshold": 99.5,
      "operator": ">=",
      "enabled": true
    }
  ],

  "reviewer_type": "user",
  "reviewer_id": "user-002",
  "reviewer_name": "Jane Doe",

  "approved_by": "user-002",
  "approved_at": "2026-01-15T14:00:00Z",
  "approval_comment": "Schema and quality rules look good.",

  "submitted_by": "user-001",
  "submitted_at": "2026-01-14T10:30:00Z",

  "owner_team": "team-001",
  "created_by": "user-001",
  "updated_by": "user-001",

  "created_at": "2026-01-10T09:00:00Z",
  "updated_at": "2026-01-15T14:00:00Z"
}
```

### PUT Request Body Extension

When creating or updating a contract, the frontend sends:

```json
{
  "name": "Customer Analytics Contract",
  "version": "1.0.0",
  "status": "draft",
  "description": "Contract for customer analytics data",
  "domain": "analytics",
  "schema": [...],

  "reviewer_type": "user",
  "reviewer_id": "user-002"
}
```

The API should:
1. Accept `reviewer_type` and `reviewer_id` on POST/PUT
2. Populate `reviewer_name` automatically from the user/team name
3. Return the full extended contract in the response

### Frontend Implementation Using These Fields

**src/app/studio/contracts/[contractId]/page.tsx:**
- Displays reviewer info in Ownership & Governance card
- Shows "Approved by {approved_by} on {approved_at}" for active contracts
- Shows review_feedback if contract was rejected
- Shows deprecation_reason if contract is deprecated

**src/components/contracts/wizard/Step1BasicInfo.tsx:**
- Sends reviewer_type and reviewer_id when creating contract

**src/app/studio/contracts/[contractId]/edit/page.tsx:**
- Preserves reviewer fields when editing
- Updates reviewer assignment

### Deadline
High priority - needed for all T-CON-002/003/004 features
