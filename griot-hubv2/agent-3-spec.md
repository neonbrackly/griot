# Agent 3: Dashboard, Reports & Marketplace

## Mission Statement
Build the executive dashboard with health metrics, the Databricks-style run timeline, all readiness reports, and the marketplace discovery experience. Focus on visual impact and data visualization excellence.

---

## Critical UX Requirements

| Requirement | Implementation |
|-------------|----------------|
| **Instant dashboard load** | Show skeletons, load data in parallel |
| **Interactive timeline** | Hover shows tooltip, click navigates |
| **Real-time feel** | Subtle animations on metric updates |
| **Report generation** | Show progress, allow background generation |

---

## Pages Owned

```
/app/
├── page.tsx                    # Dashboard (Home)
├── runs/
│   └── [date]/
│       └── page.tsx           # Run details by date
├── reports/
│   ├── page.tsx               # Reports center
│   ├── audit/page.tsx         # Audit readiness
│   ├── cost/page.tsx          # Cost readiness
│   ├── analytics/page.tsx     # Analytics readiness
│   └── ai/page.tsx            # AI readiness
└── marketplace/
    ├── page.tsx               # Browse assets
    ├── teams/
    │   ├── page.tsx           # Teams directory
    │   └── [teamId]/page.tsx  # Team detail
    └── lineage/page.tsx       # Data lineage
```

---

## Task Specifications

### A3-01: Dashboard Page

**Layout**:
```
┌─────────────────────────────────────────────────────────────────┐
│ Good morning, Jane                           [Generate Report ▼]│
├─────────────────────────────────────────────────────────────────┤
│ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐     │
│ │  🛡️ COMPLIANCE  │ │  💰 COST        │ │  📊 ANALYTICS   │     │
│ │     87%  ↑3%    │ │   $42K/mo ↓12%  │ │     91%  ↑2%    │     │
│ │  142/163 pass   │ │  8 opportunities│ │   4.2% nulls    │     │
│ └─────────────────┘ └─────────────────┘ └─────────────────┘     │
│                                                                 │
│ CONTRACT RUNS                                    [Past 30 days ▼]│
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ █ █ █ ▓ █ █ █ █ █ ▓ █ █ █ █ █ ▒ █ █ █ █ █ █ █ █ █ █ █ █ █ ░ │ │
│ │ Dec 14                                              Jan 13   │ │
│ │ Legend: █ Passed  ▓ Warnings  ▒ Failed  ░ Running           │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ ┌──────────────────────────┐ ┌────────────────────────────────┐ │
│ │ 🚨 ACTIVE ISSUES    (21) │ │ 💡 RECOMMENDATIONS             │ │
│ │                          │ │                                │ │
│ │ ⚠ Critical (2)           │ │ • 3 contracts pending > 7 days │ │
│ │   PII Exposure           │ │ • customer_events: 32% nulls   │ │
│ │   CONTRACT-045           │ │ • 2 twin assets detected       │ │
│ │                          │ │                                │ │
│ │ ⚠ Warning (12)           │ │ [View All →]                   │ │
│ │   Schema Drift...        │ │                                │ │
│ │ [