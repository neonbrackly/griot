# Schema & Database Connections Agent

## Mission Statement
Build and maintain all functionality related to Data Assets and Database Connections. Users must be able to seamlessly connect to their data warehouses, browse database structures, and register data assets with an intuitive, fast experience.

---

## Feature Ownership

### Core Responsibilities
1. **Data Asset Management** - List, detail, create, edit, delete data assets
2. **Database Connections** - Create, test, manage database connections
3. **Database Browser** - Browse schemas, tables, columns from connections
4. **Asset Creation Wizard** - 4-step guided asset creation flow
5. **Schema Viewer** - Display multi-table schemas with field details
6. **Table Preview** - Sample data and schema preview modals

### Pages Owned

```
src/app/
├── studio/
│   └── assets/
│       ├── page.tsx                    # Asset list with filters
│       ├── [assetId]/
│       │   └── page.tsx               # Asset detail (schema viewer)
│       └── new/
│           └── page.tsx               # 4-step creation wizard
└── settings/
    └── connections/
        └── page.tsx                   # Database connection management
```

### Components Owned

```
src/components/
├── assets/
│   ├── AssetList.tsx                  # Asset list with filters
│   ├── AssetCard.tsx                  # Asset card for list view
│   ├── AssetDetail.tsx                # Asset detail view
│   ├── SchemaViewer.tsx               # Multi-table schema display
│   ├── TableCard.tsx                  # Expandable table with fields
│   ├── FieldList.tsx                  # List of fields in a table
│   ├── FieldRow.tsx                   # Individual field display
│   └── wizard/
│       ├── Step1Connection.tsx        # Select database connection
│       ├── Step2Tables.tsx            # Database browser & table selection
│       ├── Step3Configure.tsx         # Asset metadata & SLA config
│       └── Step4Review.tsx            # Review & save
├── connections/
│   ├── ConnectionForm.tsx             # Create/edit connection form
│   ├── ConnectionCard.tsx             # Connection card with test button
│   ├── ConnectionList.tsx             # List of connections
│   ├── DatabaseTypeSelector.tsx       # DB type selection grid
│   ├── DatabaseTypeIcon.tsx           # Icons for each DB type
│   └── forms/
│       ├── SnowflakeForm.tsx          # Snowflake-specific fields
│       ├── BigQueryForm.tsx           # BigQuery-specific fields
│       ├── DatabricksForm.tsx         # Databricks-specific fields
│       ├── PostgresForm.tsx           # PostgreSQL-specific fields
│       └── RedshiftForm.tsx           # Redshift-specific fields
└── database-browser/
    ├── DatabaseBrowser.tsx            # Tree view of schemas/tables
    ├── SchemaNode.tsx                 # Expandable schema node
    ├── TableNode.tsx                  # Selectable table node
    └── TablePreviewModal.tsx          # Sample data preview modal
```

### Mock Handlers Owned

```
src/lib/mocks/
├── handlers/
│   ├── assets.ts                      # Asset CRUD endpoints
│   └── connections.ts                 # Connection CRUD & browse endpoints
└── data/
    ├── assets.ts                      # Mock asset data
    └── connections.ts                 # Mock connection data
```

---

## Technical Specifications

### Data Asset Entity
```typescript
interface DataAsset {
  id: string
  name: string
  description: string
  domain: string
  status: 'active' | 'draft' | 'deprecated'
  connectionId: string
  ownerTeamId: string
  tags: string[]
  tables: Table[]
  sla: {
    freshnessHours: number
    availabilityPercent: number
  }
  createdAt: string
  updatedAt: string
  lastSyncedAt: string
}

interface Table {
  id: string
  name: string
  physicalName: string
  description?: string
  fields: Field[]
  rowCount?: number
}

interface Field {
  name: string
  type: string
  description?: string
  isPrimaryKey: boolean
  isNullable: boolean
  piiType?: string
}
```

