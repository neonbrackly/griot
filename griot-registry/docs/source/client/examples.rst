Client Examples
===============

This page provides comprehensive examples of using the Griot Registry Python
client. All examples use verified, working code patterns.

Setup
-----

Before running these examples, ensure you have:

1. A running MongoDB instance
2. The Griot Registry server running
3. A valid JWT token

.. code-block:: python

   import httpx
   from griot_registry import RegistryClient, SyncRegistryClient
   from griot_core import load_contract_from_dict

   # Base URL for the registry
   BASE_URL = "http://localhost:8000"

   # Get an authentication token (POST request)
   def get_token(user_id: str = "test-user", roles: str = "admin") -> str:
       response = httpx.post(
           f"{BASE_URL}/api/v1/auth/token",
           params={"user_id": user_id, "roles": roles}
       )
       return response.json()["access_token"]

   TOKEN = get_token()

Basic Contract Operations
-------------------------

Creating a Contract
^^^^^^^^^^^^^^^^^^^

Create a new data contract using the ODCS format:

.. code-block:: python

   from griot_registry import SyncRegistryClient
   from griot_core import load_contract_from_dict

   # Define the contract in ODCS format
   contract_data = {
       "apiVersion": "v1.0.0",
       "kind": "DataContract",
       "id": "customer-orders-001",
       "name": "customer_orders",
       "version": "1.0.0",
       "status": "draft",
       "description": "Customer order data for e-commerce analytics",
       "schema": [
           {
               "name": "Order",
               "id": "order-schema",
               "logicalType": "object",
               "description": "A customer order",
               "properties": [
                   {
                       "name": "order_id",
                       "logicalType": "string",
                       "required": True,
                       "description": "Unique order identifier"
                   },
                   {
                       "name": "customer_id",
                       "logicalType": "string",
                       "required": True,
                       "description": "Customer who placed the order"
                   },
                   {
                       "name": "total_amount",
                       "logicalType": "number",
                       "required": True,
                       "description": "Total order amount in cents"
                   },
                   {
                       "name": "currency",
                       "logicalType": "string",
                       "required": True,
                       "description": "ISO 4217 currency code"
                   },
                   {
                       "name": "created_at",
                       "logicalType": "timestamp",
                       "required": True,
                       "description": "Order creation timestamp"
                   },
                   {
                       "name": "status",
                       "logicalType": "string",
                       "required": True,
                       "description": "Order status"
                   }
               ]
           },
           {
               "name": "OrderItem",
               "id": "order-item-schema",
               "logicalType": "object",
               "description": "An item within an order",
               "properties": [
                   {
                       "name": "item_id",
                       "logicalType": "string",
                       "required": True,
                       "description": "Unique item identifier"
                   },
                   {
                       "name": "order_id",
                       "logicalType": "string",
                       "required": True,
                       "description": "Parent order ID"
                   },
                   {
                       "name": "product_id",
                       "logicalType": "string",
                       "required": True,
                       "description": "Product identifier"
                   },
                   {
                       "name": "quantity",
                       "logicalType": "integer",
                       "required": True,
                       "description": "Quantity ordered"
                   },
                   {
                       "name": "unit_price",
                       "logicalType": "number",
                       "required": True,
                       "description": "Price per unit in cents"
                   }
               ]
           }
       ]
   }

   # Create the contract object
   contract = load_contract_from_dict(contract_data)

   # Push to registry
   with SyncRegistryClient(BASE_URL, token=TOKEN) as client:
       created = client.create(contract)
       print(f"Created contract: {created.id}")
       print(f"Name: {created.name}")
       print(f"Version: {created.version}")
       print(f"Status: {created.status}")

