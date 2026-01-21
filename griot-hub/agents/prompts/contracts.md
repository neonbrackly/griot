# Contracts Agent

## Mission Statement
Build and maintain all functionality related to Data Contracts including the creation wizard, YAML import/validation, quality rule management, and contract detail views. This is the most feature-rich domain of the application, enabling users to define and enforce data quality agreements.

---

## Feature Ownership

### Core Responsibilities
1. **Contract Management** - List, detail, create, edit, delete contracts
2. **Contract Creation Wizard** - Multi-step guided contract creation
3. **YAML Editor** - Import, edit, validate contract YAML
4. **Quality Rules** - Define completeness, uniqueness, validity, custom rules
5. **Schema Definition** - Define tables and fields for contracts
6. **Contract Runs** - View historical validation runs
7. **Contract Lifecycle** - Draft, Proposed, Pending Review, Active, Deprecated

### Pages Owned

```
src/app/
└── studio/
    └── contracts/
        ├── page.tsx                    # Contract list with status tabs
        ├── [contractId]/
        │   ├── page.tsx               # Contract detail (two-column)
        │   └── runs/
        │       └── page.tsx           # Run history for contract
        └── new/
            ├── page.tsx               # Method selection (wizard vs YAML)
            ├── wizard/
            │   └── page.tsx           # Multi-step creation wizard
            └── yaml/
                └── page.tsx           # YAML import/paste editor
```

### Components Owned

```
src/components/
└── contracts/
    ├── ContractList.tsx               # Contract list with filters
    ├── ContractCard.tsx               # Contract card for list view
    ├── ContractDetail.tsx             # Contract detail view
    ├── ContractHeader.tsx             # Title, status, actions
    ├── ContractSchema.tsx             # Schema diagram/viewer
    ├── QualityRulesCard.tsx           # Quality rules display
    ├── SLACard.tsx                    # SLA requirements display
    ├── ContractRunsTable.tsx          # Historical runs table
    ├── RunResultCard.tsx              # Individual run result
    ├── YAMLEditor.tsx                 # Monaco-based YAML editor
    ├── YAMLValidator.tsx              # Real-time YAML validation
    └── wizard/
        ├── Step1BasicInfo.tsx         # Name, version, description, domain
        ├── Step2Asset.tsx             # Select or propose data asset
        ├── Step3Schema.tsx            # Define tables and fields
        └── Step4Quality.tsx           # Configure quality rules & SLA
```

### Mock Handlers Owned

```
src/lib/mocks/
├── handlers/
│   ├── contracts.ts                   # Contract CRUD endpoints
│   └── runs.ts                        # Contract run endpoints
└── data/
    ├── contracts.ts                   # Mock contract data
    └── runs.ts                        # Mock run data
```

---

## Technical Specifications

### Contract Entity
```typescript
interface Contract {
  id: string
  name: string
  version: string
  description: string
  status: 'draft' | 'proposed' | 'pending_review' | 'active' | 'deprecated'
  domain: string
  assetId?: string              // Linked data asset (optional for proposed)
  ownerTeamId: string
  tags: string[]
  schema: ContractSchema
  qualityRules: QualityRule[]
  sla: SLA
  issueCount: number
  createdAt: string
  updatedAt: string
  publishedAt?: string
}

interface ContractSchema {
  tables: ContractTable[]
}

interface ContractTable {
  name: string
  description?: string
  fields: ContractField[]
}

interface ContractField {
  name: string
  type: string
  description?: string
  required: boolean
  primaryKey: boolean
  piiCategory?: string
  constraints?: FieldConstraint[]
}

interface QualityRule {
  id: string
  type: 'completeness' | 'uniqueness' | 'validity' | 'custom'
  name: string
  description?: string
  field?: string
  table?: string
  threshold?: number           // e.g., 99.5 for 99.5% completeness
  expression?: string          // For custom rules
  severity: 'critical' | 'warning' | 'info'
}

interface SLA {
  freshnessHours: number       // 1-720
  availabilityPercent: number  // 90-100
}
```

### Contract Run Entity
```typescript
interface ContractRun {
  id: string
  contractId: string
  status: 'running' | 'passed' | 'failed' | 'warning'
  startedAt: string
  completedAt?: string
  summary: {
    totalRules: number
    passed: number
    failed: number
    warnings: number
  }
  ruleResults: RuleResult[]
}

interface RuleResult {
  ruleId: string
  ruleName: string
  status: 'passed' | 'failed' | 'warning'
  actualValue?: number
  expectedValue?: number
  message?: string
}
```

