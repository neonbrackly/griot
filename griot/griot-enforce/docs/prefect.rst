Prefect Integration
===================

griot-enforce provides Prefect tasks for validating data contracts within your
Prefect flows.

Installation
------------

.. code-block:: bash

   pip install griot-enforce[prefect]

This installs griot-enforce with Prefect as a dependency.

Available Tasks
---------------

griot-enforce provides both raw functions and pre-decorated Prefect tasks:

**Raw Functions** (for custom task configuration):

- ``validate_task``
- ``validate_local_task``
- ``check_residency_task``
- ``verify_masking_task``

**Pre-decorated Tasks** (ready to use):

- ``griot_validate``
- ``griot_validate_local``
- ``griot_check_residency``
- ``griot_verify_masking``

validate_task / griot_validate
------------------------------

Validates data against a registry contract.

.. py:function:: validate_task(contract_id, data, registry_url=None, version=None, fail_on_error=True, api_key=None, verify_masking=False, environment=None)

   :param contract_id: Contract ID in the registry.
   :type contract_id: str
   :param data: Data to validate.
   :type data: pd.DataFrame | list[dict]
   :param registry_url: Registry URL (or from env var).
   :type registry_url: str | None
   :param version: Specific contract version.
   :type version: str | None
   :param fail_on_error: Raise exception on failure. Default: True.
   :type fail_on_error: bool
   :param api_key: API key (or from env var).
   :type api_key: str | None
   :param verify_masking: Verify PII masking. Default: False.
   :type verify_masking: bool
   :param environment: Environment for masking checks.
   :type environment: str | None
   :returns: ValidationResult from griot-core.

**Example:**

.. code-block:: python

   from prefect import flow
   from griot_enforce.prefect import griot_validate

   @flow
   def customer_etl():
       df = extract_customers()
       griot_validate("customer-profile", df)
       load_customers(df)

validate_local_task / griot_validate_local
------------------------------------------

Validates data against a local contract file.

.. py:function:: validate_local_task(contract_path, data, fail_on_error=True)

   :param contract_path: Path to YAML contract file.
   :type contract_path: str
   :param data: Data to validate.
   :type data: pd.DataFrame | list[dict]
   :param fail_on_error: Raise exception on failure. Default: True.
   :type fail_on_error: bool
   :returns: ValidationResult from griot-core.

**Example:**

.. code-block:: python

   from prefect import flow
   from griot_enforce.prefect import griot_validate_local

   @flow
   def local_validation_flow():
       df = extract_data()
       griot_validate_local("./contracts/customer.yaml", df)
       process_data(df)

check_residency_task / griot_check_residency
--------------------------------------------

Checks data residency compliance with auto-detection from cloud URIs.

.. py:function:: check_residency_task(contract_id, region=None, destination=None, registry_url=None, version=None, api_key=None, fail_on_violation=False)

   :param contract_id: Contract ID in the registry.
   :type contract_id: str
   :param region: Explicit region to check.
   :type region: str | None
   :param destination: Cloud URI to auto-detect region.
   :type destination: str | None
   :param registry_url: Registry URL.
   :type registry_url: str | None
   :param version: Specific contract version.
   :type version: str | None
   :param api_key: API key.
   :type api_key: str | None
   :param fail_on_violation: Raise exception on violation. Default: False.
   :type fail_on_violation: bool
   :returns: Dictionary with compliance status.

**Example:**

.. code-block:: python

   from prefect import flow
   from griot_enforce.prefect import griot_check_residency

   @flow
   def eu_data_pipeline():
       # Auto-detect region from S3 URI
       griot_check_residency(
           "customer-profile",
           destination="s3://my-bucket-eu-west-1/data/",
           fail_on_violation=True,
       )
       # Proceed with data processing
       process_eu_data()

verify_masking_task / griot_verify_masking
------------------------------------------

Verifies PII masking compliance.

.. py:function:: verify_masking_task(contract_id, data, registry_url=None, version=None, api_key=None, environment=None, fail_on_violation=False)

   :param contract_id: Contract ID in the registry.
   :type contract_id: str
   :param data: Data to check.
   :type data: pd.DataFrame | list[dict]
   :param registry_url: Registry URL.
   :type registry_url: str | None
   :param version: Specific contract version.
   :type version: str | None
   :param api_key: API key.
   :type api_key: str | None
   :param environment: Environment name.
   :type environment: str | None
   :param fail_on_violation: Raise exception on violation. Default: False.
   :type fail_on_violation: bool
   :returns: Dictionary with masking verification results.

**Example:**

.. code-block:: python

   from prefect import flow
   from griot_enforce.prefect import griot_verify_masking

   @flow
   def staging_data_flow():
       df = extract_masked_data()

       # Verify masking in staging
       griot_verify_masking(
           "customer-profile",
           df,
           environment="staging",
           fail_on_violation=True,
       )

       load_to_staging(df)

Complete Flow Examples
----------------------

Basic ETL Flow
^^^^^^^^^^^^^^

