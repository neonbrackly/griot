# REQ-registry-020: Manual Schema Management API (Standalone Schemas)

## Request: Schema CRUD Endpoints Independent of Database Connections
**From:** contracts
**To:** registry
**Priority:** High
**Blocking:** Yes

---

## Summary

The Contract Creation Wizard has been refactored to **no longer allow inline schema creation**. Users must now create schemas in the **Data Assets** section first, then select them when creating a contract.

This requires the **Registry** to implement **standalone schema management** - schemas that exist independently of database connections.

**Current State:** The Registry currently only supports schemas discovered through database connections (via `/connections` endpoints). There's no way to manually create a schema definition.

**Required:** API endpoints to create, read, update, and delete schemas as first-class entities, independent of database connections.

---

## Context: Why This Is Needed

### Current Workflow (Database-Driven)
1. User creates a database connection via POST /connections
2. Registry introspects the database and discovers schemas
3. Schemas are tied to the connection

### New Required Workflow (Manual Schema Creation)
1. User manually defines a schema in Data Assets UI
2. Schema is stored as a standalone entity (no database required)
3. User selects this schema when creating a contract
4. This enables:
   - Schema definitions for APIs, files, streams (not just databases)
   - Pre-planning schemas before data infrastructure exists
   - Schema templates and reusable patterns

---

## Required API Endpoints

### 1. GET /schemas - List All Schemas

**URL:** `GET /api/v1/schemas`

**Description:** Returns all schemas (both connection-derived and manually created).

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `search` | string | - | Search by schema name, asset name, or domain |
| `domain` | string | - | Filter by domain (analytics, finance, crm, etc.) |
| `source` | string | - | Filter by source: `manual`, `connection`, or `all` |
| `limit` | integer | 50 | Max results per page |
| `offset` | integer | 0 | Pagination offset |

**Response (200 OK):**

```json
{
  "items": [
    {
      "id": "schema-001",
      "name": "Customer Analytics Schema",
      "description": "Schema for customer analytics data mart",
      "source": "manual",
      "connectionId": null,
      "domain": "analytics",
      "tables": [
        {
          "name": "customers",
          "physicalName": "dim_customers",
          "description": "Customer dimension table",
          "fields": [
            {
              "name": "customer_id",
              "logicalType": "string",
              "physicalType": "VARCHAR(50)",
              "description": "Unique customer identifier",
              "required": true,
              "unique": true,
              "primaryKey": true,
              "piiClassification": null
            },
            {
              "name": "email",
              "logicalType": "string",
              "physicalType": "VARCHAR(255)",
              "description": "Customer email address",
              "required": true,
              "unique": true,
              "primaryKey": false,
              "piiClassification": "email"
            }
          ]
        }
      ],
      "tableCount": 1,
      "fieldCount": 2,
      "createdAt": "2026-01-10T09:00:00Z",
      "updatedAt": "2026-01-15T14:30:00Z",
      "createdBy": "user-001"
    }
  ],
  "total": 47,
  "limit": 50,
  "offset": 0
}
```

---

### 2. POST /schemas - Create Manual Schema

**URL:** `POST /api/v1/schemas`

**Description:** Creates a new manually-defined schema.

**Request Body:**

```json
{
  "name": "Customer Analytics Schema",
  "description": "Schema for customer analytics data mart",
  "domain": "analytics",
  "tables": [
    {
      "name": "customers",
      "physicalName": "dim_customers",
      "description": "Customer dimension table",
      "fields": [
        {
          "name": "customer_id",
          "logicalType": "string",
          "physicalType": "VARCHAR(50)",
          "description": "Unique customer identifier",
          "required": true,
          "unique": true,
          "primaryKey": true,
          "piiClassification": null
        },
        {
          "name": "email",
          "logicalType": "string",
          "physicalType": "VARCHAR(255)",
          "description": "Customer email address",
          "required": true,
          "unique": true,
          "primaryKey": false,
          "piiClassification": "email"
        }
      ]
    }
  ]
}
```

**Response (201 Created):**

