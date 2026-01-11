Apache Airflow Integration
==========================

griot-enforce provides native Apache Airflow operators and sensors for validating
data contracts within your DAGs.

Installation
------------

.. code-block:: bash

   pip install griot-enforce[airflow]

This installs griot-enforce with Apache Airflow as a dependency.

Operators
---------

GriotValidateOperator
^^^^^^^^^^^^^^^^^^^^^

Validates data against a Griot contract. Fails the task if validation fails.

.. py:class:: GriotValidateOperator(task_id, contract_id, data_path, registry_url=None, version=None, fail_on_error=True, error_threshold=None, verify_masking=False, environment=None, **kwargs)

   :param task_id: Airflow task ID.
   :type task_id: str
   :param contract_id: Contract ID in the registry.
   :type contract_id: str
   :param data_path: Path to data file. Supports Jinja templating.
   :type data_path: str
   :param registry_url: Registry URL (or from ``GRIOT_REGISTRY_URL`` env var).
   :type registry_url: str | None
   :param version: Specific contract version.
   :type version: str | None
   :param fail_on_error: Fail task on validation error. Default: True.
   :type fail_on_error: bool
   :param error_threshold: Fail only if error rate exceeds this threshold.
   :type error_threshold: float | None
   :param verify_masking: Verify PII masking compliance. Default: False.
   :type verify_masking: bool
   :param environment: Environment name for masking checks.
   :type environment: str | None

   **Template Fields:** ``data_path``, ``contract_id``, ``version``, ``environment``

   **UI Color:** Light green (#e4f0e8)

**Basic Example:**

.. code-block:: python

   from airflow import DAG
   from airflow.operators.python import PythonOperator
   from griot_enforce.airflow import GriotValidateOperator
   from datetime import datetime

   with DAG(
       "customer_etl",
       start_date=datetime(2024, 1, 1),
       schedule_interval="@daily",
   ) as dag:

       extract = PythonOperator(
           task_id="extract_customers",
           python_callable=extract_customers,
       )

       validate = GriotValidateOperator(
           task_id="validate_customers",
           contract_id="customer-profile",
           data_path="{{ ti.xcom_pull('extract_customers') }}",
           registry_url="https://registry.example.com",
       )

       load = PythonOperator(
           task_id="load_customers",
           python_callable=load_customers,
       )

       extract >> validate >> load

**With Error Threshold:**

.. code-block:: python

   # Allow up to 1% error rate
   validate = GriotValidateOperator(
       task_id="validate_customers",
       contract_id="customer-profile",
       data_path="/data/customers.parquet",
       error_threshold=0.01,  # 1% threshold
   )

**With Masking Verification:**

.. code-block:: python

   validate = GriotValidateOperator(
       task_id="validate_customers",
       contract_id="customer-profile",
       data_path="/data/customers.csv",
       verify_masking=True,
       environment="{{ var.value.environment }}",  # From Airflow variables
   )

GriotResidencyOperator
^^^^^^^^^^^^^^^^^^^^^^

Checks data residency compliance before allowing data writes.

.. py:class:: GriotResidencyOperator(task_id, contract_id, destination=None, region=None, registry_url=None, version=None, fail_on_violation=True, **kwargs)

   :param task_id: Airflow task ID.
   :type task_id: str
   :param contract_id: Contract ID in the registry.
   :type contract_id: str
   :param destination: Cloud URI to auto-detect region (e.g., ``s3://bucket-eu-west-1/``).
   :type destination: str | None
   :param region: Explicit region to check.
   :type region: str | None
   :param registry_url: Registry URL.
   :type registry_url: str | None
   :param version: Specific contract version.
   :type version: str | None
   :param fail_on_violation: Fail task on residency violation. Default: True.
   :type fail_on_violation: bool

   **Template Fields:** ``contract_id``, ``version``, ``destination``, ``region``

   **UI Color:** Light pink (#f0e4e8)

**Example:**

.. code-block:: python

   from griot_enforce.airflow import GriotResidencyOperator

   check_residency = GriotResidencyOperator(
       task_id="check_residency",
       contract_id="customer-profile",
       destination="{{ params.output_path }}",
   )

   extract >> validate >> check_residency >> load_to_s3

Sensors
-------

GriotFreshnessSensor
^^^^^^^^^^^^^^^^^^^^

Waits for fresh data based on contract validation history in the registry.

.. py:class:: GriotFreshnessSensor(task_id, contract_id, max_age_minutes=60, registry_url=None, version=None, require_passed=True, **kwargs)

   :param task_id: Airflow task ID.
   :type task_id: str
   :param contract_id: Contract ID in the registry.
   :type contract_id: str
   :param max_age_minutes: Maximum age of validation in minutes. Default: 60.
   :type max_age_minutes: int
   :param registry_url: Registry URL.
   :type registry_url: str | None
   :param version: Specific contract version.
   :type version: str | None
   :param require_passed: Only consider passed validations. Default: True.
   :type require_passed: bool

   **Template Fields:** ``contract_id``, ``version``

**Example:**

.. code-block:: python

   from griot_enforce.airflow import GriotFreshnessSensor

   with DAG("downstream_pipeline", ...) as dag:

       wait_for_customers = GriotFreshnessSensor(
           task_id="wait_for_customers",
           contract_id="customer-profile",
           max_age_minutes=120,  # Wait for data validated within 2 hours
           poke_interval=300,    # Check every 5 minutes
           timeout=3600,         # Timeout after 1 hour
       )

       process = PythonOperator(
           task_id="process_customers",
           python_callable=process_customers,
       )

       wait_for_customers >> process

Complete DAG Example
--------------------

Here's a complete example DAG with validation, residency checking, and freshness sensing:

.. code-block:: python

   from airflow import DAG
   from airflow.operators.python import PythonOperator
   from airflow.providers.amazon.aws.operators.s3 import S3CreateObjectOperator
   from griot_enforce.airflow import (
       GriotValidateOperator,
       GriotResidencyOperator,
       GriotFreshnessSensor,
   )
   from datetime import datetime, timedelta

   default_args = {
       "owner": "data-team",
       "retries": 1,
       "retry_delay": timedelta(minutes=5),
   }

   with DAG(
       "customer_data_pipeline",
       default_args=default_args,
       start_date=datetime(2024, 1, 1),
       schedule_interval="@daily",
       catchup=False,
   ) as dag:

       # Wait for upstream data to be fresh
       wait_for_raw_data = GriotFreshnessSensor(
           task_id="wait_for_raw_data",
           contract_id="raw-customer-events",
           max_age_minutes=60,
           poke_interval=120,
       )

       # Extract and transform
       extract = PythonOperator(
           task_id="extract_transform",
           python_callable=extract_and_transform,
       )

       # Validate transformed data
       validate = GriotValidateOperator(
           task_id="validate_data",
           contract_id="customer-profile",
           data_path="{{ ti.xcom_pull('extract_transform') }}",
           error_threshold=0.001,  # 0.1% threshold
           verify_masking=True,
           environment="production",
       )

       # Check residency before writing to S3
       check_residency = GriotResidencyOperator(
           task_id="check_residency",
           contract_id="customer-profile",
           destination="s3://customer-data-eu-west-1/profiles/",
       )

       # Load to S3
       load = S3CreateObjectOperator(
           task_id="load_to_s3",
           s3_bucket="customer-data-eu-west-1",
           s3_key="profiles/{{ ds }}/data.parquet",
           data="{{ ti.xcom_pull('extract_transform') }}",
       )

       wait_for_raw_data >> extract >> validate >> check_residency >> load

XCom Integration
----------------

The ``GriotValidateOperator`` pushes the validation result to XCom:

.. code-block:: python

   # Access validation result in downstream tasks
   def process_result(**context):
       result = context["ti"].xcom_pull(task_ids="validate_data")
       print(f"Validated {result['row_count']} rows")
       print(f"Error rate: {result['error_rate']:.2%}")
       if result.get('masking_result'):
           print(f"Masking compliant: {result['masking_result']['compliant']}")

Connection Configuration
------------------------

You can configure the registry URL via Airflow connections:

1. Create a connection with ID ``griot_registry``
2. Set the host to your registry URL
3. Set the password to your API key

Then reference it in your operators:

.. code-block:: python

   from airflow.hooks.base import BaseHook

   conn = BaseHook.get_connection("griot_registry")

   validate = GriotValidateOperator(
       task_id="validate",
       contract_id="customer-profile",
       data_path="/data/customers.csv",
       registry_url=conn.host,
   )

Best Practices
--------------

1. **Use error thresholds** for large datasets to allow minor data quality issues
2. **Enable masking verification** in non-production environments
3. **Use freshness sensors** to ensure upstream data dependencies are met
4. **Check residency** before writing to cloud storage to ensure compliance
5. **Template contract versions** to pin versions in production DAGs
