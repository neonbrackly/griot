# Agent 1: Data Assets & Database Connections

## Mission Statement
Build all functionality related to Data Assets and Database Connections. Users must be able to seamlessly connect to their data warehouses, browse database structures, and register data assets with an intuitive, fast experience.

---

## Critical UX Requirements

| Requirement | Implementation |
|-------------|----------------|
| **Instant feedback** | Every click shows immediate response (loading state, optimistic update) |
| **Progressive disclosure** | Don't overwhelm; show details on demand |
| **Error recovery** | Clear error messages with actionable solutions |
| **Keyboard navigation** | Full support for power users |
| **Prefetching** | Load data before user needs it |

---

## Pages Owned

```
/app/studio/assets/
├── page.tsx                    # Asset list
├── [assetId]/
│   └── page.tsx               # Asset detail
└── new/
    └── page.tsx               # Create asset wizard

/app/settings/connections/
└── page.tsx                   # Manage DB connections
```

---

## Task Specifications

### A1-01: Asset List Page

**Objective**: Display all data assets with filtering, search, and instant navigation.

**File**: `src/app/studio/assets/page.tsx`

**Layout**:
```
┌─────────────────────────────────────────────────────────────────┐
│ Data Assets                                    [+ New Asset]    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ [All •89] [Active •72] [Draft •12] [Deprecated •5]             │
│                                                                 │
│ 🔍 [Search assets...]              [Domain ▼] [Owner ▼] [Tags ▼]│
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ □ │ Asset            │ Domain   │ Tables │ Owner    │Status │ │
│ │───┼──────────────────┼──────────┼────────┼──────────┼───────│ │
│ │   │ 📊 Customer 360  │ CRM      │ 3      │ CRM Team │Active │ │
│ │   │ 💰 Transactions  │ Finance  │ 2      │ Finance  │Active │ │
│ │   │ ...              │          │        │          │       │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ Showing 1-10 of 89                    [← Prev] [1][2][3] [Next→]│
└─────────────────────────────────────────────────────────────────┘
```

**UX Requirements**:

1. **Instant Search**:
```tsx
// Debounce search input (300ms)
const [search, setSearch] = useState('')
const debouncedSearch = useDebounce(search, 300)

// Show loading indicator while searching
<Input
  placeholder="Search assets..."
  value={search}
  onChange={(e) => setSearch(e.target.value)}
  leftIcon={<Search className="w-4 h-4" />}
  rightIcon={isSearching && <Loader2 className="w-4 h-4 animate-spin" />}
/>
```

2. **Prefetch on Hover**:
```tsx
// Prefetch asset detail when hovering over row
<tr
  onMouseEnter={() => {
    queryClient.prefetchQuery({
      queryKey: ['asset', asset.id],
      queryFn: () => fetchAsset(asset.id),
    })
  }}
  onClick={() => router.push(`/studio/assets/${asset.id}`)}
>
```

3. **Optimistic Status Tabs**:
```tsx
// Status tabs with instant count updates
const statusCounts = useMemo(() => ({
  all: assets.length,
  active: assets.filter(a => a.status === 'active').length,
  draft: assets.filter(a => a.status === 'draft').length,
  deprecated: assets.filter(a => a.status === 'deprecated').length,
}), [assets])

<Tabs value={statusFilter} onValueChange={setStatusFilter}>
  <TabsList>
    <TabsTrigger value="all">All •{statusCounts.all}</TabsTrigger>
    <TabsTrigger value="active">Active •{statusCounts.active}</TabsTrigger>
    {/* ... */}
  </TabsList>
</Tabs>
```

4. **URL State Sync**:
```tsx
// Sync filters with URL for shareable links
const searchParams = useSearchParams()
const router = useRouter()

const updateFilters = (filters: Filters) => {
  const params = new URLSearchParams(searchParams)
  Object.entries(filters).forEach(([key, value]) => {
    if (value) params.set(key, value)
    else params.delete(key)
  })
  router.push(`?${params.toString()}`, { scroll: false })
}
```

5. **Empty State**:
```tsx
// When no assets exist
<EmptyState
  icon={Database}
  title="No data assets yet"
  description="Data assets represent tables and datasets from your data warehouse. Create your first asset to get started."
  action={{
    label: "Create Data Asset",
    onClick: () => router.push('/studio/assets/new')
  }}
/>
```

**Components Required**:
- `AssetList` - Main list container
- `AssetListFilters` - Filter controls
- `AssetListTable` - Table with columns
- `AssetRow` - Individual row with hover actions

---

### A1-02: Asset Detail Page

**Objective**: Display comprehensive asset information with multi-table schema viewer.

**File**: `src/app/studio/assets/[assetId]/page.tsx`

