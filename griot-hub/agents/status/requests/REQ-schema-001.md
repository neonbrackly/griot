# REQ-schema-001: Schema Management UI in Data Assets

## Request: Add Schema Creation and Management UI to Data Assets Section
**From:** contracts
**To:** schema
**Priority:** High
**Blocking:** Yes

---

## Summary

The Contract Creation Wizard has been refactored to **no longer allow inline schema creation**. Instead, users must now:
1. Create schemas in the **Data Assets** section first
2. Select an existing schema when creating a contract

This change requires the **Schema Agent** to implement a schema management UI in the Data Assets section.

**Note:** The backend API for schemas is being requested from the Registry agent in `REQ-registry-020.md`. This request focuses on the **frontend UI**.

---

## Context: Why This Change Was Made

### Previous Behavior
- Contract wizard had Step 2 (Asset selection) and Step 3 (Schema creation)
- Users could create tables and fields directly in the wizard
- This led to:
  - Duplicate schema definitions across contracts
  - No centralized schema management
  - Inconsistent schema structures

### New Behavior
- Contract wizard Step 2 is now "Select Schema" with a searchable dropdown
- Contract wizard Step 3 is now "Schema Review" (read-only display)
- Users MUST create schemas in Data Assets before creating a contract
- This enables:
  - Single source of truth for schemas
  - Schema reuse across multiple contracts
  - Centralized schema governance

---

## UI Requirements

### 1. Schema List View (in Data Assets Section)

Add a "Schemas" tab or section to the Data Assets page:

**Features:**
- List all schemas with columns: Name, Asset/Source, Domain, Tables, Fields, Updated
- Search bar to filter by name, domain, source
- Filter dropdown for domain
- Quick actions: Edit, Duplicate, Delete
- "Create Schema" button

**Visual Reference:**
```
┌─────────────────────────────────────────────────────────────────┐
│ Data Assets                                                      │
├─────────────────────────────────────────────────────────────────┤
│ [Connections] [Schemas] [Datasets]                               │
├─────────────────────────────────────────────────────────────────┤
│ Search: [____________]  Domain: [All ▼]   [+ Create Schema]     │
├─────────────────────────────────────────────────────────────────┤
│ Name                    │ Domain   │ Tables │ Fields │ Updated   │
│─────────────────────────┼──────────┼────────┼────────┼───────────│
│ Customer Analytics      │ analytics│   2    │   15   │ 2 days    │
│ Sales Pipeline          │ sales    │   4    │   28   │ 5 days    │
│ HR Employee Data        │ hr       │   3    │   22   │ 1 week    │
└─────────────────────────────────────────────────────────────────┘
```

---

### 2. Schema Creation Flow

A form/wizard to create a new schema manually:

**Step 1: Basic Info**
- Schema name (required)
- Description (optional)
- Domain selector (dropdown with: analytics, finance, sales, marketing, crm, hr, operations, product, engineering, other)

**Step 2: Table Builder**
- Add/remove tables
- For each table:
  - Table name (logical name)
  - Physical name (optional)
  - Description (optional)

**Step 3: Field Builder (per table)**
For each field:
- Field name
- Logical type dropdown (string, integer, number, boolean, date, datetime, timestamp, array, object, binary, uuid)
- Physical type (optional, text input)
- Description
- Checkboxes: Required, Unique, Primary Key
- PII Classification dropdown (none, email, name, phone, address, ssn, financial, health, other)