.. code-block:: python

   from prefect import flow, task
   from griot_enforce.prefect import griot_validate
   import pandas as pd

   @task
   def extract_customers() -> pd.DataFrame:
       return pd.read_csv("s3://raw-data/customers.csv")

   @task
   def transform_customers(df: pd.DataFrame) -> pd.DataFrame:
       df["email"] = df["email"].str.lower()
       df["created_at"] = pd.to_datetime(df["created_at"])
       return df

   @task
   def load_customers(df: pd.DataFrame):
       df.to_parquet("s3://processed-data/customers.parquet")

   @flow
   def customer_etl_flow():
       # Extract
       raw_df = extract_customers()

       # Transform
       transformed_df = transform_customers(raw_df)

       # Validate
       result = griot_validate(
           "customer-profile",
           transformed_df,
           registry_url="https://registry.example.com",
       )

       # Load (only if validation passed)
       load_customers(transformed_df)

       return result

   if __name__ == "__main__":
       customer_etl_flow()

Flow with Error Handling
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from prefect import flow, task
   from griot_enforce.prefect import validate_task
   from griot_enforce import RuntimeValidationError
   import pandas as pd

   @task
   def extract_data() -> pd.DataFrame:
       return pd.read_parquet("s3://data/input.parquet")

   @task
   def handle_validation_failure(error: RuntimeValidationError):
       """Handle validation failures."""
       print(f"Validation failed for {error.contract_id}")
       print(f"Error count: {error.error_count}")
       print(f"Error rate: {error.error_rate:.2%}")
       # Send alert, log to monitoring, etc.

   @flow
   def robust_etl_flow():
       df = extract_data()

       try:
           result = validate_task(
               "my-contract",
               df,
               fail_on_error=True,
           )
           print(f"Validation passed: {result.row_count} rows")
       except RuntimeValidationError as e:
           handle_validation_failure(e)
           raise

Flow with Subflows
^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from prefect import flow
   from griot_enforce.prefect import (
       griot_validate,
       griot_check_residency,
       griot_verify_masking,
   )

   @flow
   def validate_and_check_compliance(df, contract_id: str, destination: str):
       """Subflow for validation and compliance checks."""

       # Validate data
       griot_validate(contract_id, df)

       # Check residency
       griot_check_residency(
           contract_id,
           destination=destination,
           fail_on_violation=True,
       )

       # Verify masking for non-prod
       griot_verify_masking(
           contract_id,
           df,
           environment="staging",
           fail_on_violation=True,
       )

   @flow
   def main_pipeline():
       df = extract_data()

       # Run compliance subflow
       validate_and_check_compliance(
           df,
           contract_id="customer-profile",
           destination="s3://staging-bucket-eu-west-1/data/",
       )

       # Continue with processing
       process_data(df)

Concurrent Validation
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from prefect import flow, task
   from griot_enforce.prefect import griot_validate
   import pandas as pd

   @task
   def extract_customers() -> pd.DataFrame:
       return pd.read_csv("customers.csv")

   @task
   def extract_orders() -> pd.DataFrame:
       return pd.read_csv("orders.csv")

   @task
   def extract_products() -> pd.DataFrame:
       return pd.read_csv("products.csv")

   @flow
   def parallel_validation_flow():
       # Extract data concurrently
       customers = extract_customers.submit()
       orders = extract_orders.submit()
       products = extract_products.submit()

       # Validate all datasets concurrently
       customer_result = griot_validate.submit(
           "customer-profile",
           customers.result(),
       )
       order_result = griot_validate.submit(
           "order-events",
           orders.result(),
       )
       product_result = griot_validate.submit(
           "product-catalog",
           products.result(),
       )

       # Wait for all validations
       return {
           "customers": customer_result.result(),
           "orders": order_result.result(),
           "products": product_result.result(),
       }

Custom Task Configuration
-------------------------

Use raw functions for custom task configuration:

.. code-block:: python

   from prefect import flow, task
   from griot_enforce.prefect import validate_task

   # Create custom task with retries and caching
   @task(
       retries=3,
       retry_delay_seconds=60,
       cache_key_fn=lambda *args: "validation-cache",
       cache_expiration=timedelta(hours=1),
   )
   def custom_validate(contract_id: str, data):
       return validate_task(
           contract_id,
           data,
           fail_on_error=True,
       )

   @flow
   def flow_with_custom_task():
       df = extract_data()
       custom_validate("my-contract", df)

Deployment Configuration
------------------------

Configure environment variables in your deployment:

.. code-block:: yaml

   # prefect.yaml
   deployments:
     - name: customer-etl
       entrypoint: flows/customer_etl.py:customer_etl_flow
       work_pool:
         name: default
       job_variables:
         env:
           GRIOT_REGISTRY_URL: "https://registry.example.com"
           GRIOT_API_KEY: "{{ prefect.blocks.secret.griot-api-key }}"

Or use Prefect blocks:

.. code-block:: python

   from prefect.blocks.system import Secret

   @flow
   def flow_with_blocks():
       api_key = Secret.load("griot-api-key").get()

       result = validate_task(
           "my-contract",
           data,
           api_key=api_key,
       )

Best Practices
--------------

1. **Use pre-decorated tasks** (``griot_validate``, etc.) for simple cases
2. **Use raw functions** with ``@task`` for custom retry/caching configuration
3. **Set ``fail_on_error=True``** to fail flows on validation errors
4. **Use ``fail_on_violation=True``** for residency and masking checks in production
5. **Leverage concurrent validation** with ``.submit()`` for multiple datasets
6. **Store API keys in Prefect secrets** rather than environment variables
7. **Use subflows** to encapsulate validation and compliance logic
