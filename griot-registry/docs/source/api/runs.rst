Runs API
========

The Runs API tracks pipeline executions and their associated validations. Runs
provide a way to group related validations and track the overall health of data
pipelines.

Endpoints
---------

Create Run
^^^^^^^^^^

.. code-block:: text

   POST /api/v1/runs

Create a new run record.

**Request Body:**

.. code-block:: json

   {
       "contract_id": "contract-123",
       "pipeline_name": "daily-etl",
       "pipeline_id": "airflow-dag-123",
       "status": "running",
       "metadata": {
           "dag_id": "user_events_daily",
           "execution_date": "2024-01-15",
           "triggered_by": "scheduler"
       }
   }

**Response:** (201 Created)

.. code-block:: text

   {
       "id": "run-456",
       "contract_id": "contract-123",
       "pipeline_name": "daily-etl",
       "pipeline_id": "airflow-dag-123",
       "status": "running",
       "metadata": {...},
       "started_at": "2024-01-15T10:00:00Z",
       "completed_at": null,
       "created_by": "service-account"
   }

**Run Status Values:**

- ``pending``: Run is scheduled but not started
- ``running``: Run is currently executing
- ``completed``: Run finished successfully
- ``failed``: Run encountered an error
- ``cancelled``: Run was manually cancelled

**Example:**

.. code-block:: bash

   curl -X POST http://localhost:8000/api/v1/runs \
       -H "Content-Type: application/json" \
       -H "X-API-Key: $API_KEY" \
       -d '{
           "contract_id": "contract-123",
           "pipeline_name": "daily-etl",
           "status": "running"
       }'

Get Run
^^^^^^^

.. code-block:: text

   GET /api/v1/runs/{run_id}

Retrieve a specific run by ID.

**Path Parameters:**

- ``run_id``: The run's unique identifier

**Response:**

Full run object including all validations associated with the run.

**Example:**

.. code-block:: bash

   curl http://localhost:8000/api/v1/runs/run-456

Update Run
^^^^^^^^^^

.. code-block:: text

   PATCH /api/v1/runs/{run_id}

Update a run's status or metadata.

**Path Parameters:**

- ``run_id``: The run's unique identifier

**Request Body:**

.. code-block:: json

   {
       "status": "completed",
       "metadata": {
           "rows_processed": 50000,
           "duration_seconds": 120
       }
   }

**Response:**

The updated run object.

**Example:**

.. code-block:: bash

   curl -X PATCH http://localhost:8000/api/v1/runs/run-456 \
       -H "Content-Type: application/json" \
       -H "X-API-Key: $API_KEY" \
       -d '{"status": "completed"}'

List Runs
^^^^^^^^^

.. code-block:: text

   GET /api/v1/runs

List runs with optional filtering.

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
   * - ``pipeline_name``
     - string
     - Filter by pipeline name
   * - ``status``
     - string
     - Filter by status
   * - ``start_date``
     - datetime
     - Filter runs started after this date
   * - ``end_date``
     - datetime
     - Filter runs started before this date
   * - ``limit``
     - int
     - Maximum runs to return (default: 50)
   * - ``offset``
     - int
     - Number to skip (default: 0)

**Response:**

.. code-block:: json

   {
       "items": [
           {
               "id": "run-456",
               "contract_id": "contract-123",
               "pipeline_name": "daily-etl",
               "status": "completed",
               "started_at": "2024-01-15T10:00:00Z",
               "completed_at": "2024-01-15T10:05:00Z"
           }
       ],
       "total": 100,
       "limit": 50,
       "offset": 0
   }

**Example:**

.. code-block:: bash

   # List runs for a contract
   curl "http://localhost:8000/api/v1/runs?contract_id=contract-123"

   # List failed runs
   curl "http://localhost:8000/api/v1/runs?status=failed"

Run Object Schema
-----------------

.. code-block:: json

   {
       "id": "string (auto-generated)",
       "contract_id": "string (required)",
       "pipeline_name": "string (optional)",
       "pipeline_id": "string (optional, external reference)",
       "status": "string (pending|running|completed|failed|cancelled)",
       "started_at": "datetime",
       "completed_at": "datetime (null if running)",
       "metadata": "object (optional)",
       "created_by": "string (from auth)",
       "validations": [
           {
               "id": "validation-id",
               "status": "passed",
               "recorded_at": "datetime"
           }
       ]
   }

Integration Patterns
--------------------

Airflow DAG Integration
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from airflow import DAG
   from airflow.decorators import task
   from griot_registry import SyncRegistryClient
   from datetime import datetime

   @task
   def start_run(contract_id: str, **context) -> str:
       with SyncRegistryClient("http://registry:8000", api_key=API_KEY) as client:
           run = client.create_run(
               contract_id=contract_id,
               pipeline_name=context['dag'].dag_id,
               pipeline_id=context['run_id'],
               status="running",
               metadata={
                   "execution_date": str(context['execution_date']),
                   "try_number": context['ti'].try_number,
               }
           )
           return run["id"]

   @task
   def complete_run(run_id: str, status: str = "completed"):
       with SyncRegistryClient("http://registry:8000", api_key=API_KEY) as client:
           client.update_run(run_id, status=status)

   with DAG("user_events_validation", schedule_interval="@daily") as dag:
       run_id = start_run(contract_id="user-events-contract")

       # ... validation tasks ...

       complete_run(run_id)

dbt Integration
^^^^^^^^^^^^^^^

.. code-block:: python

   # dbt post-hook script
   import os
   from griot_registry import SyncRegistryClient

   def on_run_end(results):
       with SyncRegistryClient(os.environ["REGISTRY_URL"]) as client:
           run_id = os.environ.get("GRIOT_RUN_ID")

           if run_id:
               status = "completed" if results.success else "failed"
               client.update_run(
                   run_id,
                   status=status,
                   metadata={
                       "models_run": len(results.results),
                       "models_success": sum(1 for r in results.results if r.status == "success"),
                   }
               )

Prefect Integration
^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from prefect import flow, task
   from griot_registry import SyncRegistryClient

   @task
   def create_griot_run(contract_id: str, flow_run_name: str) -> str:
       with SyncRegistryClient("http://registry:8000") as client:
           run = client.create_run(
               contract_id=contract_id,
               pipeline_name=flow_run_name,
               status="running"
           )
           return run["id"]

   @flow
   def data_pipeline(contract_id: str):
       run_id = create_griot_run(contract_id, "data_pipeline")

       try:
           # ... your pipeline tasks ...
           pass
       except Exception as e:
           with SyncRegistryClient("http://registry:8000") as client:
               client.update_run(run_id, status="failed")
           raise
       else:
           with SyncRegistryClient("http://registry:8000") as client:
               client.update_run(run_id, status="completed")
