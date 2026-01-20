Getting Started
===============

This guide will help you get Griot Registry up and running quickly.

Prerequisites
-------------

- Python 3.11 or higher
- MongoDB 5.0 or higher
- pip or another Python package manager

Installation
------------

From PyPI
^^^^^^^^^

.. code-block:: bash

   pip install griot-registry

From Source
^^^^^^^^^^^

.. code-block:: bash

   git clone https://github.com/griot-project/griot.git
   cd griot/griot-registry
   pip install -e .

Running MongoDB
---------------

You can run MongoDB locally using Docker:

.. code-block:: bash

   docker run -d \
       --name griot-mongodb \
       -p 27017:27017 \
       -e MONGO_INITDB_DATABASE=griot_registry \
       mongo:7

Or install MongoDB directly on your system following the
`official installation guide <https://www.mongodb.com/docs/manual/installation/>`_.

Configuration
-------------

Griot Registry is configured using environment variables. The minimum required
configuration is:

.. code-block:: bash

   # MongoDB connection
   export MONGODB_URI="mongodb://localhost:27017"
   export MONGODB_DATABASE="griot_registry"

   # JWT authentication secret (use a strong random key in production)
   export JWT_SECRET_KEY="your-super-secret-key-change-in-production"

See :doc:`configuration` for all available options.

Starting the Server
-------------------

Once configured, start the server:

.. code-block:: bash

   griot-registry

By default, the server runs on ``http://localhost:8000``. You can access:

- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json
- **Health Check**: http://localhost:8000/api/v1/health

Basic Usage
-----------

Using the Python Client
^^^^^^^^^^^^^^^^^^^^^^^

The easiest way to interact with the registry is using the Python client.
Contracts are created using the ODCS (Open Data Contract Standard) format
via ``load_contract_from_dict()``:

.. code-block:: python

   from griot_registry import SyncRegistryClient
   from griot_core import load_contract_from_dict

   # Define contract data in ODCS format
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
               "description": "A user activity event",
               "properties": [
                   {
                       "name": "user_id",
                       "logicalType": "string",
                       "required": True,
                       "description": "Unique user identifier"
                   },
                   {
                       "name": "event_type",
                       "logicalType": "string",
                       "required": True,
                       "description": "Type of event"
                   },
                   {
                       "name": "timestamp",
                       "logicalType": "timestamp",
                       "required": True,
                       "description": "When the event occurred"
                   }
               ]
           }
       ]
   }

   # Create the contract object
   contract = load_contract_from_dict(contract_data)

   # Connect to the registry with authentication
   with SyncRegistryClient(
       "http://localhost:8000",
       token="your-jwt-token"
   ) as client:
       # Create the contract in the registry
       created = client.create(contract)
       print(f"Created contract: {created.id}")

       # Retrieve the contract
       retrieved = client.get(created.id)
       print(f"Contract name: {retrieved.name}")
       print(f"Contract version: {retrieved.version}")

Using the Async Client
^^^^^^^^^^^^^^^^^^^^^^

For async applications, use the async client:

.. code-block:: python

   import asyncio
   from griot_registry import RegistryClient
   from griot_core import load_contract_from_dict

   async def main():
       async with RegistryClient(
           "http://localhost:8000",
           token="your-jwt-token"
       ) as client:
           # List all contracts
           contracts, total = await client.list_contracts()
           print(f"Found {total} contracts")

           # Get a specific contract
           contract = await client.get("user-events-001")
           print(f"Contract: {contract.name} v{contract.version}")

   asyncio.run(main())

Using the REST API
^^^^^^^^^^^^^^^^^^

You can also interact with the API directly using ``curl`` or any HTTP client.

**Get an authentication token:**

.. code-block:: bash

   # Get a token with editor role (POST request)
   curl -X POST "http://localhost:8000/api/v1/auth/token?user_id=myuser&roles=editor"

Response:

