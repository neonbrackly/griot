Issues API
==========

The Issues API provides issue tracking for data contracts. Issues can be created
automatically from validation failures or manually by users.

Endpoints
---------

Create Issue
^^^^^^^^^^^^

.. code-block:: text

   POST /api/v1/issues

Create a new issue.

**Request Body:**

.. code-block:: json

   {
       "contract_id": "contract-123",
       "run_id": "run-456",
       "title": "Missing required field 'user_id'",
       "description": "The user_id field is null in 5% of records",
       "severity": "error",
       "category": "quality",
       "affected_field": "user_id",
       "affected_schema": "UserEvent",
       "metadata": {
           "sample_records": ["rec-1", "rec-2"],
           "affected_percentage": 5.2
       }
   }

**Response:** (201 Created)

.. code-block:: json

   {
       "id": "issue-789",
       "contract_id": "contract-123",
       "run_id": "run-456",
       "title": "Missing required field 'user_id'",
       "description": "...",
       "severity": "error",
       "category": "quality",
       "status": "open",
       "affected_field": "user_id",
       "affected_schema": "UserEvent",
       "created_at": "2024-01-15T10:30:00Z",
       "created_by": "service-account"
   }

**Severity Values:**

- ``error``: Critical issue that must be resolved
- ``warning``: Important issue that should be addressed
- ``info``: Informational, no immediate action required

**Category Values:**

- ``quality``: Data quality issue
- ``schema``: Schema violation
- ``sla``: SLA breach
- ``compliance``: Compliance concern

**Example:**

.. code-block:: bash

   curl -X POST http://localhost:8000/api/v1/issues \
       -H "Content-Type: application/json" \
       -H "Authorization: Bearer $TOKEN" \
       -d '{
           "contract_id": "contract-123",
           "title": "SLA breach: data freshness",
           "severity": "warning",
           "category": "sla"
       }'

Get Issue
^^^^^^^^^

.. code-block:: text

   GET /api/v1/issues/{issue_id}

Retrieve a specific issue by ID.

**Path Parameters:**

- ``issue_id``: The issue's unique identifier

**Response:**

Full issue object.

**Example:**

.. code-block:: bash

   curl http://localhost:8000/api/v1/issues/issue-789

Update Issue
^^^^^^^^^^^^

.. code-block:: text

   PATCH /api/v1/issues/{issue_id}

Update an issue's details.

**Path Parameters:**

- ``issue_id``: The issue's unique identifier

**Request Body:**

.. code-block:: json

   {
       "title": "Updated title",
       "severity": "warning",
       "status": "in_progress",
       "assignee": "user-123"
   }

**Response:**

The updated issue object.

**Example:**

.. code-block:: bash

   curl -X PATCH http://localhost:8000/api/v1/issues/issue-789 \
       -H "Content-Type: application/json" \
       -H "Authorization: Bearer $TOKEN" \
       -d '{"assignee": "user-123", "status": "in_progress"}'

Resolve Issue
^^^^^^^^^^^^^

.. code-block:: text

   POST /api/v1/issues/{issue_id}/resolve

Mark an issue as resolved.

**Path Parameters:**

- ``issue_id``: The issue's unique identifier

**Request Body:**

.. code-block:: json

   {
       "resolution": "Fixed null handling in ETL pipeline. Deployed in PR #456."
   }

**Response:**

.. code-block:: json

   {
       "id": "issue-789",
       "status": "resolved",
       "resolution": "Fixed null handling in ETL pipeline. Deployed in PR #456.",
       "resolved_by": "user-123",
       "resolved_at": "2024-01-16T14:00:00Z"
   }

**Example:**

.. code-block:: bash

   curl -X POST http://localhost:8000/api/v1/issues/issue-789/resolve \
       -H "Content-Type: application/json" \
       -H "Authorization: Bearer $TOKEN" \
       -d '{"resolution": "Fixed in PR #456"}'

List Issues
^^^^^^^^^^^

.. code-block:: text

   GET /api/v1/issues

List issues with optional filtering.

**Query Parameters:**

.. list-table::
   :header-rows: 1
   :widths: 20 15 65

   * - Parameter
     - Type
     - Description
   * - ``contract_id``
     - string
     - Filter by contract ID
   * - ``run_id``
     - string
     - Filter by run ID
   * - ``status``
     - string
     - Filter by status: open, in_progress, resolved
   * - ``severity``
     - string
     - Filter by severity: error, warning, info
   * - ``limit``
     - int
     - Maximum issues to return (default: 50)
   * - ``offset``
     - int
     - Number to skip (default: 0)

**Response:**

.. code-block:: json

   {
       "items": [
           {
               "id": "issue-789",
               "contract_id": "contract-123",
               "title": "Missing required field",
               "severity": "error",
               "status": "open",
               "created_at": "2024-01-15T10:30:00Z"
           }
       ],
       "total": 15,
       "limit": 50,
       "offset": 0
   }

**Example:**

.. code-block:: bash

   # List open issues for a contract
   curl "http://localhost:8000/api/v1/issues?contract_id=contract-123&status=open"

   # List all error-severity issues
   curl "http://localhost:8000/api/v1/issues?severity=error"

Issue Object Schema
-------------------

.. code-block:: json

   {
       "id": "string (auto-generated)",
       "contract_id": "string (required)",
       "run_id": "string (optional)",
       "title": "string (required)",
       "description": "string (optional)",
       "severity": "string (error|warning|info)",
       "category": "string (quality|schema|sla|compliance)",
       "status": "string (open|in_progress|resolved)",
       "affected_field": "string (optional)",
       "affected_schema": "string (optional)",
       "assignee": "string (optional, user ID)",
       "resolution": "string (set when resolved)",
       "resolved_by": "string (set when resolved)",
       "resolved_at": "datetime (set when resolved)",
       "metadata": "object (optional)",
       "created_at": "datetime",
       "updated_at": "datetime",
       "created_by": "string"
   }

Automatic Issue Creation
------------------------

Issues can be automatically created from validation failures:

.. code-block:: python

   from griot_registry import SyncRegistryClient

   def process_validation_result(client, contract_id, run_id, validation_result):
       # Record the validation
       client.record_validation(
           contract_id=contract_id,
           run_id=run_id,
           status="failed" if validation_result.errors else "passed",
           errors=validation_result.errors,
       )

       # Create issues for errors
       for error in validation_result.errors:
           client.create_issue(
               contract_id=contract_id,
               run_id=run_id,
               title=f"{error.code}: {error.field}",
               description=error.message,
               severity="error",
               category="quality",
               affected_field=error.field,
               affected_schema=error.schema_name,
           )
