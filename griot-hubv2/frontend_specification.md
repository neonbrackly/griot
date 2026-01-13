# Griot Data Contract Management System
## Frontend Specification Document v1.0

---

# Table of Contents
1. [Overview](#1-overview)
2. [Information Architecture](#2-information-architecture)
3. [Global Components](#3-global-components)
4. [Page Specifications](#4-page-specifications)
5. [Data Models](#5-data-models)
6. [Implementation Tasks](#6-implementation-tasks)

---

# 1. Overview

## 1.1 Product Description
Griot is a data contract management platform that enables organizations to define, validate, and monitor contracts between data producers and consumers. The platform provides governance, compliance tracking, and quality monitoring for enterprise data assets.

## 1.2 Key Definitions
| Term | Definition                                                                                                                                                                          |
|------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Data Asset** | A logical grouping of one or more related tables/datasets from a data warehouse or lakehouse, with a defined schema and SLAs                                                        |
| **Data Contract** | A document formalizing the relationship between a producer and consumer of a data asset; could  reference a registered Data Asset or  a proposed schema for a dataset to be created |
| **Contract Run** | A scheduled or manual execution of validation checks against a contract's source data                                                                                               |
| **Issue** | A problem detected during a contract run (e.g., schema drift, PII exposure, SLA breach)                                                                                             |
| **Database Connection** | A configured connection to a data warehouse (Snowflake, BigQuery, Databricks, etc.) from which assets are discovered                                                                |

## 1.3 Key Platform Rules
1. **Data Assets can contain multiple tables** - A single asset may include several related tables (e.g., a "Customer 360" asset with `customers`, `customer_addresses`, `customer_preferences` tables)
2. **Contracts must link to registered Data Assets** - Users should not create a contract without selecting an existing Data Asset; the schema is auto-populated from the asset, unless they are creating a new proposed dataset
3. **Data Assets are discovered from connected databases** - When creating an asset, users connect to a warehouse/lakehouse and select tables to include
4. **Draft contracts trigger save prompts** - If a user navigates away while authoring, they receive a confirmation modal to save as draft or discard

## 1.3 User Roles
| Role | Description | Primary Actions |
|------|-------------|-----------------|
| **Data Engineer** | Technical user managing contracts | Create, edit, test contracts; manage data assets |
| **Product Manager** | Non-technical stakeholder | View contracts, track issues, leave comments |
| **Management** | Executive oversight (CEO/CFO/CTO/Audit) | Generate reports, view compliance dashboards |
| **Admin** | Platform administrator | Manage users, teams, permissions |

## 1.4 Health Score Formulas

### Compliance Health Score
```
Compliance Score = (Passing Governance Checks / Total Governance Checks) × 100

Governance Checks Include:
- Ownership validation (contract has valid owner)
- Data classification (all fields classified)
- PII masking (all PII fields have masking rules)
- Naming conventions (schema follows standards)
- Mandatory fields (required metadata present)
- SLA compliance (freshness, availability met)
```

### Cost Health Score
```
Cost Score = 100 - Waste Score

Waste Score = (0.4 × Orphaned%) + (0.35 × Duplicate%) + (0.25 × Unused%)

Where:
- Orphaned% = (Assets with 0 consumers / Total Assets) × 100
- Duplicate% = (Assets flagged as twins / Total Assets) × 100
- Unused% = (Assets with no queries in 30 days / Total Assets) × 100
```

### Analytics Health Score
```
Analytics Score = 100 - Quality Penalty

Quality Penalty = (Avg Null Rate × 0.5) + (Missing Metadata × 0.3) + (Stale Data × 0.2)

Where:
- Avg Null Rate = Average % of null values across all fields
- Missing Metadata = % of fields without descriptions
- Stale Data = % of assets not updated within expected freshness
```

---

# 2. Information Architecture

## 2.1 Navigation Structure

```
GRIOT PLATFORM
│
├── 🏠 HOME (Default)
│   ├── Overview Dashboard
│   ├── Contract Run Details (drill-down by date)
│   └── Reports Center
│       ├── Audit Readiness Report
│       ├── Cost Readiness Report
│       ├── Analytics Readiness Report
│       └── AI Readiness Report
│
├── 🎨 STUDIO
│   ├── Data Assets
│   │   ├── All Data Assets (list)
│   │   ├── Data Asset Detail View
│   │   └── Create/Edit Data Asset
│   │
│   ├── Data Contracts
│   │   ├── All Data Contracts (list)
│   │   ├── Contract Detail View
│   │   ├── Create Contract (UI Builder / YAML Import / YAML Paste)
│   │   ├── Edit Contract
│   │   └── Contract Version Diff
│   │
│   ├── My Tasks
│   │   ├── Pending Authorizations
│   │   ├── Comments Requiring Response
│   │   └── My Drafts
│   │
│   └── Issues
│       ├── All Issues (with contract attribution)
│       └── Issue Detail View
│
├── 🏪 MARKETPLACE
│   ├── Browse Data Assets (discovery view)
│   ├── Teams Directory
│   │   ├── All Teams
│   │   └── Team Detail
│   └── Data Lineage View
│
└── ⚙️ SYSTEM
    ├── Settings
    │   ├── Profile Settings
    │   ├── Notification Preferences
    │   └── Integrations & API Keys
    │
    └── Admin (admin role only)
        ├── User Management
        ├── Team Management
        ├── Roles & Permissions
        └── System Configuration
```

## 2.2 URL Structure

| Page | URL Pattern |
|------|-------------|
| Dashboard | `/` or `/home` |
| Contract Run Details | `/runs/:date` |
| Reports | `/reports/:reportType` |
| All Contracts | `/studio/contracts` |
| Contract Detail | `/studio/contracts/:contractId` |
| Contract Run History | `/studio/contracts/:contractId/runs` |
| Contract Run Detail | `/studio/contracts/:contractId/runs/:runId` |
| Create Contract | `/studio/contracts/new` |
| Edit Contract | `/studio/contracts/:contractId/edit` |
| Version Diff | `/studio/contracts/:contractId/diff?v1=X&v2=Y` |
| All Assets | `/studio/assets` |
| Asset Detail | `/studio/assets/:assetId` |
| My Tasks | `/studio/tasks` |
| All Issues | `/studio/issues` |
| Issue Detail | `/studio/issues/:issueId` |
| Marketplace | `/marketplace` |
| Team Detail | `/marketplace/teams/:teamId` |
| Data Lineage | `/marketplace/lineage` |
| Settings | `/settings` |
| Admin | `/admin/:section` |

---

# 3. Global Components

## 3.1 Top Navigation Bar
**Fixed at top of all pages**

| Element | Position | Behavior |
|---------|----------|----------|
| Logo (Griot) | Left | Links to `/home` |
| Global Search | Center | Search contracts, assets, issues |
| Notifications Bell | Right | Shows unread notification count, opens dropdown |
| User Avatar | Right | Opens profile menu with settings, logout |

## 3.2 Sidebar Navigation
**Fixed left sidebar, collapsible**

### Focused Section
| Item | Icon | Link | Badge |
|------|------|------|-------|
| Home | 🏠 | `/home` | - |
| Studio | 🎨 | `/studio/contracts` | - |
| Marketplace | 🏪 | `/marketplace` | - |

### System Section (bottom)
| Item | Icon | Link |
|------|------|------|
| Settings | ⚙️ | `/settings` |
| Dark Mode Toggle | 🌙/☀️ | (toggle action) |

### Studio Sub-navigation
When in Studio section, show secondary nav:
- Data Assets
- Data Contracts
- My Tasks (with badge for pending items)
- Issues (with badge for critical count)

## 3.3 Common UI Patterns

### Status Badges
| Status | Color | Use Case |
|--------|-------|----------|
| Active | Green | Active contracts |
| Draft | Gray | Unpublished contracts |
| Pending Review | Yellow | Awaiting authorization |
| Deprecated | Red/Muted | Retired contracts |
| Passed | Green | Successful runs |
| Warning | Yellow | Runs with warnings |
| Failed | Red | Failed runs |

### Filter Panel Pattern
Standard filters available on list pages:
- Status (multi-select checkboxes)
- Domain (multi-select)
- Owner/Team (searchable dropdown)
- Tags (multi-select)
- Date Range (date picker)
- Has Issues (yes/no toggle)

### Empty States
All list pages should have meaningful empty states:
- Icon illustration
- Helpful message
- Primary action button (e.g., "Create your first contract")

---

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
Take inspiration from below:

![Screenshot 2026-01-13 090259.png](Screenshot%202026-01-13%20090259.png)

Where the green shows the compliance health, the cost health, and the analytics health sections at the top, followed by a timeline chart of contract runs below it in blue, 
and panels for active issues in red below it. The side panel on the right shows recommendations panel in purple.

# Important! Let this image be the inspiration and guide for the them and look and feel. 

### Components

#### Health Score Cards (3)
| Property | Details |
|----------|---------|
| Type | Card with circular progress indicator |
| Data | Score percentage, trend arrow, summary text |
| Interaction | Click opens detailed breakdown modal |

#### Contract Runs Timeline
| Property | Details                                                         |
|----------|-----------------------------------------------------------------|
| Type | Dots stacked on each other chart (image-inspired)               |
| X-Axis | Days (configurable: 7, 14, 30, 90 days)                         |
| Y-Axis | Stacked dots showing run duration/status                        |
| Colors | Green (passed), Yellow (warnings), Red (failed), Gray (running) |
| Interaction | Click bar → navigates to `/runs/:date`                          |
| Tooltip | Shows: date, total contracts, passed/warning/failed counts      |

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
 Take inspiration from below the data table style but sticking to the theme used in the previous screenshot.:

![Screenshot 2026-01-13 091216.png](Screenshot%202026-01-13%20083748.png)

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

# The data table should follow the theme and style used in the previous screenshots provided.

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

Take inspiration from below the two-column layout but sticking to the theme used in the previous screenshots.:
![Screenshot 2026-01-13 091216.png](Screenshot%202026-01-13%20095945.png)

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

## 4.12 STUDIO - Create Contract via YAML (Import/Paste)

### Purpose
Allow users to create contracts by importing or pasting YAML content following ODCS v3.3 format.

### URL
`/studio/contracts/new?mode=yaml`

### Key Validation Requirements
1. **YAML Syntax Validation** - Must be valid YAML
2. **ODCS Schema Validation** - Must conform to ODCS v3.3.0 structure
3. **Asset Existence Check** - If schema references server/tables, verify Data Asset exists
4. **Connection Test** - If asset exists, test connection before allowing submission

### Method Selection

```
┌─────────────────────────────────────────────────────────────────┐
│ Create Data Contract                                            │
│                                                                 │
│ How would you like to create this contract?                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐     │
│ │                 │ │                 │ │                 │     │
│ │     📝         │ │     📁         │ │     📋         │     │
│ │   STEP BY STEP  │ │  IMPORT YAML   │ │   PASTE YAML   │     │
│ │                 │ │                 │ │                 │     │
│ │ Build contract  │ │ Upload a .yaml │ │ Paste YAML     │     │
│ │ section by      │ │ or .yml file   │ │ content        │     │
│ │ section         │ │                 │ │ directly       │     │
│ │                 │ │                 │ │                 │     │
│ └─────────────────┘ └─────────────────┘ └─────────────────┘     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### YAML Import Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ Import Contract from YAML                                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ STEP 1: Upload File                                             │
│ ───────────────────                                             │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │                                                             │ │
│ │     📁 Drag and drop your YAML file here                    │ │
│ │                                                             │ │
│ │     or [Browse Files]                                       │ │
│ │                                                             │ │
│ │     Accepted formats: .yaml, .yml                           │ │
│ │                                                             │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ ✓ File uploaded: full-example.odcs.yaml (24 KB)             │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│                                                  [Next: Validate]│
└─────────────────────────────────────────────────────────────────┘
```

### YAML Paste Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ Paste Contract YAML                                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ STEP 1: Paste YAML Content                                      │
│ ──────────────────────────                                      │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ 1  │ # What's this data contract about?                     │ │
│ │ 2  │ domain: seller                                         │ │
│ │ 3  │ dataProduct: my quantum                                │ │
│ │ 4  │ version: 1.1.0                                         │ │
│ │ 5  │ status: active                                         │ │
│ │ 6  │ id: 53581432-6c55-4ba2-a65f-72344a91553a               │ │
│ │ 7  │                                                        │ │
│ │ 8  │ kind: DataContract                                     │ │
│ │ 9  │ apiVersion: v3.3.0                                     │ │
│ │ 10 │                                                        │ │
│ │ 11 │ servers:                                               │ │
│ │ 12 │   - server: my-postgres                                │ │
│ │ ...│ ...                                                    │ │
│ └─────────────────────────────────────────────────────────────┘ │
│   Monaco Editor with YAML syntax highlighting                   │
│                                                                 │
│                                                  [Next: Validate]│
└─────────────────────────────────────────────────────────────────┘
```

### YAML Validation Step (CRITICAL)

```
┌─────────────────────────────────────────────────────────────────┐
│ Validate Contract YAML                                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ STEP 2: Validation                                              │
│ ──────────────────                                              │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ 🔄 Validating...                                            │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ VALIDATION CHECKS                                               │
│ ─────────────────                                               │
│                                                                 │
│ ✓ YAML Syntax                                                   │
│   Valid YAML structure                                          │
│                                                                 │
│ ✓ ODCS Schema Compliance                                        │
│   Conforms to Open Data Contract Standard v3.3.0                │
│                                                                 │
│ ✓ Required Fields                                               │
│   domain, dataProduct, version, schema present                  │
│                                                                 │
│ ⚠ Data Asset Check                                              │
│   Server "my-postgres" references database: pypl-edw            │
│   Tables: tbl_1, receivers_master                               │
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │ Does this data already exist in a registered Data Asset?│   │
│   │                                                         │   │
│   │ ○ Yes, link to existing asset:                         │   │
│   │   🔍 [Search assets...                              ]   │   │
│   │                                                         │   │
│   │   Matching assets found:                                │   │
│   │   ● 📊 Seller Analytics (my-postgres, pypl-edw)        │   │
│   │     Tables: tbl_1, receivers_master ✓ Match!           │   │
│   │                                                         │   │
│   │ ○ No, save as Proposed contract                        │   │
│   │   (Data will be created later)                         │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│                                      [← Back]  [Next: Test]     │
└─────────────────────────────────────────────────────────────────┘
```

### Validation Error States

```
┌─────────────────────────────────────────────────────────────────┐
│ Validate Contract YAML                                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ VALIDATION CHECKS                                               │
│ ─────────────────                                               │
│                                                                 │
│ ✗ YAML Syntax                                                   │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │ Error at line 15, column 4:                             │   │
│   │ "mapping values are not allowed here"                   │   │
│   │                                                         │   │
│   │ 14 │   - server: my-postgres                            │   │
│   │ 15 │     type postgres  ← missing colon                 │   │
│   │ 16 │     host: localhost                                │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│ ○ ODCS Schema Compliance (blocked by syntax error)              │
│                                                                 │
│ ○ Required Fields (blocked by syntax error)                     │
│                                                                 │
│ ○ Data Asset Check (blocked by syntax error)                    │
│                                                                 │
│                                [← Back to Editor]               │
└─────────────────────────────────────────────────────────────────┘
```

```
┌─────────────────────────────────────────────────────────────────┐
│ Validate Contract YAML                                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ VALIDATION CHECKS                                               │
│ ─────────────────                                               │
│                                                                 │
│ ✓ YAML Syntax                                                   │
│   Valid YAML structure                                          │
│                                                                 │
│ ✗ ODCS Schema Compliance                                        │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │ Missing required field: "schema"                        │   │
│   │ The contract must define at least one table in schema   │   │
│   │                                                         │   │
│   │ Invalid field type at "price.priceAmount"               │   │
│   │ Expected: number, Got: string "9.95USD"                 │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│ ○ Required Fields (blocked)                                     │
│                                                                 │
│ ○ Data Asset Check (blocked)                                    │
│                                                                 │
│                                [← Back to Editor]               │
└─────────────────────────────────────────────────────────────────┘
```

### Connection Test Step (If Asset Exists)

```
┌─────────────────────────────────────────────────────────────────┐
│ Test Connection                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ STEP 3: Test Connection                                         │
│ ───────────────────────                                         │
│                                                                 │
│ Linked Data Asset: 📊 Seller Analytics                          │
│                                                                 │
│ Server: my-postgres (PostgreSQL)                                │
│ Host: localhost:5432                                            │
│ Database: pypl-edw                                              │
│ Schema: pp_access_views                                         │
│                                                                 │
│                    [🔌 Test Connection]                         │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ ✓ Connection successful!                                    │ │
│ │                                                             │ │
│ │ Connected in 234ms                                          │ │
│ │                                                             │ │
│ │ Schema Verification:                                        │ │
│ │ ✓ Table tbl_1 found (32 columns)                           │ │
│ │ ✓ Table receivers_master found (4 columns)                  │ │
│ │ ✓ Schema matches YAML definition                           │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│                                      [← Back]  [Next: Review]   │
└─────────────────────────────────────────────────────────────────┘
```

### Connection Test Failure

```
┌─────────────────────────────────────────────────────────────────┐
│ Test Connection                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ STEP 3: Test Connection                                         │
│ ───────────────────────                                         │
│                                                                 │
│                    [🔌 Test Connection]                         │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ ✗ Connection failed                                         │ │
│ │                                                             │ │
│ │ Error: Could not connect to database                        │ │
│ │ "Connection refused: localhost:5432"                        │ │
│ │                                                             │ │
│ │ Possible causes:                                            │ │
│ │ • Database server is not running                            │ │
│ │ • Incorrect host or port                                    │ │
│ │ • Firewall blocking connection                              │ │
│ │ • Invalid credentials                                       │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ ⚠️ Cannot proceed without successful connection test        │ │
│ │                                                             │ │
│ │ Options:                                                    │ │
│ │ • Fix connection settings in the Data Asset                 │ │
│ │ • Save as Proposed contract (skip connection test)          │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│    [Go to Data Asset]  [Save as Proposed]  [Retry Connection]   │
└─────────────────────────────────────────────────────────────────┘
```

### Final Review (YAML Import)

```
┌─────────────────────────────────────────────────────────────────┐
│ Review & Submit                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ STEP 4: Review & Submit                                         │
│ ───────────────────────                                         │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ ✓ All validations passed                                    │ │
│ │ ✓ Connection test successful                                │ │
│ │ ✓ Ready to submit                                           │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ CONTRACT SUMMARY (from YAML)                                    │
│ ────────────────────────────                                    │
│                                                                 │
│ Domain:           seller                                        │
│ Data Product:     my quantum                                    │
│ Version:          1.1.0                                         │
│ API Version:      v3.3.0                                        │
│ Linked Asset:     📊 Seller Analytics                           │
│                                                                 │
│ Schema:           2 tables, 7 fields                           │
│ Quality Rules:    2 table-level, 1 field-level                 │
│ Team:             my-team (3 members)                          │
│ Roles:            4 access roles defined                        │
│ SLAs:             8 properties (inherited from asset)          │
│ Price:            $9.95 USD per megabyte                       │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ 📄 View Full YAML                                [Expand]   │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│         [← Back]  [Save as Draft]  [Submit for Review]          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4.13 Unsaved Changes Modal (CRITICAL UX)# Appendix B: User Flows

## B.1 Create Data Asset Flow (NEW)
```
1. User navigates to Studio > Data Assets
2. User clicks [+ New Data Asset]
3. Step 1: Select Database Connection
   a. User sees list of existing connections
   b. User selects existing connection OR clicks [+ Create New Connection]
   c. If new connection:
      - User selects database type (Snowflake, BigQuery, etc.)
      - User enters connection details
      - User clicks [Test Connection]
      - If success: User clicks [Save]
      - If failure: User sees error, corrects details
4. User clicks [Next Step]
5. Step 2: Select Tables
   a. System displays database browser (tree view)
   b. User expands databases/schemas
   c. User checks one or more tables to include
   d. User can click [Preview] to see schema & sample data
6. User clicks [Next Step]
7. Step 3: Configure Asset
   a. User enters name, description, domain, owner
   b. User configures SLAs (freshness, availability)
   c. User optionally expands tables to add field descriptions
   d. User marks PII fields and classifications
8. User clicks [Next Step]
9. Step 4: Review & Save
   a. System validates asset configuration
   b. User reviews summary
   c. User clicks [Save & Publish] or [Save as Draft]
10. System creates asset, redirects to Asset Detail page
```

## B.2 Create Contract Flow (ODCS v3.3 - 8 Steps)
```
1. User navigates to Studio > Data Contracts
2. User clicks [+ New Contract]
3. User selects creation method: Step-by-Step, Import YAML, or Paste YAML
4. Step 1 - Overview & Identity:
   - User enters domain, data product name, version
   - User enters description (purpose, limitations, usage)
   - User adds authoritative definitions (optional)
5. Step 2 - Schema:
   - User chooses: "Link to Existing Asset" OR "Define Proposed Schema"
   - If existing: Select asset, schema auto-populates (read-only)
   - If proposed: Define server info and tables manually
6. Step 3 - Data Quality:
   - User adds table-level quality rules (e.g., row count)
   - User adds field-level quality rules (e.g., null checks, ranges)
7. Step 4 - Pricing:
   - User optionally defines price (amount, currency, unit)
8. Step 5 - Team & Roles:
   - User defines team name and members
   - User defines access roles and approvers
9. Step 6 - SLA Properties:
   - If linked to asset: View inherited SLAs (read-only)
   - If proposed: Define expected SLAs
10. Step 7 - Support & Custom Properties:
    - User adds support channels
    - User adds tags and custom properties
11. Step 8 - Review & Test:
    - System validates contract structure
    - If linked to asset: User must test connection
    - User reviews summary
12. User clicks [Submit for Review] or [Save as Draft] or [Save as Proposed]
13. Notification sent to approval chain (if submitted)
```

## B.3 Proposed Contract → Active Flow (NEW)
```
1. Product Manager creates contract with "Proposed Schema"
2. Contract saved with status: "Proposed"
3. Product Manager shares contract details with Data Engineering
4. Data Engineering team reviews the proposed schema
5. Data Engineering creates tables in the database
6. Data Engineer navigates to Studio > Data Assets
7. Data Engineer clicks [+ New Data Asset]
8. Data Engineer connects to database and selects the new tables
9. Data Engineer saves the Data Asset
10. Data Engineer navigates to the Proposed Contract
11. Data Engineer clicks [Link to Data Asset]
12. System prompts to select asset → selects newly created asset
13. System syncs schema from asset to contract
14. System validates schema matches proposed schema
15. If match: Contract can now be submitted for review
16. If mismatch: User sees diff and must reconcile
17. Contract submitted → authorized → status becomes "Active"
18. Scheduled validation runs begin
```

## B.4 YAML Import/Paste Flow (NEW)
```
1. User navigates to Studio > Data Contracts > New
2. User selects "Import YAML" or "Paste YAML"
3. User uploads file or pastes content
4. System performs validation:
   a. YAML syntax check
   b. ODCS v3.3.0 schema compliance
   c. Required fields present
5. If validation fails: Show errors, user must fix
6. If validation passes: Check for Data Asset
   a. System reads server/tables from YAML
   b. System searches for matching registered Data Asset
   c. If found: User confirms link to asset
   d. If not found: User chooses to save as Proposed
7. If linked to asset: User must test connection
   a. Connection test runs
   b. Schema verification against actual database
   c. If fails: User cannot proceed without fixing
8. User reviews final summary
9. User clicks [Submit for Review] or [Save as Draft]
```

## B.5 Unsaved Changes / Draft Save Flow
```
1. User is editing a contract or asset (form has changes)
2. User attempts to navigate away (click nav link, back button, close tab)
3. System detects unsaved changes
4. Modal appears: "You have unsaved changes"
5. User chooses:
   a. [Save as Draft & Leave]
      - System saves current state as draft
      - Draft appears in My Tasks > My Drafts
      - User navigates to intended destination
   b. [Discard Changes]
      - System discards all changes
      - User navigates to intended destination
   c. [Cancel]
      - Modal closes
      - User stays on current page
6. If user chose Save as Draft:
   - Later, user goes to My Tasks > My Drafts
   - User clicks draft to resume editing
   - Form is restored to saved state
```

## B.6 Investigate Failed Run Flow
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

## B.7 Generate Audit Report Flow
```
1. User clicks [Generate Report] on dashboard
2. User selects "Audit Readiness"
3. System generates report (may take a few seconds)
4. Report displays in browser
5. User reviews PII inventory, residency, ownership
6. User clicks [Export PDF] or [Export CSV]
7. System downloads report file
```

## B.8 Resume Draft Contract Flow
```
1. User navigates to Studio > My Tasks
2. User clicks "My Drafts" tab
3. User sees list of draft contracts with:
   - Draft name
   - Linked asset (or "Proposed")
   - Last saved timestamp
   - Completion percentage (steps completed)
4. User clicks on a draft
5. System loads contract creation wizard at last step
6. User continues editing from where they left off
7. User can [Save as Draft] again or [Submit for Review]
```# Griot Data Contract Management System
## Frontend Specification Document v1.0

---

# Table of Contents
1. [Overview](#1-overview)
2. [Information Architecture](#2-information-architecture)
3. [Global Components](#3-global-components)
4. [Page Specifications](#4-page-specifications)
5. [Data Models](#5-data-models)
6. [Implementation Tasks](#6-implementation-tasks)

---

# 1. Overview

## 1.1 Product Description
Griot is a data contract management platform that enables organizations to define, validate, and monitor contracts between data producers and consumers. The platform provides governance, compliance tracking, and quality monitoring for enterprise data assets.

## 1.2 Key Definitions
| Term | Definition |
|------|------------|
| **Data Asset** | A logical grouping of one or more related tables/datasets from a data warehouse or lakehouse, with a defined schema and SLAs |
| **Data Contract** | A document formalizing the relationship between a producer and consumer of a data asset; must reference a registered Data Asset |
| **Contract Run** | A scheduled or manual execution of validation checks against a contract's source data |
| **Issue** | A problem detected during a contract run (e.g., schema drift, PII exposure, SLA breach) |
| **Database Connection** | A configured connection to a data warehouse (Snowflake, BigQuery, Databricks, etc.) from which assets are discovered |

## 1.3 Key Platform Rules
1. **Data Assets can contain multiple tables** - A single asset may include several related tables (e.g., a "Customer 360" asset with `customers`, `customer_addresses`, `customer_preferences` tables)
2. **Contracts reference Data Assets** - Contracts can link to existing Data Assets OR define proposed schemas for data that doesn't exist yet
3. **Data Assets are discovered from connected databases** - When creating an asset, users connect to a warehouse/lakehouse and select tables to include
4. **Schema changes only via re-sync** - Asset schemas cannot be manually edited; changes must come from re-syncing with the source database
5. **SLAs are inherited without modification** - Contracts inherit SLAs from their linked Data Asset; contract-specific SLA overrides are not supported
6. **Draft contracts trigger save prompts** - If a user navigates away while authoring, they receive a confirmation modal to save as draft or discard
7. **Proposed contracts for unmaterialized data** - Contracts can be created for data assets that don't exist yet (proactive/request mode); these cannot go "active" until the data is materialized

## 1.4 Contract Statuses

| Status | Description | Can Run Tests? | Can Go Live? |
|--------|-------------|----------------|--------------|
| **Draft** | Work in progress, not submitted | No | No |
| **Proposed** | Schema defined but data asset not yet materialized | No | No |
| **Pending Review** | Submitted for authorization | Yes (if asset exists) | No |
| **Active** | Authorized and running validations | Yes | Yes (is live) |
| **Deprecated** | No longer in active use | No | No |

### Proposed → Active Workflow
```
1. User creates contract with "proposed" schema (no existing data)
2. Contract saved with status: "proposed"
3. Data Engineering team materializes the tables in database
4. Data Engineer registers the Data Asset (connects to real tables)
5. Data Engineer links the proposed contract to the new asset
6. Contract schema is synced from actual asset
7. Contract can now be submitted for review → authorized → active
```

## 1.3 User Roles
| Role | Description | Primary Actions |
|------|-------------|-----------------|
| **Data Engineer** | Technical user managing contracts | Create, edit, test contracts; manage data assets |
| **Product Manager** | Non-technical stakeholder | View contracts, track issues, leave comments |
| **Management** | Executive oversight (CEO/CFO/CTO/Audit) | Generate reports, view compliance dashboards |
| **Admin** | Platform administrator | Manage users, teams, permissions |

## 1.4 Health Score Formulas

### Compliance Health Score
```
Compliance Score = (Passing Governance Checks / Total Governance Checks) × 100

Governance Checks Include:
- Ownership validation (contract has valid owner)
- Data classification (all fields classified)
- PII masking (all PII fields have masking rules)
- Naming conventions (schema follows standards)
- Mandatory fields (required metadata present)
- SLA compliance (freshness, availability met)
```

### Cost Health Score
```
Cost Score = 100 - Waste Score

Waste Score = (0.4 × Orphaned%) + (0.35 × Duplicate%) + (0.25 × Unused%)

Where:
- Orphaned% = (Assets with 0 consumers / Total Assets) × 100
- Duplicate% = (Assets flagged as twins / Total Assets) × 100
- Unused% = (Assets with no queries in 30 days / Total Assets) × 100
```

### Analytics Health Score
```
Analytics Score = 100 - Quality Penalty

Quality Penalty = (Avg Null Rate × 0.5) + (Missing Metadata × 0.3) + (Stale Data × 0.2)

Where:
- Avg Null Rate = Average % of null values across all fields
- Missing Metadata = % of fields without descriptions
- Stale Data = % of assets not updated within expected freshness
```

---

# 2. Information Architecture

## 2.1 Navigation Structure

```
GRIOT PLATFORM
│
├── 🏠 HOME (Default)
│   ├── Overview Dashboard
│   ├── Contract Run Details (drill-down by date)
│   └── Reports Center
│       ├── Audit Readiness Report
│       ├── Cost Readiness Report
│       ├── Analytics Readiness Report
│       └── AI Readiness Report
│
├── 🎨 STUDIO
│   ├── Data Assets
│   │   ├── All Data Assets (list)
│   │   ├── Data Asset Detail View
│   │   └── Create/Edit Data Asset
│   │
│   ├── Data Contracts
│   │   ├── All Data Contracts (list)
│   │   ├── Contract Detail View
│   │   ├── Create Contract (UI Builder / YAML Import / YAML Paste)
│   │   ├── Edit Contract
│   │   └── Contract Version Diff
│   │
│   ├── My Tasks
│   │   ├── Pending Authorizations
│   │   ├── Comments Requiring Response
│   │   └── My Drafts
│   │
│   └── Issues
│       ├── All Issues (with contract attribution)
│       └── Issue Detail View
│
├── 🏪 MARKETPLACE
│   ├── Browse Data Assets (discovery view)
│   ├── Teams Directory
│   │   ├── All Teams
│   │   └── Team Detail
│   └── Data Lineage View
│
└── ⚙️ SYSTEM
    ├── Settings
    │   ├── Profile Settings
    │   ├── Notification Preferences
    │   └── Integrations & API Keys
    │
    └── Admin (admin role only)
        ├── User Management
        ├── Team Management
        ├── Roles & Permissions
        └── System Configuration
```

## 2.2 URL Structure

| Page | URL Pattern |
|------|-------------|
| Dashboard | `/` or `/home` |
| Contract Run Details | `/runs/:date` |
| Reports | `/reports/:reportType` |
| All Contracts | `/studio/contracts` |
| Contract Detail | `/studio/contracts/:contractId` |
| Contract Run History | `/studio/contracts/:contractId/runs` |
| Contract Run Detail | `/studio/contracts/:contractId/runs/:runId` |
| Create Contract | `/studio/contracts/new` |
| Edit Contract | `/studio/contracts/:contractId/edit` |
| Version Diff | `/studio/contracts/:contractId/diff?v1=X&v2=Y` |
| All Assets | `/studio/assets` |
| Asset Detail | `/studio/assets/:assetId` |
| My Tasks | `/studio/tasks` |
| All Issues | `/studio/issues` |
| Issue Detail | `/studio/issues/:issueId` |
| Marketplace | `/marketplace` |
| Team Detail | `/marketplace/teams/:teamId` |
| Data Lineage | `/marketplace/lineage` |
| Settings | `/settings` |
| Admin | `/admin/:section` |

---

# 3. Global Components

## 3.1 Top Navigation Bar
**Fixed at top of all pages**

| Element | Position | Behavior |
|---------|----------|----------|
| Logo (Griot) | Left | Links to `/home` |
| Global Search | Center | Search contracts, assets, issues |
| Notifications Bell | Right | Shows unread notification count, opens dropdown |
| User Avatar | Right | Opens profile menu with settings, logout |

## 3.2 Sidebar Navigation
**Fixed left sidebar, collapsible**

### Focused Section
| Item | Icon | Link | Badge |
|------|------|------|-------|
| Home | 🏠 | `/home` | - |
| Studio | 🎨 | `/studio/contracts` | - |
| Marketplace | 🏪 | `/marketplace` | - |

### System Section (bottom)
| Item | Icon | Link |
|------|------|------|
| Settings | ⚙️ | `/settings` |
| Dark Mode Toggle | 🌙/☀️ | (toggle action) |

### Studio Sub-navigation
When in Studio section, show secondary nav:
- Data Assets
- Data Contracts
- My Tasks (with badge for pending items)
- Issues (with badge for critical count)

## 3.3 Common UI Patterns

### Status Badges
| Status | Color | Use Case |
|--------|-------|----------|
| Active | Green | Active contracts |
| Draft | Gray | Unpublished contracts |
| Pending Review | Yellow | Awaiting authorization |
| Deprecated | Red/Muted | Retired contracts |
| Passed | Green | Successful runs |
| Warning | Yellow | Runs with warnings |
| Failed | Red | Failed runs |

### Filter Panel Pattern
Standard filters available on list pages:
- Status (multi-select checkboxes)
- Domain (multi-select)
- Owner/Team (searchable dropdown)
- Tags (multi-select)
- Date Range (date picker)
- Has Issues (yes/no toggle)

### Empty States
All list pages should have meaningful empty states:
- Icon illustration
- Helpful message
- Primary action button (e.g., "Create your first contract")

---