**Layout** (Two-column like contract detail):
```
┌─────────────────────────────────────────────────────────────────┐
│ ← All Assets                                                    │
│                                                                 │
│ 📊 Customer 360                                                 │
│ customer_360 • Active • CRM Domain                             │
│                                                                 │
│ [Sync Schema] [Edit] [Create Contract from Asset]              │
├─────────────────────────────────────────────────────────────────┤
│ LEFT COLUMN                    │ RIGHT COLUMN                   │
│                                │                                │
│ ┌────────────────────────────┐ │ ┌────────────────────────────┐ │
│ │ SCHEMA DIAGRAM             │ │ │ CONNECTION INFO            │ │
│ │ [Interactive ERD]          │ │ │ ❄️ prod-snowflake          │ │
│ │                            │ │ │ Status: ✓ Connected        │ │
│ └────────────────────────────┘ │ └────────────────────────────┘ │
│                                │                                │
│ ┌────────────────────────────┐ │ ┌────────────────────────────┐ │
│ │ TABLES (3)                 │ │ │ SERVICE LEVEL AGREEMENTS   │ │
│ │                            │ │ │ Freshness: 24 hours        │ │
│ │ ▼ customers (32 fields)    │ │ │ Availability: 99.5%        │ │
│ │   customer_id  VARCHAR 🔑  │ │ └────────────────────────────┘ │
│ │   email        VARCHAR 📧  │ │                                │
│ │   first_name   VARCHAR     │ │ ┌────────────────────────────┐ │
│ │   ...                      │ │ │ CONTRACTS USING THIS ASSET │ │
│ │                            │ │ │ • Customer Analytics v2.0  │ │
│ │ ▶ addresses (12 fields)    │ │ │ • Churn Prediction v1.5    │ │
│ │ ▶ preferences (8 fields)   │ │ └────────────────────────────┘ │
│ └────────────────────────────┘ │                                │
│                                │ ┌────────────────────────────┐ │
│ ┌────────────────────────────┐ │ │ AUDIT TRAIL                │ │
│ │ DESCRIPTION                │ │ │ Schema synced - 2h ago     │ │
│ │ Comprehensive customer...  │ │ │ Asset created - Jan 5      │ │
│ └────────────────────────────┘ │ └────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

**UX Requirements**:

1. **Instant Page Load with Skeleton**:
```tsx
// Show skeleton immediately while data loads
export default function AssetDetailPage({ params }) {
  return (
    <Suspense fallback={<AssetDetailSkeleton />}>
      <AssetDetail assetId={params.assetId} />
    </Suspense>
  )
}
```

2. **Expandable Tables with Animation**:
```tsx
// Smooth expand/collapse for table fields
<motion.div
  initial={false}
  animate={{ height: isExpanded ? 'auto' : 0 }}
  transition={{ duration: 0.2 }}
  className="overflow-hidden"
>
  <FieldList fields={table.fields} />
</motion.div>
```

3. **Schema Sync with Progress**:
```tsx
// Sync schema button with loading state
const syncMutation = useMutation({
  mutationFn: () => syncAssetSchema(assetId),
  onSuccess: () => {
    toast.success('Schema synced', 'Schema has been updated from database')
    queryClient.invalidateQueries(['asset', assetId])
  },
  onError: (error) => {
    toast.error('Sync failed', error.message)
  }
})

<Button 
  onClick={() => syncMutation.mutate()}
  loading={syncMutation.isPending}
>
  <RefreshCw className={cn("w-4 h-4 mr-2", syncMutation.isPending && "animate-spin")} />
  Sync Schema
</Button>
```

4. **Field Detail on Click**:
```tsx
// Click field to see full details in slide-over panel
<FieldRow 
  field={field}
  onClick={() => setSelectedField(field)}
/>

<SlideOver open={!!selectedField} onClose={() => setSelectedField(null)}>
  <FieldDetailPanel field={selectedField} />
</SlideOver>
```

**Components Required**:
- `AssetDetailView` - Main container
- `AssetHeader` - Title, status, actions
- `SchemaViewer` - Multi-table schema display
- `TableCard` - Expandable table with fields
- `FieldList` - List of fields in a table
- `FieldRow` - Individual field display
- `FieldDetailPanel` - Detailed field info (slide-over)
- `ConnectionInfoCard` - Database connection status
- `SLACard` - SLA display
- `ContractsUsingAsset` - List of contracts
- `AssetAuditTrail` - Change history

---

### A1-03 to A1-06: Create Asset Wizard

**Objective**: Guide users through creating a data asset in 4 intuitive steps.

#### Wizard Container

**File**: `src/app/studio/assets/new/page.tsx`

```tsx
'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { WizardStepper } from '@/components/forms/WizardStepper'
import { useUnsavedChanges } from '@/lib/hooks/useUnsavedChanges'
import { UnsavedChangesModal } from '@/components/feedback/UnsavedChangesModal'

const steps = [
  { id: 'connection', label: 'Connection', description: 'Select database' },
  { id: 'tables', label: 'Tables', description: 'Choose tables' },
  { id: 'configure', label: 'Configure', description: 'Set metadata' },
  { id: 'review', label: 'Review', description: 'Confirm & save' },
]

export default function CreateAssetPage() {
  const router = useRouter()
  const [currentStep, setCurrentStep] = useState(0)
  const [formData, setFormData] = useState<AssetFormData>({})
  const [isDirty, setIsDirty] = useState(false)
  
  // Block navigation when form has unsaved changes
  useUnsavedChanges(isDirty)
  
  const updateFormData = (data: Partial<AssetFormData>) => {
    setFormData(prev => ({ ...prev, ...data }))
    setIsDirty(true)
  }
  
  const goToStep = (step: number) => {
    // Validate current step before proceeding
    if (step > currentStep && !validateStep(currentStep)) {
      return
    }
    setCurrentStep(step)
  }
  
  const renderStep = () => {
    switch (currentStep) {
      case 0:
        return (
          <Step1Connection 
            data={formData} 
            onUpdate={updateFormData}
            onNext={() => goToStep(1)}
          />
        )
      case 1:
        return (
          <Step2Tables 
            data={formData} 
            onUpdate={updateFormData}
            onBack={() => goToStep(0)}
            onNext={() => goToStep(2)}
          />
        )
      case 2:
        return (
          <Step3Configure 
            data={formData} 
            onUpdate={updateFormData}
            onBack={() => goToStep(1)}
            onNext={() => goToStep(3)}
          />
        )
      case 3:
        return (
          <Step4Review 
            data={formData}
            onBack={() => goToStep(2)}
            onSaveDraft={handleSaveDraft}
            onPublish={handlePublish}
          />
        )
    }
  }
  
  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-text-primary">Create Data Asset</h1>
        <p className="text-text-secondary mt-1">
          Connect to your database and register tables as a data asset
        </p>
      </div>
      
      <WizardStepper 
        steps={steps} 
        currentStep={currentStep}
        onStepClick={goToStep}
        allowNavigation={true}
      />
      
      <div className="mt-8">
        {renderStep()}
      </div>
    </div>
  )
}
```

#### Step 1: Database Connection

**File**: `src/components/assets/wizard/Step1Connection.tsx`

```tsx
'use client'