Reading and Inspecting Contracts
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from griot_registry import SyncRegistryClient

   with SyncRegistryClient(BASE_URL, token=TOKEN) as client:
       # Get a contract by ID
       contract = client.get("customer-orders-001")

       # Inspect basic properties
       print(f"Contract: {contract.name} v{contract.version}")
       print(f"ID: {contract.id}")
       print(f"Status: {contract.status}")
       print(f"Description: {contract.description}")

       # Convert to dict for inspection
       data = contract.to_dict()
       print(f"\nSchemas ({len(data.get('schema', []))}):")
       for schema in data.get("schema", []):
           print(f"\n  {schema['name']}:")
           print(f"    ID: {schema['id']}")
           print(f"    Type: {schema['logicalType']}")
           if "properties" in schema:
               print(f"    Fields ({len(schema['properties'])}):")
               for field in schema["properties"]:
                   req = "required" if field.get("required") else "optional"
                   print(f"      - {field['name']}: {field['logicalType']} ({req})")

Listing Contracts
^^^^^^^^^^^^^^^^^

.. code-block:: python

   from griot_registry import SyncRegistryClient

   with SyncRegistryClient(BASE_URL, token=TOKEN) as client:
       # List all contracts
       contracts, total = client.list_contracts()
       print(f"Total contracts: {total}")

       for contract in contracts:
           print(f"  - {contract.name} v{contract.version} [{contract.status}]")

       # Pagination
       contracts, total = client.list_contracts(limit=10, offset=0)
       print(f"\nFirst page: {len(contracts)} of {total}")

       # Filter by status
       active_contracts, _ = client.list_contracts(status="active")
       print(f"\nActive contracts: {len(active_contracts)}")

       # Filter by owner
       team_contracts, _ = client.list_contracts(owner="data-team")
       print(f"Team contracts: {len(team_contracts)}")

Updating Contracts
^^^^^^^^^^^^^^^^^^

Updates create new versions automatically based on change_type:

.. code-block:: python

   from griot_registry import SyncRegistryClient
   from griot_core import load_contract_from_dict

   with SyncRegistryClient(BASE_URL, token=TOKEN) as client:
       # Get current contract
       contract = client.get("customer-orders-001")
       print(f"Current version: {contract.version}")  # e.g., "1.0.0"

       # Modify the contract data
       updated_data = contract.to_dict()

       # Add a new optional field (non-breaking change)
       updated_data["schema"][0]["properties"].append({
           "name": "notes",
           "logicalType": "string",
           "description": "Optional order notes"
       })

       # Create updated contract object
       updated_contract = load_contract_from_dict(updated_data)

       # PATCH version (1.0.0 -> 1.0.1)
       result = client.update(
           updated_contract,
           change_type="patch",
           change_notes="Added optional notes field to Order"
       )
       print(f"New version: {result.version}")  # "1.0.1"

       # MINOR version - add new schema (1.0.1 -> 1.1.0)
       data = result.to_dict()
       data["schema"].append({
           "name": "OrderShipment",
           "id": "shipment-schema",
           "logicalType": "object",
           "description": "Shipment tracking for orders",
           "properties": [
               {"name": "shipment_id", "logicalType": "string", "required": True},
               {"name": "order_id", "logicalType": "string", "required": True},
               {"name": "carrier", "logicalType": "string", "required": True},
               {"name": "tracking_number", "logicalType": "string"}
           ]
       })

       minor_contract = load_contract_from_dict(data)
       result = client.update(
           minor_contract,
           change_type="minor",
           change_notes="Added OrderShipment schema for tracking"
       )
       print(f"New version: {result.version}")  # "1.1.0"

       # MAJOR version with breaking changes (requires allow_breaking=True)
       data = result.to_dict()
       # Remove a required field (breaking change)
       data["schema"][0]["properties"] = [
           p for p in data["schema"][0]["properties"]
           if p["name"] != "currency"
       ]

       major_contract = load_contract_from_dict(data)

       # This would fail without allow_breaking=True
       result = client.update(
           major_contract,
           change_type="major",
           change_notes="BREAKING: Removed currency field",
           allow_breaking=True
       )
       print(f"New version: {result.version}")  # "2.0.0"

Contract Lifecycle
^^^^^^^^^^^^^^^^^^

Manage contract status through its lifecycle:

.. code-block:: python

   from griot_registry import SyncRegistryClient
   from griot_core import load_contract_from_dict

   with SyncRegistryClient(BASE_URL, token=TOKEN) as client:
       # Create a draft contract
       contract_data = {
           "apiVersion": "v1.0.0",
           "kind": "DataContract",
           "id": "feature-events-001",
           "name": "feature_events",
           "version": "1.0.0",
           "status": "draft",
           "schema": [
               {
                   "name": "FeatureEvent",
                   "id": "feature-event-schema",
                   "logicalType": "object",
                   "properties": [
                       {"name": "event_id", "logicalType": "string", "required": True},
                       {"name": "feature_name", "logicalType": "string", "required": True}
                   ]
               }
           ]
       }
       contract = load_contract_from_dict(contract_data)
       created = client.create(contract)
       print(f"Created draft: {created.id}")

       # Activate the contract (draft -> active)
       activated = client.update_status(created.id, "active")
       print(f"Status: {activated.status}")  # "active"

       # Deprecate the contract (active -> deprecated)
       deprecated = client.update_status(created.id, "deprecated")
       print(f"Status: {deprecated.status}")  # "deprecated"

       # Retire the contract (deprecated -> retired)
       retired = client.update_status(created.id, "retired")
       print(f"Status: {retired.status}")  # "retired"

       # Delete (deprecate) a contract
       success = client.delete(created.id)
       print(f"Deleted: {success}")

Version History
^^^^^^^^^^^^^^^

Access the complete version history of a contract:

.. code-block:: python

   from griot_registry import SyncRegistryClient

   with SyncRegistryClient(BASE_URL, token=TOKEN) as client:
       # List all versions
       versions, total = client.list_versions("customer-orders-001")
       print(f"Version history ({total} versions):")
       for v in versions:
           notes = v.get("change_notes", "No notes")
           breaking = " [BREAKING]" if v.get("is_breaking") else ""
           print(f"  v{v['version']} - {notes}{breaking}")

       # Get a specific version
       old_contract = client.get_version("customer-orders-001", "1.0.0")
       print(f"\nVersion 1.0.0:")
       print(f"  Name: {old_contract.name}")
       print(f"  Schemas: {len(old_contract.to_dict().get('schema', []))}")

Validation
^^^^^^^^^^

Validate contracts before creating them using the validation endpoint:

.. code-block:: python

   import httpx

   # A contract with potential issues
   contract_data = {
       "apiVersion": "v1.0.0",
       "kind": "DataContract",
       "id": "test-validation",
       "name": "test_validation",
       "version": "1.0.0",
       "status": "draft",
       "schema": [
           {
               "name": "TestSchema",
               "id": "test-schema",
               "logicalType": "object",
               "properties": [
                   {"name": "id", "logicalType": "string", "required": True}
               ]
           }
       ]
   }

   # Call the validation endpoint directly
   response = httpx.post(
       f"{BASE_URL}/api/v1/contracts/validate",
       json=contract_data,
       headers={"Authorization": f"Bearer {TOKEN}"}
   )
   result = response.json()

   print(f"Valid: {result['is_valid']}")
   print(f"Errors: {result['error_count']}")
   print(f"Warnings: {result['warning_count']}")

   if result["issues"]:
       print("\nIssues:")
       for issue in result["issues"]:
           print(f"  [{issue['severity']}] {issue['code']}: {issue['message']}")
           if issue.get("suggestion"):
               print(f"    Suggestion: {issue['suggestion']}")

Async Client Usage
------------------

FastAPI Integration
^^^^^^^^^^^^^^^^^^^

Integrate the async client with FastAPI:

.. code-block:: python

   from fastapi import FastAPI, Depends, HTTPException
   from contextlib import asynccontextmanager
   from griot_registry import RegistryClient
   from griot_core import load_contract_from_dict

   # Global client instance
   registry_client: RegistryClient | None = None

   @asynccontextmanager
   async def lifespan(app: FastAPI):
       global registry_client
       registry_client = RegistryClient(
           "http://registry:8000",
           token="your-service-token"
       )
       await registry_client.__aenter__()
       yield
       await registry_client.__aexit__(None, None, None)

   app = FastAPI(lifespan=lifespan)

   def get_registry() -> RegistryClient:
       return registry_client

   @app.get("/contracts/{contract_id}")
   async def get_contract(
       contract_id: str,
       registry: RegistryClient = Depends(get_registry)
   ):
       try:
           contract = await registry.get(contract_id)
           return {
               "id": contract.id,
               "name": contract.name,
               "version": contract.version,
               "status": contract.status
           }
       except Exception as e:
           raise HTTPException(status_code=404, detail=str(e))

   @app.get("/contracts")
   async def list_contracts(
       status: str | None = None,
       limit: int = 50,
       registry: RegistryClient = Depends(get_registry)
   ):
       contracts, total = await registry.list_contracts(
           status=status,
           limit=limit
       )
       return {
           "items": [{"id": c.id, "name": c.name} for c in contracts],
           "total": total
       }

