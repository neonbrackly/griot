Contracts API
=============

The Contracts API provides full CRUD operations for data contracts, including
versioning, status management, and validation. All contracts use the ODCS
(Open Data Contract Standard) format.

Endpoints
---------

List Contracts
^^^^^^^^^^^^^^

.. code-block:: text

   GET /api/v1/contracts

List all contracts with optional filtering.

**Query Parameters:**

.. list-table::
   :header-rows: 1
   :widths: 20 15 65

   * - Parameter
     - Type
     - Description
   * - ``limit``
     - int
     - Maximum number of contracts (1-100, default: 50)
   * - ``offset``
     - int
     - Number to skip (default: 0)
   * - ``status``
     - string
     - Filter by status: draft, active, deprecated, retired
   * - ``schema_name``
     - string
     - Filter by schema name
   * - ``owner``
     - string
     - Filter by owner/team

**Response:**

.. code-block:: text

   {
       "items": [
           {
               "apiVersion": "v1.0.0",
               "kind": "DataContract",
               "id": "user-events-001",
               "name": "user_events",
               "version": "1.0.0",
               "status": "active",
               "schema": [...]
           }
       ],
       "total": 1,
       "limit": 50,
       "offset": 0
   }

**Example:**

.. code-block:: bash

   # List all active contracts
   curl "http://localhost:8000/api/v1/contracts?status=active"

Create Contract
^^^^^^^^^^^^^^^

.. code-block:: text

   POST /api/v1/contracts

Create a new contract. The contract is validated before storage. Requires
``editor`` or ``admin`` role.

**Request Body:**

Contracts must use the ODCS format:

.. code-block:: json

   {
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
                       "required": true,
                       "description": "Unique user identifier"
                   },
                   {
                       "name": "event_type",
                       "logicalType": "string",
                       "required": true,
                       "description": "Type of event"
                   },
                   {
                       "name": "timestamp",
                       "logicalType": "timestamp",
                       "required": true,
                       "description": "When the event occurred"
                   }
               ]
           }
       ]
   }

**Response:** (201 Created)

The created contract with all fields preserved.

**Example:**

.. code-block:: bash

   # Get a token first
   TOKEN=$(curl -s "http://localhost:8000/api/v1/auth/token?user_id=myuser&roles=editor" | jq -r .access_token)

   # Create the contract
   curl -X POST http://localhost:8000/api/v1/contracts \
       -H "Content-Type: application/json" \
       -H "Authorization: Bearer $TOKEN" \
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
                   "id": "my-schema",
                   "logicalType": "object",
                   "properties": [
                       {"name": "id", "logicalType": "string", "required": true}
                   ]
               }
           ]
       }'

Get Contract
^^^^^^^^^^^^

.. code-block:: text

   GET /api/v1/contracts/{contract_id}

Retrieve a specific contract by ID.

**Path Parameters:**

- ``contract_id``: The contract's unique identifier

**Query Parameters:**

- ``version``: Optional specific version to retrieve (e.g., "1.0.0")

**Response:**

Full contract object in ODCS format.

**Example:**

.. code-block:: bash

   curl http://localhost:8000/api/v1/contracts/user-events-001

   # Get a specific version
   curl "http://localhost:8000/api/v1/contracts/user-events-001?version=1.0.0"

Update Contract
^^^^^^^^^^^^^^^

.. code-block:: text

   PUT /api/v1/contracts/{contract_id}

Update an existing contract. Creates a new version automatically based on
``change_type``. Supports breaking change detection.

**Path Parameters:**

- ``contract_id``: The contract's unique identifier

**Query Parameters:**

.. list-table::
   :header-rows: 1
   :widths: 20 15 65

   * - Parameter
     - Type
     - Description
   * - ``allow_breaking``
     - boolean
     - Allow breaking changes (default: false)

**Request Body:**

The complete updated contract in ODCS format. Include ``change_type`` and
``change_notes`` in the body:

.. code-block:: json

   {
       "apiVersion": "v1.0.0",
       "kind": "DataContract",
       "id": "user-events-001",
       "name": "user_events",
       "version": "1.0.0",
       "status": "draft",
       "change_type": "minor",
       "change_notes": "Added new field for session tracking",
       "schema": [
           {
               "name": "UserEvent",
               "id": "user-event-schema",
               "logicalType": "object",
               "properties": [
                   {"name": "user_id", "logicalType": "string", "required": true},
                   {"name": "event_type", "logicalType": "string", "required": true},
                   {"name": "timestamp", "logicalType": "timestamp", "required": true},
                   {"name": "session_id", "logicalType": "string", "description": "Browser session"}
               ]
           }
       ]
   }

