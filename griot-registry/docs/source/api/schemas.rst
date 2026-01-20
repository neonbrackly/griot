Schemas API
===========

The Schemas API provides access to the schema catalog, enabling cross-contract
schema discovery and querying. The schema catalog is a denormalized view of all
schemas across all contracts, optimized for search and discovery.

Endpoints
---------

List Schemas
^^^^^^^^^^^^

.. code-block:: text

   GET /api/v1/schemas

List all schemas in the catalog with optional filtering.

**Query Parameters:**

.. list-table::
   :header-rows: 1
   :widths: 20 15 65

   * - Parameter
     - Type
     - Description
   * - ``limit``
     - int
     - Maximum schemas to return (1-100, default: 50)
   * - ``offset``
     - int
     - Number to skip (default: 0)
   * - ``name``
     - string
     - Filter by schema name (partial match)
   * - ``has_pii``
     - boolean
     - Filter by PII presence
   * - ``field_name``
     - string
     - Filter by field name

**Response:**

.. code-block:: json

   {
       "items": [
           {
               "contract_id": "contract-123",
               "contract_name": "user-events",
               "contract_version": "1.0.0",
               "schema_name": "UserEvent",
               "description": "A user activity event",
               "field_count": 5,
               "has_pii": true,
               "fields": ["user_id", "event_type", "timestamp", "email", "ip_address"]
           }
       ],
       "total": 1,
       "limit": 50,
       "offset": 0
   }

**Examples:**

.. code-block:: bash

   # List all schemas
   curl http://localhost:8000/api/v1/schemas

   # Find schemas with PII
   curl "http://localhost:8000/api/v1/schemas?has_pii=true"

   # Find schemas containing a field named 'email'
   curl "http://localhost:8000/api/v1/schemas?field_name=email"

Get Contracts by Schema Name
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: text

   GET /api/v1/schemas/contracts/{schema_name}

Find all contracts that contain a schema with the given name.

**Path Parameters:**

- ``schema_name``: The schema name to search for

**Response:**

.. code-block:: json

   {
       "schema_name": "UserEvent",
       "contracts": [
           {
               "contract_id": "contract-123",
               "contract_name": "user-events",
               "version": "1.0.0",
               "status": "active"
           },
           {
               "contract_id": "contract-456",
               "contract_name": "analytics-events",
               "version": "2.1.0",
               "status": "active"
           }
       ],
       "total": 2
   }

**Example:**

.. code-block:: bash

   curl http://localhost:8000/api/v1/schemas/contracts/UserEvent

Rebuild Schema Catalog
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: text

   POST /api/v1/schemas/rebuild

Rebuild the schema catalog from all contracts. This is an administrative
operation that should rarely be needed.

**Authentication:** Requires admin role.

**Response:**

.. code-block:: json

   {
       "status": "success",
       "schemas_indexed": 42,
       "contracts_processed": 15
   }

**Example:**

.. code-block:: bash

   curl -X POST http://localhost:8000/api/v1/schemas/rebuild \
       -H "Authorization: Bearer $ADMIN_TOKEN"

Schema Catalog Object
---------------------

Each entry in the schema catalog contains:

.. code-block:: json

   {
       "id": "catalog-entry-id",
       "contract_id": "parent-contract-id",
       "contract_name": "user-events",
       "contract_version": "1.0.0",
       "schema_name": "UserEvent",
       "description": "Schema description",
       "fields": [
           {
               "name": "user_id",
               "data_type": "string",
               "required": true,
               "pii": false
           }
       ],
       "field_count": 5,
       "has_pii": true,
       "pii_fields": ["email", "ip_address"],
       "indexed_at": "2024-01-15T10:30:00Z"
   }

Use Cases
---------

Data Discovery
^^^^^^^^^^^^^^

Find all schemas that might contain user data:

.. code-block:: bash

   # Find schemas with PII
   curl "http://localhost:8000/api/v1/schemas?has_pii=true"

   # Find schemas with 'user' in the name
   curl "http://localhost:8000/api/v1/schemas?name=user"

Schema Lineage
^^^^^^^^^^^^^^

Find all contracts that use a particular schema:

.. code-block:: bash

   curl http://localhost:8000/api/v1/schemas/contracts/UserEvent

Field Search
^^^^^^^^^^^^

Find all schemas that contain a specific field:

.. code-block:: bash

   # Find schemas with an 'email' field
   curl "http://localhost:8000/api/v1/schemas?field_name=email"

   # Useful for impact analysis when changing a common field