### Connection Entity
```typescript
interface Connection {
  id: string
  name: string
  type: 'snowflake' | 'bigquery' | 'databricks' | 'postgres' | 'redshift'
  status: 'active' | 'inactive' | 'error'
  config: ConnectionConfig
  lastTestedAt?: string
  lastTestStatus?: 'success' | 'failure'
  createdAt: string
}

// Type-specific configs
interface SnowflakeConfig {
  account: string
  warehouse: string
  database: string
  schema?: string
  role?: string
}

interface BigQueryConfig {
  projectId: string
  dataset: string
  location?: string
}
```

### API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/assets` | List assets with filters |
| GET | `/api/assets/:id` | Get asset detail |
| POST | `/api/assets` | Create asset |
| PUT | `/api/assets/:id` | Update asset |
| DELETE | `/api/assets/:id` | Delete asset |
| POST | `/api/assets/:id/sync` | Sync schema from database |
| GET | `/api/connections` | List connections |
| POST | `/api/connections` | Create connection |
| POST | `/api/connections/:id/test` | Test connection |
| GET | `/api/connections/:id/browse` | Browse database structure |
| GET | `/api/connections/:id/preview/:table` | Preview table data |

### UX Requirements
| Requirement | Implementation |
|-------------|----------------|
| Instant feedback | Every click shows immediate response (loading state, optimistic update) |
| Progressive disclosure | Don't overwhelm; show details on demand |
| Error recovery | Clear error messages with actionable solutions |
| Keyboard navigation | Full support for power users |
| Prefetching | Load data before user needs it (hover prefetch) |
| Search | Debounced (300ms) with loading indicator |
| URL state sync | Filters persist in URL for shareable links |

---

## Feature Details

### Asset List Page
- Status tabs: All, Active, Draft, Deprecated (with counts)
- Search with debounce (300ms)
- Filters: Domain, Owner, Tags
- Table columns: Asset name, Domain, Tables count, Owner, Status
- Row click navigates to detail
- Hover prefetches asset detail
- Empty state with CTA to create asset

### Asset Detail Page (Two-Column Layout)
**Left Column:**
- Schema diagram (interactive ERD placeholder)
- Tables list (expandable with fields)
- Description

**Right Column:**
- Connection info with status
- SLA display (freshness, availability)
- Contracts using this asset
- Audit trail

**Actions:**
- Sync Schema (with loading state)
- Edit Asset
- Create Contract from Asset

### Asset Creation Wizard (4 Steps)
1. **Connection** - Select existing or create new connection
2. **Tables** - Browse database, select tables (tree view with checkboxes)
3. **Configure** - Name, description, domain, owner, tags, SLA
4. **Review** - Validation checklist, summary, save options (draft/publish)

### Database Browser
- Tree structure: Schema > Tables > (Columns on expand)
- Checkbox selection for tables
- Preview button opens modal with sample data
- Search/filter within browser
- Selected tables summary panel

---

## Dependencies

### Provides To Other Agents
- Asset data for contract creation (Contracts Agent)
- Asset list for marketplace (Dashboards-Reports Agent)
- Schema viewer component

### Depends On
- Design Agent: UI components, DataTable, Form components, Toast
- Design Agent: API client, mock infrastructure

---

## Code References

### Key Files
| Purpose | Path |
|---------|------|
| Asset list page | `src/app/studio/assets/page.tsx` |
| Asset detail page | `src/app/studio/assets/[assetId]/page.tsx` |
| Asset wizard | `src/app/studio/assets/new/page.tsx` |
| Wizard steps | `src/components/assets/wizard/Step*.tsx` |
| Mock handlers | `src/lib/mocks/handlers/assets.ts` |
| Mock data | `src/lib/mocks/data/assets.ts` |
| Types | `src/types/index.ts` (DataAsset, Connection) |
| Schemas | `src/types/schemas.ts` (assetSchema, connectionSchema) |
