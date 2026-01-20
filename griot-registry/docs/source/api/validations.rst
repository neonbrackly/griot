Validations API
===============

The Validations API manages validation records, tracking the history of contract
validations over time. This is useful for monitoring data quality trends and
compliance reporting.

Endpoints
---------

Record Validation
^^^^^^^^^^^^^^^^^

.. code-block:: text

   POST /api/v1/validations

Record a validation result for a contract.

**Request Body:**

.. code-block:: json

   {
       "contract_id": "contract-123",
       "run_id": "run-456",
       "status": "passed",
       "errors": [],
       "warnings": [
           {
               "code": "FRESHNESS_WARNING",
               "message": "Data is 2 hours old, SLA is 1 hour"
           }
       ],
       "metrics": {
           "rows_validated": 10000,
           "rows_passed": 9950,
           "rows_failed": 50,
           "duration_ms": 1234
       },
       "metadata": {
           "source": "airflow",
           "dag_id": "daily_validation"
       }
   }

**Response:** (201 Created)

.. code-block:: text

   {
       "id": "validation-789",
       "contract_id": "contract-123",
       "run_id": "run-456",
       "status": "passed",
       "errors": [],
       "warnings": [...],
       "metrics": {...},
       "metadata": {...},
       "recorded_at": "2024-01-15T10:30:00Z",
       "recorded_by": "service-account"
   }

**Validation Status Values:**

- ``passed``: Validation successful with no errors
- ``failed``: Validation found errors
- ``warning``: Passed with warnings
- ``skipped``: Validation was skipped

**Example:**

.. code-block:: bash

   curl -X POST http://localhost:8000/api/v1/validations \
       -H "Content-Type: application/json" \
       -H "X-API-Key: $API_KEY" \
       -d @validation-result.json

List Validations
^^^^^^^^^^^^^^^^

.. code-block:: text

   GET /api/v1/validations

List validation records with optional filtering.

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
     - Filter by status (passed, failed, warning, skipped)
   * - ``start_date``
     - datetime
     - Filter validations after this date
   * - ``end_date``
     - datetime
     - Filter validations before this date
   * - ``limit``
     - int
     - Maximum records to return (default: 50)
   * - ``offset``
     - int
     - Number to skip (default: 0)

**Response:**

.. code-block:: json

   {
       "items": [
           {
               "id": "validation-789",
               "contract_id": "contract-123",
               "status": "passed",
               "recorded_at": "2024-01-15T10:30:00Z"
           }
       ],
       "total": 100,
       "limit": 50,
       "offset": 0
   }

**Example:**

.. code-block:: bash

   # Get validations for a specific contract
   curl "http://localhost:8000/api/v1/validations?contract_id=contract-123"

   # Get failed validations in the last week
   curl "http://localhost:8000/api/v1/validations?status=failed&start_date=2024-01-08"

Get Validation Statistics
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: text

   GET /api/v1/validations/stats/{contract_id}

Get aggregated validation statistics for a contract.

**Path Parameters:**

- ``contract_id``: The contract ID

**Query Parameters:**

.. list-table::
   :header-rows: 1
   :widths: 20 15 65

   * - Parameter
     - Type
     - Description
   * - ``days``
     - int
     - Number of days to include (default: 30)
   * - ``granularity``
     - string
     - Aggregation granularity: hour, day, week (default: day)

**Response:**

.. code-block:: json

   {
       "contract_id": "contract-123",
       "period_start": "2023-12-15T00:00:00Z",
       "period_end": "2024-01-15T00:00:00Z",
       "total_validations": 720,
       "passed": 695,
       "failed": 20,
       "warning": 5,
       "pass_rate": 96.5,
       "avg_duration_ms": 1150,
       "by_day": [
           {
               "date": "2024-01-15",
               "total": 24,
               "passed": 23,
               "failed": 1,
               "pass_rate": 95.8
           }
       ],
       "common_errors": [
           {
               "code": "NULL_VALUE",
               "count": 15,
               "message": "Required field 'user_id' is null"
           }
       ]
   }

**Example:**

.. code-block:: bash

   # Get 30-day stats
   curl http://localhost:8000/api/v1/validations/stats/contract-123

   # Get 7-day stats with hourly granularity
   curl "http://localhost:8000/api/v1/validations/stats/contract-123?days=7&granularity=hour"

Validation Record Object
------------------------

.. code-block:: json

   {
       "id": "string (auto-generated)",
       "contract_id": "string (required)",
       "run_id": "string (optional, links to a run)",
       "status": "string (passed|failed|warning|skipped)",
       "errors": [
           {
               "code": "string",
               "message": "string",
               "path": "string (optional)",
               "row_count": "integer (optional)"
           }
       ],
       "warnings": [
           {
               "code": "string",
               "message": "string"
           }
       ],
       "metrics": {
           "rows_validated": "integer",
           "rows_passed": "integer",
           "rows_failed": "integer",
           "duration_ms": "integer"
       },
       "metadata": "object (optional, custom data)",
       "recorded_at": "datetime (auto-generated)",
       "recorded_by": "string (from auth)"
   }

Integration Examples
--------------------

Airflow Integration
^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from airflow.decorators import task
   from griot_registry import SyncRegistryClient

   @task
   def validate_and_record(contract_id: str, run_id: str):
       with SyncRegistryClient("http://registry:8000", api_key=API_KEY) as client:
           # Your validation logic here
           errors = run_validation()

           # Record the result
           client.record_validation(
               contract_id=contract_id,
               run_id=run_id,
               status="passed" if not errors else "failed",
               errors=errors,
               metrics={
                   "rows_validated": 10000,
                   "rows_passed": 9950,
                   "rows_failed": 50,
               }
           )

Great Expectations Integration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from great_expectations.checkpoint import Checkpoint
   from griot_registry import SyncRegistryClient

   def record_ge_results(checkpoint_result, contract_id: str):
       with SyncRegistryClient("http://registry:8000") as client:
           for result in checkpoint_result.run_results.values():
               validation_result = result.validation_result

               errors = []
               for r in validation_result.results:
                   if not r.success:
                       errors.append({
                           "code": r.expectation_config.expectation_type,
                           "message": r.result.get("partial_unexpected_list", [])[:5]
                       })

               client.record_validation(
                   contract_id=contract_id,
                   status="passed" if validation_result.success else "failed",
                   errors=errors,
                   metrics={
                       "expectations_total": len(validation_result.results),
                       "expectations_passed": sum(1 for r in validation_result.results if r.success),
                   }
               )