### API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/contracts` | List contracts with filters |
| GET | `/api/contracts/:id` | Get contract detail |
| POST | `/api/contracts` | Create contract |
| PUT | `/api/contracts/:id` | Update contract |
| DELETE | `/api/contracts/:id` | Delete contract |
| POST | `/api/contracts/:id/submit` | Submit for review |
| POST | `/api/contracts/:id/approve` | Approve contract |
| POST | `/api/contracts/:id/reject` | Reject with reason |
| GET | `/api/contracts/:id/runs` | Get run history |
| POST | `/api/contracts/:id/run` | Trigger manual run |
| POST | `/api/contracts/validate-yaml` | Validate YAML syntax |

### Contract Status Workflow
```
┌─────────┐    Submit    ┌──────────────┐   Approve   ┌────────┐
│  Draft  │ ──────────►  │ Pending Review│ ──────────► │ Active │
└─────────┘              └──────────────┘             └────────┘
     │                         │                           │
     │                         │ Reject                    │ Deprecate
     │                         ▼                           ▼
     │                   ┌──────────┐              ┌────────────┐
     └──────────────────►│ Proposed │              │ Deprecated │
                         └──────────┘              └────────────┘
```

### UX Requirements
| Requirement | Implementation |
|-------------|----------------|
| Wizard persistence | Never lose user progress; auto-save drafts |
| Validation feedback | Real-time validation as user types |
| Schema auto-population | When linking to asset, schema loads instantly |
| YAML validation | Immediate syntax and schema feedback |
| Status visualization | Clear visual distinction between statuses |

---

## Feature Details

### Contract List Page
- Status tabs: All, Draft, Proposed, Pending Review, Active, Deprecated
- Counts in each tab
- Search by name, domain
- Filters: Domain, Owner, Has Issues
- Table columns: Contract name, Asset, Domain, Version, Status, Issues
- Issue count badge on contracts with issues

### Contract Detail Page (Two-Column Layout)
**Left Column (Blue - Definition):**
- Schema diagram/ERD
- Tables and fields list
- Quality rules list

**Right Column (Green - Runtime):**
- Data products using this contract
- Recent runs timeline
- Active issues
- Audit trail

**Header Actions:**
- Watch/Unwatch
- Generate Report dropdown
- Edit (if draft)
- Run Checks (if active)
- Submit for Review (if draft)
- Approve/Reject (if pending, with permission)

### Contract Creation Wizard (4 Steps)
1. **Basic Info** - Name, version, description, domain, tags
2. **Data Asset** - Select existing asset OR mark as "proposed" (no asset yet)
3. **Schema** - Define tables and fields (auto-populated if asset selected)
4. **Quality & SLA** - Configure quality rules, set SLA thresholds

### YAML Editor
- Monaco editor with YAML syntax highlighting
- Real-time validation against ODCS schema
- Error markers in gutter
- Import from file
- Paste from clipboard
- Download as YAML

---

## Dependencies

### Provides To Other Agents
- Contract data for dashboard (Dashboards-Reports Agent)
- Contract data for issues (Platform Agent)
- Contract runs for timeline

### Depends On
- Design Agent: UI components, DataTable, Form components, Toast, Monaco setup
- Schema Agent: Asset data for linking, schema viewer patterns
- Design Agent: API client, mock infrastructure

---

## Code References

### Key Files
| Purpose | Path |
|---------|------|
| Contract list page | `src/app/studio/contracts/page.tsx` |
| Contract detail page | `src/app/studio/contracts/[contractId]/page.tsx` |
| Contract wizard | `src/app/studio/contracts/new/wizard/page.tsx` |
| YAML editor page | `src/app/studio/contracts/new/yaml/page.tsx` |
| Wizard steps | `src/components/contracts/wizard/Step*.tsx` |
| Mock handlers | `src/lib/mocks/handlers/contracts.ts` |
| Mock data | `src/lib/mocks/data/contracts.ts` |
| Types | `src/types/index.ts` (Contract, ContractRun) |
| Schemas | `src/types/schemas.ts` (contractSchema) |
