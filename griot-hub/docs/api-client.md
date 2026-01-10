# API Client

The API client (`lib/api.ts`) provides typed methods for all Registry API endpoints.

---

## Overview

```typescript
import api from '@/lib/api';

// Fetch contracts
const contracts = await api.getContracts();

// Get a specific contract
const contract = await api.getContract('my-contract-id');

// Create a new contract
const newContract = await api.createContract({
  id: 'new-contract',
  name: 'New Contract',
  fields: [/* ... */]
});
```

---

## Configuration

The API client uses the `NEXT_PUBLIC_REGISTRY_API_URL` environment variable:

```env
NEXT_PUBLIC_REGISTRY_API_URL=http://localhost:8000/api/v1
```

### Setting API Key

For authenticated requests:

```typescript
import api from '@/lib/api';

// Set API key for authenticated requests
api.setApiKey('your-api-key');
```

---

## API Methods

### Health

```typescript
// Check registry health
const health = await api.health();
// Returns: { status: 'healthy', version: '1.0.0', timestamp: '...' }
```

### Contracts

#### List Contracts

```typescript
// Get all contracts
const result = await api.getContracts();
// Returns: { items: Contract[], total: number, limit: number, offset: number }

// With filters
const result = await api.getContracts({
  status: 'active',
  owner: 'data-team',
  limit: 20,
  offset: 0
});
```

#### Get Contract

```typescript
// Get latest version
const contract = await api.getContract('contract-id');

// Get specific version
const contract = await api.getContract('contract-id', '1.2.0');
```

#### Create Contract

```typescript
const contract = await api.createContract({
  id: 'user-events',
  name: 'User Events Contract',
  description: 'Defines the schema for user event data',
  owner: 'analytics-team',
  fields: [
    {
      name: 'user_id',
      type: 'string',
      description: 'Unique user identifier',
      nullable: false,
      constraints: {
        format: 'uuid'
      }
    },
    {
      name: 'event_type',
      type: 'string',
      description: 'Type of event',
      constraints: {
        enum: ['click', 'view', 'purchase']
      }
    },
    {
      name: 'timestamp',
      type: 'datetime',
      description: 'When the event occurred'
    }
  ]
});
```

#### Update Contract

```typescript
const updated = await api.updateContract('contract-id', {
  name: 'Updated Name',
  description: 'Updated description',
  fields: [/* updated fields */],
  change_type: 'minor',  // 'patch' | 'minor' | 'major'
  change_notes: 'Added new field for tracking'
});
```

#### Deprecate Contract

```typescript
await api.deprecateContract('contract-id');
```

### Versions

#### List Versions

```typescript
const versions = await api.getVersions('contract-id');
// Returns: { items: VersionSummary[], total: number }

// With pagination
const versions = await api.getVersions('contract-id', { limit: 10, offset: 0 });
```

#### Get Specific Version

```typescript
const contract = await api.getVersion('contract-id', '1.0.0');
```

#### Diff Versions

```typescript
const diff = await api.diffVersions('contract-id', '1.0.0', '2.0.0');
// Returns: ContractDiff
// {
//   from_version: '1.0.0',
//   to_version: '2.0.0',
//   has_breaking_changes: true,
//   added_fields: ['new_field'],
//   removed_fields: ['old_field'],
//   type_changes: [...],
//   constraint_changes: [...]
// }
```

### Validations

#### Report Validation

```typescript
const record = await api.reportValidation({
  contract_id: 'user-events',
  contract_version: '1.2.0',
  passed: true,
  row_count: 150000,
  error_count: 0,
  duration_ms: 2500,
  environment: 'production',
  pipeline_id: 'daily-etl',
  run_id: 'run-12345'
});
```

#### List Validations

```typescript
// All validations
const validations = await api.getValidations();

// With filters
const validations = await api.getValidations({
  contract_id: 'user-events',
  passed: false,
  from_date: '2024-01-01',
  to_date: '2024-01-31',
  limit: 50
});
```

#### Contract Validations

```typescript
const validations = await api.getContractValidations('contract-id', {
  limit: 20
});
```

### Search

```typescript
const results = await api.search({
  q: 'user',
  limit: 20
});
// Returns: SearchResults
// {
//   query: 'user',
//   items: [
//     { contract_id: '...', contract_name: '...', match_type: 'name', snippet: '...' },
//     { contract_id: '...', field_name: 'user_id', match_type: 'field', snippet: '...' }
//   ],
//   total: 15
// }
```

### Reports

#### Audit Report

