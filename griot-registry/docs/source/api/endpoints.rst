API Endpoints Overview
======================

Griot Registry exposes a RESTful API for managing data contracts and related
resources. All endpoints are prefixed with ``/api/v1`` by default.

Base URL
--------

.. code-block:: text

   http://localhost:8000/api/v1

Interactive Documentation
-------------------------

The API includes built-in interactive documentation:

- **Swagger UI**: ``/docs`` - Interactive API explorer
- **ReDoc**: ``/redoc`` - Alternative documentation view
- **OpenAPI Schema**: ``/openapi.json`` - Machine-readable API specification

Endpoint Categories
-------------------

.. list-table::
   :header-rows: 1
   :widths: 20 40 40

   * - Category
     - Base Path
     - Description
   * - Health
     - ``/health``
     - Service health checks
   * - Auth
     - ``/auth``
     - Authentication and token management
   * - Contracts
     - ``/contracts``
     - Contract CRUD and versioning
   * - Schemas
     - ``/schemas``
     - Schema catalog queries
   * - Validations
     - ``/validations``
     - Validation record management
   * - Runs
     - ``/runs``
     - Pipeline run tracking
   * - Issues
     - ``/issues``
     - Issue management
   * - Comments
     - ``/comments``
     - Collaboration comments
   * - Approvals
     - ``/approvals``
     - Approval workflows
   * - Search
     - ``/search``
     - Full-text search

Health Endpoints
----------------

These endpoints are used for monitoring and orchestration:

.. list-table::
   :header-rows: 1
   :widths: 15 25 60

   * - Method
     - Path
     - Description
   * - GET
     - ``/health``
     - Basic health check with status
   * - GET
     - ``/health/live``
     - Kubernetes liveness probe
   * - GET
     - ``/health/ready``
     - Kubernetes readiness probe (checks MongoDB)

Common Response Formats
-----------------------

Success Response
^^^^^^^^^^^^^^^^

Most endpoints return JSON with the resource data:

.. code-block:: json

   {
       "id": "contract-123",
       "name": "user-events",
       "version": "1.0.0",
       "status": "active",
       "created_at": "2024-01-15T10:30:00Z"
   }

List Response
^^^^^^^^^^^^^

List endpoints return paginated results:

.. code-block:: text

   {
       "items": [...],
       "total": 42,
       "limit": 50,
       "offset": 0
   }

Error Response
^^^^^^^^^^^^^^

Errors follow a consistent format:

.. code-block:: json

   {
       "detail": {
           "code": "NOT_FOUND",
           "message": "Contract 'unknown-id' not found"
       }
   }

Common error codes:

- ``NOT_FOUND``: Resource does not exist
- ``VALIDATION_ERROR``: Request validation failed
- ``ALREADY_EXISTS``: Resource already exists
- ``NOT_AUTHORIZED``: User lacks permission
- ``BREAKING_CHANGE``: Update would cause breaking change

HTTP Status Codes
-----------------

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Code
     - Meaning
   * - 200 OK
     - Request succeeded
   * - 201 Created
     - Resource created successfully
   * - 204 No Content
     - Request succeeded, no response body
   * - 400 Bad Request
     - Invalid request data
   * - 401 Unauthorized
     - Authentication required
   * - 403 Forbidden
     - Insufficient permissions
   * - 404 Not Found
     - Resource not found
   * - 409 Conflict
     - Resource conflict (e.g., duplicate)
   * - 422 Unprocessable Entity
     - Validation error
   * - 500 Internal Server Error
     - Server error

Pagination
----------

List endpoints support pagination via query parameters:

.. list-table::
   :header-rows: 1
   :widths: 20 20 60

   * - Parameter
     - Default
     - Description
   * - ``limit``
     - 50
     - Maximum items to return (1-100)
   * - ``offset``
     - 0
     - Number of items to skip

Example:

.. code-block:: bash

   # Get page 2 with 20 items per page
   curl "http://localhost:8000/api/v1/contracts?limit=20&offset=20"

Filtering
---------

Many list endpoints support filtering via query parameters. Common filters:

.. code-block:: bash

   # Filter contracts by status
   curl "http://localhost:8000/api/v1/contracts?status=active"

   # Filter by owner
   curl "http://localhost:8000/api/v1/contracts?owner=data-team"

   # Multiple filters
   curl "http://localhost:8000/api/v1/contracts?status=active&owner=data-team"

Rate Limiting
-------------

The API does not implement rate limiting by default. For production deployments,
configure rate limiting at the reverse proxy level (nginx, Kong, etc.).

CORS
----

Cross-Origin Resource Sharing (CORS) is configured via the ``CORS_ORIGINS``
environment variable. By default, all origins are allowed for development.

For production:

.. code-block:: bash

   export CORS_ORIGINS='["https://app.example.com", "https://admin.example.com"]'

API Versioning
--------------

The API uses URL path versioning. The current version is ``v1``:

.. code-block:: text

   /api/v1/contracts
   /api/v1/schemas
   /api/v1/search

Future versions will be accessible at ``/api/v2``, etc. Breaking changes will
only be introduced in new API versions.
