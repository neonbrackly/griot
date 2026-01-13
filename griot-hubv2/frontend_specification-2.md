# 4. Page Specifications

## 4.1 HOME - Overview Dashboard

### Purpose
Executive-level view of organizational data health with actionable insights.

### Layout
```
┌─────────────────────────────────────────────────────────────────┐
│ Header: "Good morning, {userName}"          [Generate Report ▼] │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐         │
│  │ COMPLIANCE    │ │ COST HEALTH   │ │ ANALYTICS     │         │
│  │ HEALTH        │ │               │ │ HEALTH        │         │
│  │   87% ↑3%     │ │  $42K/mo ↓12% │ │   91% ↑2%     │         │
│  │ 142/163 pass  │ │ 8 optimize    │ │ 4.2% nulls    │         │
│  └───────────────┘ └───────────────┘ └───────────────┘         │
│                                                                 │
│  CONTRACT RUNS TIMELINE                           [Past 30 days]│
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ [Interactive daily bar chart - Databricks style]            ││
│  │ Clickable bars showing: passed/warnings/failed per day      ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  ┌──────────────────────────┐ ┌────────────────────────────────┐│
│  │ 🚨 ACTIVE ISSUES    (21) │ │ 💡 RECOMMENDATIONS             ││
│  │                          │ │                                ││
│  │ ⚠ Critical (2)          │ │ • 3 contracts pending auth     ││
│  │   PII Exposure           │ │   > 7 days                     ││
│  │   CONTRACT-045           │ │ • customer_events: 32% nulls  ││
│  │                          │ │ • 2 twin assets detected       ││
│  │ ⚠ Warning (12)          │ │                                ││
│  │   Schema Drift...        │ │                                ││
│  │                          │ │ [View All →]                   ││
│  │ [View All Issues →]      │ │                                ││
│  └──────────────────────────┘ └────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

### Components

#### Health Score Cards (3)
| Property | Details |
|----------|---------|
| Type | Card with circular progress indicator |
| Data | Score percentage, trend arrow, summary text |
| Interaction | Click opens detailed breakdown modal |

#### Contract Runs Timeline
| Property | Details |
|----------|---------|
| Type | Horizontal bar chart (Databricks-inspired) |
| X-Axis | Days (configurable: 7, 14, 30, 90 days) |
| Y-Axis | Stacked bar showing run duration/status |
| Colors | Green (passed), Yellow (warnings), Red (failed), Gray (running) |
| Interaction | Click bar → navigates to `/runs/:date` |
| Tooltip | Shows: date, total contracts, passed/warning/failed counts |

#### Active Issues Panel
| Property | Details |
|----------|---------|
| Type | Scrollable list grouped by severity |
| Grouping | Critical → Warning → Info |
| Each Item | Issue title, contract ID, time ago |
| Interaction | Click → navigates to issue detail |
| Footer | "View All Issues" link |

#### Recommendations Panel
| Property | Details |
|----------|---------|
| Type | AI-generated action items |
| Content | Prioritized list of suggested actions |
| Logic | Based on: stale authorizations, high null rates, duplicate detection, PII exposure |

### Actions
| Action | Behavior |
|--------|----------|
| Generate Report | Opens dropdown: Audit, Cost, Analytics, AI Readiness |
| Click timeline bar | Navigate to run details for that date |
| Click issue | Navigate to issue detail page |

---

## 4.2 HOME - Contract Run Details

### Purpose
View all contract runs for a specific date with drill-down capability.

### URL
`/runs/:date` (e.g., `/runs/2025-01-13`)

### Layout
```
┌─────────────────────────────────────────────────────────────────┐
│ ← Back to Dashboard                                             │
│                                                                 │
│ Contract Runs: January 13, 2025                    [Export CSV] │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ 📊 Summary                                                      │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Total: 47  │  ✓ Passed: 43  │  ⚠ Warning: 3  │  ✗ Failed: 1│ │
│ │ Duration: 2h 34m  │  Started: 02:00 AM  │  Completed: 04:34 │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ 🔍 [Search...]                    [Status ▼] [Domain ▼]         │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Status │ Contract          │ Version │ Duration │ Issues   │ │
│ │────────┼───────────────────┼─────────┼──────────┼──────────│ │
│ │   ✗    │ User Profile Data │ v2.1.0  │ 0m 45s   │ 1        │ │
│ │   ⚠    │ Transaction Events│ v1.5.2  │ 12m 05s  │ 2        │ │
│ │   ✓    │ Sales Metrics     │ v1.2.0  │ 3m 22s   │ 0        │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ Showing 1-10 of 47                    [← Prev] [1] [2] [Next →] │
└─────────────────────────────────────────────────────────────────┘
```

### Data Requirements
| Field | Source |
|-------|--------|
| Run Date | URL parameter |
| Contracts Run | All contract runs for that date |
| Version | Contract version active at run time |
| Duration | End time - start time |
| Issues | Count of issues generated by this run |

---

## 4.3 STUDIO - All Data Contracts (List)

### Purpose
Browse, search, filter, and manage all data contracts.

### URL
`/studio/contracts`

### Layout
```
┌─────────────────────────────────────────────────────────────────┐
│ Data Contracts                               [+ New Contract]   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ [All 152] [Draft 24] [Pending 12] [Active 98] [Deprecated 18]  │
│                                                                 │
│ 🔍 [Search by name, ID, or description...]                      │
│                                                                 │
│ Filters: [Domain ▼] [Owner ▼] [Tags ▼] [Has Issues ▼]          │
│          [Clear All]                                            │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ □ │ Contract            │ Domain   │ Owner  │ Ver   │Status │ │
│ │───┼─────────────────────┼──────────┼────────┼───────┼───────│ │
│ │ □ │ 📄 Customer Churn   │Analytics │ML Team │v3.0.0 │🟢 Active│
│ │   │ Predicts customer...│          │        │       │⚠1 issue│
│ │───┼─────────────────────┼──────────┼────────┼───────┼───────│ │
│ │ □ │ 📄 Transaction Log  │Finance   │Data Eng│v1.5.2 │🟢 Active│
│ │   │ All financial...    │          │        │       │       │ │
│ │───┼─────────────────────┼──────────┼────────┼───────┼───────│ │
│ │ □ │ 📄 User Profiles    │CRM       │Platform│v2.1.0 │🟡Pending│
│ │   │ Core user identity..│          │        │       │Review │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ Showing 1-10 of 152              [← Prev] [1] [2] ... [Next →]  │
│                                                                 │
│ With selected: [Bulk Edit Tags] [Export] [Compare]              │
└─────────────────────────────────────────────────────────────────┘
```

### Table Columns
| Column | Type | Sortable | Description |
|--------|------|----------|-------------|
| Checkbox | Selection | No | For bulk actions |
| Contract | Text + subtext | Yes | Name and truncated description |
| Domain | Badge | Yes | Analytics, Finance, CRM, etc. |
| Owner | Text | Yes | Team name |
| Version | Text | Yes | Semantic version |
| Status | Badge | Yes | Active, Draft, Pending, Deprecated |
| Issues | Badge (optional) | Yes | Issue count if > 0 |

### Actions
| Action | Behavior |
|--------|----------|
| + New Contract | Navigate to `/studio/contracts/new` |
| Click row | Navigate to `/studio/contracts/:id` |
| Status tabs | Filter list by status |
| Bulk Edit Tags | Modal to add/remove tags from selected |
| Export | Download filtered list as CSV |
| Compare | Opens diff view for 2 selected contracts |

---

## 4.4 STUDIO - Contract Detail View (CRITICAL PAGE)

### Purpose
Comprehensive view of a single contract with two-column layout:
- **Left column (Blue)**: Contract definition, schema, fundamentals
- **Right column (Green)**: Daily runs, quality, governance, versions

### URL
`/studio/contracts/:contractId`

### Layout Structure
```
┌─────────────────────────────────────────────────────────────────┐
│ ← All Contracts                                                 │
│                                                                 │
│ 📄 Articles                                                     │
│ snowflake_articles_latest • v1.0.0                             │
│ 🏷 Products • ✉ active • Open Data Contract Standard v3.1.0    │
│                                                                 │
│ [👁 Not watching ▼] [Generate ▼] [Edit] [Request Access]       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ ┌─────────────────────────┬─────────────────────────────────────┐
│ │                         │                                     │
│ │  LEFT COLUMN (BLUE)     │  RIGHT COLUMN (GREEN)               │
│ │  Contract Definition    │  Runs, Quality, Governance          │
│ │                         │                                     │
│ │  • Schema Diagram       │  • Data Products                    │
│ │  • Fundamentals         │  • Data Quality (with date picker)  │
│ │  • Schema Fields        │  • Data Governance Checks           │
│ │  • Price                │  • Version Management               │
│ │  • Team                 │  • Consumers                        │
│ │  • Servers              │  • Git Integration                  │
│ │  • Custom Properties    │  • Audit Trail                      │
│ │  • How to Test          │  • Comments                         │
│ │                         │                                     │
│ └─────────────────────────┴─────────────────────────────────────┘
└─────────────────────────────────────────────────────────────────┘
```

### Left Column Sections

#### Schema Diagram
| Property | Details |
|----------|---------|
| Type | Interactive ERD visualization |
| Features | Zoom, pan, click field to highlight |
| Tools | [Enlarge] [Apply Layout] buttons |
| Right panel | Shows table with fields and types |

#### Fundamentals
| Field | Description |
|-------|-------------|
| Usage | Usage limits (e.g., "Max 10x queries per day") |
| Purpose | What this data is for |
| Limitations | Known constraints |

#### Schema
| Property | Details |
|----------|---------|
| Display | Expandable field cards |
| Each field shows | Name, physical name, type, description, example, constraints |
| Constraints | Tags: primaryKey, required, unique, internal, etc. |

#### Price
| Field | Description |
|-------|-------------|
| Price Amount | Numeric value |
| Currency | USD, EUR, etc. |
| Unit | month, query, etc. |

#### Team
| Field | Description |
|-------|-------------|
| Members | List of username, name, role |

#### Servers
| Field | Description |
|-------|-------------|
| Server | Connection name |
| Type | snowflake, postgres, bigquery, etc. |
| Account | Account identifier |
| Database | Database name |
| Schema | Schema name |

#### Custom Properties
| Property | Details |
|----------|---------|
| Type | Key-value pairs |
| Example | noticePeriod: P3M |

#### How to Test
| Property | Details |
|----------|---------|
| Console | Bash script with env vars and CLI command |
| Python | Python code snippet |
| Copy button | For each code block |

### Right Column Sections

#### Data Products
| Property | Details |
|----------|---------|
| Type | List of products implementing this contract |
| Each item | Icon, name, output port description |

#### Data Quality (CRITICAL)
| Property | Details |
|----------|---------|
| Date Picker | **Select any date to view that day's run** |
| Current selection shows | Run date, duration, status, issue count |
| "View Full Run Details" | Link to detailed run page |

**This section must support historical date selection to show:**
- The contract version that was active on that date
- The run results for that date
- Issues generated on that date

#### Data Governance
| Property | Details |
|----------|---------|
| Type | Checklist of automated policy checks |
| Categories | Ownership, Classification, Mandatory Fields, Naming, PII |
| Each item | Status (✓ or ⚠), issue count if failed, details |
| "Run Checks" button | Manually trigger validation |
| AI disclaimer | "AI can make mistakes. Check important results." |

#### Version Management
| Property | Details |
|----------|---------|
| Current version | Display current version number |
| "Create X.0.0" button | Start new major version |
| Version history | Link to version list |

#### Consumers
| Property | Details |
|----------|---------|
| Type | List of teams/products with access |
| Each item | Icon, name, type (Data Product, Team, etc.) |

#### Git Integration
| Property | Details |
|----------|---------|
| Status | Connected or "No integration configured" |
| Action | "Add file to Git" button |

#### Audit Trail
| Property | Details |
|----------|---------|
| Type | Chronological list of changes |
| Each entry | Action, version, time ago, author, "show changes" link |

#### Comments
| Property | Details |
|----------|---------|
| Type | Threaded comments |
| Each comment | Author, time, content, [Reply] [Resolve] actions |
| Resolved state | Grayed out with checkmark |
| Add comment | Text input at bottom |

### Page Actions
| Action | Behavior |
|--------|----------|
| Edit | Navigate to edit page |
| Generate | Dropdown: YAML, JSON, Documentation |
| Request Access | Opens access request modal |
| Watch/Unwatch | Toggle notifications |
| Run Checks | Execute validation against production |

---

## 4.5 STUDIO - Create Contract

### Purpose
Create new contracts via three methods: UI Builder, YAML Import, YAML Paste.

### URL
`/studio/contracts/new`

### Step 1: Method Selection
```
┌─────────────────────────────────────────────────────────────────┐
│ Create New Data Contract                                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ How would you like to create this contract?                     │
│                                                                 │
│ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐     │
│ │     📝         │ │     📁         │ │     📋         │     │
│ │  UI BUILDER     │ │  IMPORT YAML   │ │  PASTE YAML    │     │
│ │                 │ │                 │ │                 │     │
│ │ Step-by-step    │ │ Upload .yaml    │ │ Paste content   │     │
│ │ guided forms    │ │ file            │ │ directly        │     │
│ └─────────────────┘ └─────────────────┘ └─────────────────┘     │
│                                                                 │
│ ─────────────────────── OR ───────────────────────              │
│                                                                 │
│ 🔗 Create from existing Data Asset                              │
│    [Select a Data Asset ▼]                                      │
└─────────────────────────────────────────────────────────────────┘
```

### UI Builder Steps

| Step | Name | Fields |
|------|------|--------|
| 1 | Identity & Fundamentals | Contract ID (auto), Name*, Description*, Domain*, Owner Team*, Tags, Purpose*, Usage, Limitations |
| 2 | Schema Definition | Add tables, Add fields per table, Field properties (name, type, description, example, constraints) |
| 3 | Privacy & Compliance | Per-field: PII type, Classification, Masking rule |
| 4 | SLAs & Quality | Freshness target, Availability %, Quality thresholds |
| 5 | Team & Access | Add team members, Assign roles, Define approval chain |
| 6 | Review & Submit | Full preview, Validation results, Submit action |

### YAML Import
| Property | Details |
|----------|---------|
| File upload | Drag & drop or file picker |
| Validation | Immediate YAML syntax validation |
| Preview | Parsed contract preview |
| Error display | Line-by-line error indicators |

### YAML Paste
| Property | Details |
|----------|---------|
| Editor | Monaco editor with YAML syntax highlighting |
| Validation | Real-time validation as you type |
| Actions | [Validate] [Save Draft] [Submit] |

### Validation Rules
- **Correctness**: All required fields present, valid types
- **Breaking Changes**: If editing existing contract, detect backward-incompatible changes
- **Governance**: Check against organizational policies

---

## 4.6 STUDIO - All Issues

### Purpose
Centralized view of all issues across all contracts with source attribution.

### URL
`/studio/issues`

### Layout
```
┌─────────────────────────────────────────────────────────────────┐
│ All Issues                                         [Export CSV] │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ [All 21] [Critical 2] [Warning 12] [Info 7] [Resolved 45]      │
│                                                                 │
│ 🔍 [Search issues...]                                           │
│                                                                 │
│ Filters: [Category ▼] [Contract ▼] [Assigned ▼] [Date ▼]       │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │                                                             │ │
│ │ 🔴 CRITICAL                                                 │ │
│ │ ───────────────────────────────────────────────────────     │ │
│ │                                                             │ │
│ │ ⚠ PII Exposure Detected                        2 hours ago  │ │
│ │   Category: Personal Identifiable Information               │ │
│ │   Contract: User Profile Data (CONTRACT-045) • v2.1.0       │ │
│ │   Field: ssn_number                                         │ │
│ │   Assigned: Security Team                                   │ │
│ │   [View Contract] [View Issue Details]                      │ │
│ │                                                             │ │
│ │ 🟡 WARNING                                                  │ │
│ │ ───────────────────────────────────────────────────────     │ │
│ │                                                             │ │
│ │ ⚠ Missing Data Classification                  1 day ago    │ │
│ │   Category: Data Classification                             │ │
│ │   Contract: Articles (CONTRACT-001) • v1.0.0                │ │
│ │   [View Contract] [View Issue Details]                      │ │
│ │                                                             │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ Showing 1-10 of 21                         [← Prev] [Next →]    │
└─────────────────────────────────────────────────────────────────┘
```

### Issue Categories
| Category | Severity Options | Description |
|----------|------------------|-------------|
| PII Detection | Critical, Warning | Unmasked personal data |
| Schema Drift | Critical, Warning | Source schema doesn't match contract |
| Data Classification | Warning, Info | Missing or incorrect classification |
| Mandatory Fields | Warning | Required metadata missing |
| Naming Conventions | Warning, Info | Schema naming violations |
| SLA Breach | Critical, Warning | Freshness or availability failures |
| Ownership | Warning | Missing or invalid owner |

### Issue Properties
| Property | Description |
|----------|-------------|
| ID | Unique identifier |
| Title | Brief description |
| Category | Classification type |
| Severity | Critical, Warning, Info |
| Contract | Source contract (with link) |
| Version | Contract version when detected |
| Field | Specific field if applicable |
| Detected | Timestamp |
| Assigned To | Team responsible |
| Status | Open, In Progress, Resolved |

---

## 4.7 STUDIO - My Tasks

### Purpose
Personal task queue for the logged-in user.

### URL
`/studio/tasks`

### Tabs
| Tab | Content |
|-----|---------|
| Pending Authorization | Contracts awaiting user's approval |
| Comments to Review | Unresolved comments on user's contracts |
| My Drafts | User's unpublished contracts |

### Pending Authorization Table
| Column | Description |
|--------|-------------|
| Contract | Name and ID |
| Requested By | User who submitted |
| Requested | Time since request |
| Priority | High, Medium, Low |
| Action | [Review] button |

---

## 4.8 MARKETPLACE - Browse Data Assets

### Purpose
Discovery interface for finding available data assets.

### URL
`/marketplace`

### Layout
```
┌─────────────────────────────────────────────────────────────────┐
│ Data Marketplace                                                │
│ Discover and request access to data across the organization     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ 🔍 [Search data assets...]                                      │
│                                                                 │
│ Browse by Domain:                                               │
│ [All] [Analytics •23] [Finance •15] [CRM •31] [Marketing •12]  │
│                                                                 │
│ ┌────────────────┐ ┌────────────────┐ ┌────────────────┐        │
│ │ 📊 Customer 360│ │ 💰 Transaction │ │ 📈 Sales       │        │
│ │                │ │    Ledger      │ │    Metrics     │        │
│ │ Domain: CRM    │ │ Domain: Finance│ │ Domain: Sales  │        │
│ │ Owner: CRM Team│ │ Owner: Finance │ │ Owner: BI Team │        │
│ │                │ │                │ │                │        │
│ │ 32 fields      │ │ 18 fields      │ │ 45 fields      │        │
│ │ 12 consumers   │ │ 5 consumers    │ │ 8 consumers    │        │
│ │                │ │                │ │                │        │
│ │ ⭐ AI-Ready    │ │ 🔒 Restricted  │ │ ⭐ AI-Ready    │        │
│ │ 📗 Documented  │ │ 📗 Documented  │ │ 📙 Partial     │        │
│ │                │ │                │ │                │        │
│ │ [View Details] │ │ [Request Access│ │ [View Details] │        │
│ └────────────────┘ └────────────────┘ └────────────────┘        │
└─────────────────────────────────────────────────────────────────┘
```

### Asset Card Properties
| Property | Description |
|----------|-------------|
| Name | Asset name |
| Domain | Category badge |
| Owner | Team name |
| Field count | Number of fields |
| Consumer count | Number of consuming contracts/products |
| Badges | AI-Ready, Documented, Restricted |
| Last updated | Relative time |
| Action | View Details or Request Access |

---

## 4.9 Reports - Audit Readiness Report

### Purpose
Generate audit-ready documentation for compliance.

### URL
`/reports/audit`

### Sections

#### Executive Summary
- Overall compliance score with visual gauge
- Passing vs failing check counts
- Critical issues summary

#### PII Inventory
| Column | Description |
|--------|-------------|
| Contract | Source contract |
| Table | Table name |
| Field | Field name |
| PII Type | Email, SSN, Phone, Name, etc. |
| Masked | Yes/No with warning if No |

#### Data Residency
- World map visualization
- Data centers with asset counts
- Regional breakdown

#### Data Ownership
| Column | Description |
|--------|-------------|
| Team | Team name |
| Assets Owned | Count |
| Contracts | Count |
| Compliance | Percentage |

#### Issues Summary
- Grouped by category
- With remediation status

### Export Options
- PDF (styled report)
- CSV (raw data)
- JSON (machine-readable)

---

## 4.10 STUDIO - Create/Edit Data Asset

### Purpose
Create a new data asset by connecting to a data warehouse/lakehouse and selecting tables.

### URL
`/studio/assets/new` or `/studio/assets/:id/edit`

### Flow Overview
```
1. Select or Create Database Connection
           ↓
2. Browse & Select Tables from Database
           ↓
3. Configure Asset Metadata & SLAs
           ↓
4. Review & Save
```

### Step 1: Database Connection

```
┌─────────────────────────────────────────────────────────────────┐
│ Create Data Asset                                               │
│                                                                 │
│ Step 1 of 4: Connect to Database                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ Select an existing connection or create a new one               │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ EXISTING CONNECTIONS                                        │ │
│ │                                                             │ │
│ │ ○ ❄️ Production Snowflake                                   │ │
│ │     acme-prod.snowflakecomputing.com • Last tested: 2h ago │ │
│ │     Status: ✓ Connected                                     │ │
│ │                                                             │ │
│ │ ○ 🔷 Analytics BigQuery                                     │ │
│ │     project: acme-analytics-prod • Last tested: 1d ago     │ │
│ │     Status: ✓ Connected                                     │ │
│ │                                                             │ │
│ │ ○ 🧱 Databricks Lakehouse                                   │ │
│ │     workspace: acme.cloud.databricks.com                    │ │
│ │     Status: ⚠ Not tested recently                          │ │
│ │                                                             │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ ─────────────────────── OR ───────────────────────              │
│                                                                 │
│ [+ Create New Connection]                                       │
│                                                                 │
│                                        [Cancel]  [Next Step →]  │
└─────────────────────────────────────────────────────────────────┘
```

### Create New Connection Modal

```
┌─────────────────────────────────────────────────────────────────┐
│ Create Database Connection                              [×]     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ Connection Type *                                               │
│ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐   │
│ │   ❄️    │ │   🔷    │ │   🧱    │ │   🐘    │ │   🔶    │   │
│ │Snowflake│ │BigQuery │ │Databricks│ │Postgres │ │ Redshift│   │
│ └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘   │
│                                                                 │
│ ─────────────────────────────────────────────────────────────── │
│                                                                 │
│ Connection Name *        [Production Snowflake              ]   │
│                                                                 │
│ ═══════════════════════════════════════════════════════════════ │
│ SNOWFLAKE CONFIGURATION                                         │
│ ─────────────────────────────────────────────────────────────── │
│                                                                 │
│ Account *                [acme-prod.snowflakecomputing.com  ]   │
│ Warehouse *              [COMPUTE_WH                        ]   │
│ Database                 [ANALYTICS_DB                      ]   │
│ Schema                   [PUBLIC                            ]   │
│                          (Leave empty to browse all schemas)    │
│                                                                 │
│ ═══════════════════════════════════════════════════════════════ │
│ AUTHENTICATION                                                  │
│ ─────────────────────────────────────────────────────────────── │
│                                                                 │
│ Auth Method *            [Username & Password            ▼]     │
│                          ├─ Username & Password            │    │
│                          ├─ Key Pair Authentication        │    │
│                          ├─ OAuth / SSO                    │    │
│                          └─ External Browser              │    │
│                                                                 │
│ Username *               [data_platform_svc             ]       │
│ Password *               [••••••••••••••••              ]       │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ 🔒 Credentials are encrypted and stored securely.          │ │
│ │    Only connection metadata is visible to other users.     │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│                          [Test Connection]  [Cancel]  [Save]    │
└─────────────────────────────────────────────────────────────────┘
```

### Step 2: Select Tables

```
┌─────────────────────────────────────────────────────────────────┐
│ Create Data Asset                                               │
│                                                                 │
│ Step 2 of 4: Select Tables                                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ Connected to: ❄️ Production Snowflake                          │
│                                                                 │
│ Browse database and select one or more tables for this asset    │
│                                                                 │
│ ┌───────────────────────┐ ┌─────────────────────────────────┐   │
│ │ DATABASE BROWSER      │ │ SELECTED TABLES (3)             │   │
│ │                       │ │                                 │   │
│ │ 🔍 [Search tables...] │ │ ┌─────────────────────────────┐ │   │
│ │                       │ │ │ 📋 customers                │ │   │
│ │ 📁 ANALYTICS_DB       │ │ │    ANALYTICS_DB.CUSTOMER.   │ │   │
│ │   📁 CUSTOMER         │ │ │    customers                │ │   │
│ │     ☑ customers       │ │ │    32 columns • 1.2M rows   │ │   │
│ │     ☑ addresses       │ │ │    [Preview] [Remove]       │ │   │
│ │     ☑ preferences     │ │ └─────────────────────────────┘ │   │
│ │     ☐ customer_logs   │ │                                 │   │
│ │   📁 ORDERS           │ │ ┌─────────────────────────────┐ │   │
│ │     ☐ orders          │ │ │ 📋 addresses                │ │   │
│ │     ☐ order_items     │ │ │    ANALYTICS_DB.CUSTOMER.   │ │   │
│ │   📁 PRODUCTS         │ │ │    addresses                │ │   │
│ │     ☐ products        │ │ │    12 columns • 2.4M rows   │ │   │
│ │     ☐ inventory       │ │ │    [Preview] [Remove]       │ │   │
│ │                       │ │ └─────────────────────────────┘ │   │
│ │ 📁 FINANCE_DB         │ │                                 │   │
│ │   📁 TRANSACTIONS     │ │ ┌─────────────────────────────┐ │   │
│ │     ☐ transactions    │ │ │ 📋 preferences              │ │   │
│ │     ☐ payments        │ │ │    ANALYTICS_DB.CUSTOMER.   │ │   │
│ │                       │ │ │    preferences              │ │   │
│ │                       │ │ │    8 columns • 890K rows    │ │   │
│ │                       │ │ │    [Preview] [Remove]       │ │   │
│ │                       │ │ └─────────────────────────────┘ │   │
│ └───────────────────────┘ └─────────────────────────────────┘   │
│                                                                 │
│                                     [← Back]  [Next Step →]     │
└─────────────────────────────────────────────────────────────────┘
```

### Table Preview Modal

```
┌─────────────────────────────────────────────────────────────────┐
│ Table Preview: customers                                [×]     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ Full Path: ANALYTICS_DB.CUSTOMER.customers                      │
│ Rows: ~1,234,567 • Size: ~2.3 GB • Last Updated: 2 hours ago   │
│                                                                 │
│ SCHEMA (32 columns)                                             │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Column Name        │ Type      │ Nullable │ Sample Value    │ │
│ │────────────────────┼───────────┼──────────┼─────────────────│ │
│ │ customer_id        │ VARCHAR   │ NO       │ CUST-12345      │ │
│ │ email              │ VARCHAR   │ NO       │ john@example.com│ │
│ │ first_name         │ VARCHAR   │ YES      │ John            │ │
│ │ last_name          │ VARCHAR   │ YES      │ Doe             │ │
│ │ created_at         │ TIMESTAMP │ NO       │ 2024-01-15 10:30│ │
│ │ ...                │ ...       │ ...      │ ...             │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ SAMPLE DATA (5 rows)                                            │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ customer_id │ email              │ first_name │ last_name   │ │
│ │─────────────┼────────────────────┼────────────┼─────────────│ │
│ │ CUST-12345  │ john@example.com   │ John       │ Doe         │ │
│ │ CUST-12346  │ jane@example.com   │ Jane       │ Smith       │ │
│ │ ...         │ ...                │ ...        │ ...         │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│                                                        [Close]  │
└─────────────────────────────────────────────────────────────────┘
```

### Step 3: Configure Asset

```
┌─────────────────────────────────────────────────────────────────┐
│ Create Data Asset                                               │
│                                                                 │
│ Step 3 of 4: Configure Asset                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ BASIC INFORMATION                                               │
│ ─────────────────                                               │
│                                                                 │
│ Asset Name *             [Customer 360                      ]   │
│                                                                 │
│ Description *            [Comprehensive customer data        ]  │
│                          [including profiles, addresses,     ]  │
│                          [and preferences                    ]  │
│                                                                 │
│ Domain *                 [CRM                             ▼]    │
│                                                                 │
│ Owner Team *             [Customer Data Team              ▼]    │
│                                                                 │
│ Tags                     [customer] [pii] [core] [+ Add]        │
│                                                                 │
│ ═══════════════════════════════════════════════════════════════ │
│                                                                 │
│ SERVICE LEVEL AGREEMENTS (SLAs)                                 │
│ ───────────────────────────────                                 │
│ These SLAs will be inherited by all contracts using this asset  │
│                                                                 │
│ Data Freshness *         [24        ] hours                     │
│                          Data should be updated within this time│
│                                                                 │
│ Availability Target *    [99.5      ] %                         │
│                          Expected uptime percentage             │
│                                                                 │
│ Query Response Time      [5000      ] ms (optional)             │
│                          Target query response time             │
│                                                                 │
│ ═══════════════════════════════════════════════════════════════ │
│                                                                 │
│ FIELD CONFIGURATION                                             │
│ ───────────────────                                             │
│ Add descriptions and classify sensitive fields                  │
│                                                                 │
│ Table: customers (32 fields)                          [Expand ▼]│
│ Table: addresses (12 fields)                          [Expand ▼]│
│ Table: preferences (8 fields)                         [Expand ▼]│
│                                                                 │
│                                     [← Back]  [Next Step →]     │
└─────────────────────────────────────────────────────────────────┘
```

### Step 4: Review & Save

```
┌─────────────────────────────────────────────────────────────────┐
│ Create Data Asset                                               │
│                                                                 │
│ Step 4 of 4: Review & Save                                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ ✓ Validation Passed                                         │ │
│ │   All required fields are complete                          │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ ASSET SUMMARY                                                   │
│ ─────────────                                                   │
│                                                                 │
│ Name:           Customer 360                                    │
│ Domain:         CRM                                             │
│ Owner:          Customer Data Team                              │
│ Connection:     ❄️ Production Snowflake                         │
│                                                                 │
│ Tables (3):                                                     │
│   • customers (32 fields, ~1.2M rows)                          │
│   • addresses (12 fields, ~2.4M rows)                          │
│   • preferences (8 fields, ~890K rows)                         │
│                                                                 │
│ SLAs:                                                           │
│   • Freshness: 24 hours                                        │
│   • Availability: 99.5%                                        │
│   • Response Time: 5000ms                                      │
│                                                                 │
│ Governance:                                                     │
│   • 5 PII fields identified                                    │
│   • 0 fields missing classification                            │
│                                                                 │
│                                                                 │
│                      [← Back]  [Save as Draft]  [Save & Publish]│
└─────────────────────────────────────────────────────────────────┘
```

### Database Connection Types

| Type | Icon | Configuration Fields |
|------|------|---------------------|
| **Snowflake** | ❄️ | Account, Warehouse, Database, Schema, Auth (user/pass, key pair, OAuth) |
| **BigQuery** | 🔷 | Project ID, Dataset, Service Account JSON |
| **Databricks** | 🧱 | Host, HTTP Path, Catalog, Schema, Token |
| **PostgreSQL** | 🐘 | Host, Port, Database, Schema, Username, Password, SSL |
| **Redshift** | 🔶 | Host, Port, Database, Schema, Username, Password |
| **MySQL** | 🐬 | Host, Port, Database, Username, Password |
| **SQL Server** | 🔷 | Host, Port, Database, Schema, Auth (SQL, Windows) |

---

## 4.11 STUDIO - Create Contract (Revised: Must Link to Asset)

### Purpose
Create a new data contract by selecting a registered Data Asset and configuring contract-specific details.

### Key Change
**Users MUST select an existing Data Asset first. The schema is auto-populated from the asset.**

### URL
`/studio/contracts/new`

### Step 1: Select Data Asset (NEW - Required First Step)

```
┌─────────────────────────────────────────────────────────────────┐
│ Create Data Contract                                            │
│                                                                 │
│ Step 1 of 5: Select Data Asset                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ A contract must be linked to a registered Data Asset.           │
│ The schema will be automatically populated from the asset.      │
│                                                                 │
│ 🔍 [Search data assets...]                                      │
│                                                                 │
│ Filter by: [All Domains ▼] [All Teams ▼]                       │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │                                                             │ │
│ │ ○ 📊 Customer 360                                           │ │
│ │     Domain: CRM • Owner: Customer Data Team                 │ │
│ │     3 tables: customers, addresses, preferences             │ │
│ │     52 fields • SLA: 24h freshness                         │ │
│ │     [View Asset Details]                                    │ │
│ │                                                             │ │
│ │ ○ 💰 Transaction Ledger                                     │ │
│ │     Domain: Finance • Owner: Finance Data Team              │ │
│ │     2 tables: transactions, payments                        │ │
│ │     28 fields • SLA: 1h freshness                          │ │
│ │     [View Asset Details]                                    │ │
│ │                                                             │ │
│ │ ○ 📈 Sales Metrics                                          │ │
│ │     Domain: Analytics • Owner: BI Team                      │ │
│ │     4 tables: daily_sales, products, regions, targets      │ │
│ │     67 fields • SLA: 6h freshness                          │ │
│ │     [View Asset Details]                                    │ │
│ │                                                             │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ Don't see the asset you need?  [+ Register New Data Asset]      │
│                                                                 │
│                                         [Cancel]  [Next Step →] │
└─────────────────────────────────────────────────────────────────┘
```

### Step 2: Contract Details

```
┌─────────────────────────────────────────────────────────────────┐
│ Create Data Contract                                            │
│                                                                 │
│ Step 2 of 5: Contract Details                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ Linked Asset: 📊 Customer 360                    [Change Asset] │
│                                                                 │
│ ═══════════════════════════════════════════════════════════════ │
│                                                                 │
│ CONTRACT IDENTITY                                               │
│ ─────────────────                                               │
│                                                                 │
│ Contract ID              [AUTO: CONTRACT-CUST360-001        ]   │
│                                                                 │
│ Contract Name *          [Customer Analytics Contract       ]   │
│                                                                 │
│ Description *            [Provides customer data for the    ]   │
│                          [analytics team's churn prediction ]   │
│                          [models and segmentation           ]   │
│                                                                 │
│ ═══════════════════════════════════════════════════════════════ │
│                                                                 │
│ FUNDAMENTALS                                                    │
│ ────────────                                                    │
│                                                                 │
│ Purpose *                [Customer churn prediction and     ]   │
│                          [segmentation analytics            ]   │
│                                                                 │
│ Usage Limits             [Max 100 queries per hour          ]   │
│                                                                 │
│ Limitations              [Not for real-time use cases       ]   │
│                                                                 │
│ Domain                   [CRM (inherited)               ▼]      │
│                                                                 │
│ Owner Team *             [Analytics Team                ▼]      │
│                                                                 │
│ Tags                     [ml-ready] [analytics] [+ Add]         │
│                                                                 │
│                                      [← Back]  [Next Step →]    │
└─────────────────────────────────────────────────────────────────┘
```

### Step 3: Schema Review & Quality Rules

```
┌─────────────────────────────────────────────────────────────────┐
│ Create Data Contract                                            │
│                                                                 │
│ Step 3 of 5: Schema & Quality Rules                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ Schema auto-populated from: Customer 360                        │
│ Add contract-specific quality rules and constraints             │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ 📋 Table: customers (32 fields)                    [Expand] │ │
│ │    Inherited from asset • Add quality rules per field       │ │
│ ├─────────────────────────────────────────────────────────────┤ │
│ │                                                             │ │
│ │ customer_id    VARCHAR    🔑 Primary Key                    │ │
│ │ Quality Rules: [+ Add Rule]                                 │ │
│ │                                                             │ │
│ │ email          VARCHAR    📧 PII: Email                     │ │
│ │ Quality Rules: ☑ Not Null  ☑ Valid Email Format             │ │
│ │                [+ Add Rule]                                 │ │
│ │                                                             │ │
│ │ first_name     VARCHAR    👤 PII: Name                      │ │
│ │ Quality Rules: [+ Add Rule]                                 │ │
│ │                                                             │ │
│ │ churn_score    FLOAT                                        │ │
│ │ Quality Rules: ☑ Range (0.0 - 1.0)                         │ │
│ │                [+ Add Rule]                                 │ │
│ │                                                             │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ 📋 Table: addresses (12 fields)                   [Expand]  │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ 📋 Table: preferences (8 fields)                  [Expand]  │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│                                      [← Back]  [Next Step →]    │
└─────────────────────────────────────────────────────────────────┘
```

### Step 4: SLAs & Team

```
┌─────────────────────────────────────────────────────────────────┐
│ Create Data Contract                                            │
│                                                                 │
│ Step 4 of 5: SLAs & Team                                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ SERVICE LEVEL AGREEMENTS                                        │
│ ─────────────────────────                                       │
│                                                                 │
│ Inherited from Asset: Customer 360                              │
│ You can make SLAs stricter, but not looser than the asset      │
│                                                                 │
│                          Asset Default    Contract Override     │
│ Data Freshness           24 hours         [12       ] hours     │
│                                           (must be ≤ 24)        │
│                                                                 │
│ Availability             99.5%            [99.5     ] %         │
│                                           (must be ≥ 99.5)      │
│                                                                 │
│ ═══════════════════════════════════════════════════════════════ │
│                                                                 │
│ TEAM & APPROVAL                                                 │
│ ───────────────                                                 │
│                                                                 │
│ Contract Owner *         [jane.doe@company.com          ▼]      │
│                                                                 │
│ Team Members             [+ Add Team Member]                    │
│                          • bob.smith@company.com (Reviewer)     │
│                          • alice.wong@company.com (Consumer)    │
│                                                                 │
│ Approval Chain *         [Asset Owner → Data Governance  ▼]     │
│                                                                 │
│                                      [← Back]  [Next Step →]    │
└─────────────────────────────────────────────────────────────────┘
```

### Step 5: Review & Submit

```
┌─────────────────────────────────────────────────────────────────┐
│ Create Data Contract                                            │
│                                                                 │
│ Step 5 of 5: Review & Submit                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ ✓ Validation Passed                                         │ │
│ │   Contract is ready to submit for review                    │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ CONTRACT SUMMARY                                                │
│ ────────────────                                                │
│                                                                 │
│ Contract:       Customer Analytics Contract                     │
│ Linked Asset:   📊 Customer 360                                 │
│ Domain:         CRM                                             │
│ Owner:          jane.doe@company.com                            │
│ Team:           Analytics Team                                  │
│                                                                 │
│ Schema:                                                         │
│   • 3 tables (inherited from asset)                            │
│   • 52 fields                                                   │
│   • 8 quality rules configured                                 │
│                                                                 │
│ SLAs:                                                           │
│   • Freshness: 12 hours (stricter than asset's 24h)           │
│   • Availability: 99.5%                                        │
│                                                                 │
│ Governance:                                                     │
│   • 5 PII fields (masking inherited from asset)               │
│   • Will be sent to: Asset Owner → Data Governance            │
│                                                                 │
│                                                                 │
│              [← Back]  [Save as Draft]  [Submit for Review]     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4.12 Unsaved Changes Modal (CRITICAL UX)

### Purpose
Prevent users from accidentally losing work when navigating away during contract or asset authoring.

### Trigger Conditions
This modal appears when ALL of these conditions are true:
1. User is on Create/Edit Contract or Create/Edit Asset page
2. User has made changes to the form (form is "dirty")
3. User attempts to navigate away via:
   - Clicking a sidebar/nav link
   - Clicking browser back button
   - Closing the browser tab
   - Clicking [Cancel] button

### Modal Design

```
┌─────────────────────────────────────────────────────────────────┐
│                        Unsaved Changes                     [×]  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                          ⚠️                                     │
│                                                                 │
│     You have unsaved changes that will be lost if you           │
│     leave this page.                                            │
│                                                                 │
│     Would you like to save your progress as a draft?            │
│                                                                 │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 💾 Draft Name                                               ││
│  │ [Customer Analytics Contract - Draft                     ]  ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│                                                                 │
│    [Discard Changes]      [Cancel]      [Save as Draft & Leave] │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Button Actions

| Button | Action | Result |
|--------|--------|--------|
| **Save as Draft & Leave** | Save current form state as draft | Navigate to intended destination; draft appears in "My Tasks > My Drafts" |
| **Discard Changes** | Abandon all unsaved changes | Navigate to intended destination; no draft saved |
| **Cancel** | Close modal | Stay on current page; continue editing |
| **[×] Close** | Close modal | Stay on current page; continue editing |

### Implementation Notes

```typescript
// Hook for detecting unsaved changes
const useUnsavedChanges = (isDirty: boolean) => {
  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (isDirty) {
        e.preventDefault();
        e.returnValue = ''; // Required for Chrome
      }
    };
    
    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, [isDirty]);
};

// Navigation blocking (React Router)
const blocker = useBlocker(
  ({ currentLocation, nextLocation }) =>
    isDirty && currentLocation.pathname !== nextLocation.pathname
);
```

### Draft Auto-Save (Enhancement)
Consider implementing auto-save every 30 seconds when form is dirty:
- Show subtle "Draft saved" toast
- Update `lastDraftSavedAt` timestamp
- Show "Last saved: X minutes ago" in form header

---

## 4.13 ADMIN - User Management

### Purpose
Create, edit, and manage platform users.

### URL
`/admin/users`

### Layout
```
┌─────────────────────────────────────────────────────────────────┐
│ User Management                                [+ Invite User]  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ 🔍 [Search users...]                             [Filters ▼]    │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ User          │ Email              │ Role   │ Team │ Status │ │
│ │───────────────┼────────────────────┼────────┼──────┼────────│ │
│ │ Jane Doe      │ jane@company.com   │ Admin  │ Plat │ Active │ │
│ │ Bob Smith     │ bob@company.com    │ Engineer│ Data │ Active │ │
│ │ Alice Wong    │ alice@company.com  │ Analyst│ BI   │ Pending│ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### User Properties
| Property | Description |
|----------|-------------|
| ID | Unique identifier |
| Name | Display name |
| Email | Login email |
| Role | Admin, Engineer, Analyst, Viewer |
| Team | Primary team assignment |
| Status | Active, Pending, Deactivated |
| Last Login | Timestamp |

### Actions
- Invite User (email invitation flow)
- Edit User (modal form)
- Deactivate User
- Reset Password
- Change Role/Team

---

# 5. Data Models

## 5.1 Entity Relationship Overview

```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│  Data Asset │◄──────│  Contract   │──────►│   Team      │
│             │  1:N  │             │  N:1  │             │
│ - id        │       │ - id        │       │ - id        │
│ - name      │       │ - name      │       │ - name      │
│ - schema    │       │ - version   │       │ - members   │
│ - slas      │       │ - status    │       └─────────────┘
└─────────────┘       │ - assetId   │              │
                      └─────────────┘              │
                            │                      │
                            │ 1:N                  │
                            ▼                      ▼
                      ┌─────────────┐       ┌─────────────┐
                      │ ContractRun │       │    User     │
                      │             │       │             │
                      │ - id        │       │ - id        │
                      │ - contractId│       │ - email     │
                      │ - version   │       │ - role      │
                      │ - runDate   │       │ - teamId    │
                      │ - status    │       └─────────────┘
                      │ - duration  │
                      └─────────────┘
                            │
                            │ 1:N
                            ▼
                      ┌─────────────┐
                      │   Issue     │
                      │             │
                      │ - id        │
                      │ - contractId│
                      │ - runId     │
                      │ - category  │
                      │ - severity  │
                      │ - status    │
                      └─────────────┘
```

## 5.2 Database Connection Entity

```typescript
interface DatabaseConnection {
  id: string;                    // Unique identifier
  name: string;                  // Display name (e.g., "Production Snowflake")
  type: DatabaseType;            // snowflake | bigquery | databricks | postgres | redshift
  status: 'active' | 'inactive' | 'error';
  
  // Connection details (varies by type)
  config: {
    // Snowflake
    account?: string;
    warehouse?: string;
    database?: string;
    schema?: string;
    
    // BigQuery
    projectId?: string;
    dataset?: string;
    
    // Databricks
    host?: string;
    httpPath?: string;
    catalog?: string;
    schema?: string;
    
    // Generic
    host?: string;
    port?: number;
    database?: string;
  };
  
  // Authentication (stored securely, not exposed in API)
  authMethod: 'credentials' | 'oauth' | 'service_account' | 'token';
  
  // Metadata
  createdBy: string;
  createdAt: DateTime;
  lastTestedAt?: DateTime;
  lastTestStatus?: 'success' | 'failed';
}

type DatabaseType = 'snowflake' | 'bigquery' | 'databricks' | 'postgres' | 'redshift' | 'mysql' | 'sqlserver';
```

## 5.3 Data Asset Entity (Multi-Table Support)

```typescript
interface DataAsset {
  id: string;                    // Unique identifier (ASSET-XXX)
  name: string;                  // Display name
  description: string;           // Detailed description
  
  // Database Connection
  connectionId: string;          // Reference to DatabaseConnection
  
  // Multi-table schema (IMPORTANT: Asset can contain multiple tables)
  tables: AssetTable[];          // One or more tables in this asset
  
  // Ownership
  ownerTeamId: string;           // Owning team
  createdBy: string;             // User ID
  
  // Classification
  domain: string;                // Analytics, Finance, CRM, etc.
  tags: string[];                // Searchable tags
  
  // SLAs (inherited by contracts)
  slas: {
    freshnessHours: number;      // Data should be updated within X hours
    availabilityPercent: number; // Target availability (e.g., 99.9)
    responseTimeMs?: number;     // Query response time target
  };
  
  // Metadata
  status: 'draft' | 'active' | 'deprecated';
  createdAt: DateTime;
  updatedAt: DateTime;
  lastSyncedAt?: DateTime;       // Last schema sync from database
}

interface AssetTable {
  id: string;                    // Unique identifier within asset
  name: string;                  // Table name in database
  physicalName: string;          // Full path (e.g., "database.schema.table")
  description?: string;          // Table description
  
  // Schema (auto-discovered from database)
  fields: TableField[];
  
  // Table metadata
  rowCount?: number;             // Approximate row count
  sizeBytes?: number;            // Approximate size
  lastUpdatedAt?: DateTime;      // Last data update in source
}

interface TableField {
  name: string;                  // Field name
  physicalName: string;          // Name in database
  type: string;                  // Data type (string, integer, timestamp, etc.)
  description?: string;          // Field description
  example?: string;              // Example value
  
  // Constraints
  isPrimaryKey: boolean;
  isNullable: boolean;
  isUnique: boolean;
  
  // Governance
  piiType?: PIIType;             // email | ssn | phone | name | address | etc.
  classification?: string;       // public | internal | confidential | restricted
  maskingRule?: string;          // Masking policy to apply
}

type PIIType = 'email' | 'ssn' | 'phone' | 'name' | 'address' | 'dob' | 'financial' | 'health' | 'other';
```

## 5.4 Contract Entity

```typescript
interface Contract {
  id: string;                    // Unique identifier (CONTRACT-XXX)
  name: string;                  // Display name
  description: string;           // Detailed description
  version: string;               // Semantic version (e.g., "1.0.0")
  status: ContractStatus;        // draft | pending_review | active | deprecated
  
  // IMPORTANT: Must link to registered Data Asset
  assetId: string;               // Reference to Data Asset (REQUIRED)
  
  // Ownership
  ownerTeamId: string;           // Owning team
  createdBy: string;             // User ID
  
  // Fundamentals
  domain: string;                // Inherited from asset, can be overridden
  purpose: string;               // What this data is for
  usage: string;                 // Usage limits
  limitations: string;           // Known constraints
  tags: string[];                // Searchable tags
  
  // Schema (auto-populated from Data Asset, can add contract-specific rules)
  // Note: The base schema comes from the linked asset
  schemaOverrides?: {
    tableId: string;
    fieldName: string;
    // Contract-specific overrides
    contractDescription?: string;
    contractConstraints?: string[];
    qualityRules?: QualityRule[];
  }[];
  
  // SLAs (inherited from asset by default, can be made stricter)
  slaOverrides?: {
    freshnessHours?: number;
    availabilityPercent?: number;
  };
  
  // Pricing
  price?: {
    amount: number;
    currency: string;
    unit: string;
  };
  
  // Custom properties
  customProperties: Record<string, string>;
  
  // Draft tracking
  isDraft: boolean;              // True if saved as draft
  lastDraftSavedAt?: DateTime;   // When draft was last saved
  
  // Metadata
  createdAt: DateTime;
  updatedAt: DateTime;
}

type ContractStatus = 'draft' | 'pending_review' | 'active' | 'deprecated';

interface QualityRule {
  field: string;
  rule: 'not_null' | 'unique' | 'range' | 'regex' | 'custom';
  parameters?: Record<string, any>;
  severity: 'error' | 'warning';
}
```

## 5.3 Contract Run Entity

```typescript
interface ContractRun {
  id: string;                    // Unique identifier
  contractId: string;            // Reference to Contract
  contractVersion: string;       // Version at time of run (IMPORTANT)
  
  // Timing
  runDate: Date;                 // Date of run (YYYY-MM-DD)
  startedAt: DateTime;           // Exact start time
  completedAt: DateTime;         // Exact end time
  duration: number;              // Duration in seconds
  
  // Results
  status: RunStatus;             // passed | warning | failed | running
  totalChecks: number;           // Number of checks performed
  passedChecks: number;          // Number passed
  warningChecks: number;         // Number with warnings
  failedChecks: number;          // Number failed
  
  // Issues generated
  issueIds: string[];            // References to Issue entities
  
  // Execution details
  triggeredBy: 'scheduled' | 'manual';
  triggeredByUser?: string;      // User ID if manual
}

type RunStatus = 'passed' | 'warning' | 'failed' | 'running';
```

## 5.4 Issue Entity

```typescript
interface Issue {
  id: string;                    // Unique identifier
  
  // Source
  contractId: string;            // Source contract
  contractVersion: string;       // Version when detected
  runId: string;                 // Run that detected this
  
  // Classification
  category: IssueCategory;
  severity: 'critical' | 'warning' | 'info';
  
  // Details
  title: string;                 // Brief description
  description: string;           // Full details
  field?: string;                // Specific field if applicable
  table?: string;                // Specific table if applicable
  
  // Assignment
  assignedTeamId: string;        // Responsible team
  assignedUserId?: string;       // Specific user if assigned
  
  // Status
  status: 'open' | 'in_progress' | 'resolved';
  resolvedAt?: DateTime;
  resolvedBy?: string;
  resolution?: string;
  
  // Metadata
  detectedAt: DateTime;
  updatedAt: DateTime;
}

type IssueCategory = 
  | 'pii_detection'
  | 'schema_drift'
  | 'data_classification'
  | 'mandatory_fields'
  | 'naming_conventions'
  | 'sla_breach'
  | 'ownership';
```

---

# 6. Implementation Tasks

## 6.1 Task Breakdown by Priority

### P0 - Core MVP (Must Have)

| ID | Task | Description | Dependencies |
|----|------|-------------|--------------|
| P0-01 | Global Layout | Implement sidebar, top nav, theme toggle | None |
| P0-02 | Dashboard Page | Health cards, timeline, issues panel, recommendations | P0-01 |
| P0-03 | Contracts List Page | Table with filters, status tabs, search, pagination | P0-01 |
| P0-04 | Contract Detail Page | Two-column layout with all sections | P0-03 |
| P0-05 | Contract Detail - Date Picker | Historical run selection with version tracking | P0-04 |
| P0-06 | Assets List Page | Table similar to contracts list | P0-01 |
| P0-07 | Asset Detail Page | Multi-table schema view, SLA inheritance display | P0-06 |
| P0-08 | **Database Connections** | Connection management (Snowflake, BigQuery, Databricks, etc.) | P0-01 |
| P0-09 | **Create Data Asset - Step 1** | Select/create database connection | P0-08 |
| P0-10 | **Create Data Asset - Step 2** | Browse & select tables from connected database | P0-09 |
| P0-11 | **Create Data Asset - Step 3** | Configure metadata, SLAs, field classifications | P0-10 |
| P0-12 | **Create Data Asset - Step 4** | Review & save asset | P0-11 |
| P0-13 | **Create Contract - Step 1** | Select registered Data Asset (REQUIRED) | P0-07 |
| P0-14 | **Create Contract - Steps 2-5** | Contract details, schema review, SLAs, submit | P0-13 |
| P0-15 | Edit Contract | Form pre-populated, link to asset read-only | P0-14 |
| P0-16 | **Unsaved Changes Modal** | Draft save prompt on navigation away | P0-14 |
| P0-17 | Issues List Page | All issues with contract attribution | P0-01 |
| P0-18 | Run Checks Action | Manual validation trigger | P0-04 |

### P1 - Essential Features

| ID | Task | Description | Dependencies |
|----|------|-------------|--------------|
| P1-01 | Contract Run Details Page | Drill-down from dashboard timeline | P0-02 |
| P1-02 | Create Contract - YAML Import | File upload with validation, must still link to asset | P0-14 |
| P1-03 | Create Contract - YAML Paste | Monaco editor with validation | P0-14 |
| P1-04 | Version Management | Create new version, version history | P0-04 |
| P1-05 | Comments System | Add, reply, resolve comments | P0-04 |
| P1-06 | My Tasks Page | Pending authorizations, drafts, comments | P0-01 |
| P1-07 | Authorization Workflow | Approve/reject contracts | P1-06 |
| P1-08 | Audit Readiness Report | Full report generation | P0-02 |
| P1-09 | Cost Readiness Report | Full report generation | P0-02 |
| P1-10 | User Management | Admin CRUD for users | P0-01 |
| P1-11 | Profile Settings | User profile management | P0-01 |
| P1-12 | Marketplace Browse | Asset discovery interface | P0-06 |
| P1-13 | **Table Preview Modal** | Preview schema & sample data from database | P0-10 |
| P1-14 | **Connection Test** | Test database connection before saving | P0-08 |
| P1-15 | **Draft Auto-Save** | Auto-save draft every 30 seconds | P0-16 |
| P1-16 | **Schema Sync** | Re-sync asset schema from database | P0-07 |

### P2 - Enhanced Features

| ID | Task | Description | Dependencies |
|----|------|-------------|--------------|
| P2-01 | Version Diff View | Compare two versions side-by-side | P1-04 |
| P2-02 | Issue Detail Page | Full issue view with actions | P0-17 |
| P2-03 | Analytics Readiness Report | Full report generation | P1-08 |
| P2-04 | AI Readiness Report | Full report generation | P1-08 |
| P2-05 | Teams Directory | List all teams | P1-12 |
| P2-06 | Team Detail Page | Team assets and contracts | P2-05 |
| P2-07 | Data Lineage View | Visual graph of data flow | P1-12 |
| P2-08 | Notification Preferences | Manage notification settings | P1-11 |
| P2-09 | Team Management | Admin CRUD for teams | P1-10 |
| P2-10 | Roles & Permissions | Fine-grained access control | P2-09 |
| P2-11 | Git Integration | Connect contracts to Git repos | P0-04 |
| P2-12 | Bulk Actions | Multi-select operations on lists | P0-03 |
| P2-13 | **Connection Scheduler** | Schedule schema syncs from database | P1-16 |
| P2-14 | **Multi-Database Asset** | Asset spanning multiple connections | P0-09 |

## 6.2 Component Library Tasks

| ID | Component | Description |
|----|-----------|-------------|
| C-01 | StatusBadge | Reusable status indicator |
| C-02 | HealthScoreCard | Circular progress with trend |
| C-03 | TimelineChart | Databricks-style run visualization |
| C-04 | DataTable | Sortable, filterable table |
| C-05 | FilterPanel | Collapsible filter controls |
| C-06 | SchemaViewer | **Multi-table** field list with expandable details |
| C-07 | ERDDiagram | Interactive schema visualization (multiple tables) |
| C-08 | CommentThread | Threaded comment display |
| C-09 | AuditTrail | Chronological change list |
| C-10 | CodeBlock | Syntax-highlighted code with copy |
| C-11 | DateRangePicker | Date selection component |
| C-12 | MultiSelectDropdown | Searchable multi-select |
| C-13 | WizardStepper | Multi-step form navigation |
| C-14 | EmptyState | Meaningful empty state display |
| C-15 | ConfirmationModal | Action confirmation dialog |
| C-16 | **UnsavedChangesModal** | Draft save prompt |
| C-17 | **DatabaseBrowser** | Tree view of database/schema/tables |
| C-18 | **ConnectionForm** | Dynamic form for different database types |
| C-19 | **TableSelector** | Checkbox list with table details |
| C-20 | **TablePreviewModal** | Schema and sample data preview |

## 6.3 API Endpoints Required

### Contracts
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/contracts` | GET | List contracts with filters |
| `/api/contracts` | POST | Create new contract (requires assetId) |
| `/api/contracts/:id` | GET | Get contract detail |
| `/api/contracts/:id` | PUT | Update contract |
| `/api/contracts/:id` | DELETE | Delete contract |
| `/api/contracts/:id/runs` | GET | Get run history |
| `/api/contracts/:id/runs/:date` | GET | Get specific run with version |
| `/api/contracts/:id/validate` | POST | Run validation against database |
| `/api/contracts/:id/authorize` | POST | Authorize contract |
| `/api/contracts/:id/versions` | GET | Get version history |
| `/api/contracts/:id/comments` | GET/POST | Manage comments |
| `/api/contracts/drafts` | GET | Get user's draft contracts |
| `/api/contracts/drafts/:id` | PUT | Update draft |

### Data Assets
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/assets` | GET | List assets with filters |
| `/api/assets` | POST | Create new asset |
| `/api/assets/:id` | GET | Get asset detail with all tables |
| `/api/assets/:id` | PUT | Update asset |
| `/api/assets/:id` | DELETE | Delete asset |
| `/api/assets/:id/sync` | POST | Re-sync schema from database |
| `/api/assets/:id/contracts` | GET | List contracts using this asset |

### Database Connections
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/connections` | GET | List all connections |
| `/api/connections` | POST | Create new connection |
| `/api/connections/:id` | GET | Get connection details |
| `/api/connections/:id` | PUT | Update connection |
| `/api/connections/:id` | DELETE | Delete connection |
| `/api/connections/:id/test` | POST | Test connection |
| `/api/connections/:id/browse` | GET | Browse databases/schemas/tables |
| `/api/connections/:id/tables/:table/preview` | GET | Get table schema & sample data |

### Other Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/issues` | GET | List issues |
| `/api/issues/:id` | GET/PUT | Issue detail/update |
| `/api/runs/:date` | GET | All runs for date |
| `/api/reports/:type` | GET | Generate report |
| `/api/users` | GET/POST | User management |
| `/api/teams` | GET/POST | Team management |
| `/api/dashboard/summary` | GET | Dashboard metrics |

---

# Appendix A: Design Tokens

## Colors (Light Theme)
| Token | Value | Use |
|-------|-------|-----|
| `--color-primary` | #6366F1 | Primary actions |
| `--color-success` | #10B981 | Passed, Active |
| `--color-warning` | #F59E0B | Warnings |
| `--color-error` | #EF4444 | Failed, Critical |
| `--color-info` | #3B82F6 | Info badges |
| `--color-muted` | #6B7280 | Secondary text |
| `--color-background` | #FFFFFF | Page background |
| `--color-surface` | #F9FAFB | Card background |
| `--color-border` | #E5E7EB | Borders |

## Typography
| Token | Value |
|-------|-------|
| `--font-family` | Inter, system-ui, sans-serif |
| `--font-size-xs` | 12px |
| `--font-size-sm` | 14px |
| `--font-size-base` | 16px |
| `--font-size-lg` | 18px |
| `--font-size-xl` | 20px |
| `--font-size-2xl` | 24px |
| `--font-size-3xl` | 30px |

## Spacing
| Token | Value |
|-------|-------|
| `--space-1` | 4px |
| `--space-2` | 8px |
| `--space-3` | 12px |
| `--space-4` | 16px |
| `--space-6` | 24px |
| `--space-8` | 32px |

---

# Appendix B: User Flows

## B.1 Create and Authorize Contract Flow
```
1. User clicks [+ New Contract]
2. User selects creation method (UI Builder)
3. User completes 6-step wizard
4. System validates contract (shows errors if any)
5. User clicks [Submit for Review]
6. Contract status → "pending_review"
7. Notification sent to approval chain
8. Approver views contract in My Tasks
9. Approver clicks [Review]
10. Approver clicks [Authorize] or [Request Changes]
11. If authorized: status → "active", runs scheduled
12. If changes requested: author notified, edits contract
```

## B.2 Investigate Failed Run Flow
```
1. User sees red bar on dashboard timeline
2. User clicks the failed day
3. System shows Contract Run Details for that date
4. User sees failed contract in list
5. User clicks [View Run] on failed contract
6. System shows Contract Detail with that date selected
7. User sees Data Quality section with failure details
8. User sees Data Governance with specific issues
9. User clicks issue to see full details
10. User assigns issue to team member
11. User leaves comment with investigation notes
```

## B.3 Generate Audit Report Flow
```
1. User clicks [Generate Report] on dashboard
2. User selects "Audit Readiness"
3. System generates report (may take a few seconds)
4. Report displays in browser
5. User reviews PII inventory, residency, ownership
6. User clicks [Export PDF] or [Export CSV]
7. System downloads report file
```

---

*Document Version: 1.0*
*Last Updated: January 2025*
*Author: Generated with Claude AI*