Concurrent Operations
^^^^^^^^^^^^^^^^^^^^^

Fetch multiple contracts concurrently:

.. code-block:: python

   import asyncio
   from griot_registry import RegistryClient

   async def fetch_multiple_contracts(contract_ids: list[str]):
       async with RegistryClient(BASE_URL, token=TOKEN) as client:
           # Fetch all contracts concurrently
           tasks = [client.get(cid) for cid in contract_ids]
           contracts = await asyncio.gather(*tasks, return_exceptions=True)

           for i, result in enumerate(contracts):
               if isinstance(result, Exception):
                   print(f"Error fetching {contract_ids[i]}: {result}")
               else:
                   print(f"Fetched: {result.name} v{result.version}")

           return [c for c in contracts if not isinstance(c, Exception)]

   # Run the async function
   contract_ids = ["contract-1", "contract-2", "contract-3"]
   asyncio.run(fetch_multiple_contracts(contract_ids))

Approval Workflows
------------------

Request and manage approvals for contract changes:

.. code-block:: python

   from griot_registry import SyncRegistryClient
   from griot_core import load_contract_from_dict
   import httpx

   # Create approval request via API
   def create_approval_request(contract_id: str, token: str):
       response = httpx.post(
           f"{BASE_URL}/api/v1/approvals",
           headers={"Authorization": f"Bearer {token}"},
           json={
               "contract_id": contract_id,
               "request_type": "activation",
               "title": "Request to activate contract",
               "description": "Please review and approve this contract for production use"
           }
       )
       return response.json()

   # List pending approvals
   def list_pending_approvals(token: str):
       response = httpx.get(
           f"{BASE_URL}/api/v1/approvals/pending",
           headers={"Authorization": f"Bearer {token}"}
       )
       return response.json()

   # Approve a request
   def approve_request(request_id: str, token: str):
       response = httpx.post(
           f"{BASE_URL}/api/v1/approvals/{request_id}/approve",
           headers={"Authorization": f"Bearer {token}"},
           json={"comment": "Approved - looks good!"}
       )
       return response.json()

   # Reject a request
   def reject_request(request_id: str, token: str):
       response = httpx.post(
           f"{BASE_URL}/api/v1/approvals/{request_id}/reject",
           headers={"Authorization": f"Bearer {token}"},
           json={"comment": "Please add more documentation"}
       )
       return response.json()

   # Example usage
   admin_token = get_token("admin-user", "admin")

   # Create an approval request
   approval = create_approval_request("customer-orders-001", TOKEN)
   print(f"Created approval request: {approval['id']}")

   # List pending approvals
   pending = list_pending_approvals(admin_token)
   print(f"Pending approvals: {len(pending)}")

   # Approve the request
   result = approve_request(approval["id"], admin_token)
   print(f"Approval status: {result['status']}")

Error Handling
--------------

Handle common errors gracefully:

