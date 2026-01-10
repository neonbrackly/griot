API Reference
=============

Complete reference for the griot-registry REST API.

.. contents:: Table of Contents
   :local:
   :depth: 2

Base URL
--------

All API endpoints are prefixed with ``/api/v1``.

.. code-block:: text

   http://localhost:8000/api/v1

OpenAPI Specification
---------------------

The full OpenAPI 3.0 specification is available at:

- **Swagger UI**: ``/docs``
- **ReDoc**: ``/redoc``
- **OpenAPI JSON**: ``/openapi.json``

Health Endpoints
----------------

GET /health
~~~~~~~~~~~

Check server and storage backend health.

**Request:**

.. code-block:: bash

   curl http://localhost:8000/api/v1/health

**Response (200 OK):**

.. code-block:: json

   {
     "status": "healthy",
     "storage": "healthy",
     "version": "0.1.0",
     "timestamp": "2024-01-10T14:30:00Z"
   }

Contract Endpoints
------------------

GET /contracts
~~~~~~~~~~~~~~

List all contracts with optional filtering.

**Query Parameters:**

.. list-table::
   :header-rows: 1
   :widths: 20 15 15 50

   * - Parameter
     - Type
     - Default
     - Description
   * - ``owner``
     - string
     - —
     - Filter by owner
   * - ``status``
     - string
     - —
     - Filter by status (active, deprecated)
   * - ``limit``
     - integer
     - 100
     - Maximum results
   * - ``offset``
     - integer
     - 0
     - Pagination offset

**Request:**

.. code-block:: bash

   curl "http://localhost:8000/api/v1/contracts?owner=data-team&limit=10" \
     -H "X-API-Key: your-key"

**Response (200 OK):**

.. code-block:: json

   {
     "contracts": [
       {
         "name": "user_profile",
         "description": "User profile data contract",
         "owner": "data-team",
         "current_version": "1.2.0",
         "status": "active",
         "created_at": "2024-01-01T00:00:00Z",
         "updated_at": "2024-01-10T14:30:00Z"
       }
     ],
     "total": 1,
     "limit": 10,
     "offset": 0
   }

POST /contracts
~~~~~~~~~~~~~~~

Create a new contract.

**Request Body:**

.. code-block:: json

   {
     "name": "order_events",
     "description": "E-commerce order events",
     "owner": "data-team",
     "fields": [
       {
         "name": "order_id",
         "type": "string",
         "required": true,
         "description": "Unique order identifier"
       },
       {
         "name": "amount",
         "type": "number",
         "constraints": {
           "min": 0
         }
       },
       {
         "name": "status",
         "type": "string",
         "constraints": {
           "enum": ["pending", "confirmed", "shipped", "delivered"]
         }
       }
     ]
   }

**Response (201 Created):**

.. code-block:: json

   {
     "name": "order_events",
     "description": "E-commerce order events",
     "owner": "data-team",
     "current_version": "1.0.0",
     "status": "active",
     "fields": [...],
     "created_at": "2024-01-10T14:30:00Z"
   }

GET /contracts/{name}
~~~~~~~~~~~~~~~~~~~~~

Get a specific contract by name.

**Request:**

.. code-block:: bash

   curl http://localhost:8000/api/v1/contracts/user_profile \
     -H "X-API-Key: your-key"

**Response (200 OK):**

.. code-block:: json

   {
     "name": "user_profile",
     "description": "User profile data contract",
     "owner": "data-team",
     "current_version": "1.2.0",
     "status": "active",
     "fields": [
       {
         "name": "user_id",
         "type": "string",
         "required": true
       },
       {
         "name": "email",
         "type": "string",
         "format": "email",
         "pii": {
           "category": "contact",
           "sensitivity": "high"
         }
       }
     ],
     "metadata": {
       "tags": ["users", "pii"],
       "domain": "identity"
     }
   }

PUT /contracts/{name}
~~~~~~~~~~~~~~~~~~~~~

Update an existing contract. Creates a new version.

**Request Body:**

.. code-block:: json

   {
     "description": "Updated description",
     "fields": [...],
     "changelog": "Added phone_number field"
   }

**Response (200 OK):**

.. code-block:: json

   {
     "name": "user_profile",
     "current_version": "1.3.0",
     "previous_version": "1.2.0",
     "changelog": "Added phone_number field"
   }