import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { Plus, Check, Loader2, AlertCircle } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/layout/Card'
import { ConnectionForm } from '@/components/connections/ConnectionForm'
import { DatabaseTypeIcon } from '@/components/connections/DatabaseTypeIcon'

interface Step1Props {
  data: AssetFormData
  onUpdate: (data: Partial<AssetFormData>) => void
  onNext: () => void
}

export function Step1Connection({ data, onUpdate, onNext }: Step1Props) {
  const [showNewConnection, setShowNewConnection] = useState(false)
  
  // Fetch existing connections
  const { data: connections, isLoading } = useQuery({
    queryKey: ['connections'],
    queryFn: fetchConnections,
  })
  
  // Test connection mutation
  const testMutation = useMutation({
    mutationFn: testConnection,
    onSuccess: () => {
      toast.success('Connection successful')
    },
    onError: (error) => {
      toast.error('Connection failed', error.message)
    }
  })
  
  const handleSelectConnection = (connection: Connection) => {
    onUpdate({ connectionId: connection.id, connection })
  }
  
  const handleConnectionCreated = (connection: Connection) => {
    onUpdate({ connectionId: connection.id, connection })
    setShowNewConnection(false)
    toast.success('Connection created', `${connection.name} is ready to use`)
  }
  
  const canProceed = !!data.connectionId
  
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-medium text-text-primary">
          Step 1: Select Database Connection
        </h2>
        <p className="text-sm text-text-secondary mt-1">
          Choose an existing connection or create a new one
        </p>
      </div>
      
      {/* Existing Connections */}
      <div className="space-y-3">
        <h3 className="text-sm font-medium text-text-primary">
          Existing Connections
        </h3>
        
        {isLoading ? (
          <div className="grid grid-cols-1 gap-3">
            {[1, 2, 3].map(i => (
              <ConnectionCardSkeleton key={i} />
            ))}
          </div>
        ) : connections?.length === 0 ? (
          <Card className="p-6 text-center">
            <p className="text-text-secondary">No connections configured yet</p>
          </Card>
        ) : (
          <div className="grid grid-cols-1 gap-3">
            {connections?.map(connection => (
              <ConnectionCard
                key={connection.id}
                connection={connection}
                selected={data.connectionId === connection.id}
                onSelect={() => handleSelectConnection(connection)}
                onTest={() => testMutation.mutate(connection.id)}
                isTesting={testMutation.isPending && testMutation.variables === connection.id}
              />
            ))}
          </div>
        )}
      </div>
      
      {/* Create New Connection */}
      {!showNewConnection ? (
        <Button
          variant="secondary"
          onClick={() => setShowNewConnection(true)}
          className="w-full"
        >
          <Plus className="w-4 h-4 mr-2" />
          Create New Connection
        </Button>
      ) : (
        <Card className="p-6">
          <h3 className="text-sm font-medium text-text-primary mb-4">
            New Database Connection
          </h3>
          <ConnectionForm
            onSuccess={handleConnectionCreated}
            onCancel={() => setShowNewConnection(false)}
          />
        </Card>
      )}
      
      {/* Navigation */}
      <div className="flex justify-end pt-6 border-t border-border-default">
        <Button
          onClick={onNext}
          disabled={!canProceed}
        >
          Next: Select Tables
        </Button>
      </div>
    </div>
  )
}

// Connection Card Component
function ConnectionCard({ 
  connection, 
  selected, 
  onSelect, 
  onTest,
  isTesting 
}: ConnectionCardProps) {
  return (
    <button
      onClick={onSelect}
      className={cn(
        "w-full p-4 rounded-lg border-2 text-left transition-all duration-fast",
        "hover:border-primary-300 hover:shadow-sm",
        selected 
          ? "border-primary-500 bg-primary-50 dark:bg-primary-900/20" 
          : "border-border-default bg-bg-secondary"
      )}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <DatabaseTypeIcon type={connection.type} className="w-8 h-8" />
          <div>
            <div className="font-medium text-text-primary">{connection.name}</div>
            <div className="text-sm text-text-secondary">
              {connection.config.host || connection.config.account}
            </div>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          {connection.lastTestStatus === 'success' && (
            <span className="text-xs text-green-600 flex items-center gap-1">
              <Check className="w-3 h-3" />
              Connected
            </span>
          )}
          
          <Button
            variant="ghost"
            size="sm"
            onClick={(e) => {
              e.stopPropagation()
              onTest()
            }}
            loading={isTesting}
          >
            Test
          </Button>
          
          {selected && (
            <div className="w-5 h-5 rounded-full bg-primary-500 flex items-center justify-center">
              <Check className="w-3 h-3 text-white" />
            </div>
          )}
        </div>
      </div>
    </button>
  )
}
```

#### Step 2: Table Selection (Database Browser)

**File**: `src/components/assets/wizard/Step2Tables.tsx`

```tsx
'use client'