.. code-block:: json

   {
       "access_token": "eyJhbGciOiJIUzI1NiIs...",
       "token_type": "bearer"
   }

**List all contracts:**

.. code-block:: bash

   curl http://localhost:8000/api/v1/contracts

**Create a contract:**

.. code-block:: bash

   curl -X POST http://localhost:8000/api/v1/contracts \
       -H "Content-Type: application/json" \
       -H "Authorization: Bearer YOUR_TOKEN" \
       -d '{
           "apiVersion": "v1.0.0",
           "kind": "DataContract",
           "id": "my-contract-001",
           "name": "my_contract",
           "version": "1.0.0",
           "status": "draft",
           "schema": [
               {
                   "name": "MySchema",
                   "id": "schema-001",
                   "logicalType": "object",
                   "properties": [
                       {"name": "id", "logicalType": "string", "required": true},
                       {"name": "value", "logicalType": "integer"}
                   ]
               }
           ]
       }'

**Get a specific contract:**

.. code-block:: bash

   curl http://localhost:8000/api/v1/contracts/my-contract-001

**Update a contract:**

.. code-block:: bash

   curl -X PUT http://localhost:8000/api/v1/contracts/my-contract-001 \
       -H "Content-Type: application/json" \
       -H "Authorization: Bearer YOUR_TOKEN" \
       -d '{
           "apiVersion": "v1.0.0",
           "kind": "DataContract",
           "id": "my-contract-001",
           "name": "my_contract",
           "version": "1.0.0",
           "status": "draft",
           "change_type": "minor",
           "change_notes": "Added new field",
           "schema": [
               {
                   "name": "MySchema",
                   "id": "schema-001",
                   "logicalType": "object",
                   "properties": [
                       {"name": "id", "logicalType": "string", "required": true},
                       {"name": "value", "logicalType": "integer"},
                       {"name": "new_field", "logicalType": "string"}
                   ]
               }
           ]
       }'

Authentication
--------------

The registry uses JWT authentication. For development, you can obtain a token
via the auth endpoint:

.. code-block:: bash

   # Get a token with specific roles (POST request)
   curl -X POST "http://localhost:8000/api/v1/auth/token?user_id=myuser&roles=admin"

Available roles:

- ``viewer``: Read-only access to contracts
- ``editor``: Create, read, and update contracts
- ``admin``: Full access including delete and approval operations

See :doc:`authentication` for more details on authentication options.

Contract Format
---------------

Griot Registry uses the ODCS (Open Data Contract Standard) format. A minimal
contract requires:

.. code-block:: json

   {
       "apiVersion": "v1.0.0",
       "kind": "DataContract",
       "id": "unique-contract-id",
       "name": "contract_name",
       "version": "1.0.0",
       "status": "draft",
       "schema": []
   }

**Required fields:**

- ``apiVersion``: API version (e.g., "v1.0.0")
- ``kind``: Must be "DataContract"
- ``id``: Unique identifier for the contract
- ``name``: Human-readable name
- ``version``: Semantic version (e.g., "1.0.0")
- ``status``: One of "draft", "active", "deprecated", "retired"
- ``schema``: Array of schema definitions

**Schema format:**

.. code-block:: json

   {
       "name": "SchemaName",
       "id": "schema-unique-id",
       "logicalType": "object",
       "description": "Optional description",
       "properties": [
           {
               "name": "field_name",
               "logicalType": "string",
               "required": true,
               "description": "Field description"
           }
       ]
   }

**Supported logical types:**

- ``string``: Text data
- ``integer``: Whole numbers
- ``number``: Decimal numbers
- ``boolean``: True/false values
- ``timestamp``: Date and time
- ``date``: Date only
- ``object``: Nested object
- ``array``: List of values

Next Steps
----------

- Learn about :doc:`configuration` options
- Understand :doc:`authentication` mechanisms
- Explore the :doc:`api/endpoints` reference
- See :doc:`client/examples` for more usage patterns
