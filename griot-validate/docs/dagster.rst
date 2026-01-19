Dagster Integration
===================

griot-enforce provides native Dagster resources and decorators for validating
data contracts within your Dagster pipelines.

Installation
------------

.. code-block:: bash

   pip install griot-enforce[dagster]

This installs griot-enforce with Dagster as a dependency.

GriotResource
-------------

The ``GriotResource`` is a Dagster ``ConfigurableResource`` that provides validation
capabilities to your assets and ops.

.. py:class:: GriotResource(registry_url=None, api_key=None, cache_ttl=300, report_results=True)

   Dagster resource for Griot validation.

   :param registry_url: Registry URL.
   :type registry_url: str | None
   :param api_key: API key for registry.
   :type api_key: str | None
   :param cache_ttl: Contract cache TTL in seconds. Default: 300.
   :type cache_ttl: int
   :param report_results: Report results to registry. Default: True.
   :type report_results: bool

**Methods:**

- ``validate(contract_id, data, version=None, fail_on_error=True, verify_masking=False, environment=None)``
- ``validate_local(contract_path, data, fail_on_error=True)``
- ``get_contract(contract_id, version=None)``
- ``check_residency(contract_id, region=None, destination=None, version=None, fail_on_violation=False)``
- ``verify_masking(contract_id, data, version=None, environment=None, fail_on_violation=False)``

Basic Usage
-----------

**Resource Definition:**

.. code-block:: python

   from dagster import Definitions, asset, EnvVar
   from griot_enforce.dagster import GriotResource

   @asset
   def customers(griot: GriotResource):
       """Extract and validate customer data."""
       df = extract_customers()

       # Validate against contract
       result = griot.validate("customer-profile", df)

       if result.passed:
           return df
       else:
           raise ValueError(f"Validation failed: {result.error_count} errors")

   defs = Definitions(
       assets=[customers],
       resources={
           "griot": GriotResource(
               registry_url=EnvVar("GRIOT_REGISTRY_URL"),
               api_key=EnvVar("GRIOT_API_KEY"),
           )
       },
   )

**With Masking Verification:**

.. code-block:: python

   @asset
   def customer_profiles(griot: GriotResource):
       df = extract_customer_profiles()

       # Validate with masking verification
       result = griot.validate(
           "customer-profile",
           df,
           verify_masking=True,
           environment="staging",
       )

       return df

**Residency Check:**

.. code-block:: python

   @asset
   def eu_customers(griot: GriotResource):
       df = extract_eu_customers()

       # Check residency before processing
       residency = griot.check_residency(
           "customer-profile",
           destination="s3://eu-customer-data-eu-west-1/profiles/",
           fail_on_violation=True,
       )

       return df

Decorators
----------

griot_asset
^^^^^^^^^^^

The ``@griot_asset`` decorator automatically validates asset output against a contract.

.. py:decorator:: griot_asset(contract_id, version=None, fail_on_error=True)

   Decorator that wraps an asset with automatic validation.

   :param contract_id: Contract ID in the registry.
   :type contract_id: str
   :param version: Specific contract version.
   :type version: str | None
   :param fail_on_error: Fail if validation fails. Default: True.
   :type fail_on_error: bool

**Example:**

.. code-block:: python

   from griot_enforce.dagster import griot_asset

   @griot_asset(contract_id="customer-profile")
   def customers(griot: GriotResource):
       """Output is automatically validated before return."""
       return extract_customers()

   @griot_asset(contract_id="order-events", version="2.0.0")
   def orders(griot: GriotResource):
       return extract_orders()

griot_op
^^^^^^^^

The ``@griot_op`` decorator validates op output against a contract.

.. py:decorator:: griot_op(contract_id, version=None, fail_on_error=True)

   Decorator that wraps an op with automatic validation.

   :param contract_id: Contract ID in the registry.
   :type contract_id: str
   :param version: Specific contract version.
   :type version: str | None
   :param fail_on_error: Fail if validation fails. Default: True.
   :type fail_on_error: bool

**Example:**

.. code-block:: python

   from griot_enforce.dagster import griot_op

   @griot_op(contract_id="transformed-customers")
   def transform_customers(griot: GriotResource, raw_customers):
       """Transform and validate customer data."""
       return transform(raw_customers)

Complete Example
----------------

Here's a complete Dagster project with griot-enforce:

