# Architecture

This document describes the architectural decisions and patterns used in Griot Hub.

---

## Overview

Griot Hub is built with **Next.js 14** using the **App Router** pattern. It follows a clean separation between:

- **Pages** (`app/`) - Route handlers and page components
- **Components** (`components/`) - Reusable UI components
- **Library** (`lib/`) - API client and utilities

---

## Directory Structure

```
src/
├── app/                          # Next.js App Router
│   ├── layout.tsx                # Root layout (navigation, footer)
│   ├── page.tsx                  # Home dashboard (/)
│   ├── globals.css               # Global Tailwind styles
│   │
│   ├── contracts/
│   │   ├── page.tsx              # Contract browser (/contracts)
│   │   └── [id]/
│   │       └── page.tsx          # Contract detail (/contracts/:id)
│   │
│   ├── studio/
│   │   └── page.tsx              # Contract editor (/studio)
│   │
│   ├── monitor/
│   │   └── page.tsx              # Validation monitor (/monitor)
│   │
│   ├── audit/
│   │   └── page.tsx              # Audit dashboard (/audit)
│   │
│   ├── finops/
│   │   └── page.tsx              # FinOps dashboard (/finops)
│   │
│   ├── ai-readiness/
│   │   └── page.tsx              # AI readiness (/ai-readiness)
│   │
│   ├── residency/
│   │   └── page.tsx              # Residency map (/residency)
│   │
│   └── settings/
│       └── page.tsx              # Settings (/settings)
│
├── components/
│   ├── ContractCard.tsx          # Contract summary card
│   ├── FieldEditor.tsx           # Field definition editor
│   ├── ConstraintEditor.tsx      # Constraint configuration
│   ├── ValidationBadge.tsx       # Pass/fail indicator
│   ├── YamlPreview.tsx           # Syntax-highlighted YAML
│   └── ErrorTrendChart.tsx       # Validation trends chart
│
└── lib/
    ├── api.ts                    # Registry API client
    └── types.ts                  # TypeScript type definitions
```

---

## Next.js App Router

Griot Hub uses the App Router introduced in Next.js 13. Key concepts:

### File-based Routing

Each folder in `app/` represents a route segment:
- `app/page.tsx` → `/`
- `app/contracts/page.tsx` → `/contracts`
- `app/contracts/[id]/page.tsx` → `/contracts/:id`

### Layouts

The root `layout.tsx` provides consistent navigation across all pages:

```tsx
// app/layout.tsx
export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        <header>{/* Navigation */}</header>
        <main>{children}</main>
        <footer>{/* Footer */}</footer>
      </body>
    </html>
  );
}
```

### Client Components

All pages use the `'use client'` directive because they:
- Use React hooks (`useState`, `useEffect`)
- Handle user interactions
- Fetch data dynamically

```tsx
'use client';

import { useState, useEffect } from 'react';
import api from '@/lib/api';

export default function ContractsPage() {
  const [contracts, setContracts] = useState([]);

  useEffect(() => {
    api.getContracts().then(setContracts);
  }, []);

  return <div>{/* ... */}</div>;
}
```

---

## Component Hierarchy

```
RootLayout
├── Header (navigation)
│   ├── Logo
│   ├── NavLinks (Contracts, Studio, Monitor, Reports dropdown)
│   └── SettingsLink
│
├── Page Content
│   ├── Page-specific components
│   └── Shared components
│       ├── ContractCard
│       ├── ValidationBadge
│       ├── FieldEditor
│       └── ...
│
└── Footer
```

---

## Data Flow

### API Client Pattern

All data fetching goes through the centralized API client:

```
Page Component
      │
      ▼
  api.ts (API Client)
      │
      ▼
  Registry API
      │
      ▼
  griot-registry
```

### State Management

Each page manages its own state using React hooks:

```tsx
export default function ContractBrowserPage() {
  // Data state
  const [contracts, setContracts] = useState<Contract[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // UI state
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<ContractStatus | null>(null);

  // Fetch data on mount
  useEffect(() => {
    fetchContracts();
  }, []);

  // Filter logic
  const filteredContracts = contracts.filter(c =>
    c.name.includes(searchQuery) &&
    (!statusFilter || c.status === statusFilter)
  );

  return (/* ... */);
}
```

---

## Styling

### Tailwind CSS

All styling uses Tailwind CSS utility classes:

```tsx
<div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
  <h2 className="text-lg font-semibold text-gray-800 mb-4">
    Contract Details
  </h2>
  <p className="text-gray-500">
    {contract.description}
  </p>
</div>
```

### Custom CSS Classes

Global styles are defined in `globals.css`:

```css
/* Custom card component */
.card {
  @apply bg-white rounded-lg shadow-sm p-6 border border-gray-200;
}

/* Button variants */
.btn {
  @apply px-4 py-2 rounded-md font-medium transition-colors;
}

.btn-primary {
  @apply bg-primary-600 text-white hover:bg-primary-700;
}

.btn-secondary {
  @apply bg-gray-100 text-gray-700 hover:bg-gray-200;
}
```

### Color Scheme

| Color | Usage |
|-------|-------|
| `primary-*` | Brand colors, links, active states |
| `gray-*` | Text, borders, backgrounds |
| `success-*` | Passed validations, compliant status |
| `warning-*` | Warnings, degraded status |
| `error-*` | Failed validations, violations |

---

## Type Safety

### TypeScript Throughout

All code is written in TypeScript with strict mode enabled:

```json
// tsconfig.json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true
  }
}
```

### Shared Types

Types are defined in `lib/types.ts` and match the Registry API schemas:

```typescript
// lib/types.ts
export interface Contract {
  id: string;
  name: string;
  description?: string;
  version: string;
  status: ContractStatus;
  fields: FieldDefinition[];
  // ...
}

export type ContractStatus = 'draft' | 'active' | 'deprecated';
```

### Path Aliases

The `@/` alias points to `src/`:

```typescript
import api from '@/lib/api';
import type { Contract } from '@/lib/types';
import ContractCard from '@/components/ContractCard';
```

---

## Error Handling

### API Errors

The API client provides structured error handling:

```typescript
try {
  const contracts = await api.getContracts();
  setContracts(contracts.items);
} catch (err) {
  if (err instanceof ApiClientError) {
    setError(`API Error: ${err.message} (${err.code})`);
  } else {
    setError('An unexpected error occurred');
  }
}
```

### UI Error States

All pages handle loading and error states:

```tsx
if (loading) {
  return <div className="text-center py-16">Loading...</div>;
}

if (error) {
  return (
    <div className="bg-error-50 border border-error-500 text-error-700 p-4 rounded">
      {error}
    </div>
  );
}

return <div>{/* Normal content */}</div>;
```

---

## Performance Considerations

### Client-Side Data Fetching

Data is fetched client-side to:
- Show immediate UI feedback
- Handle dynamic user interactions
- Support real-time updates

### Future Optimizations

Potential improvements for production:
- **SWR/React Query** - Caching, revalidation, deduplication
- **Server Components** - Where possible for static content
- **API Route Handlers** - For BFF patterns or caching
- **Incremental Static Regeneration** - For semi-static pages

---

## Security

### No Secrets in Client

All environment variables prefixed with `NEXT_PUBLIC_` are exposed to the browser. Never store secrets here.

### API Key Handling

API keys should be:
- Stored server-side when possible
- Set per-session in settings
- Never committed to version control

### XSS Prevention

React handles XSS prevention by default. Avoid:
- `dangerouslySetInnerHTML`
- Unescaped user input

---

## Next Steps

- [API Client](./api-client.md) - Detailed API client documentation
- [Components](./components.md) - Component API reference
- [Deployment](./deployment.md) - Production deployment