**Visual Reference - Field Builder:**
```
┌─────────────────────────────────────────────────────────────────┐
│ Table: customers                                        [Remove] │
├─────────────────────────────────────────────────────────────────┤
│ Physical Name: dim_customers                                     │
│ Description: [Customer dimension table________________]          │
├─────────────────────────────────────────────────────────────────┤
│ Fields:                                              [+ Add Field]│
│ ┌───────────────────────────────────────────────────────────────┐│
│ │ Name        │ Type   │ Description       │ PII   │ PK │ R │ U ││
│ │─────────────┼────────┼───────────────────┼───────┼────┼───┼───││
│ │ customer_id │ string │ Unique identifier │ -     │ ✓  │ ✓ │ ✓ ││
│ │ email       │ string │ Customer email    │ email │    │ ✓ │ ✓ ││
│ │ full_name   │ string │ Customer name     │ name  │    │ ✓ │   ││
│ └───────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

---

### 3. Schema Edit View

Same as creation, but:
- Pre-populated with existing schema data
- Shows "last modified" info
- Has version history (nice to have)
- Shows dependent contracts (which contracts use this schema)

**Warning on Edit:**
If schema is used by contracts, show warning:
> "This schema is used by 3 contracts. Changes may affect: Customer Data Contract, Sales Analytics Contract, Marketing Pipeline Contract"

---

### 4. Schema Detail View

Read-only view of a schema with:
- Full schema metadata
- Table listing with expand/collapse
- Field details per table
- PII summary (count of PII fields by type)
- List of contracts using this schema
- Edit button
- Duplicate button
- Delete button (with confirmation if used by contracts)

---

## API Endpoints to Call

The Registry agent is implementing these endpoints (see REQ-registry-020.md):

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/schemas` | GET | List all schemas |
| `/schemas` | POST | Create new schema |
| `/schemas/{id}` | GET | Get schema details |
| `/schemas/{id}` | PUT | Update schema |
| `/schemas/{id}` | DELETE | Delete schema |

---

## Schema Data Structure

```typescript
interface Schema {
  id: string
  name: string
  description?: string
  source: 'manual' | 'connection'
  connectionId?: string
  domain: string
  tables: SchemaTable[]
  tableCount: number
  fieldCount: number
  createdAt: string
  updatedAt: string
  createdBy: string
}

interface SchemaTable {
  name: string
  physicalName?: string
  description?: string
  fields: SchemaField[]
}

interface SchemaField {
  name: string
  logicalType: string  // string, integer, number, boolean, date, datetime, timestamp, array, object, binary, uuid
  physicalType?: string
  description?: string
  required: boolean
  unique: boolean
  primaryKey: boolean
  piiClassification?: string  // email, name, phone, address, ssn, financial, health, other
}
```

---

## Files Changed in Contracts Agent

For reference, these files were modified to implement the new schema selection flow:

### 1. `src/components/contracts/wizard/Step2Asset.tsx`
- Complete rewrite from asset selection to schema selection
- Implements searchable dropdown calling `GET /schemas`
- When schema selected, populates `formData.tables` for Step 3

### 2. `src/components/contracts/wizard/Step3Schema.tsx`
- Complete rewrite from editable to read-only
- Displays schema from selected Data Asset
- Shows "Edit in Data Assets" link pointing to your schema management UI

### 3. `src/app/studio/contracts/new/wizard/page.tsx`
- Updated `ContractFormData` interface with `selectedSchemaName`, `selectedAssetName`
- Updated step labels

---

## Implementation Checklist

For the Schema Agent:

- [ ] Add "Schemas" tab/section to Data Assets page
- [ ] Implement schema list view with search/filter
- [ ] Implement schema creation form/wizard
- [ ] Implement schema edit view
- [ ] Implement schema detail view
- [ ] Add schema duplicate functionality
- [ ] Add schema delete with dependency check
- [ ] Show which contracts use each schema
- [ ] Add query keys for schemas in `src/lib/api/query-keys.ts`

---

## Query Keys

Please add to `src/lib/api/query-keys.ts`:

```typescript
assets: {
  all: ['assets'] as const,
  schemas: ['assets', 'schemas'] as const,
  schema: (id: string) => ['assets', 'schemas', id] as const,
}
```

---

## Related Files

| File | Agent | Purpose |
|------|-------|---------|
| `src/app/studio/assets/page.tsx` | schema | Main Data Assets page |
| `src/components/contracts/wizard/Step2Asset.tsx` | contracts | Consumes schema list |
| `src/components/contracts/wizard/Step3Schema.tsx` | contracts | Shows read-only schema |
| `src/lib/api/query-keys.ts` | design | Query key definitions |

---

## Deadline

**Priority:** High - This blocks contract creation in the UI until schemas can be created.

The contract wizard shows "No schemas available" until schemas exist in the Data Assets section.

---

## Contact

If you have questions about:
- The expected schema format: See data structures above
- The contract wizard integration: Check `Step2Asset.tsx` and `Step3Schema.tsx`
- The API endpoints: See `REQ-registry-020.md` for Registry API details
