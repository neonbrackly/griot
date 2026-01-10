# Pages Reference

Documentation for all pages in Griot Hub.

---

## Route Structure

| Route | Page | Description |
|-------|------|-------------|
| `/` | Home | Dashboard with overview metrics |
| `/contracts` | Contract Browser | List and search contracts |
| `/contracts/:id` | Contract Detail | View contract details |
| `/studio` | Contract Studio | Create/edit contracts |
| `/monitor` | Validation Monitor | View validation results |
| `/audit` | Audit Dashboard | PII and compliance |
| `/finops` | FinOps Dashboard | Usage and analytics |
| `/ai-readiness` | AI Readiness | Semantic coverage scores |
| `/residency` | Residency Map | Geographic compliance |
| `/settings` | Settings | Configuration |

---

## Home Dashboard

**Route:** `/`
**File:** `app/page.tsx`

### Features

- Summary statistics (contract count, validation count)
- Recent contracts list
- Recent validation results
- Quick action buttons
- Registry health status

### API Calls

```typescript
const [contracts] = await api.getContracts({ limit: 5 });
const [validations] = await api.getValidations({ limit: 10 });
const health = await api.health();
```

---

## Contract Browser

**Route:** `/contracts`
**File:** `app/contracts/page.tsx`

### Features

- Paginated contract list
- Search by name, description, field
- Filter by status (draft, active, deprecated)
- Sort by name, version, updated date
- Click to view details

### State

```typescript
const [contracts, setContracts] = useState<Contract[]>([]);
const [searchQuery, setSearchQuery] = useState('');
const [statusFilter, setStatusFilter] = useState<ContractStatus | null>(null);
const [sortBy, setSortBy] = useState<'name' | 'updated_at'>('updated_at');
```

### API Calls

```typescript
// List contracts
const result = await api.getContracts({
  status: statusFilter,
  limit: 20,
  offset: page * 20
});

// Search
const results = await api.search({ q: searchQuery });
```

---

## Contract Detail

**Route:** `/contracts/:id`
**File:** `app/contracts/[id]/page.tsx`

### Features

- Contract metadata (name, description, owner, version)
- Full field list with constraints
- Version history with timeline
- Recent validations for this contract
- Version diff comparison
- Download as YAML button
- Edit in Studio link

### Params

```typescript
// Access route parameter
const params = useParams();
const contractId = params.id;
```

### API Calls

```typescript
// Get contract
const contract = await api.getContract(contractId);

// Get versions
const versions = await api.getVersions(contractId);

// Get validations
const validations = await api.getContractValidations(contractId, { limit: 10 });

// Diff versions
const diff = await api.diffVersions(contractId, fromVersion, toVersion);
```

---

## Contract Studio

**Route:** `/studio`
**File:** `app/studio/page.tsx`

### Features

- Create new contract
- Edit existing contract (via query param)
- Visual field editor
- Add/remove/reorder fields
- Constraint configuration
- Live YAML preview
- Save as draft
- Publish (make active)

### Query Params

```typescript
// Edit existing: /studio?contract=contract-id
const searchParams = useSearchParams();
const contractId = searchParams.get('contract');
```

### State

```typescript
const [contract, setContract] = useState<ContractCreate>({
  id: '',
  name: '',
  description: '',
  fields: []
});
const [yamlPreview, setYamlPreview] = useState('');
const [errors, setErrors] = useState<string[]>([]);
```

### API Calls

```typescript
// Load existing
if (contractId) {
  const existing = await api.getContract(contractId);
  setContract(existing);
}

// Save new
const created = await api.createContract(contract);

// Update existing
const updated = await api.updateContract(contractId, {
  ...contract,
  change_type: 'minor',
  change_notes: 'Updated via Studio'
});
```

---

## Validation Monitor

**Route:** `/monitor`
**File:** `app/monitor/page.tsx`

### Features

- Real-time validation feed
- Filter by contract
- Filter by status (passed/failed)
- Filter by date range
- Error rate trends chart
- Drill down to validation details
- Sample errors display

### State

```typescript
const [validations, setValidations] = useState<ValidationRecord[]>([]);
const [contractFilter, setContractFilter] = useState<string | null>(null);
const [passedFilter, setPassedFilter] = useState<boolean | null>(null);
const [dateRange, setDateRange] = useState<{ from: string; to: string }>();
```

### API Calls

```typescript
const result = await api.getValidations({
  contract_id: contractFilter,
  passed: passedFilter,
  from_date: dateRange?.from,
  to_date: dateRange?.to,
  limit: 50
});
```

---

## Audit Dashboard

**Route:** `/audit`
**File:** `app/audit/page.tsx`

### Features

- Summary stats (contracts, fields, PII fields, compliance rate)
- PII by category breakdown (bar chart)
- Sensitivity level distribution (circular badges)
- Legal basis coverage
- Residency compliance checks
- PII inventory table

### API Calls

```typescript
const report = await api.getAuditReport({ include_details: true });
```

### Key Data