import { useState, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { ChevronRight, ChevronDown, Table, Database, Search, Eye } from 'lucide-react'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'
import { Checkbox } from '@/components/ui/Checkbox'
import { Badge } from '@/components/ui/Badge'
import { motion, AnimatePresence } from 'framer-motion'

interface Step2Props {
  data: AssetFormData
  onUpdate: (data: Partial<AssetFormData>) => void
  onBack: () => void
  onNext: () => void
}

export function Step2Tables({ data, onUpdate, onBack, onNext }: Step2Props) {
  const [search, setSearch] = useState('')
  const [expandedSchemas, setExpandedSchemas] = useState<Set<string>>(new Set())
  const [previewTable, setPreviewTable] = useState<string | null>(null)
  
  // Fetch database structure
  const { data: dbStructure, isLoading } = useQuery({
    queryKey: ['connection-browse', data.connectionId],
    queryFn: () => browseConnection(data.connectionId!),
    enabled: !!data.connectionId,
  })
  
  // Filter tables by search
  const filteredStructure = useMemo(() => {
    if (!search || !dbStructure) return dbStructure
    
    return dbStructure.schemas.map(schema => ({
      ...schema,
      tables: schema.tables.filter(table => 
        table.name.toLowerCase().includes(search.toLowerCase())
      )
    })).filter(schema => schema.tables.length > 0)
  }, [dbStructure, search])
  
  const selectedTables = data.selectedTables || []
  
  const toggleTable = (schemaName: string, tableName: string) => {
    const tableId = `${schemaName}.${tableName}`
    const isSelected = selectedTables.some(t => t.id === tableId)
    
    if (isSelected) {
      onUpdate({
        selectedTables: selectedTables.filter(t => t.id !== tableId)
      })
    } else {
      const schema = dbStructure?.schemas.find(s => s.name === schemaName)
      const table = schema?.tables.find(t => t.name === tableName)
      if (table) {
        onUpdate({
          selectedTables: [...selectedTables, { 
            id: tableId, 
            schema: schemaName, 
            name: tableName,
            columns: table.columns,
            rowCount: table.rowCount,
          }]
        })
      }
    }
  }
  
  const toggleSchema = (schemaName: string) => {
    const newExpanded = new Set(expandedSchemas)
    if (newExpanded.has(schemaName)) {
      newExpanded.delete(schemaName)
    } else {
      newExpanded.add(schemaName)
    }
    setExpandedSchemas(newExpanded)
  }
  
  const canProceed = selectedTables.length > 0
  
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-medium text-text-primary">
          Step 2: Select Tables
        </h2>
        <p className="text-sm text-text-secondary mt-1">
          Browse your database and select tables to include in this asset
        </p>
      </div>
      
      <div className="grid grid-cols-2 gap-6">
        {/* Left: Database Browser */}
        <div className="space-y-4">
          <Input
            placeholder="Search tables..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            leftIcon={<Search className="w-4 h-4" />}
          />
          
          <div className="border border-border-default rounded-lg overflow-hidden max-h-[500px] overflow-y-auto">
            {isLoading ? (
              <DatabaseBrowserSkeleton />
            ) : (
              <div className="divide-y divide-border-default">
                {filteredStructure?.schemas.map(schema => (
                  <SchemaNode
                    key={schema.name}
                    schema={schema}
                    expanded={expandedSchemas.has(schema.name)}
                    onToggle={() => toggleSchema(schema.name)}
                    selectedTables={selectedTables}
                    onToggleTable={toggleTable}
                    onPreview={setPreviewTable}
                  />
                ))}
              </div>
            )}
          </div>
        </div>
        
        {/* Right: Selected Tables */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium text-text-primary">
              Selected Tables ({selectedTables.length})
            </h3>
            {selectedTables.length > 0 && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onUpdate({ selectedTables: [] })}
              >
                Clear All
              </Button>
            )}
          </div>
          
          <div className="border border-border-default rounded-lg p-4 min-h-[200px]">
            {selectedTables.length === 0 ? (
              <div className="text-center text-text-tertiary py-8">
                <Table className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p>No tables selected</p>
                <p className="text-sm">Click tables on the left to add them</p>
              </div>
            ) : (
              <div className="space-y-2">
                {selectedTables.map(table => (
                  <SelectedTableCard
                    key={table.id}
                    table={table}
                    onRemove={() => toggleTable(table.schema, table.name)}
                    onPreview={() => setPreviewTable(table.id)}
                  />
                ))}
              </div>
            )}
          </div>
          
          {/* Summary Stats */}
          {selectedTables.length > 0 && (
            <div className="bg-bg-tertiary rounded-lg p-4">
              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <div className="text-2xl font-semibold text-text-primary">
                    {selectedTables.length}
                  </div>
                  <div className="text-xs text-text-secondary">Tables</div>
                </div>
                <div>
                  <div className="text-2xl font-semibold text-text-primary">
                    {selectedTables.reduce((acc, t) => acc + t.columns.length, 0)}
                  </div>
                  <div className="text-xs text-text-secondary">Columns</div>
                </div>
                <div>
                  <div className="text-2xl font-semibold text-text-primary">
                    {formatNumber(selectedTables.reduce((acc, t) => acc + (t.rowCount || 0), 0))}
                  </div>
                  <div className="text-xs text-text-secondary">Est. Rows</div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
      
      {/* Table Preview Modal */}
      <TablePreviewModal
        open={!!previewTable}
        onClose={() => setPreviewTable(null)}
        connectionId={data.connectionId!}
        tableId={previewTable}
      />
      
      {/* Navigation */}
      <div className="flex justify-between pt-6 border-t border-border-default">
        <Button variant="secondary" onClick={onBack}>
          Back
        </Button>
        <Button onClick={onNext} disabled={!canProceed}>
          Next: Configure Asset
        </Button>
      </div>
    </div>
  )
}

// Schema Tree Node
function SchemaNode({ schema, expanded, onToggle, selectedTables, onToggleTable, onPreview }) {
  const selectedInSchema = selectedTables.filter(t => t.schema === schema.name).length
  
  return (
    <div>
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between px-4 py-3 hover:bg-bg-hover transition-colors"
      >
        <div className="flex items-center gap-2">
          {expanded ? (
            <ChevronDown className="w-4 h-4 text-text-tertiary" />
          ) : (
            <ChevronRight className="w-4 h-4 text-text-tertiary" />
          )}
          <Database className="w-4 h-4 text-text-secondary" />
          <span className="font-medium text-text-primary">{schema.name}</span>
          <Badge variant="secondary" size="sm">
            {schema.tables.length} tables
          </Badge>
        </div>
        {selectedInSchema > 0 && (
          <Badge variant="primary" size="sm">
            {selectedInSchema} selected
          </Badge>
        )}
      </button>
      
      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0 }}
            animate={{ height: 'auto' }}
            exit={{ height: 0 }}
            className="overflow-hidden"
          >
            <div className="pl-8 py-1 space-y-1">
              {schema.tables.map(table => {
                const tableId = `${schema.name}.${table.name}`
                const isSelected = selectedTables.some(t => t.id === tableId)
                
                return (
                  <div
                    key={table.name}
                    className={cn(
                      "flex items-center justify-between px-3 py-2 rounded-md",
                      "hover:bg-bg-hover transition-colors",
                      isSelected && "bg-primary-50 dark:bg-primary-900/20"
                    )}
                  >
                    <label className="flex items-center gap-3 cursor-pointer flex-1">
                      <Checkbox
                        checked={isSelected}
                        onCheckedChange={() => onToggleTable(schema.name, table.name)}
                      />
                      <Table className="w-4 h-4 text-text-tertiary" />
                      <span className="text-sm text-text-primary">{table.name}</span>
                      <span className="text-xs text-text-tertiary">
                        {table.columns.length} cols
                      </span>
                    </label>
                    
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => onPreview(tableId)}
                    >
                      <Eye className="w-4 h-4" />
                    </Button>
                  </div>
                )
              })}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
