# Griot Registry

Central registry API for managing Griot data contracts. Provides storage, versioning, validation history, and search capabilities for ODCS-compliant data contracts.

## Features

- **Contract Management**: Full CRUD operations with semantic versioning
- **MongoDB Storage**: Scalable document storage with full-text search
- **Schema Catalog**: Cross-contract schema discovery and querying
- **Validation History**: Track validation results over time
- **Pipeline Integration**: Run tracking for data pipeline executions
- **Collaboration**: Comments, issues, and approval workflows
- **Authentication**: JWT token authentication with role-based access
- **Python Client**: Async and sync clients for easy integration

## Installation

```bash
pip install griot-registry
```

## Quick Start

### 1. Start MongoDB

```bash
# Using Docker
docker run -d --name mongodb -p 27017:27017 mongo:7

# Or use an existing MongoDB instance
```

### 2. Configure Environment

```bash
# Required
export MONGODB_URI="mongodb://localhost:27017"
export MONGODB_DATABASE="griot_registry"
export JWT_SECRET_KEY="your-secret-key-change-in-production"

# Optional
export HOST="0.0.0.0"
export PORT="8000"
```

### 3. Start the Server

```bash
griot-registry
```

The API will be available at `http://localhost:8000`. Visit `/docs` for interactive API documentation.

### 4. Get an Authentication Token

```bash
# Get a token with editor role (POST request)
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/token?user_id=myuser&roles=editor" | jq -r .access_token)

# Verify your token
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/auth/me
```

### 5. Create Your First Contract

```bash
curl -X POST http://localhost:8000/api/v1/contracts \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d '{
        "apiVersion": "v1.0.0",
        "kind": "DataContract",
        "id": "my-first-contract",
        "name": "my_first_contract",
        "version": "1.0.0",
        "status": "draft",
        "schema": [
            {
                "name": "MySchema",
                "id": "my-schema",
                "logicalType": "object",
                "properties": [
                    {"name": "id", "logicalType": "string", "required": true},
                    {"name": "name", "logicalType": "string", "required": true}
                ]
            }
        ]
    }'
```

## Using the Python Client

### Sync Client

```python
import httpx
from griot_registry import SyncRegistryClient
from griot_core import load_contract_from_dict

# Get an authentication token
response = httpx.get(
    "http://localhost:8000/api/v1/auth/token",
    params={"user_id": "myuser", "roles": "editor"}
)
token = response.json()["access_token"]

# Connect to the registry
with SyncRegistryClient("http://localhost:8000", token=token) as client:
    # Create a contract
    contract_data = {
        "apiVersion": "v1.0.0",
        "kind": "DataContract",
        "id": "user-events-001",
        "name": "user_events",
        "version": "1.0.0",
        "status": "draft",
        "schema": [
            {
                "name": "UserEvent",
                "id": "user-event-schema",
                "logicalType": "object",
                "properties": [
                    {"name": "user_id", "logicalType": "string", "required": True},
                    {"name": "event_type", "logicalType": "string", "required": True},
                    {"name": "timestamp", "logicalType": "timestamp", "required": True}
                ]
            }
        ]
    }
    contract = load_contract_from_dict(contract_data)
    created = client.create(contract)
    print(f"Created contract: {created.id}")

    # Retrieve the contract
    retrieved = client.get(created.id)
    print(f"Contract name: {retrieved.name}")

    # List all contracts
    contracts, total = client.list_contracts()
    print(f"Total contracts: {total}")
```

### Async Client

```python
import asyncio
import httpx
from griot_registry import RegistryClient
from griot_core import load_contract_from_dict

async def main():
    # Get token
    response = httpx.get(
        "http://localhost:8000/api/v1/auth/token",
        params={"user_id": "myuser", "roles": "editor"}
    )
    token = response.json()["access_token"]

    async with RegistryClient("http://localhost:8000", token=token) as client:
        contracts, total = await client.list_contracts(status="active")
        print(f"Found {total} active contracts")

asyncio.run(main())
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `MONGODB_URI` | `mongodb://localhost:27017` | MongoDB connection URI |
| `MONGODB_DATABASE` | `griot_registry` | Database name |
| `JWT_SECRET_KEY` | *required* | Secret key for JWT tokens |
| `HOST` | `0.0.0.0` | Server host |
| `PORT` | `8000` | Server port |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Token expiration time |

See the [Configuration Guide](docs/source/configuration.rst) for all options.

## API Endpoints

| Category | Base Path | Description |
|----------|-----------|-------------|
| Health | `/api/v1/health` | Service health checks |
| Auth | `/api/v1/auth` | Authentication and tokens |
| Contracts | `/api/v1/contracts` | Contract CRUD and versioning |
| Approvals | `/api/v1/approvals` | Approval workflows |

### Key Endpoints

```bash
# Authentication
GET  /api/v1/auth/token?user_id=...&roles=...  # Get JWT token
GET  /api/v1/auth/me                            # Get current user info

# Contracts
GET    /api/v1/contracts                        # List contracts
POST   /api/v1/contracts                        # Create contract
GET    /api/v1/contracts/{id}                   # Get contract
PUT    /api/v1/contracts/{id}                   # Update contract
DELETE /api/v1/contracts/{id}                   # Deprecate contract
PATCH  /api/v1/contracts/{id}/status            # Update status
GET    /api/v1/contracts/{id}/versions          # List versions
GET    /api/v1/contracts/{id}/versions/{v}      # Get specific version
POST   /api/v1/contracts/validate               # Validate without storing

# Approvals
POST   /api/v1/approvals                        # Create approval request
GET    /api/v1/approvals/pending                # List pending approvals
GET    /api/v1/approvals/{id}                   # Get approval details
POST   /api/v1/approvals/{id}/approve           # Approve request
POST   /api/v1/approvals/{id}/reject            # Reject request
```

## Contract Format (ODCS)

Griot Registry uses the ODCS (Open Data Contract Standard) format:

```json
{
    "apiVersion": "v1.0.0",
    "kind": "DataContract",
    "id": "unique-contract-id",
    "name": "contract_name",
    "version": "1.0.0",
    "status": "draft",
    "description": "Optional description",
    "schema": [
        {
            "name": "SchemaName",
            "id": "schema-id",
            "logicalType": "object",
            "properties": [
                {
                    "name": "field_name",
                    "logicalType": "string",
                    "required": true,
                    "description": "Field description"
                }
            ]
        }
    ]
}
```

**Supported logical types:** `string`, `integer`, `number`, `boolean`, `timestamp`, `date`, `array`, `object`, `bytes`

## Documentation

Build the documentation:

```bash
pip install griot-registry[docs]
cd docs
make html
```

Then open `docs/build/html/index.html` in your browser.

## Development

```bash
# Clone the repository
git clone https://github.com/griot-project/griot.git
cd griot/griot-registry

# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Start in development mode
DEBUG=true griot-registry
```

## Docker

```bash
# Build the image
docker build -t griot-registry .

# Run with Docker
docker run -p 8000:8000 \
    -e MONGODB_URI="mongodb://host.docker.internal:27017" \
    -e JWT_SECRET_KEY="your-secret-key" \
    griot-registry
```

### Docker Compose

```yaml
version: '3.8'

services:
  registry:
    image: griot-registry:latest
    ports:
      - "8000:8000"
    environment:
      MONGODB_URI: mongodb://mongodb:27017
      MONGODB_DATABASE: griot_registry
      JWT_SECRET_KEY: ${JWT_SECRET_KEY}
    depends_on:
      - mongodb

  mongodb:
    image: mongo:7
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db

volumes:
  mongodb_data:
```

## License

Apache-2.0