**Version Bump Types:**

- ``patch``: Bug fixes, documentation (1.0.0 -> 1.0.1)
- ``minor``: New features, optional fields (1.0.0 -> 1.1.0)
- ``major``: Breaking changes (1.0.0 -> 2.0.0)

**Response:**

The updated contract with new version.

**Breaking Change Detection:**

The API automatically detects breaking changes such as:

- Removing required fields
- Changing field types (logicalType)
- Removing schemas
- Making optional fields required

If a breaking change is detected and ``allow_breaking`` is false, the request
returns a 409 Conflict with details of the breaking changes.

**Example:**

.. code-block:: bash

   curl -X PUT "http://localhost:8000/api/v1/contracts/user-events-001" \
       -H "Content-Type: application/json" \
       -H "Authorization: Bearer $TOKEN" \
       -d '{
           "apiVersion": "v1.0.0",
           "kind": "DataContract",
           "id": "user-events-001",
           "name": "user_events",
           "version": "1.0.0",
           "status": "draft",
           "change_type": "minor",
           "change_notes": "Added session_id field",
           "schema": [...]
       }'

   # Allow breaking changes (major version bump)
   curl -X PUT "http://localhost:8000/api/v1/contracts/user-events-001?allow_breaking=true" \
       -H "Content-Type: application/json" \
       -H "Authorization: Bearer $TOKEN" \
       -d '{...}'

Update Contract Status
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: text

   PATCH /api/v1/contracts/{contract_id}/status

Update only the contract's status. Requires ``editor`` or ``admin`` role.

**Path Parameters:**

- ``contract_id``: The contract's unique identifier

**Request Body:**

.. code-block:: json

   {
       "status": "active"
   }

**Valid Status Values:**

- ``draft``: Initial state, can be modified freely
- ``active``: Production-ready, changes create new versions
- ``deprecated``: Marked for removal, still accessible
- ``retired``: No longer in use

**Status Transitions:**

.. code-block:: text

   draft -> active -> deprecated -> retired

**Example:**

.. code-block:: bash

   # Activate a contract
   curl -X PATCH http://localhost:8000/api/v1/contracts/user-events-001/status \
       -H "Content-Type: application/json" \
       -H "Authorization: Bearer $TOKEN" \
       -d '{"status": "active"}'

   # Deprecate a contract
   curl -X PATCH http://localhost:8000/api/v1/contracts/user-events-001/status \
       -H "Content-Type: application/json" \
       -H "Authorization: Bearer $TOKEN" \
       -d '{"status": "deprecated"}'

Delete Contract
^^^^^^^^^^^^^^^

.. code-block:: text

   DELETE /api/v1/contracts/{contract_id}

Deprecate a contract (soft delete). The contract remains accessible but is
marked as deprecated. Requires ``editor`` or ``admin`` role.

**Path Parameters:**

- ``contract_id``: The contract's unique identifier

**Response:** 204 No Content

**Example:**

.. code-block:: bash

   curl -X DELETE http://localhost:8000/api/v1/contracts/user-events-001 \
       -H "Authorization: Bearer $TOKEN"

List Contract Versions
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: text

   GET /api/v1/contracts/{contract_id}/versions

List all versions of a contract.

**Path Parameters:**

- ``contract_id``: The contract's unique identifier

**Query Parameters:**

- ``limit``: Maximum versions to return (default: 50)
- ``offset``: Number to skip (default: 0)

**Response:**

.. code-block:: json

   {
       "items": [
           {
               "contract_id": "user-events-001",
               "version": "1.1.0",
               "change_type": "minor",
               "change_notes": "Added session_id field",
               "is_breaking": false,
               "created_at": "2024-01-20T10:00:00Z",
               "created_by": "myuser"
           },
           {
               "contract_id": "user-events-001",
               "version": "1.0.0",
               "change_type": null,
               "change_notes": null,
               "is_breaking": false,
               "created_at": "2024-01-15T10:00:00Z",
               "created_by": "myuser"
           }
       ],
       "total": 2
   }

**Example:**

.. code-block:: bash

   curl http://localhost:8000/api/v1/contracts/user-events-001/versions

