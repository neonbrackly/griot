# griot-registry API Reference

FastAPI server for contract management.

## Deployment

### Docker

```bash
docker run -p 8000:8000 griot/registry:latest
```

### From Source

```bash
pip install griot-registry
uvicorn griot_registry.server:app --host 0.0.0.0 --port 8000
```

## Configuration

Environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `GRIOT_STORAGE_BACKEND` | Storage backend | `filesystem` |
| `GRIOT_STORAGE_PATH` | Filesystem storage path | `./contracts` |
| `GRIOT_DATABASE_URL` | PostgreSQL connection URL | - |
| `GRIOT_GIT_REPO_URL` | Git repository URL | - |
| `GRIOT_AUTH_ENABLED` | Enable authentication | `false` |
| `GRIOT_API_KEYS` | Comma-separated API keys | - |
| `GRIOT_OIDC_ISSUER` | OIDC issuer URL | - |

## API Endpoints

### Health

```http
GET /health
```

Returns server health status.

**Response:**
```json
{
  "status": "healthy",
  "storage": "connected",
  "version": "0.1.0"
}
```

---

### Create Contract

```http
POST /contracts
```

Create a new contract.

**Request Body:**
```json
{
  "name": "customer",
  "description": "Customer data contract",
  "fields": {
    "customer_id": {
      "type": "string",
      "description": "Unique identifier",
      "primary_key": true
    }
  }
}
```

**Response:**
```json
{
  "name": "customer",
  "version": "1.0.0",
  "created_at": "2025-01-10T12:00:00Z"
}
```

---

### Get Contract

```http
GET /contracts/{name}
```

Get the latest version of a contract.

**Parameters:**
- `name` - Contract name

**Response:**
```json
{
  "name": "customer",
  "version": "1.0.0",
  "description": "Customer data contract",
  "fields": { ... }
}
```

---

### List Versions

```http
GET /contracts/{name}/versions
```

List all versions of a contract.

**Response:**
```json
{
  "contract": "customer",
  "versions": [
    {"version": "1.0.0", "created_at": "2025-01-01T00:00:00Z"},
    {"version": "1.1.0", "created_at": "2025-01-10T00:00:00Z"}
  ]
}
```

---

### Get Specific Version

```http
GET /contracts/{name}/versions/{version}
```

Get a specific version of a contract.

---

### Update Contract

```http
PUT /contracts/{name}
```

Update a contract (creates new version).

---

### Deprecate Contract

```http
DELETE /contracts/{name}
```

Mark a contract as deprecated.

---

### Validate Data

```http
POST /contracts/{name}/validate
```

Validate data against a contract.

**Request Body:**
```json
{
  "data": [
    {"customer_id": "CUST-001", "email": "test@example.com"}
  ]
}
```

**Response:**
```json
{
  "passed": true,
  "row_count": 1,
  "error_count": 0,
  "errors": []
}
```

---

### Diff Contracts

```http
POST /contracts/{name}/diff
```

Compare two versions of a contract.

**Request Body:**
```json
{
  "base_version": "1.0.0",
  "target_version": "1.1.0"
}
```

---

### Search Contracts

```http
GET /contracts/search?q={query}
```

Search contracts by name or description.

---

### Validation History

```http
GET /contracts/{name}/validations
```

Get validation history for a contract.

---

### Record Validation

```http
POST /contracts/{name}/validations
```

Record a validation result.

---

### Approval Chain

```http
POST /contracts/{name}/approvals
```

Create an approval request.

```http
GET /contracts/{name}/approvals/{id}
```

Get approval status.

```http
POST /contracts/{name}/approvals/{id}/decide
```

Approve or reject a request.

---

### Generate Reports

```http
GET /contracts/{name}/reports/analytics
GET /contracts/{name}/reports/ai-readiness
GET /contracts/{name}/reports/audit
```

Generate reports for a contract.

## Storage Backends

### Filesystem

```python
GRIOT_STORAGE_BACKEND=filesystem
GRIOT_STORAGE_PATH=/var/lib/griot/contracts
```

### Git

```python
GRIOT_STORAGE_BACKEND=git
GRIOT_GIT_REPO_URL=https://github.com/org/contracts.git
GRIOT_GIT_BRANCH=main
```

### PostgreSQL

```python
GRIOT_STORAGE_BACKEND=postgres
GRIOT_DATABASE_URL=postgresql://user:pass@host/griot
```

## Authentication

### API Key

```python
GRIOT_AUTH_ENABLED=true
GRIOT_API_KEYS=key1,key2,key3
```

```bash
curl -H "X-API-Key: key1" https://registry.example.com/contracts
```

### OAuth2/OIDC

```python
GRIOT_AUTH_ENABLED=true
GRIOT_OIDC_ISSUER=https://auth.example.com
GRIOT_OIDC_AUDIENCE=griot-registry
```

```bash
curl -H "Authorization: Bearer $TOKEN" https://registry.example.com/contracts
```

## Python Client

```python
from griot_registry.client import RegistryClient

client = RegistryClient(
    url="https://registry.example.com",
    api_key="your-key",
)

# Get contract
contract = client.get_contract("customer")

# Create contract
client.create_contract(contract_data)

# Validate data
result = client.validate("customer", data)
```