```

#### Step 3: Configure Asset

**File**: `src/components/assets/wizard/Step3Configure.tsx`

```tsx
'use client'

import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { FormField } from '@/components/forms/FormField'
import { Input } from '@/components/ui/Input'
import { Textarea } from '@/components/ui/Textarea'
import { Select } from '@/components/ui/Select'
import { TagInput } from '@/components/forms/TagInput'
import { Button } from '@/components/ui/Button'

const configSchema = z.object({
  name: z.string().min(3, 'Name must be at least 3 characters'),
  description: z.string().min(20, 'Description must be at least 20 characters'),
  domain: z.string().min(1, 'Domain is required'),
  ownerTeamId: z.string().min(1, 'Owner team is required'),
  tags: z.array(z.string()),
  sla: z.object({
    freshnessHours: z.number().min(1).max(720),
    availabilityPercent: z.number().min(90).max(100),
  }),
})

export function Step3Configure({ data, onUpdate, onBack, onNext }: Step3Props) {
  const form = useForm({
    resolver: zodResolver(configSchema),
    defaultValues: {
      name: data.name || '',
      description: data.description || '',
      domain: data.domain || '',
      ownerTeamId: data.ownerTeamId || '',
      tags: data.tags || [],
      sla: data.sla || {
        freshnessHours: 24,
        availabilityPercent: 99.5,
      },
    },
  })
  
  const handleSubmit = form.handleSubmit((values) => {
    onUpdate(values)
    onNext()
  })
  
  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <h2 className="text-lg font-medium text-text-primary">
          Step 3: Configure Asset
        </h2>
        <p className="text-sm text-text-secondary mt-1">
          Add metadata and configure service level agreements
        </p>
      </div>
      
      {/* Basic Information */}
      <div className="space-y-4">
        <h3 className="text-sm font-medium text-text-primary">Basic Information</h3>
        
        <FormField name="name" label="Asset Name" required>
          <Input {...form.register('name')} placeholder="e.g., Customer 360" />
        </FormField>
        
        <FormField name="description" label="Description" required>
          <Textarea 
            {...form.register('description')} 
            placeholder="Describe what this data asset contains and its purpose..."
            rows={3}
          />
        </FormField>
        
        <div className="grid grid-cols-2 gap-4">
          <FormField name="domain" label="Domain" required>
            <Select {...form.register('domain')}>
              <option value="">Select domain...</option>
              <option value="analytics">Analytics</option>
              <option value="finance">Finance</option>
              <option value="crm">CRM</option>
              <option value="operations">Operations</option>
              <option value="marketing">Marketing</option>
            </Select>
          </FormField>
          
          <FormField name="ownerTeamId" label="Owner Team" required>
            <Select {...form.register('ownerTeamId')}>
              <option value="">Select team...</option>
              {/* Teams loaded from API */}
            </Select>
          </FormField>
        </div>
        
        <FormField name="tags" label="Tags">
          <TagInput
            value={form.watch('tags')}
            onChange={(tags) => form.setValue('tags', tags)}
            suggestions={['pii', 'ml-ready', 'real-time', 'batch', 'core']}
          />
        </FormField>
      </div>
      
      {/* SLAs */}
      <div className="space-y-4">
        <h3 className="text-sm font-medium text-text-primary">
          Service Level Agreements
        </h3>
        <p className="text-sm text-text-tertiary">
          These SLAs will be inherited by all contracts using this asset
        </p>
        
        <div className="grid grid-cols-2 gap-4">
          <FormField 
            name="sla.freshnessHours" 
            label="Data Freshness"
            description="Data should be updated within this many hours"
          >
            <div className="flex items-center gap-2">
              <Input 
                type="number"
                {...form.register('sla.freshnessHours', { valueAsNumber: true })}
                className="w-24"
              />
              <span className="text-sm text-text-secondary">hours</span>
            </div>
          </FormField>
          
          <FormField 
            name="sla.availabilityPercent" 
            label="Availability Target"
            description="Expected uptime percentage"
          >
            <div className="flex items-center gap-2">
              <Input 
                type="number"
                step="0.1"
                {...form.register('sla.availabilityPercent', { valueAsNumber: true })}
                className="w-24"
              />
              <span className="text-sm text-text-secondary">%</span>
            </div>
          </FormField>
        </div>
      </div>
      
      {/* Navigation */}
      <div className="flex justify-between pt-6 border-t border-border-default">
        <Button type="button" variant="secondary" onClick={onBack}>
          Back
        </Button>
        <Button type="submit">
          Next: Review
        </Button>
      </div>
    </form>
  )
}
```

#### Step 4: Review & Save

**File**: `src/components/assets/wizard/Step4Review.tsx`

```tsx
'use client'