.. code-block:: python

   # definitions.py
   from dagster import (
       Definitions,
       asset,
       AssetExecutionContext,
       EnvVar,
       AssetIn,
   )
   from griot_enforce.dagster import GriotResource, griot_asset
   import pandas as pd

   @asset
   def raw_customers() -> pd.DataFrame:
       """Extract raw customer data from source."""
       return pd.read_csv("s3://raw-data/customers.csv")

   @griot_asset(contract_id="customer-profile")
   def validated_customers(
       context: AssetExecutionContext,
       griot: GriotResource,
       raw_customers: pd.DataFrame,
   ) -> pd.DataFrame:
       """Clean and validate customer data."""
       # Transform data
       df = raw_customers.copy()
       df["email"] = df["email"].str.lower()
       df["created_at"] = pd.to_datetime(df["created_at"])

       context.log.info(f"Processing {len(df)} customer records")
       return df  # Automatically validated

   @asset
   def customer_analytics(
       griot: GriotResource,
       validated_customers: pd.DataFrame,
   ) -> pd.DataFrame:
       """Generate customer analytics after residency check."""

       # Check residency before writing
       griot.check_residency(
           "customer-profile",
           destination="s3://analytics-eu-west-1/customers/",
           fail_on_violation=True,
       )

       # Generate analytics
       analytics = validated_customers.groupby("segment").agg({
           "customer_id": "count",
           "lifetime_value": "sum",
       })

       return analytics

   @asset
   def masked_customers_staging(
       griot: GriotResource,
       validated_customers: pd.DataFrame,
   ) -> pd.DataFrame:
       """Prepare masked data for staging environment."""
       # Apply masking
       df = validated_customers.copy()
       df["email"] = df["email"].apply(lambda x: f"***@{x.split('@')[1]}")
       df["phone"] = df["phone"].apply(lambda x: f"***{x[-4:]}")

       # Verify masking
       result = griot.verify_masking(
           "customer-profile",
           df,
           environment="staging",
           fail_on_violation=True,
       )

       return df

   # Resource configuration
   defs = Definitions(
       assets=[
           raw_customers,
           validated_customers,
           customer_analytics,
           masked_customers_staging,
       ],
       resources={
           "griot": GriotResource(
               registry_url=EnvVar("GRIOT_REGISTRY_URL"),
               api_key=EnvVar("GRIOT_API_KEY"),
               cache_ttl=600,  # 10 minute cache
           ),
       },
   )

IO Managers Integration
-----------------------

You can integrate griot-enforce with custom IO managers:

.. code-block:: python

   from dagster import IOManager, OutputContext, InputContext
   from griot_enforce.dagster import GriotResource

   class ValidatingIOManager(IOManager):
       def __init__(self, griot: GriotResource, contract_id: str):
           self.griot = griot
           self.contract_id = contract_id

       def handle_output(self, context: OutputContext, obj):
           # Validate before persisting
           result = self.griot.validate(self.contract_id, obj)
           if not result.passed:
               raise ValueError(f"Validation failed: {result.error_count} errors")

           # Persist data
           obj.to_parquet(f"/data/{context.asset_key.path[-1]}.parquet")

       def load_input(self, context: InputContext):
           return pd.read_parquet(f"/data/{context.asset_key.path[-1]}.parquet")

Schedules and Sensors
---------------------

Use griot-enforce with Dagster schedules and sensors:

.. code-block:: python

   from dagster import (
       schedule,
       sensor,
       RunRequest,
       SkipReason,
       DefaultSensorStatus,
   )

   @schedule(cron_schedule="0 6 * * *", job=my_job)
   def daily_validation_schedule():
       return RunRequest(
           run_config={
               "resources": {
                   "griot": {
                       "config": {
                           "registry_url": "https://registry.example.com",
                       }
                   }
               }
           }
       )

   @sensor(job=revalidation_job, default_status=DefaultSensorStatus.RUNNING)
   def contract_update_sensor(context):
       """Trigger revalidation when contracts are updated."""
       # Check for contract updates via registry API
       # Return RunRequest if updates detected
       pass

Best Practices
--------------

1. **Use ConfigurableResource** for environment-specific configuration
2. **Leverage decorators** (``@griot_asset``) for cleaner code
3. **Check residency** before writing to region-specific storage
4. **Verify masking** in non-production environments
5. **Use EnvVar** for sensitive configuration like API keys
6. **Cache contracts** appropriately based on your update frequency