```typescript
const audit = await api.getAuditReport({
  contract_ids: ['contract-1', 'contract-2'],  // Optional filter
  include_details: true
});
// Returns: AuditReport
// {
//   generated_at: '...',
//   contract_count: 10,
//   field_count: 150,
//   pii_inventory: [...],
//   pii_by_category: { direct_identifier: 5, quasi_identifier: 12, ... },
//   residency_checks: [...],
//   residency_compliance_rate: 0.95
// }
```

#### Analytics Report

```typescript
const analytics = await api.getAnalyticsReport({
  from_date: '2024-01-01',
  to_date: '2024-01-31',
  include_details: true
});
// Returns: AnalyticsReport
// {
//   generated_at: '...',
//   total_contracts: 25,
//   total_validations: 15000,
//   overall_pass_rate: 0.98,
//   contract_metrics: [...],
//   validations_by_day: [...],
//   top_failing_contracts: [...]
// }
```

#### AI Readiness Report

```typescript
const aiReadiness = await api.getAIReadinessReport({
  include_details: true
});
// Returns: AIReadinessReport
// {
//   generated_at: '...',
//   overall_score: { overall_score: 75, documentation_score: 80, ... },
//   semantic_coverage: { fields_with_description: 120, total_fields: 150, ... },
//   contracts: [...],
//   top_recommendations: [...]
// }
```

#### Combined Readiness Report

```typescript
const readiness = await api.getReadinessReport({
  include_details: true
});
// Returns: ReadinessReport
// {
//   generated_at: '...',
//   audit: AuditReport,
//   analytics: AnalyticsReport,
//   ai_readiness: AIReadinessReport,
//   overall_health_score: 82
// }
```

### Residency

#### Check Residency

```typescript
const status = await api.checkResidency('contract-id', 'eu');
// Returns: ResidencyStatus[]
// [
//   { contract_id: '...', field_name: 'email', current_region: 'us', required_region: 'eu', compliant: false }
// ]
```

#### Get Residency Map

```typescript
const map = await api.getResidencyMap();
// Returns: Record<Region, string[]>
// {
//   us: ['contract-1', 'contract-2'],
//   eu: ['contract-3'],
//   global: ['contract-4']
// }
```

---

## Error Handling

The API client throws `ApiClientError` for failed requests:

```typescript
import { ApiClientError } from '@/lib/api';

try {
  const contract = await api.getContract('non-existent');
} catch (err) {
  if (err instanceof ApiClientError) {
    console.log(err.code);     // 'NOT_FOUND'
    console.log(err.message);  // 'Contract not found'
    console.log(err.status);   // 404
  }
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `NOT_FOUND` | 404 | Resource does not exist |
| `VALIDATION_ERROR` | 422 | Invalid request data |
| `UNAUTHORIZED` | 401 | Missing or invalid API key |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `CONFLICT` | 409 | Resource already exists |
| `INTERNAL_ERROR` | 500 | Server error |

---

## TypeScript Types

All API responses are fully typed. Types are defined in `lib/types.ts`:

```typescript
import type {
  Contract,
  ContractCreate,
  ContractUpdate,
  ContractList,
  ContractStatus,
  FieldDefinition,
  FieldType,
  FieldConstraints,
  ValidationReport,
  ValidationRecord,
  AuditReport,
  AnalyticsReport,
  AIReadinessReport,
  Region,
  PIICategory,
  SensitivityLevel
} from '@/lib/types';
```

See [types.ts](../src/lib/types.ts) for the complete type definitions.

---

## Usage Patterns

### Loading State

```typescript
const [contracts, setContracts] = useState<Contract[]>([]);
const [loading, setLoading] = useState(true);
const [error, setError] = useState<string | null>(null);

useEffect(() => {
  async function fetchData() {
    try {
      setLoading(true);
      const result = await api.getContracts();
      setContracts(result.items);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load');
    } finally {
      setLoading(false);
    }
  }
  fetchData();
}, []);
```

### Pagination

```typescript
const [page, setPage] = useState(0);
const pageSize = 20;

const result = await api.getContracts({
  limit: pageSize,
  offset: page * pageSize
});

const hasMore = result.offset + result.items.length < result.total;
```

### Polling

```typescript
useEffect(() => {
  const interval = setInterval(async () => {
    const validations = await api.getValidations({ limit: 10 });
    setValidations(validations.items);
  }, 30000); // Every 30 seconds

  return () => clearInterval(interval);
}, []);
```

---

## Next Steps

- [Components](./components.md) - Using components with API data
- [Pages](./pages.md) - Page-level data fetching patterns
