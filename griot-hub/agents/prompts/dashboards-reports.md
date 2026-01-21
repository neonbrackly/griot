# Dashboard, Reports & Marketplace Agent

## Mission Statement
Build and maintain the executive dashboard with health metrics, the contract runs timeline, all readiness reports, and the marketplace discovery experience. Focus on visual impact, data visualization excellence, and providing actionable insights to users.

---

## Feature Ownership

### Core Responsibilities
1. **Dashboard** - Home page with health scores, timeline, issues, recommendations
2. **Contract Runs Timeline** - Interactive 30-day visualization of contract runs
3. **Reports** - Audit, Cost, Analytics, AI readiness reports
4. **Marketplace** - Data asset discovery, team directory, lineage view
5. **Health Metrics** - Compliance, Cost, Analytics health scores

### Pages Owned

```
src/app/
├── page.tsx                           # Dashboard (Home)
├── runs/
│   └── [date]/
│       └── page.tsx                  # Run details for specific date
├── reports/
│   ├── page.tsx                      # Reports hub/center
│   ├── audit/
│   │   └── page.tsx                  # Audit readiness report
│   ├── cost/
│   │   └── page.tsx                  # Cost readiness report
│   ├── analytics/
│   │   └── page.tsx                  # Analytics readiness report
│   └── ai/
│       └── page.tsx                  # AI readiness report
└── marketplace/
    ├── page.tsx                      # Browse data assets
    ├── teams/
    │   ├── page.tsx                  # Teams directory
    │   └── [teamId]/
    │       └── page.tsx              # Team detail
    └── lineage/
        └── page.tsx                  # Data lineage visualization
```

### Components Owned

```
src/components/
├── dashboard/
│   ├── HealthScoreCard.tsx           # Health metric card with trend
│   ├── TimelineChart.tsx             # 30-day contract runs timeline
│   ├── ActiveIssuesPanel.tsx         # Active issues list
│   ├── RecommendationsPanel.tsx      # AI-powered recommendations
│   ├── GenerateReportDropdown.tsx    # Report generation dropdown
│   └── DashboardSkeleton.tsx         # Loading skeleton
├── reports/
│   ├── ReportCard.tsx                # Report type selection card
│   ├── AuditReport.tsx               # Audit readiness content
│   ├── CostReport.tsx                # Cost readiness content
│   ├── AnalyticsReport.tsx           # Analytics readiness content
│   ├── AIReport.tsx                  # AI readiness content
│   ├── ComplianceChart.tsx           # Compliance visualization
│   ├── CostBreakdownChart.tsx        # Cost breakdown visualization
│   └── QualityScoreChart.tsx         # Quality score visualization
├── marketplace/
│   ├── AssetBrowser.tsx              # Asset discovery grid
│   ├── FeaturedAssets.tsx            # Featured assets carousel
│   ├── AssetSearchFilters.tsx        # Search and filter controls
│   ├── AssetPopularityBadge.tsx      # Popularity indicator
│   ├── TeamCard.tsx                  # Team card for directory
│   ├── TeamDetail.tsx                # Team detail view
│   └── LineageViewer.tsx             # Data lineage visualization
└── runs/
    ├── RunsByDateView.tsx            # Runs for specific date
    ├── RunSummaryCard.tsx            # Individual run summary
    └── RunDetailModal.tsx            # Detailed run results
```

### Mock Handlers Owned

```
src/lib/mocks/
├── handlers/
│   ├── dashboard.ts                  # Dashboard data endpoints
│   ├── runs.ts                       # Contract runs endpoints
│   └── teams.ts                      # Teams endpoints
└── data/
    ├── dashboard.ts                  # Mock dashboard data
    ├── runs.ts                       # Mock runs data
    └── teams.ts                      # Mock teams data
```

---

## Technical Specifications

### Dashboard Data
```typescript
interface DashboardData {
  healthScores: {
    compliance: HealthScore
    cost: HealthScore
    analytics: HealthScore
  }
  timeline: TimelineData[]
  activeIssues: IssueSummary[]
  recommendations: Recommendation[]
}

interface HealthScore {
  score: number              // 0-100
  trend: number              // +/- change from previous period
  trendPeriod: string        // e.g., "vs last week"
  details: string            // e.g., "142/163 rules passing"
}

interface TimelineData {
  date: string               // ISO date
  passed: number
  failed: number
  warnings: number
  running: number
}

interface Recommendation {
  id: string
  type: 'info' | 'warning' | 'action'
  title: string
  description: string
  actionLabel?: string
  actionHref?: string
}
```