.. code-block:: python

   from griot_registry import SyncRegistryClient
   from griot_core import load_contract_from_dict
   import httpx

   with SyncRegistryClient(BASE_URL, token=TOKEN) as client:
       # Handle contract not found
       try:
           contract = client.get("nonexistent-contract-id")
       except httpx.HTTPStatusError as e:
           if e.response.status_code == 404:
               print("Contract not found")
           else:
               print(f"HTTP error: {e.response.status_code}")

       # Handle validation errors
       try:
           invalid_data = {
               "apiVersion": "v1.0.0",
               "kind": "DataContract",
               "id": "",  # Invalid: empty ID
               "name": "test",
               "version": "not-semver",  # Invalid version
               "status": "draft",
               "schema": []
           }
           contract = load_contract_from_dict(invalid_data)
           client.create(contract)
       except Exception as e:
           print(f"Validation error: {e}")

       # Handle breaking changes
       try:
           contract = client.get("customer-orders-001")
           data = contract.to_dict()

           # Remove a required field (breaking change)
           data["schema"][0]["properties"] = [
               p for p in data["schema"][0]["properties"]
               if p["name"] != "order_id"
           ]

           updated = load_contract_from_dict(data)

           # This will fail without allow_breaking=True
           client.update(updated, change_notes="Remove order_id")
       except httpx.HTTPStatusError as e:
           if e.response.status_code == 409:
               error_detail = e.response.json()
               print(f"Breaking change detected: {error_detail}")
               print("Use allow_breaking=True to force the update")
           else:
               raise

       # Handle authentication errors
       try:
           # Client without token
           with SyncRegistryClient(BASE_URL) as unauth_client:
               # Creating requires authentication
               contract_data = {
                   "apiVersion": "v1.0.0",
                   "kind": "DataContract",
                   "id": "test",
                   "name": "test",
                   "version": "1.0.0",
                   "status": "draft",
                   "schema": []
               }
               contract = load_contract_from_dict(contract_data)
               unauth_client.create(contract)
       except httpx.HTTPStatusError as e:
           if e.response.status_code == 401:
               print("Authentication required")
           elif e.response.status_code == 403:
               print("Permission denied - need editor role")
           else:
               raise

Complete Workflow Example
-------------------------

A complete example showing contract creation, updates, and lifecycle:

.. code-block:: python

   import httpx
   from griot_registry import SyncRegistryClient
   from griot_core import load_contract_from_dict

   BASE_URL = "http://localhost:8000"

   def main():
       # Get authentication token (POST request)
       response = httpx.post(
           f"{BASE_URL}/api/v1/auth/token",
           params={"user_id": "developer", "roles": "admin"}
       )
       token = response.json()["access_token"]

       with SyncRegistryClient(BASE_URL, token=token) as client:
           # 1. Create a new contract
           contract_data = {
               "apiVersion": "v1.0.0",
               "kind": "DataContract",
               "id": "workflow-example-001",
               "name": "workflow_example",
               "version": "1.0.0",
               "status": "draft",
               "description": "Example contract for workflow demonstration",
               "schema": [
                   {
                       "name": "Event",
                       "id": "event-schema",
                       "logicalType": "object",
                       "properties": [
                           {"name": "id", "logicalType": "string", "required": True},
                           {"name": "name", "logicalType": "string", "required": True},
                           {"name": "timestamp", "logicalType": "timestamp", "required": True}
                       ]
                   }
               ]
           }
           contract = load_contract_from_dict(contract_data)
           created = client.create(contract)
           print(f"1. Created: {created.id} v{created.version}")

           # 2. Update with new field (minor version bump)
           data = created.to_dict()
           data["schema"][0]["properties"].append({
               "name": "metadata",
               "logicalType": "object",
               "description": "Additional event metadata"
           })
           updated_contract = load_contract_from_dict(data)
           updated = client.update(
               updated_contract,
               change_type="minor",
               change_notes="Added metadata field"
           )
           print(f"2. Updated: {updated.id} v{updated.version}")

           # 3. Activate the contract
           activated = client.update_status(created.id, "active")
           print(f"3. Activated: status={activated.status}")

           # 4. List version history
           versions, total = client.list_versions(created.id)
           print(f"4. Versions: {total}")
           for v in versions:
               print(f"   - v{v['version']}: {v.get('change_notes', 'Initial')}")

           # 5. Deprecate the contract
           deprecated = client.update_status(created.id, "deprecated")
           print(f"5. Deprecated: status={deprecated.status}")

           # 6. Clean up (deprecate performs a soft delete)
           client.deprecate(created.id)
           print("6. Contract deprecated")

           print("\nWorkflow complete!")

   if __name__ == "__main__":
       main()
