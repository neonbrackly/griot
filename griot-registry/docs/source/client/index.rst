Python Client
=============

Griot Registry provides both async and synchronous Python clients for easy
integration with your applications. The clients work with ``griot-core``'s
``Contract`` objects, providing a seamless experience with the Griot ecosystem.

Installation
------------

The client is included with the registry package:

.. code-block:: bash

   pip install griot-registry

Or install griot-core separately for client-only usage:

.. code-block:: bash

   pip install griot-core httpx

Client Types
------------

RegistryClient (Async)
^^^^^^^^^^^^^^^^^^^^^^

The async client is recommended for high-performance applications and when
integrating with async frameworks like FastAPI or aiohttp.

.. code-block:: python

   from griot_registry import RegistryClient

   async def main():
       async with RegistryClient(
           "http://localhost:8000",
           token="your-jwt-token"
       ) as client:
           contracts, total = await client.list_contracts()
           print(f"Found {total} contracts")

SyncRegistryClient (Synchronous)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The sync client wraps the async client and is convenient for scripts, notebooks,
and synchronous applications.

.. code-block:: python

   from griot_registry import SyncRegistryClient

   with SyncRegistryClient(
       "http://localhost:8000",
       token="your-jwt-token"
   ) as client:
       contracts, total = client.list_contracts()
       print(f"Found {total} contracts")

Authentication
--------------

Both clients support JWT token authentication:

.. code-block:: python

   # Using JWT token
   client = SyncRegistryClient(
       "http://localhost:8000",
       token="eyJhbGciOiJIUzI1NiIs..."
   )

   # Using custom headers
   client = SyncRegistryClient(
       "http://localhost:8000",
       headers={"Authorization": "Bearer your-token"}
   )

To obtain a token, use the auth endpoint:

.. code-block:: python

   import httpx

   # Get a token with editor role (POST request)
   response = httpx.post(
       "http://localhost:8000/api/v1/auth/token",
       params={"user_id": "myuser", "roles": "editor"}
   )
   token = response.json()["access_token"]

   # Use the token with the client
   with SyncRegistryClient("http://localhost:8000", token=token) as client:
       # ... use the client

Working with Contracts
----------------------

Contracts are created using the ODCS (Open Data Contract Standard) format via
``load_contract_from_dict()`` from ``griot-core``.

Creating a Contract
^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from griot_registry import SyncRegistryClient
   from griot_core import load_contract_from_dict

   # Define the contract in ODCS format
   contract_data = {
       "apiVersion": "v1.0.0",
       "kind": "DataContract",
       "id": "user-events-001",
       "name": "user_events",
       "version": "1.0.0",
       "status": "draft",
       "description": "User activity events for analytics",
       "schema": [
           {
               "name": "UserEvent",
               "id": "user-event-schema",
               "logicalType": "object",
               "description": "A single user activity event",
               "properties": [
                   {
                       "name": "event_id",
                       "logicalType": "string",
                       "required": True,
                       "description": "Unique event identifier"
                   },
                   {
                       "name": "user_id",
                       "logicalType": "string",
                       "required": True,
                       "description": "User who triggered the event"
                   },
                   {
                       "name": "event_type",
                       "logicalType": "string",
                       "required": True,
                       "description": "Type of event (click, view, purchase)"
                   },
                   {
                       "name": "timestamp",
                       "logicalType": "timestamp",
                       "required": True,
                       "description": "When the event occurred"
                   },
                   {
                       "name": "properties",
                       "logicalType": "object",
                       "description": "Additional event properties"
                   }
               ]
           }
       ]
   }

   # Create the contract object
   contract = load_contract_from_dict(contract_data)

   # Push to the registry
   with SyncRegistryClient("http://localhost:8000", token=TOKEN) as client:
       created = client.create(contract)
       print(f"Created contract: {created.id}")
       print(f"Version: {created.version}")

Retrieving Contracts
^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from griot_registry import SyncRegistryClient

   with SyncRegistryClient("http://localhost:8000", token=TOKEN) as client:
       # Get by ID
       contract = client.get("user-events-001")
       print(f"Name: {contract.name}")
       print(f"Version: {contract.version}")

       # List all contracts
       contracts, total = client.list_contracts(limit=100)
       print(f"Found {total} contracts")

       # Filter by status
       active_contracts, _ = client.list_contracts(status="active")

       # Filter by owner
       team_contracts, _ = client.list_contracts(owner="data-platform-team")

Updating Contracts
^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from griot_registry import SyncRegistryClient
   from griot_core import load_contract_from_dict

   with SyncRegistryClient("http://localhost:8000", token=TOKEN) as client:
       # Get the current contract
       contract = client.get("user-events-001")

       # Create updated contract data (add a new field)
       updated_data = contract.to_dict()
       updated_data["schema"][0]["properties"].append({
           "name": "session_id",
           "logicalType": "string",
           "description": "Browser session identifier"
       })

       # Create updated contract object
       updated_contract = load_contract_from_dict(updated_data)

       # Update with automatic version bump
       result = client.update(
           updated_contract,
           change_type="minor",  # or "patch", "major"
           change_notes="Added session_id field for session tracking"
       )
       print(f"New version: {result.version}")  # e.g., "1.1.0"