import { useMutation } from '@tanstack/react-query'
import { Check, AlertCircle } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/layout/Card'
import { Badge } from '@/components/ui/Badge'
import { SchemaPreview } from '@/components/schema/SchemaPreview'

export function Step4Review({ data, onBack, onSaveDraft, onPublish }: Step4Props) {
  const createMutation = useMutation({
    mutationFn: (status: 'draft' | 'active') => createAsset({ ...data, status }),
    onSuccess: (asset) => {
      toast.success(
        'Asset created',
        `${asset.name} has been created successfully`
      )
      router.push(`/studio/assets/${asset.id}`)
    },
    onError: (error) => {
      toast.error('Failed to create asset', error.message)
    },
  })
  
  // Validation checks
  const validations = [
    { 
      label: 'Connection verified', 
      passed: data.connection?.lastTestStatus === 'success' 
    },
    { 
      label: 'Tables selected', 
      passed: data.selectedTables?.length > 0 
    },
    { 
      label: 'Metadata complete', 
      passed: !!data.name && !!data.description && !!data.domain 
    },
    { 
      label: 'SLAs configured', 
      passed: !!data.sla?.freshnessHours 
    },
  ]
  
  const allPassed = validations.every(v => v.passed)
  
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-medium text-text-primary">
          Step 4: Review & Save
        </h2>
        <p className="text-sm text-text-secondary mt-1">
          Review your asset configuration before saving
        </p>
      </div>
      
      {/* Validation Results */}
      <Card className="p-4">
        <h3 className="text-sm font-medium text-text-primary mb-3">
          Validation
        </h3>
        <div className="space-y-2">
          {validations.map((validation, i) => (
            <div key={i} className="flex items-center gap-2">
              {validation.passed ? (
                <Check className="w-4 h-4 text-green-500" />
              ) : (
                <AlertCircle className="w-4 h-4 text-yellow-500" />
              )}
              <span className={cn(
                "text-sm",
                validation.passed ? "text-text-primary" : "text-text-secondary"
              )}>
                {validation.label}
              </span>
            </div>
          ))}
        </div>
      </Card>
      
      {/* Asset Summary */}
      <Card className="p-4 space-y-4">
        <h3 className="text-sm font-medium text-text-primary">Asset Summary</h3>
        
        <div className="grid grid-cols-2 gap-4">
          <div>
            <div className="text-xs text-text-tertiary uppercase">Name</div>
            <div className="text-sm text-text-primary font-medium">{data.name}</div>
          </div>
          <div>
            <div className="text-xs text-text-tertiary uppercase">Domain</div>
            <div className="text-sm text-text-primary">{data.domain}</div>
          </div>
          <div>
            <div className="text-xs text-text-tertiary uppercase">Connection</div>
            <div className="text-sm text-text-primary">{data.connection?.name}</div>
          </div>
          <div>
            <div className="text-xs text-text-tertiary uppercase">Tables</div>
            <div className="text-sm text-text-primary">
              {data.selectedTables?.length} tables
            </div>
          </div>
        </div>
        
        <div>
          <div className="text-xs text-text-tertiary uppercase mb-1">SLAs</div>
          <div className="flex gap-2">
            <Badge>Freshness: {data.sla?.freshnessHours}h</Badge>
            <Badge>Availability: {data.sla?.availabilityPercent}%</Badge>
          </div>
        </div>
      </Card>
      
      {/* Schema Preview */}
      <Card className="p-4">
        <h3 className="text-sm font-medium text-text-primary mb-3">
          Schema Preview
        </h3>
        <SchemaPreview tables={data.selectedTables} maxHeight={300} />
      </Card>
      
      {/* Navigation */}
      <div className="flex justify-between pt-6 border-t border-border-default">
        <Button variant="secondary" onClick={onBack}>
          Back
        </Button>
        <div className="flex gap-3">
          <Button
            variant="secondary"
            onClick={() => createMutation.mutate('draft')}
            loading={createMutation.isPending && createMutation.variables === 'draft'}
          >
            Save as Draft
          </Button>
          <Button
            onClick={() => createMutation.mutate('active')}
            disabled={!allPassed}
            loading={createMutation.isPending && createMutation.variables === 'active'}
          >
            Publish Asset
          </Button>
        </div>
      </div>
    </div>
  )
}
```

---

### A1-07 to A1-08: Connection Form by Database Type

**File**: `src/components/connections/ConnectionForm.tsx`

```tsx
'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation } from '@tanstack/react-query'
import { DatabaseTypeSelector } from './DatabaseTypeSelector'
import { SnowflakeForm } from './forms/SnowflakeForm'
import { BigQueryForm } from './forms/BigQueryForm'
import { DatabricksForm } from './forms/DatabricksForm'
import { PostgresForm } from './forms/PostgresForm'

const databaseTypes = [
  { id: 'snowflake', name: 'Snowflake', icon: '❄️' },
  { id: 'bigquery', name: 'BigQuery', icon: '🔷' },
  { id: 'databricks', name: 'Databricks', icon: '🧱' },
  { id: 'postgres', name: 'PostgreSQL', icon: '🐘' },
  { id: 'redshift', name: 'Redshift', icon: '🔶' },
]

