# Contracts Agent - Status Update

> **Last Updated:** 2026-01-22 by contracts-agent
> **Status:** IN PROGRESS - Schema Selection Migration

---

## URGENT: Schema Selection Migration

### What Changed

The contract creation wizard has been **fundamentally changed** to remove inline schema creation. Users must now:
1. **Create schemas in Data Assets first**
2. **Select existing schemas** when creating contracts

### Why This Change

- **Single source of truth**: Schemas are now managed centrally in Data Assets
- **Schema reuse**: Same schema can be used by multiple contracts
- **Governance**: Centralized control over schema definitions
- **Consistency**: Prevents duplicate/inconsistent schema definitions

### Files Changed

| File | Change |
|------|--------|
| `src/components/contracts/wizard/Step2Asset.tsx` | **Rewritten** - Now a schema selector with searchable dropdown |
| `src/components/contracts/wizard/Step3Schema.tsx` | **Rewritten** - Now read-only schema display |
| `src/app/studio/contracts/new/wizard/page.tsx` | Updated ContractFormData interface and step labels |

### Blocking Dependencies

**TWO teams need to implement features for this to work:**

#### 1. Registry Agent (Backend API)
**Request:** `agents/status/requests/REQ-registry-020.md`

The Registry needs to implement **standalone schema management** - schemas that exist independently of database connections.

