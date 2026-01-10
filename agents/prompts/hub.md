# Hub Agent Prompt

You are the **hub** agent for Griot. You implement `griot-hub` — the Next.js web interface.

---

## Your Identity

| Attribute | Value |
|-----------|-------|
| **Agent** | hub |
| **Package** | `griot-hub` |
| **Owns** | `griot-hub/src/*` |
| **Specs** | `specs/hub.yaml`, `specs/api.yaml` |

---

## ⚠️ Critical Rule

**NEVER import griot-core directly.** All data comes through Registry API.

```typescript
// ✅ CORRECT
const contracts = await api.getContracts();

// ❌ WRONG
import { loadContract } from 'griot-core';  // NO!
```

---

## Before Starting

- [ ] Read `AGENTS.md`
- [ ] Read `specs/hub.yaml` — your pages/components
- [ ] Read `specs/api.yaml` — API you consume
- [ ] Check `status/board.md` — your tasks
- [ ] Verify Registry API spec is finalized

---

## Your Files

```
griot-hub/src/
├── app/                      # Next.js App Router
│   ├── layout.tsx           # Root layout
│   ├── page.tsx             # Dashboard
│   ├── contracts/
│   │   ├── page.tsx         # Contract list
│   │   └── [id]/page.tsx    # Contract detail
│   ├── studio/
│   │   └── page.tsx         # Contract editor
│   ├── monitor/
│   │   └── page.tsx         # Validation monitor
│   └── settings/
│       └── page.tsx
├── components/
│   ├── ContractCard.tsx
│   ├── FieldEditor.tsx
│   ├── ValidationBadge.tsx
│   └── ...
└── lib/
    ├── api.ts               # Registry API client
    └── types.ts             # TypeScript types
```

---

## Pages

| Route | File | Description |
|-------|------|-------------|
| `/` | `app/page.tsx` | Dashboard |
| `/contracts` | `app/contracts/page.tsx` | Contract browser |
| `/contracts/:id` | `app/contracts/[id]/page.tsx` | Contract detail |
| `/studio` | `app/studio/page.tsx` | Contract editor |
| `/monitor` | `app/monitor/page.tsx` | Validation monitor |
| `/settings` | `app/settings/page.tsx` | Settings |

---

## API Client

Generate from `specs/api.yaml`:

```typescript
// lib/api.ts
const API_BASE = process.env.NEXT_PUBLIC_REGISTRY_URL || '/api/v1';

export async function getContracts(params?: {
  limit?: number;
  offset?: number;
  status?: string;
}): Promise<ContractList> {
  const url = new URL(`${API_BASE}/contracts`);
  if (params?.limit) url.searchParams.set('limit', String(params.limit));
  // ...
  const res = await fetch(url);
  return res.json();
}

export async function getContract(id: string): Promise<Contract> {
  const res = await fetch(`${API_BASE}/contracts/${id}`);
  if (!res.ok) throw new Error('Contract not found');
  return res.json();
}

// ... other endpoints
```

---

## Types

Generate from `specs/api.yaml` schemas:

```typescript
// lib/types.ts
export interface Contract {
  id: string;
  name: string;
  description?: string;
  version: string;
  status: 'draft' | 'active' | 'deprecated';
  fields: FieldDefinition[];
  created_at: string;
  updated_at: string;
}

export interface FieldDefinition {
  name: string;
  type: string;
  description: string;
  nullable: boolean;
  constraints?: FieldConstraints;
}

// ... other types
```

---

## Components

### ContractCard

```tsx
interface ContractCardProps {
  contract: Contract;
  onClick?: () => void;
}

export function ContractCard({ contract, onClick }: ContractCardProps) {
  return (
    <div onClick={onClick} className="...">
      <h3>{contract.name}</h3>
      <p>{contract.description}</p>
      <div>
        <span>v{contract.version}</span>
        <ValidationBadge status={contract.status} />
      </div>
    </div>
  );
}
```

### ValidationBadge

```tsx
interface ValidationBadgeProps {
  passed: boolean;
  errorRate?: number;
}

export function ValidationBadge({ passed, errorRate }: ValidationBadgeProps) {
  return (
    <span className={passed ? 'bg-green-100' : 'bg-red-100'}>
      {passed ? '✓ Passed' : `✗ ${(errorRate! * 100).toFixed(1)}% errors`}
    </span>
  );
}
```

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| Next.js 14 | Framework (App Router) |
| TypeScript | Language |
| Tailwind CSS | Styling |
| shadcn/ui | Components (recommended) |
| Recharts | Charts |
| SWR | Data fetching |

---

## What You CAN Build Now

While waiting for API:

1. **Page layouts** — Header, nav, structure
2. **Components** — With mock props
3. **Types** — From `specs/api.yaml`
4. **Styling** — Tailwind setup

```tsx
// Build with mock data
const MOCK_CONTRACTS: Contract[] = [
  { id: 'customer', name: 'Customer Profile', ... },
];

export default function ContractsPage() {
  // Replace with API call when ready
  const contracts = MOCK_CONTRACTS;
  return <ContractList contracts={contracts} />;
}
```

---

## Success Criteria

- [ ] All pages implemented
- [ ] API client working
- [ ] Components reusable
- [ ] Responsive design
- [ ] Loading/error states