export function ConnectionForm({ onSuccess, onCancel }: ConnectionFormProps) {
  const [selectedType, setSelectedType] = useState<string | null>(null)
  const [testStatus, setTestStatus] = useState<'idle' | 'testing' | 'success' | 'error'>('idle')
  
  const createMutation = useMutation({
    mutationFn: createConnection,
    onSuccess: (connection) => {
      onSuccess(connection)
    },
  })
  
  const testMutation = useMutation({
    mutationFn: testConnection,
    onSuccess: () => setTestStatus('success'),
    onError: () => setTestStatus('error'),
  })
  
  const renderForm = () => {
    switch (selectedType) {
      case 'snowflake':
        return <SnowflakeForm onSubmit={handleSubmit} onTest={handleTest} />
      case 'bigquery':
        return <BigQueryForm onSubmit={handleSubmit} onTest={handleTest} />
      case 'databricks':
        return <DatabricksForm onSubmit={handleSubmit} onTest={handleTest} />
      case 'postgres':
        return <PostgresForm onSubmit={handleSubmit} onTest={handleTest} />
      default:
        return null
    }
  }
  
  if (!selectedType) {
    return (
      <div className="space-y-4">
        <h4 className="text-sm font-medium text-text-primary">
          Select Database Type
        </h4>
        <div className="grid grid-cols-5 gap-3">
          {databaseTypes.map(type => (
            <button
              key={type.id}
              onClick={() => setSelectedType(type.id)}
              className={cn(
                "p-4 rounded-lg border-2 text-center transition-all",
                "hover:border-primary-300 hover:shadow-sm",
                "border-border-default"
              )}
            >
              <span className="text-2xl block mb-1">{type.icon}</span>
              <span className="text-xs text-text-secondary">{type.name}</span>
            </button>
          ))}
        </div>
      </div>
    )
  }
  
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <button
          onClick={() => setSelectedType(null)}
          className="text-sm text-text-link hover:underline"
        >
          ← Change database type
        </button>
        <Badge>{databaseTypes.find(t => t.id === selectedType)?.name}</Badge>
      </div>
      
      {renderForm()}
      
      <div className="flex justify-end gap-3 pt-4 border-t border-border-default">
        <Button variant="secondary" onClick={onCancel}>
          Cancel
        </Button>
        <Button
          variant="secondary"
          onClick={() => testMutation.mutate(formData)}
          loading={testMutation.isPending}
        >
          Test Connection
        </Button>
        <Button
          onClick={() => createMutation.mutate(formData)}
          disabled={testStatus !== 'success'}
          loading={createMutation.isPending}
        >
          Save Connection
        </Button>
      </div>
    </div>
  )
}
```

---

### A1-11: Table Preview Modal

**File**: `src/components/database-browser/TablePreviewModal.tsx`

```tsx
'use client'

import { useQuery } from '@tanstack/react-query'
import { Modal } from '@/components/feedback/Modal'
import { DataTable } from '@/components/data-display/DataTable'
import { Skeleton } from '@/components/ui/Skeleton'

interface TablePreviewModalProps {
  open: boolean
  onClose: () => void
  connectionId: string
  tableId: string | null
}