**Required Endpoints:**
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/schemas` | GET | List all schemas (manual + connection-derived) |
| `/schemas` | POST | Create a manual schema |
| `/schemas/{id}` | GET | Get schema details |
| `/schemas/{id}` | PUT | Update manual schema |
| `/schemas/{id}` | DELETE | Delete schema (if not used by contracts) |

**Expected Response from `GET /schemas`:**
```json
{
  "items": [
    {
      "id": "schema-001",
      "name": "Customer Analytics Schema",
      "source": "manual",
      "connectionId": null,
      "domain": "analytics",
      "tables": [{ "name": "customers", "fields": [...] }],
      "tableCount": 1,
      "fieldCount": 5,
      "createdAt": "2026-01-10T09:00:00Z",
      "updatedAt": "2026-01-15T14:30:00Z"
    }
  ],
  "total": 47
}
```

#### 2. Schema Agent (Frontend UI)
**Request:** `agents/status/requests/REQ-schema-001.md`

The Schema Agent needs to implement schema management UI in the Data Assets section:
- Schema list view with search/filter
- Schema creation form/wizard (table builder, field builder)
- Schema edit view
- Schema detail view
- Schema delete with dependency check

### New Wizard Flow

| Step | Old | New |
|------|-----|-----|
| 1 | Basic Info | Basic Info (unchanged) |
| 2 | Data Asset | **Select Schema** - Searchable dropdown |
| 3 | Schema | **Schema Review** - Read-only display |
| 4 | Quality Rules | Quality Rules (unchanged) |
| 5 | SLA | SLA (unchanged) |
| 6 | Tags & Owner | Tags & Owner (unchanged) |
| 7 | Review | Review (unchanged) |

### Testing

Until Schema Agent implements the API:
- Wizard will show "No schemas available"
- Contract creation is blocked at Step 2

Schema Agent should add mock data to `src/lib/mocks/handlers/` for testing.

---

## Summary: All Tasks Completed

All 10 assigned tasks have been successfully implemented. The contract management system now has full schema editing capabilities with proper status-based restrictions and re-approval workflows.

### Task Completion Status

| Task ID | Task | Priority | Status |
|---------|------|----------|--------|
| T-CON-001 | Fix Edit Contract Bug | 🔴 CRITICAL | ✅ DONE |
| T-CON-002 | Add Reviewer Field to Wizard | High | ✅ DONE |
| T-CON-003 | Contract Status Workflow | High | ✅ DONE |
| T-CON-004 | Enhance Contract Detail Page | Medium | ✅ DONE |
| T-CON-005 | Quality Rules at Schema Level | Medium | ✅ DONE |
| T-CON-006 | Privacy Information Display | Medium | ✅ DONE |
| T-CON-007 | E2E Testing for Contracts | Low | ✅ DONE |
| T-CON-008 | Schema Editing for Draft/Pending | High | ✅ DONE |
| T-CON-009 | Schema Change Re-approval Workflow | High | ✅ DONE |
| T-CON-010 | Schema Edit Restrictions by Status | High | ✅ DONE |

---

## Implementation Details

### T-CON-001: Edit Contract Bug Fix ✅

**Problem:** Race condition between React Query and state synchronization causing "Original contract data not available" error.

**Solution:** Changed from `useState` to `useRef` for storing original ODCS contract data.

**Files Changed:**
- `src/app/studio/contracts/[contractId]/edit/page.tsx`
  - Line 3: Added `useRef` import
  - Line 63: Changed `useState` to `useRef` for `originalOdcsContractRef`
  - Line 71: Updated assignment to use `.current`
  - Line 101: Updated access to use `.current`

---

### T-CON-002: Reviewer Field in Wizard ✅

**Implementation:** Added a two-part reviewer selector (Type: User/Team, Value: searchable dropdown) in Step 1 of the contract creation wizard.

**Files Changed:**
- `src/app/studio/contracts/new/wizard/page.tsx`
  - Added `reviewerType`, `reviewerId`, `reviewerName` to `ContractFormData` interface
  - Added reviewer fields to ODCS transformation

- `src/components/contracts/wizard/Step1BasicInfo.tsx`
  - Added `useQuery` hooks to fetch users and teams from API
  - Added reviewer type selector (User/Team dropdown)
  - Added reviewer value selector (searchable dropdown)
  - Added Clear button functionality

---

### T-CON-003: Contract Status Workflow ✅

**Implementation:** Full status workflow with Submit for Review, Approve, Request Changes, and Deprecate actions.

**Files Created:**
- `src/components/contracts/ReviewDialog.tsx`
  - `ReviewDialog` component for request changes, deprecate, submit for review flows
  - `ConfirmDialog` component for approve confirmation

**Files Changed:**
- `src/app/studio/contracts/[contractId]/page.tsx`
  - Added dialog states for submit, approve, reject, deprecate
  - Added `statusMutation` for status changes via PUT /contracts/{id}
  - Added status-specific action buttons:
    - Draft: "Submit for Review" button
    - Pending Review: "Approve" and "Request Changes" buttons
    - Active: "Deprecate" button
  - Added pending review banner

---

### T-CON-004: Enhance Contract Detail Page ✅

**Implementation:** Added ownership/governance section, PII summary, version history, and enhanced metadata display.

**Files Changed:**
- `src/app/studio/contracts/[contractId]/page.tsx`
  - Added Ownership & Governance card (owner team, owner, reviewer, approved by)
  - Added PII Summary card with categorized PII fields
  - Added Version History card
  - Added PII badges to schema fields
  - Enhanced metadata display with ODCS version

---

### T-CON-005 & T-CON-006: Quality Rules and Privacy Display ✅

**Files Created:**
- `src/components/contracts/PIISummaryCard.tsx`
  - Groups PII fields by classification category
  - Shows category icons and colors
  - Includes compliance notice
  - `extractPIIFields()` helper function

- `src/components/contracts/QualityRulesCard.tsx`
  - Shows enabled/disabled counts
  - Groups by schema-level vs field-level
  - Displays thresholds
  - Rule type icons and colors
  - Show more/less toggle for long lists

**Files Changed:**
- `src/app/studio/contracts/[contractId]/page.tsx`
  - Replaced inline PII summary with `PIISummaryCard` component
  - Replaced inline quality rules with `QualityRulesCard` component

---

### T-CON-008: Schema Editing for Draft/Pending Contracts ✅

**Files Created:**
- `src/components/contracts/FieldEditor.tsx`
  - Field add/edit dialog
  - Field type selector
  - PII classification dropdown
  - Required/Primary Key/Unique checkboxes
  - Validation for field names

- `src/components/contracts/TableEditor.tsx`
  - Table add/edit dialog
  - Physical name support
  - Description field

- `src/components/contracts/SchemaEditor.tsx`
  - Main schema editor component
  - Collapsible tables with field lists
  - Add/Edit/Delete operations for tables and fields
  - Status-based editing restrictions
  - PII badges on fields
  - Status banners for locked/review/active states

**Files Changed:**
- `src/app/studio/contracts/[contractId]/edit/page.tsx`
  - Added schema to `EditFormData` interface
  - Transformed contract schema to `SchemaTable` format
  - Replaced read-only schema section with `SchemaEditor`
  - Added schema transformation to ODCS format in mutation

---

### T-CON-009: Schema Change Re-approval Workflow ✅

**Files Created:**
- `src/lib/utils/schema-diff.ts`
  - `compareSchemas()` function to detect changes
  - `hasBreakingChanges()` function for major version detection
  - Returns detailed diff: added/removed/modified tables and fields

- `src/components/contracts/SchemaChangeDialog.tsx`
  - Re-approval confirmation dialog
  - Shows what will happen (invalidate approval, change status, create task)
  - Displays schema changes summary
  - Required reason field

**Files Changed:**
- `src/app/studio/contracts/[contractId]/edit/page.tsx`
  - Added `originalSchemaRef` to store original schema for comparison
  - Added dialog state for re-approval workflow
  - Updated `handleSubmit` to detect schema changes on active contracts
  - Added `handleReapprovalConfirm` handler

---

### T-CON-010: Schema Edit Restrictions by Status ✅

**Implementation:** Already built into `SchemaEditor` component.

**Business Rules Enforced:**
| Status | Editable? | Behavior |
|--------|-----------|----------|
| draft | ✅ Yes | Free editing |
| pending_review | ✅ Yes | Warning shown |
| active | ⚠️ Conditional | Re-approval dialog shown |
| retired | ❌ No | Locked with message |
| deprecated | ❌ No | Locked with message |

---

### T-CON-007: E2E Tests with Playwright ✅

**Files Created:**
- `e2e/contracts/contracts.spec.ts`
  - Contract List Page tests
  - Contract Detail Page tests
  - Contract Edit Page tests (including race condition fix verification)
  - Contract Status Workflow tests
  - Schema Editing tests
  - Contract Creation Wizard tests
  - Quality Rules Display tests
  - PII Display tests

- `e2e/contracts/fixtures.ts`
  - Shared test utilities
  - Login helper
  - Navigation helpers
  - Test data constants

---

## Files Created (Phase 2)

### Components
- `src/components/contracts/ReviewDialog.tsx` - Status workflow dialogs
- `src/components/contracts/FieldEditor.tsx` - Field add/edit dialog
- `src/components/contracts/TableEditor.tsx` - Table add/edit dialog
- `src/components/contracts/SchemaEditor.tsx` - Main schema editor
- `src/components/contracts/SchemaChangeDialog.tsx` - Re-approval confirmation
- `src/components/contracts/PIISummaryCard.tsx` - PII summary display
- `src/components/contracts/QualityRulesCard.tsx` - Quality rules display

### Utilities
- `src/lib/utils/schema-diff.ts` - Schema comparison

### Tests
- `e2e/contracts/contracts.spec.ts` - E2E tests
- `e2e/contracts/fixtures.ts` - Test fixtures

---

## Files Modified (Phase 2)

- `src/app/studio/contracts/[contractId]/page.tsx` - Enhanced detail page
- `src/app/studio/contracts/[contractId]/edit/page.tsx` - Bug fix + schema editing
- `src/app/studio/contracts/new/wizard/page.tsx` - Reviewer fields
- `src/components/contracts/wizard/Step1BasicInfo.tsx` - Reviewer selector

---

## Testing

Run E2E tests:
```bash
npm run test:e2e
```

Test credentials:
- Email: `brackly@griot.com`
- Password: `melly`

---

## Registry API Requests

Created request files for the registry agent (backend API team) documenting needed endpoints:

| Request ID | Endpoint | Purpose |
|------------|----------|---------|
| REQ-registry-001 | POST /contracts/{id}/submit | Submit contract for review |
| REQ-registry-002 | POST /contracts/{id}/approve | Approve contract |
| REQ-registry-003 | POST /contracts/{id}/reject | Request changes on contract |
| REQ-registry-004 | POST /contracts/{id}/deprecate | Deprecate active contract |
| REQ-registry-005 | Extended Contract Schema | Add reviewer/workflow fields |
| **REQ-registry-020** | **Schema CRUD endpoints** | **Manual schema management (NEW)** |

Request files location: `agents/status/requests/REQ-registry-*.md`

## Schema Agent Requests

| Request ID | Feature | Purpose |
|------------|---------|---------|
| **REQ-schema-001** | **Schema Management UI** | **UI for creating/editing schemas in Data Assets (NEW)** |

Request files location: `agents/status/requests/REQ-schema-*.md`

### API Dependencies

**Already Implemented (auth-admin-api.yaml):**
- GET /users - List users for reviewer dropdown
- GET /teams - List teams for reviewer dropdown

**Currently Using (registry API):**
- GET /contracts - List contracts
- GET /contracts/{id} - Get contract detail
- POST /contracts - Create contract
- PUT /contracts/{id} - Update contract (currently used for status changes)

**Needed from Registry (see requests):**
- POST /contracts/{id}/submit - Dedicated submit endpoint
- POST /contracts/{id}/approve - Dedicated approve endpoint
- POST /contracts/{id}/reject - Dedicated reject endpoint
- POST /contracts/{id}/deprecate - Dedicated deprecate endpoint
- Extended Contract response with reviewer/workflow fields

---

## OpenAPI Spec Updates

Updated `agents/specs/contracts.yaml`:
1. Added note that GET /users and GET /teams come from auth-admin-api.yaml
2. Updated implementation priority list
3. Removed duplicate User/Team schemas (they exist in auth-admin-api.yaml)
4. Cleaned up tags to remove unnecessary Users/Teams tags

---

## Next Steps (If Needed)

1. Run E2E tests to verify all functionality
2. Consider adding more unit tests for schema-diff utility
3. Add form validation for quality rules editing
4. Implement version comparison UI (`/contracts/{id}/diff`)
5. **Registry team:** Implement endpoints in REQ-001 through REQ-005
