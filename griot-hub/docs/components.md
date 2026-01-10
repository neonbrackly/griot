# Component Reference

Reusable React components in Griot Hub.

---

## ContractCard

Displays a contract summary in a card format.

**File:** `components/ContractCard.tsx`

### Props

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `contract` | `Contract` | Yes | Contract data to display |
| `onClick` | `() => void` | No | Click handler |

### Usage

```tsx
import ContractCard from '@/components/ContractCard';

<ContractCard
  contract={contract}
  onClick={() => router.push(`/contracts/${contract.id}`)}
/>
```

### Display Elements

- Contract name
- Description (truncated to 2 lines)
- Version badge
- Status badge (draft/active/deprecated)
- Field count
- Last updated timestamp

### Example

```tsx
// In a contract list
{contracts.map((contract) => (
  <ContractCard
    key={contract.id}
    contract={contract}
    onClick={() => setSelectedContract(contract)}
  />
))}
```

---

## FieldEditor

Form component for editing field definitions.

**File:** `components/FieldEditor.tsx`

### Props

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `field` | `FieldDefinition` | Yes | Field to edit |
| `onChange` | `(field: FieldDefinition) => void` | Yes | Change handler |
| `onDelete` | `() => void` | Yes | Delete handler |

### Usage

```tsx
import FieldEditor from '@/components/FieldEditor';

<FieldEditor
  field={field}
  onChange={(updated) => updateField(index, updated)}
  onDelete={() => removeField(index)}
/>
```

### Features

- Field name input
- Type selector (string, integer, float, boolean, date, datetime, array, object)
- Description textarea
- Nullable toggle
- Primary key toggle
- Unique toggle
- Constraint editing (via ConstraintEditor)
- Metadata editing (unit, aggregation, glossary term)

### Example

```tsx
// In the Contract Studio
{fields.map((field, index) => (
  <FieldEditor
    key={field.name}
    field={field}
    onChange={(updated) => {
      const newFields = [...fields];
      newFields[index] = updated;
      setFields(newFields);
    }}
    onDelete={() => {
      setFields(fields.filter((_, i) => i !== index));
    }}
  />
))}
```

---

## ConstraintEditor

Dynamic constraint editor that changes based on field type.

**File:** `components/ConstraintEditor.tsx`

### Props

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `fieldType` | `FieldType` | Yes | Type of the field |
| `constraints` | `FieldConstraints` | Yes | Current constraints |
| `onChange` | `(constraints: FieldConstraints) => void` | Yes | Change handler |

### Usage

```tsx
import ConstraintEditor from '@/components/ConstraintEditor';

<ConstraintEditor
  fieldType={field.type}
  constraints={field.constraints || {}}
  onChange={(constraints) => onChange({ ...field, constraints })}
/>
```

### Constraints by Type

**String:**
- `min_length` - Minimum string length
- `max_length` - Maximum string length
- `pattern` - Regex pattern
- `format` - Predefined format (email, uri, uuid, etc.)
- `enum` - Allowed values

**Integer/Float:**
- `ge` - Greater than or equal
- `le` - Less than or equal
- `gt` - Greater than
- `lt` - Less than
- `multiple_of` - Must be multiple of value

**Date/Datetime:**
- Format selection (ISO 8601, custom)

---

## ValidationBadge

Badge component showing validation pass/fail status.

**File:** `components/ValidationBadge.tsx`

### Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `passed` | `boolean` | Yes | - | Whether validation passed |
| `errorRate` | `number` | No | - | Error rate (0-1) |
| `size` | `'sm' \| 'md' \| 'lg'` | No | `'md'` | Badge size |

### Usage

```tsx
import ValidationBadge from '@/components/ValidationBadge';

// Simple pass/fail
<ValidationBadge passed={true} />

// With error rate
<ValidationBadge passed={false} errorRate={0.05} />

// Different sizes
<ValidationBadge passed={true} size="sm" />
<ValidationBadge passed={true} size="lg" />
```

### Appearance

| State | Color | Text |
|-------|-------|------|
| Passed | Green | "Passed" |
| Failed | Red | "Failed" or error rate % |

---

## YamlPreview

Syntax-highlighted YAML preview with copy functionality.

**File:** `components/YamlPreview.tsx`

### Props

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `content` | `string` | Yes | YAML content to display |
| `onCopy` | `() => void` | No | Copy button click handler |

### Usage

```tsx
import YamlPreview from '@/components/YamlPreview';

<YamlPreview
  content={yamlString}
  onCopy={() => navigator.clipboard.writeText(yamlString)}
/>
```

### Features

- Syntax highlighting for YAML
- Line numbers
- Copy to clipboard button
- Scrollable container for long content

---

## ErrorTrendChart

Line chart showing validation error trends over time.

**File:** `components/ErrorTrendChart.tsx`

### Props

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `data` | `ValidationRecord[]` | Yes | Validation history data |
| `contractId` | `string` | No | Filter to specific contract |

### Usage

```tsx
import ErrorTrendChart from '@/components/ErrorTrendChart';

<ErrorTrendChart
  data={validations}
  contractId="user-events"
/>
```

### Display

- X-axis: Date
- Y-axis: Error rate (%)
- Color coding based on error severity
- Tooltip with details on hover

---

## Common Patterns

### Loading States

All components that fetch data should handle loading:

```tsx
function MyComponent() {
  const [loading, setLoading] = useState(true);

  if (loading) {
    return <div className="animate-pulse bg-gray-200 h-32 rounded" />;
  }

  return <div>{/* content */}</div>;
}
```

### Error States

Display errors gracefully:

```tsx
{error && (
  <div className="bg-error-50 border border-error-500 text-error-700 p-4 rounded">
    {error}
  </div>
)}
```

### Empty States

Handle empty data:

```tsx
{contracts.length === 0 ? (
  <div className="text-gray-500 text-center py-8">
    No contracts found. Create your first contract to get started.
  </div>
) : (
  contracts.map(c => <ContractCard key={c.id} contract={c} />)
)}
```

---

## Styling Components

All components use Tailwind CSS classes:

```tsx
// Use consistent card styling
<div className="card">
  {/* Uses .card class from globals.css */}
</div>

// Use consistent button styling
<button className="btn btn-primary">
  Save
</button>

// Color semantics
<span className="text-success-600">Passed</span>
<span className="text-error-600">Failed</span>
<span className="text-warning-600">Warning</span>
```

---

## Creating New Components

When adding new components:

1. Create in `src/components/`
2. Use TypeScript with explicit props interface
3. Export as default
4. Add JSDoc comments for props
5. Follow existing naming conventions

```tsx
// components/MyComponent.tsx

interface MyComponentProps {
  /** The data to display */
  data: SomeType;
  /** Optional click handler */
  onClick?: () => void;
}

/**
 * MyComponent - Brief description
 *
 * Longer description of what this component does.
 */
export default function MyComponent({ data, onClick }: MyComponentProps) {
  return (
    <div className="...">
      {/* implementation */}
    </div>
  );
}
```

---

## Next Steps

- [Pages](./pages.md) - How pages use these components
- [API Client](./api-client.md) - Fetching data for components