Deleting Contracts
^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from griot_registry import SyncRegistryClient

   with SyncRegistryClient("http://localhost:8000", token=TOKEN) as client:
       # Delete deprecates the contract (soft delete)
       success = client.delete("user-events-001")
       print(f"Contract deprecated: {success}")

Version Management
^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from griot_registry import SyncRegistryClient

   with SyncRegistryClient("http://localhost:8000", token=TOKEN) as client:
       # List all versions of a contract
       versions, total = client.list_versions("user-events-001")
       print(f"Found {total} versions:")
       for v in versions:
           print(f"  v{v['version']} - {v.get('change_notes', 'No notes')}")

       # Get a specific version
       v1_contract = client.get_version("user-events-001", "1.0.0")
       print(f"Version 1.0.0: {v1_contract.name}")

Validation
^^^^^^^^^^

Validate a contract without storing it using the validation endpoint:

.. code-block:: python

   import httpx

   # Validate a contract without storing it
   contract_data = {
       "apiVersion": "v1.0.0",
       "kind": "DataContract",
       "id": "test-contract",
       "name": "test",
       "version": "1.0.0",
       "status": "draft",
       "schema": []
   }

   # Call the validation endpoint directly
   response = httpx.post(
       "http://localhost:8000/api/v1/contracts/validate",
       json=contract_data,
       headers={"Authorization": f"Bearer {TOKEN}"}
   )
   result = response.json()
   print(f"Valid: {result['is_valid']}")
   if result['issues']:
       for issue in result['issues']:
           print(f"  [{issue['severity']}] {issue['message']}")

API Reference
-------------

.. toctree::
   :maxdepth: 2

   examples

Client Classes
^^^^^^^^^^^^^^

.. py:class:: RegistryClient(base_url, token=None, headers=None, timeout=30.0)

   Async client for the Griot Registry API.

   :param base_url: Registry server URL (e.g., "http://localhost:8000")
   :param token: Optional JWT token for authentication
   :param headers: Optional additional headers
   :param timeout: Request timeout in seconds (default: 30.0)

   .. py:method:: create(contract)
      :async:

      Create a new contract in the registry.

      :param contract: Contract object to create (from ``load_contract_from_dict``)
      :returns: Created Contract with server-assigned metadata
      :raises HTTPException: If creation fails (409 for duplicates, 422 for validation)

   .. py:method:: get(contract_id)
      :async:

      Retrieve a contract by ID.

      :param contract_id: The contract's unique identifier
      :returns: Contract object
      :raises HTTPException: 404 if contract doesn't exist

   .. py:method:: update(contract, change_type=None, change_notes=None, allow_breaking=False)
      :async:

      Update an existing contract, creating a new version.

      :param contract: Updated Contract object
      :param change_type: Version bump type ("patch", "minor", "major")
      :param change_notes: Description of changes
      :param allow_breaking: Allow breaking changes (default: False)
      :returns: Updated Contract with new version
      :raises HTTPException: 409 if breaking change detected without allow_breaking

   .. py:method:: delete(contract_id)
      :async:

      Deprecate a contract (soft delete).

      :param contract_id: Contract ID to deprecate
      :returns: True if successful
      :raises HTTPException: 404 if contract doesn't exist

   .. py:method:: list_contracts(limit=50, offset=0, status=None, schema_name=None, owner=None)
      :async:

      List contracts with optional filtering.

      :param limit: Maximum results to return (1-100)
      :param offset: Number of results to skip
      :param status: Filter by status ("draft", "active", "deprecated", "retired")
      :param schema_name: Filter by schema name
      :param owner: Filter by owner/team
      :returns: Tuple of (contracts list, total count)

   .. py:method:: list_versions(contract_id, limit=50, offset=0)
      :async:

      List all versions of a contract.

      :param contract_id: Contract ID
      :param limit: Maximum results to return
      :param offset: Number of results to skip
      :returns: Tuple of (versions list, total count)

   .. py:method:: get_version(contract_id, version)
      :async:

      Get a specific version of a contract.

      :param contract_id: Contract ID
      :param version: Version string (e.g., "1.0.0")
      :returns: Contract object at that version

   .. py:method:: validate(contract)
      :async:

      Validate a contract without storing it.

      :param contract: Contract object to validate
      :returns: Validation result dict with is_valid, issues, etc.

   .. py:method:: update_status(contract_id, status)
      :async:

      Update the status of a contract.

      :param contract_id: Contract ID
      :param status: New status ("draft", "active", "deprecated", "retired")
      :returns: Updated Contract

.. py:class:: SyncRegistryClient(base_url, token=None, headers=None, timeout=30.0)

   Synchronous wrapper around RegistryClient.

   All methods have the same signatures as RegistryClient but are synchronous.
   Use within a context manager (``with`` statement) for automatic cleanup.

Exception Classes
^^^^^^^^^^^^^^^^^

.. py:exception:: RegistryClientError

   Base exception for all client errors.

.. py:exception:: ContractNotFoundError

   Raised when a requested contract doesn't exist (HTTP 404).

.. py:exception:: ValidationError

   Raised when contract validation fails (HTTP 422).

.. py:exception:: BreakingChangeError

   Raised when an update would cause a breaking change (HTTP 409).