```typescript
// PII breakdown
report.pii_by_category  // { direct_identifier: 5, quasi_identifier: 12, ... }
report.pii_by_sensitivity  // { restricted: 2, confidential: 8, ... }

// Compliance
report.residency_compliance_rate  // 0.95
report.residency_checks  // Array of check results

// Inventory
report.pii_inventory  // Array of PIIInventoryItem
```

---

## FinOps Dashboard

**Route:** `/finops`
**File:** `app/finops/page.tsx`

### Features

- Key metrics (contracts, fields, validations, pass rate)
- Date range selector (7d, 30d, 90d)
- Validations over time chart
- Top failing contracts
- Top error types
- Contract metrics table
- Field usage patterns

### State

```typescript
const [dateRange, setDateRange] = useState<'7d' | '30d' | '90d'>('30d');
```

### API Calls

```typescript
const report = await api.getAnalyticsReport({
  from_date: calculateFromDate(dateRange),
  to_date: today,
  include_details: true
});
```

### Key Data

```typescript
report.total_contracts
report.total_validations
report.overall_pass_rate
report.validations_by_day  // Array for chart
report.top_failing_contracts
report.top_error_types
report.contract_metrics  // Per-contract breakdown
```

---

## AI Readiness

**Route:** `/ai-readiness`
**File:** `app/ai-readiness/page.tsx`

### Features

- Overall readiness score (circular progress)
- Component scores (documentation, semantic, quality, consistency)
- Semantic coverage breakdown
- Top recommendations list
- Per-contract readiness scores
- Detailed contract analysis table

### API Calls

```typescript
const report = await api.getAIReadinessReport({ include_details: true });
```

### Key Data

```typescript
// Overall scores
report.overall_score.overall_score  // 0-100
report.overall_score.documentation_score
report.overall_score.semantic_coverage_score
report.overall_score.data_quality_score
report.overall_score.consistency_score

// Coverage
report.semantic_coverage.fields_with_description
report.semantic_coverage.fields_with_unit
report.semantic_coverage.total_fields

// Recommendations
report.top_recommendations  // Array of strings

// Per contract
report.contracts  // Array with individual scores
report.readiness_by_contract  // Sorted by score
```

---

## Residency Map

**Route:** `/residency`
**File:** `app/residency/page.tsx`

### Features

- Global stats (total contracts, violations, compliance rate)
- Interactive region grid (click to select)
- Region details panel
  - Contracts in region
  - Compliance checks
  - Violations list
- All violations table
- Region reference legend

### State

```typescript
const [selectedRegion, setSelectedRegion] = useState<Region | null>(null);
const [residencyMap, setResidencyMap] = useState<Record<Region, string[]>>();
const [auditReport, setAuditReport] = useState<AuditReport>();
```

### API Calls

```typescript
const [mapData, auditData] = await Promise.allSettled([
  api.getResidencyMap(),
  api.getAuditReport({ include_details: true })
]);
```

### Regions

```typescript
const REGIONS: Region[] = ['us', 'eu', 'uk', 'apac', 'latam', 'mea', 'global'];
```

---

## Settings

**Route:** `/settings`
**File:** `app/settings/page.tsx`

### Features

- API key configuration
- Registry URL setting
- Theme toggle (light/dark)
- Connection test button

### State

```typescript
const [apiKey, setApiKey] = useState('');
const [registryUrl, setRegistryUrl] = useState('');
const [theme, setTheme] = useState<'light' | 'dark'>('light');
```

### Storage

Settings are stored in localStorage:

```typescript
// Save
localStorage.setItem('griot-api-key', apiKey);
localStorage.setItem('griot-registry-url', registryUrl);
localStorage.setItem('griot-theme', theme);

// Load
const savedKey = localStorage.getItem('griot-api-key');
```

---

## Navigation

The root layout (`app/layout.tsx`) provides consistent navigation:

### Main Navigation

- **Contracts** - `/contracts`
- **Studio** - `/studio`
- **Monitor** - `/monitor`
- **Reports** (dropdown)
  - Audit Dashboard - `/audit`
  - FinOps Dashboard - `/finops`
  - AI Readiness - `/ai-readiness`
  - Residency Map - `/residency`
- **Settings** - `/settings`

### Breadcrumbs

Contract detail pages show breadcrumbs:

```
Contracts > contract-name
```

---

## Common Patterns

### Page Structure

```tsx
'use client';

import { useState, useEffect } from 'react';
import api from '@/lib/api';

export default function MyPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        const result = await api.getData();
        setData(result);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  if (loading) return <Loading />;
  if (error) return <Error message={error} />;

  return (
    <div className="space-y-6">
      <PageHeader title="Page Title" />
      <Content data={data} />
    </div>
  );
}
```

### Page Header Pattern

```tsx
<div className="flex items-center justify-between">
  <div>
    <h1 className="text-2xl font-bold text-gray-900">Page Title</h1>
    <p className="text-gray-500 mt-1">Page description</p>
  </div>
  <div className="flex gap-2">
    <button className="btn btn-secondary">Secondary Action</button>
    <button className="btn btn-primary">Primary Action</button>
  </div>
</div>
```

---

## Next Steps

- [Components](./components.md) - Reusable components used in pages
- [Deployment](./deployment.md) - Deploying to production
