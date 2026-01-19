# Agent 2: Contracts & Quality

## Mission Statement
Build all functionality related to Data Contracts including the comprehensive 8-step creation wizard following ODCS v3.3, YAML import/validation, quality rule management, and contract detail views. This is the most feature-rich domain of the application.

---

## Critical UX Requirements

| Requirement | Implementation |
|-------------|----------------|
| **Wizard persistence** | Never lose user progress; auto-save drafts |
| **Validation feedback** | Real-time validation as user types |
| **Schema auto-population** | When linking to asset, schema loads instantly |
| **YAML validation** | Immediate syntax and schema feedback |
| **Connection testing** | Clear progress and status indicators |

---

## Pages Owned

```
/app/studio/contracts/
├── page.tsx                    # Contract list
├── [contractId]/
│   ├── page.tsx               # Contract detail
│   └── runs/
│       └── page.tsx           # Run history
└── new/
    ├── page.tsx               # Method selection
    ├── wizard/
    │   └── page.tsx           # 8-step wizard
    └── yaml/
        └── page.tsx           # YAML import/paste
```

---

## Task Specifications

### A2-01: Contract List Page

**Objective**: Display all contracts with comprehensive filtering and status management.

**Layout**:
```
┌─────────────────────────────────────────────────────────────────┐
│ Data Contracts                                 [+ New Contract] │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ [All •152] [Draft •24] [Proposed •8] [Pending •12] [Active •98] [Deprecated •10]│
│                                                                 │
│ 🔍 [Search...]              [Domain ▼] [Owner ▼] [Tags ▼] [Has Issues ▼]│
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ □ │ Contract           │ Asset    │ Domain │ Ver   │ Status │ │
│ │───┼────────────────────┼──────────┼────────┼───────┼────────│ │
│ │   │ Customer Analytics │ Cust 360 │ CRM    │ v2.0  │ Active │ │
│ │   │ Churn Prediction   │ Cust 360 │ ML     │ v1.5  │ Active │ │
│ │   │ New Sales Pipeline │ -        │ Sales  │ v0.1  │Proposed│ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

**Key Features**:

1. **Status Tabs with Visual Distinction**:
```tsx
const statusConfig = {
  all: { label: 'All', color: 'neutral' },
  draft: { label: 'Draft', color: 'neutral', icon: FileEdit },
  proposed: { label: 'Proposed', color: 'orange', icon: Lightbulb },
  pending: { label: 'Pending Review', color: 'yellow', icon: Clock },
  active: { label: 'Active', color: 'green', icon: CheckCircle },
  deprecated: { label: 'Deprecated', color: 'red', icon: Archive },
}
```

2. **Linked Asset Display**:
```tsx
// Show linked asset or "Proposed" indicator
<td>
  {contract.assetId ? (
    <Link 
      href={`/studio/assets/${contract.assetId}`}
      className="text-text-link hover:underline"
    >
      {contract.asset?.name}
    </Link>
  ) : (
    <span className="text-text-tertiary italic">No asset (proposed)</span>
  )}
</td>
```

3. **Issue Indicator**:
```tsx
// Show issue count badge if contract has issues
{contract.issueCount > 0 && (
  <Badge variant="warning" size="sm">
    ⚠ {contract.issueCount} {contract.issueCount === 1 ? 'issue' : 'issues'}
  </Badge>
)}
```

---

### A2-02: Contract Detail Page (Two-Column Layout)

**Objective**: Display comprehensive contract information following the reference design with Blue (definition) and Green (runtime) sections.

**File**: `src/app/studio/contracts/[contractId]/page.tsx`

**Layout**:
```
┌─────────────────────────────────────────────────────────────────┐
│ ← All Contracts                                                 │
│                                                                 │
│ 📄 Customer Analytics Contract                                  │
│ customer_analytics • v2.0.0 • Active                           │
│ 🏷 Analytics • ✉ Domain: CRM • ODCS v3.3.0                     │
│                                                                 │
│ [👁 Watching ▼] [Generate ▼] [Edit] [Run Checks]               │
├───────────────────────────────┬─────────────────────────────────┤
│ LEFT COLUMN (Blue)            │ RIGHT COLUMN (Green)            │
│ Contract Definition           │ Runtime & Governance            │
│                               │                                 │
│ ┌───────────────────────────┐ │ ┌─────────────────────────────┐ │
│ │ SCHEMA DIAGRAM            │ │ │ DATA PRODUCTS               │ │
│ │ [Interactive ERD]         │ │ │ Products using this contract│ │
│ └───────────────────────────┘ │ └─────────────────────────────┘ │
│                               │                                 │
│ ┌───────────────────────────┐ │ ┌─