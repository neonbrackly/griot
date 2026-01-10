# Griot Hub Documentation

> **Version:** 0.1.0
> **Framework:** Next.js 14 (App Router)
> **Language:** TypeScript

Griot Hub is the web interface for the Griot data contract management system. It provides a visual interface for browsing contracts, editing definitions, monitoring validations, and viewing compliance reports.

---

## Table of Contents

1. [Getting Started](./getting-started.md) - Installation and development setup
2. [Architecture](./architecture.md) - Project structure and design patterns
3. [API Client](./api-client.md) - Registry API integration
4. [Components](./components.md) - Reusable component reference
5. [Pages](./pages.md) - Page structure and routing
6. [Deployment](./deployment.md) - Production deployment options

---

## Quick Start

```bash
# Install dependencies
cd griot-hub
npm install

# Set environment variables
cp .env.example .env.local
# Edit .env.local with your Registry API URL

# Start development server
npm run dev

# Open http://localhost:3000
```

---

## Key Features

### Contract Management
- **Contract Browser** - Search, filter, and browse all contracts
- **Contract Studio** - Visual editor for creating and modifying contracts
- **Version History** - View and compare contract versions

### Validation Monitoring
- **Validation Monitor** - Real-time validation results across pipelines
- **Error Trends** - Visualize validation error patterns over time

### Compliance Dashboards
- **Audit Dashboard** - PII inventory, sensitivity levels, legal basis coverage
- **FinOps Dashboard** - Usage metrics, validation trends, error analysis
- **AI Readiness** - Semantic coverage scores and improvement recommendations
- **Residency Map** - Geographic data distribution and compliance status

### Settings
- **API Configuration** - Registry connection settings
- **Theme** - Light/dark mode preferences

---

## Architecture Overview

```
griot-hub/
├── src/
│   ├── app/                 # Next.js App Router pages
│   │   ├── layout.tsx       # Root layout with navigation
│   │   ├── page.tsx         # Home dashboard
│   │   ├── contracts/       # Contract browser & detail
│   │   ├── studio/          # Contract editor
│   │   ├── monitor/         # Validation monitor
│   │   ├── audit/           # Audit dashboard
│   │   ├── finops/          # FinOps dashboard
│   │   ├── ai-readiness/    # AI readiness scores
│   │   ├── residency/       # Residency map
│   │   └── settings/        # Settings page
│   ├── components/          # Reusable React components
│   └── lib/                 # Utilities and API client
│       ├── api.ts           # Registry API client
│       └── types.ts         # TypeScript type definitions
├── public/                  # Static assets
├── docs/                    # Documentation (you are here)
└── package.json             # Dependencies and scripts
```

---

## Technology Stack

| Category | Technology |
|----------|------------|
| Framework | Next.js 14 (App Router) |
| Language | TypeScript |
| Styling | Tailwind CSS |
| Charts | Recharts |
| Data Fetching | SWR / fetch |
| State | React hooks (useState, useEffect) |

---

## Critical Constraint

> **Never import `griot-core` directly in the Hub.**
>
> All data must come through the Registry API. The Hub is a pure frontend that communicates exclusively with `griot-registry`.

```typescript
// CORRECT - Use the API client
import api from '@/lib/api';
const contracts = await api.getContracts();

// WRONG - Never do this
import { Contract } from 'griot-core';  // DO NOT DO THIS
```

---

## Related Documentation

- [griot-core](../../griot-core/docs/) - Core library documentation
- [griot-registry](../../griot-registry/docs/) - Registry API documentation
- [Registry OpenAPI Spec](../../agents/specs/registry.yaml) - Full API specification