Get Specific Version
^^^^^^^^^^^^^^^^^^^^

.. code-block:: text

   GET /api/v1/contracts/{contract_id}/versions/{version}

Retrieve a specific version of a contract.

**Path Parameters:**

- ``contract_id``: The contract's unique identifier
- ``version``: Semantic version string (e.g., "1.0.0")

**Response:**

The contract as it existed at that version, in full ODCS format.

**Example:**

.. code-block:: bash

   curl http://localhost:8000/api/v1/contracts/user-events-001/versions/1.0.0

Validate Contract
^^^^^^^^^^^^^^^^^

.. code-block:: text

   POST /api/v1/contracts/validate

Validate a contract without storing it. Useful for CI/CD pipelines and
pre-flight checks.

**Request Body:**

A contract object in ODCS format to validate.

**Response:**

.. code-block:: json

   {
       "is_valid": true,
       "has_errors": false,
       "has_warnings": true,
       "error_count": 0,
       "warning_count": 1,
       "issues": [
           {
               "code": "MISSING_DESCRIPTION",
               "field": "schema[0].properties[0]",
               "message": "Field 'user_id' is missing a description",
               "severity": "warning",
               "suggestion": "Add a description to document this field"
           }
       ]
   }

**Example:**

.. code-block:: bash

   curl -X POST http://localhost:8000/api/v1/contracts/validate \
       -H "Content-Type: application/json" \
       -d '{
           "apiVersion": "v1.0.0",
           "kind": "DataContract",
           "id": "test-contract",
           "name": "test",
           "version": "1.0.0",
           "status": "draft",
           "schema": []
       }'

Contract Object Schema (ODCS Format)
------------------------------------

Griot Registry uses the ODCS (Open Data Contract Standard) format:

.. code-block:: json

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
               "id": "unique-schema-id",
               "logicalType": "object",
               "description": "Optional schema description",
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

**Required Fields:**

- ``apiVersion``: API version string (e.g., "v1.0.0")
- ``kind``: Must be "DataContract"
- ``id``: Unique identifier for the contract
- ``name``: Human-readable name
- ``version``: Semantic version (e.g., "1.0.0")
- ``status``: One of "draft", "active", "deprecated", "retired"
- ``schema``: Array of schema definitions (can be empty)

**Schema Fields:**

- ``name``: Schema name (required)
- ``id``: Unique schema identifier (required)
- ``logicalType``: Type of the schema, typically "object" (required)
- ``description``: Optional description
- ``properties``: Array of field definitions

**Property Fields:**

- ``name``: Field name (required)
- ``logicalType``: Data type (required)
- ``required``: Whether field is required (default: false)
- ``description``: Optional description

Supported Logical Types
-----------------------

The following logical types are supported for schema properties:

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Type
     - Description
   * - ``string``
     - Text data
   * - ``integer``
     - Whole numbers
   * - ``number``
     - Decimal numbers
   * - ``boolean``
     - True/false values
   * - ``timestamp``
     - Date and time (ISO 8601)
   * - ``date``
     - Date only (ISO 8601)
   * - ``array``
     - List of values
   * - ``object``
     - Nested structure
   * - ``bytes``
     - Binary data

Error Responses
---------------

**400 Bad Request** - Invalid contract data:

.. code-block:: json

   {
       "detail": {
           "code": "INVALID_CONTRACT",
           "message": "Failed to parse contract: ..."
       }
   }

**404 Not Found** - Contract doesn't exist:

.. code-block:: json

   {
       "detail": {
           "code": "NOT_FOUND",
           "message": "Contract 'unknown-id' not found"
       }
   }

**409 Conflict** - Breaking changes detected:

.. code-block:: json

   {
       "code": "BREAKING_CHANGES_DETECTED",
       "message": "Update contains 1 breaking change(s)",
       "breaking_changes": [
           {
               "change_type": "field_removed",
               "field": "user_id",
               "description": "Required field 'user_id' was removed",
               "migration_hint": "Add back the field or use allow_breaking=true"
           }
       ],
       "allow_breaking_hint": "Add ?allow_breaking=true to force the update"
   }

**422 Unprocessable Entity** - Validation failed:

.. code-block:: text

   {
       "code": "VALIDATION_FAILED",
       "message": "Contract validation failed",
       "validation": {
           "is_valid": false,
           "has_errors": true,
           "error_count": 1,
           "issues": [...]
       }
   }