DELETE /contracts/{name}
~~~~~~~~~~~~~~~~~~~~~~~~

Deprecate a contract (soft delete).

**Request:**

.. code-block:: bash

   curl -X DELETE http://localhost:8000/api/v1/contracts/legacy_users \
     -H "X-API-Key: your-key"

**Response (200 OK):**

.. code-block:: json

   {
     "name": "legacy_users",
     "status": "deprecated",
     "deprecated_at": "2024-01-10T14:30:00Z"
   }

Version Endpoints
-----------------

GET /contracts/{name}/versions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

List all versions of a contract.

**Response (200 OK):**

.. code-block:: json

   {
     "contract": "user_profile",
     "versions": [
       {
         "version": "1.2.0",
         "created_at": "2024-01-10T14:30:00Z",
         "created_by": "alice@example.com",
         "changelog": "Added email validation"
       },
       {
         "version": "1.1.0",
         "created_at": "2024-01-05T10:00:00Z",
         "created_by": "bob@example.com",
         "changelog": "Added age field"
       },
       {
         "version": "1.0.0",
         "created_at": "2024-01-01T00:00:00Z",
         "created_by": "alice@example.com",
         "changelog": "Initial version"
       }
     ]
   }

GET /contracts/{name}/versions/{version}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Get a specific version of a contract.

**Response (200 OK):**

Returns the contract as it existed at that version.

GET /contracts/{name}/diff
~~~~~~~~~~~~~~~~~~~~~~~~~~

Compare two versions of a contract.

**Query Parameters:**

- ``from``: Source version (default: previous version)
- ``to``: Target version (default: current version)

**Request:**

.. code-block:: bash

   curl "http://localhost:8000/api/v1/contracts/user_profile/diff?from=1.0.0&to=1.2.0" \
     -H "X-API-Key: your-key"

**Response (200 OK):**

.. code-block:: json

   {
     "contract": "user_profile",
     "from_version": "1.0.0",
     "to_version": "1.2.0",
     "breaking": false,
     "changes": [
       {
         "type": "field_added",
         "field": "age",
         "breaking": false
       },
       {
         "type": "constraint_added",
         "field": "email",
         "constraint": "format",
         "value": "email",
         "breaking": false
       }
     ]
   }

Validation Endpoints
--------------------

POST /contracts/{name}/validate
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Record a validation result.

**Request Body:**

.. code-block:: json

   {
     "version": "1.2.0",
     "status": "passed",
     "total_rows": 10000,
     "valid_rows": 9950,
     "error_count": 50,
     "errors": [
       {
         "field": "email",
         "error_type": "format",
         "count": 30
       },
       {
         "field": "age",
         "error_type": "range",
         "count": 20
       }
     ],
     "stats": {
       "email": {"null_count": 5, "unique_count": 9800}
     }
   }

**Response (201 Created):**

.. code-block:: json

   {
     "id": "val_abc123",
     "contract": "user_profile",
     "version": "1.2.0",
     "status": "passed",
     "validated_at": "2024-01-10T14:30:00Z"
   }

GET /contracts/{name}/validations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Get validation history for a contract.

**Query Parameters:**

- ``version``: Filter by version
- ``status``: Filter by status (passed, failed, warning)
- ``from_date``: Start date (ISO 8601)
- ``to_date``: End date (ISO 8601)
- ``limit``: Maximum results (default: 100)

**Response (200 OK):**

.. code-block:: json

   {
     "contract": "user_profile",
     "validations": [
       {
         "id": "val_abc123",
         "version": "1.2.0",
         "status": "passed",
         "total_rows": 10000,
         "valid_rows": 9950,
         "error_count": 50,
         "validated_at": "2024-01-10T14:30:00Z"
       }
     ],
     "total": 1
   }

Search Endpoints
----------------

GET /search
~~~~~~~~~~~

Search contracts by various criteria.

**Query Parameters:**

- ``q``: Full-text search query
- ``field_name``: Search for contracts containing a field
- ``field_type``: Filter by field type
- ``owner``: Filter by owner
- ``has_pii``: Filter contracts with PII fields (true/false)

**Request:**