export function TablePreviewModal({ 
  open, 
  onClose, 
  connectionId, 
  tableId 
}: TablePreviewModalProps) {
  const { data, isLoading } = useQuery({
    queryKey: ['table-preview', connectionId, tableId],
    queryFn: () => fetchTablePreview(connectionId, tableId!),
    enabled: !!tableId,
  })
  
  return (
    <Modal
      open={open}
      onClose={onClose}
      title={`Table Preview: ${tableId?.split('.').pop()}`}
      size="xl"
    >
      {isLoading ? (
        <div className="space-y-4">
          <div className="space-y-2">
            {Array.from({ length: 5 }).map((_, i) => (
              <Skeleton key={i} className="h-8 w-full" />
            ))}
          </div>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Table Info */}
          <div className="grid grid-cols-4 gap-4">
            <div>
              <div className="text-xs text-text-tertiary">Rows</div>
              <div className="text-lg font-semibold">{formatNumber(data?.rowCount)}</div>
            </div>
            <div>
              <div className="text-xs text-text-tertiary">Columns</div>
              <div className="text-lg font-semibold">{data?.columns.length}</div>
            </div>
            <div>
              <div className="text-xs text-text-tertiary">Size</div>
              <div className="text-lg font-semibold">{formatBytes(data?.sizeBytes)}</div>
            </div>
            <div>
              <div className="text-xs text-text-tertiary">Last Updated</div>
              <div className="text-lg font-semibold">{formatRelativeTime(data?.lastUpdated)}</div>
            </div>
          </div>
          
          {/* Schema */}
          <div>
            <h4 className="text-sm font-medium text-text-primary mb-2">
              Schema ({data?.columns.length} columns)
            </h4>
            <div className="border border-border-default rounded-lg overflow-hidden max-h-[200px] overflow-y-auto">
              <table className="w-full text-sm">
                <thead className="bg-bg-tertiary sticky top-0">
                  <tr>
                    <th className="px-3 py-2 text-left text-xs font-medium text-text-secondary">Column</th>
                    <th className="px-3 py-2 text-left text-xs font-medium text-text-secondary">Type</th>
                    <th className="px-3 py-2 text-left text-xs font-medium text-text-secondary">Nullable</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border-default">
                  {data?.columns.map(col => (
                    <tr key={col.name}>
                      <td className="px-3 py-2 font-mono text-text-primary">{col.name}</td>
                      <td className="px-3 py-2 text-text-secondary">{col.type}</td>
                      <td className="px-3 py-2 text-text-secondary">{col.nullable ? 'Yes' : 'No'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
          
          {/* Sample Data */}
          <div>
            <h4 className="text-sm font-medium text-text-primary mb-2">
              Sample Data (5 rows)
            </h4>
            <div className="border border-border-default rounded-lg overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-bg-tertiary">
                  <tr>
                    {data?.columns.slice(0, 6).map(col => (
                      <th key={col.name} className="px-3 py-2 text-left text-xs font-medium text-text-secondary whitespace-nowrap">
                        {col.name}
                      </th>
                    ))}
                    {data?.columns.length > 6 && (
                      <th className="px-3 py-2 text-xs text-text-tertiary">
                        +{data.columns.length - 6} more
                      </th>
                    )}
                  </tr>
                </thead>
                <tbody className="divide-y divide-border-default">
                  {data?.sampleData.map((row, i) => (
                    <tr key={i}>
                      {data.columns.slice(0, 6).map(col => (
                        <td key={col.name} className="px-3 py-2 text-text-primary whitespace-nowrap max-w-[200px] truncate">
                          {row[col.name]}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </Modal>
  )
}
```

---

### A1-15: Mock Data

**File**: `src/lib/mocks/data/assets.ts`

```typescript
import { faker } from '@faker-js/faker'

export const mockConnections: Connection[] = [
  {
    id: 'conn-1',
    name: 'Production Snowflake',
    type: 'snowflake',
    status: 'active',
    config: {
      account: 'acme-prod.snowflakecomputing.com',
      warehouse: 'COMPUTE_WH',
      database: 'ANALYTICS_DB',
    },
    lastTestedAt: new Date().toISOString(),
    lastTestStatus: 'success',
  },
  {
    id: 'conn-2',
    name: 'Analytics BigQuery',
    type: 'bigquery',
    status: 'active',
    config: {
      projectId: 'acme-analytics-prod',
      dataset: 'analytics',
    },
    lastTestedAt: new Date(Date.now() - 86400000).toISOString(),
    lastTestStatus: 'success',
  },
]

export const mockAssets: DataAsset[] = [
  {
    id: 'asset-1',
    name: 'Customer 360',
    description: 'Comprehensive customer data including profiles, addresses, and preferences for analytics and CRM applications.',
    domain: 'crm',
    status: 'active',
    connectionId: 'conn-1',
    ownerTeamId: 'team-1',
    tags: ['customer', 'pii', 'core'],
    tables: [
      {
        id: 'tbl-1',
        name: 'customers',
        physicalName: 'ANALYTICS_DB.CUSTOMER.customers',
        description: 'Core customer profile data',
        fields: [
          { name: 'customer_id', type: 'VARCHAR', isPrimaryKey: true, isNullable: false },
          { name: 'email', type: 'VARCHAR', isPrimaryKey: false, isNullable: false, piiType: 'email' },
          { name: 'first_name', type: 'VARCHAR', isPrimaryKey: false, isNullable: true, piiType: 'name' },
          { name: 'last_name', type: 'VARCHAR', isPrimaryKey: false, isNullable: true, piiType: 'name' },
          { name: 'created_at', type: 'TIMESTAMP', isPrimaryKey: false, isNullable: false },
        ],
        rowCount: 1234567,
      },
      {
        id: 'tbl-2',
        name: 'addresses',
        physicalName: 'ANALYTICS_DB.CUSTOMER.addresses',
        description: 'Customer address information',
        fields: [
          { name: 'address_id', type: 'VARCHAR', isPrimaryKey: true, isNullable: false },
          { name: 'customer_id', type: 'VARCHAR', isPrimaryKey: false, isNullable: false },
          { name: 'street', type: 'VARCHAR', isPrimaryKey: false, isNullable: true, piiType: 'address' },
          { name: 'city', type: 'VARCHAR', isPrimaryKey: false, isNullable: true },
          { name: 'country', type: 'VARCHAR', isPrimaryKey: false, isNullable: true },
        ],
        rowCount: 2456789,
      },
    ],
    sla: {
      freshnessHours: 24,
      availabilityPercent: 99.5,
    },
    createdAt: '2024-01-05T10:30:00Z',
    updatedAt: '2025-01-10T15:45:00Z',
    lastSyncedAt: '2025-01-13T02:00:00Z',
  },
  // Add more mock assets...
]
```

---

## Performance Optimization Guidelines

### 1. Route Prefetching
```tsx
// Prefetch asset detail on list page load
useEffect(() => {
  assets.slice(0, 5).forEach(asset => {
    router.prefetch(`/studio/assets/${asset.id}`)
  })
}, [assets])
```

### 2. Optimistic Updates
```tsx
// When syncing schema, show optimistic update
const syncMutation = useMutation({
  mutationFn: syncAssetSchema,
  onMutate: async (assetId) => {
    // Cancel outgoing queries
    await queryClient.cancelQueries(['asset', assetId])
    
    // Snapshot current state
    const previous = queryClient.getQueryData(['asset', assetId])
    
    // Optimistically update
    queryClient.setQueryData(['asset', assetId], old => ({
      ...old,
      lastSyncedAt: new Date().toISOString(),
    }))
    
    return { previous }
  },
  onError: (err, assetId, context) => {
    // Rollback on error
    queryClient.setQueryData(['asset', assetId], context.previous)
  },
})
```

### 3. Virtualization for Large Lists
```tsx
// Use virtual list for database browser with many tables
import { useVirtualizer } from '@tanstack/react-virtual'

const virtualizer = useVirtualizer({
  count: tables.length,
  getScrollElement: () => scrollRef.current,
  estimateSize: () => 44,
})
```

---

## Exit Criteria Checklist

- [ ] Asset list loads instantly with skeleton
- [ ] Search debounces and shows loading indicator
- [ ] Filters sync with URL
- [ ] Row hover prefetches asset detail
- [ ] Asset detail page renders all sections
- [ ] Schema viewer expands/collapses smoothly
- [ ] Create wizard guides user through all 4 steps
- [ ] Database browser shows tree structure
- [ ] Table preview modal loads schema and sample data
- [ ] Connection test shows real-time status
- [ ] Unsaved changes modal appears when navigating away
- [ ] All mock data is realistic and comprehensive
- [ ] No layout shift during loading
- [ ] All interactions feel instant (< 100ms feedback)