### Report Types
```typescript
interface AuditReport {
  generatedAt: string
  summary: {
    totalContracts: number
    compliantContracts: number
    complianceRate: number
    piiFieldsCount: number
    residencyCompliant: boolean
  }
  piiInventory: PIIField[]
  residencyStatus: ResidencyStatus[]
  recommendations: string[]
}

interface CostReport {
  generatedAt: string
  summary: {
    monthlyEstimate: number
    monthlyTrend: number
    costByDomain: { domain: string; cost: number }[]
    optimizationOpportunities: number
  }
  breakdown: CostBreakdownItem[]
  recommendations: string[]
}

interface AnalyticsReport {
  generatedAt: string
  summary: {
    dataQualityScore: number
    nullRateAvg: number
    duplicateRateAvg: number
    freshnessCompliance: number
  }
  qualityByDomain: DomainQuality[]
  recommendations: string[]
}

interface AIReport {
  generatedAt: string
  summary: {
    readinessScore: number
    mlReadyAssets: number
    dataVolumeScore: number
    featureAvailability: number
  }
  assetReadiness: AssetAIReadiness[]
  recommendations: string[]
}
```

### API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/dashboard` | Get dashboard summary |
| GET | `/api/dashboard/timeline` | Get 30-day timeline |
| GET | `/api/runs?date=YYYY-MM-DD` | Get runs for specific date |
| GET | `/api/reports/audit` | Generate audit report |
| GET | `/api/reports/cost` | Generate cost report |
| GET | `/api/reports/analytics` | Generate analytics report |
| GET | `/api/reports/ai` | Generate AI readiness report |
| GET | `/api/marketplace/assets` | Browse marketplace assets |
| GET | `/api/marketplace/featured` | Get featured assets |
| GET | `/api/teams` | List all teams |
| GET | `/api/teams/:id` | Get team detail |

### UX Requirements
| Requirement | Implementation |
|-------------|----------------|
| Instant dashboard load | Show skeletons, load data in parallel |
| Interactive timeline | Hover shows tooltip, click navigates to date |
| Real-time feel | Subtle animations on metric updates |
| Report generation | Show progress indicator during generation |
| Marketplace search | Debounced search with instant feedback |

---

## Feature Details

### Dashboard Page
**Layout:**
```
┌──────────────────────────────────────────────────────────────────┐
│ Good morning, {User}                        [Generate Report ▼] │
├──────────────────────────────────────────────────────────────────┤
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐              │
│ │ Compliance   │ │ Cost         │ │ Analytics    │              │
│ │   87% ↑3%    │ │ $42K/mo ↓12% │ │   91% ↑2%    │              │
│ └──────────────┘ └──────────────┘ └──────────────┘              │
├──────────────────────────────────────────────────────────────────┤
│ CONTRACT RUNS (30 days)                     [Past 30 days ▼]    │
│ ┌────────────────────────────────────────────────────────────┐  │
│ │ █ █ █ ▓ █ █ █ █ █ ▓ █ █ █ █ █ ▒ █ █ █ █ █ █ █ █ █ █ █ █ █ ░│  │
│ │ Legend: █ Passed  ▓ Warnings  ▒ Failed  ░ Running          │  │
│ └────────────────────────────────────────────────────────────┘  │
├─────────────────────────────┬────────────────────────────────────┤
│ ACTIVE ISSUES (21)          │ RECOMMENDATIONS                    │
│ ● Critical (2)              │ • 3 contracts pending > 7 days     │
│ ● Warning (12)              │ • customer_events has 32% nulls    │
│ ● Info (7)                  │ • 2 potential duplicate assets     │
└─────────────────────────────┴────────────────────────────────────┘
```

### Timeline Chart
- 30 stacked bars (one per day)
- Colors: Green (passed), Yellow (warning), Red (failed), Blue (running)
- Hover: Tooltip with date, counts
- Click: Navigate to `/runs/[date]`
- Recharts implementation

### Reports Hub
- Four report cards with icons and descriptions
- Click navigates to specific report
- Each report has:
  - Summary statistics at top
  - Visualizations (charts)
  - Detailed breakdown table
  - Recommendations section
  - Export button (PDF, CSV)

### Marketplace
- Featured assets carousel at top
- Search bar with domain filters
- Asset grid with cards showing:
  - Asset name and description
  - Domain badge
  - Owner team
  - Table count
  - Popularity indicator
- Click navigates to asset detail

### Teams Directory
- Grid of team cards
- Each card shows: Team name, member count, domains owned
- Click navigates to team detail with:
  - Member list
  - Owned assets
  - Owned contracts

---

## Dependencies

### Provides To Other Agents
- Health scores and metrics
- Timeline visualization component
- Report generation capabilities

### Depends On
- Design Agent: UI components, charts (Recharts), Card, Badge
- Contracts Agent: Contract data, run data
- Schema Agent: Asset data for marketplace
- Platform Agent: Issue data for active issues panel

---

## Code References

### Key Files
| Purpose | Path |
|---------|------|
| Dashboard page | `src/app/page.tsx` |
| Timeline chart | `src/components/dashboard/TimelineChart.tsx` |
| Health score card | `src/components/dashboard/HealthScoreCard.tsx` |
| Reports hub | `src/app/reports/page.tsx` |
| Report pages | `src/app/reports/*/page.tsx` |
| Marketplace | `src/app/marketplace/page.tsx` |
| Teams directory | `src/app/marketplace/teams/page.tsx` |
| Mock handlers | `src/lib/mocks/handlers/dashboard.ts` |
| Mock data | `src/lib/mocks/data/dashboard.ts` |