.. code-block:: bash

   curl "http://localhost:8000/api/v1/search?q=user&has_pii=true" \
     -H "X-API-Key: your-key"

**Response (200 OK):**

.. code-block:: json

   {
     "results": [
       {
         "name": "user_profile",
         "description": "User profile data contract",
         "score": 0.95,
         "highlights": ["<em>user</em> profile"]
       }
     ],
     "total": 1
   }

Report Endpoints
----------------

GET /reports
~~~~~~~~~~~~

List available report types.

**Response (200 OK):**

.. code-block:: json

   {
     "report_types": [
       {"type": "analytics", "description": "Data quality metrics"},
       {"type": "ai_readiness", "description": "ML/AI readiness assessment"},
       {"type": "audit", "description": "Compliance audit report"},
       {"type": "readiness", "description": "Combined readiness report"}
     ]
   }

GET /contracts/{name}/reports/{type}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Generate a report for a contract.

**Path Parameters:**

- ``name``: Contract name
- ``type``: Report type (analytics, ai_readiness, audit, readiness)

**Query Parameters:**

- ``version``: Contract version (default: current)

**Response (200 OK):**

.. code-block:: json

   {
     "report_type": "analytics",
     "contract": "user_profile",
     "version": "1.2.0",
     "generated_at": "2024-01-10T14:30:00Z",
     "data": {
       "field_count": 10,
       "required_fields": 5,
       "pii_fields": 3,
       "constraint_coverage": 0.85
     }
   }

Approval Endpoints
------------------

POST /contracts/{name}/versions/{version}/approval-chain
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create an approval chain for a contract version.

**Request Body:**

.. code-block:: json

   {
     "approvers": [
       {"user": "alice@example.com", "role": "data-owner"},
       {"user": "bob@example.com", "role": "security"}
     ],
     "require_all": true
   }

GET /contracts/{name}/versions/{version}/approval-status
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Get approval status for a contract version.

**Response (200 OK):**

.. code-block:: json

   {
     "contract": "user_profile",
     "version": "2.0.0",
     "status": "pending",
     "approvals": [
       {
         "user": "alice@example.com",
         "role": "data-owner",
         "status": "approved",
         "decided_at": "2024-01-10T14:00:00Z"
       },
       {
         "user": "bob@example.com",
         "role": "security",
         "status": "pending"
       }
     ]
   }

POST /approvals/{approval_id}/decision
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Submit an approval decision.

**Request Body:**

.. code-block:: json

   {
     "decision": "approved",
     "comment": "LGTM, security review passed"
   }

GET /approvals/pending
~~~~~~~~~~~~~~~~~~~~~~

List pending approvals for the current user.

**Response (200 OK):**

.. code-block:: json

   {
     "pending": [
       {
         "id": "apr_xyz789",
         "contract": "order_events",
         "version": "2.0.0",
         "requested_at": "2024-01-10T10:00:00Z",
         "requested_by": "charlie@example.com"
       }
     ]
   }

Error Responses
---------------

All error responses follow this format:

.. code-block:: json

   {
     "error": {
       "code": "CONTRACT_NOT_FOUND",
       "message": "Contract 'unknown' not found",
       "details": {}
     }
   }

**Common Error Codes:**

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Code
     - HTTP Status
     - Description
   * - ``VALIDATION_ERROR``
     - 422
     - Request body validation failed
   * - ``CONTRACT_NOT_FOUND``
     - 404
     - Contract does not exist
   * - ``CONTRACT_EXISTS``
     - 409
     - Contract with name already exists
   * - ``VERSION_NOT_FOUND``
     - 404
     - Specified version does not exist
   * - ``UNAUTHORIZED``
     - 401
     - Missing or invalid authentication
   * - ``FORBIDDEN``
     - 403
     - Insufficient permissions
   * - ``STORAGE_ERROR``
     - 500
     - Storage backend error

Rate Limiting
-------------

Rate limits are returned in response headers:

.. code-block:: text

   X-RateLimit-Limit: 1000
   X-RateLimit-Remaining: 999
   X-RateLimit-Reset: 1704931200

When rate limited, you'll receive:

.. code-block:: json

   {
     "error": {
       "code": "RATE_LIMITED",
       "message": "Rate limit exceeded. Try again in 60 seconds.",
       "retry_after": 60
     }
   }
