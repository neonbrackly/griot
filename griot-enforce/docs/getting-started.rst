Getting Started
===============

This guide will help you get started with griot-enforce for runtime data validation
in your data pipelines.

Installation
------------

Basic Installation
^^^^^^^^^^^^^^^^^^

Install the core package:

.. code-block:: bash

   pip install griot-enforce

This installs griot-enforce with griot-core and httpx for registry integration.

Orchestrator-Specific Installation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Install with your preferred orchestrator:

.. code-block:: bash

   # Apache Airflow
   pip install griot-enforce[airflow]

   # Dagster
   pip install griot-enforce[dagster]

   # Prefect
   pip install griot-enforce[prefect]

   # All orchestrators
   pip install griot-enforce[all]

Development Installation
^^^^^^^^^^^^^^^^^^^^^^^^

For development with testing tools:

.. code-block:: bash

   pip install griot-enforce[dev]

Configuration
-------------

Environment Variables
^^^^^^^^^^^^^^^^^^^^^

griot-enforce uses the following environment variables:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Variable
     - Description
   * - ``GRIOT_REGISTRY_URL``
     - Default registry URL for contract fetching
   * - ``GRIOT_API_KEY``
     - API key for registry authentication

Basic Usage
-----------

Using RuntimeValidator
^^^^^^^^^^^^^^^^^^^^^^

The ``RuntimeValidator`` class is the core component for runtime validation:

.. code-block:: python

   from griot_enforce import RuntimeValidator

   # Create a validator with registry integration
   validator = RuntimeValidator(
       registry_url="https://registry.example.com",
       api_key="your-api-key",  # Optional, can use env var
       cache_ttl=300,           # Cache contracts for 5 minutes
       report_results=True,     # Report results to registry
   )

   # Validate data against a contract
   result = validator.validate(
       contract_id="customer-profile",
       data=dataframe,
       version="1.0.0",         # Optional, defaults to latest
       fail_on_error=True,      # Raise exception on failure
   )

   if result.passed:
       print(f"Validation passed! {result.row_count} rows validated.")
   else:
       print(f"Validation failed with {result.error_count} errors.")

Local Contract Validation
^^^^^^^^^^^^^^^^^^^^^^^^^

For validating against local contract files:

.. code-block:: python

   from griot_enforce import RuntimeValidator

   validator = RuntimeValidator()

   result = validator.validate_local(
       contract_path="./contracts/customer.yaml",
       data=dataframe,
       fail_on_error=True,
   )

Context Manager Usage
^^^^^^^^^^^^^^^^^^^^^

Use the context manager for automatic resource cleanup:

.. code-block:: python

   from griot_enforce import RuntimeValidator

   with RuntimeValidator(registry_url="https://registry.example.com") as validator:
       result = validator.validate("customer-profile", dataframe)
       # HTTP client is automatically closed when exiting the context

Residency Enforcement
---------------------

Check data residency compliance before writing data:

.. code-block:: python

   from griot_enforce import RuntimeValidator, ResidencyViolationError

   validator = RuntimeValidator(registry_url="https://registry.example.com")

   # Auto-detect region from S3 URI
   try:
       result = validator.check_residency(
           contract_id="customer-profile",
           destination="s3://my-bucket-eu-west-1/data/",
           fail_on_violation=True,
       )
       print(f"Residency check passed for region: {result['target_region']}")
   except ResidencyViolationError as e:
       print(f"Residency violation: {e}")
       print(f"Allowed regions: {e.allowed_regions}")

   # Or specify region explicitly
   result = validator.check_residency(
       contract_id="customer-profile",
       region="eu-west-1",
   )

Masking Verification
--------------------

Verify PII fields are properly masked in non-production environments:

.. code-block:: python

   from griot_enforce import RuntimeValidator, MaskingViolationError

   validator = RuntimeValidator(registry_url="https://registry.example.com")

   # Verify masking in staging environment
   try:
       result = validator.verify_masking(
           contract_id="customer-profile",
           data=dataframe,
           environment="staging",  # Skips verification in "prod"/"production"
           fail_on_violation=True,
       )
       print(f"Masking verified for {len(result['pii_fields_checked'])} PII fields")
   except MaskingViolationError as e:
       print(f"Masking violation: {e}")
       for violation in e.violations:
           print(f"  - {violation['field']}: {violation['message']}")

Combined Validation and Masking
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use the ``verify_masking`` parameter in ``validate()`` for combined checks:

.. code-block:: python

   result = validator.validate(
       contract_id="customer-profile",
       data=dataframe,
       verify_masking=True,
       environment="staging",
       fail_on_error=True,
   )

   # Access masking result
   if hasattr(result, 'masking_result'):
       print(f"Masking compliant: {result.masking_result['compliant']}")

Next Steps
----------

- :doc:`api-reference` - Complete API documentation
- :doc:`airflow` - Apache Airflow integration guide
- :doc:`dagster` - Dagster integration guide
- :doc:`prefect` - Prefect integration guide
- :doc:`examples` - Real-world pipeline examples