```json
{
  "id": "schema-001",
  "name": "Customer Analytics Schema",
  "description": "Schema for customer analytics data mart",
  "source": "manual",
  "connectionId": null,
  "domain": "analytics",
  "tables": [...],
  "tableCount": 1,
  "fieldCount": 2,
  "createdAt": "2026-01-20T10:00:00Z",
  "updatedAt": "2026-01-20T10:00:00Z",
  "createdBy": "user-001"
}
```

---

### 3. GET /schemas/{id} - Get Schema Details

**URL:** `GET /api/v1/schemas/{id}`

**Response (200 OK):** Same as item in list response.

---

### 4. PUT /schemas/{id} - Update Schema

**URL:** `PUT /api/v1/schemas/{id}`

**Note:** Only manually-created schemas can be edited. Connection-derived schemas are read-only (refresh via connection sync).

**Request Body:** Same as POST /schemas

**Response (200 OK):** Updated schema object

---

### 5. DELETE /schemas/{id} - Delete Schema

**URL:** `DELETE /api/v1/schemas/{id}`

**Note:** Cannot delete schemas that are in use by contracts. Return 409 Conflict with list of dependent contracts.

**Response (204 No Content):** Success

**Response (409 Conflict):**
```json
{
  "error": "SCHEMA_IN_USE",
  "message": "Cannot delete schema. It is used by 3 contracts.",
  "dependentContracts": [
    { "id": "contract-001", "name": "Customer Data Contract" },
    { "id": "contract-002", "name": "Sales Analytics Contract" }
  ]
}
```

---

## Schema Field Properties

Each field in a schema table must support:

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `name` | string | Yes | Field name |
| `logicalType` | string | Yes | Logical type (string, integer, number, boolean, date, datetime, timestamp, array, object, binary, uuid) |
| `physicalType` | string | No | Physical database type (VARCHAR, INT, etc.) |
| `description` | string | No | Field description |
| `required` | boolean | Yes | Whether field is nullable |
| `unique` | boolean | Yes | Whether field values must be unique |
| `primaryKey` | boolean | Yes | Whether field is part of primary key |
| `piiClassification` | string | No | PII category (email, name, phone, address, ssn, financial, health, other) |

---

## Domain Values

Suggested domain enum values:
- `analytics`
- `finance`
- `sales`
- `marketing`
- `crm`
- `hr`
- `operations`
- `product`
- `engineering`
- `other`

---

## Files Changed in Contracts Agent

The contracts wizard now calls `GET /schemas` in Step 2 to fetch available schemas:

### `src/components/contracts/wizard/Step2Asset.tsx`
```typescript
// Fetch schemas from Registry
const { data: schemasData, isLoading, error } = useQuery({
  queryKey: queryKeys.assets?.schemas ?? ['assets', 'schemas'],
  queryFn: async () => {
    const response = await api.get<{ items: AssetSchema[] } | AssetSchema[]>('/schemas')
    if (Array.isArray(response)) {
      return response
    }
    return response.items || []
  },
})
```

---

## Migration Considerations

1. **Existing Contracts:** Contracts created before this change may have inline schemas. These should continue to work, but new contracts must select from the schema repository.

2. **Connection-Derived Schemas:** Schemas discovered via database connections should appear in the same list but marked as `source: "connection"` and be read-only.

3. **Schema Versioning:** Consider adding version support for schemas to track changes over time.

---

## Impact

| Component | Impact |
|-----------|--------|
| Contract Wizard Step 2 | Calls GET /schemas |
| Contract Wizard Step 3 | Displays read-only schema |
| Data Assets UI (Schema Agent) | Calls POST/PUT/DELETE /schemas |
| Contract Creation | Requires schema selection |

---

## Related Requests

- **REQ-schema-001**: Request to Schema Agent for frontend UI to manage schemas
- This request provides the backend API that the Schema Agent UI will consume

---

## Deadline

**Priority:** High - This blocks the contract creation wizard. The wizard currently shows "No schemas available" until this is implemented.

---

## Contact

Questions about:
- Expected schema format: See response examples above
- UI integration: Check `Step2Asset.tsx` in contracts agent
- Contract workflow: The wizard requires schema selection before proceeding
