griot-enforce Documentation
============================

**griot-enforce** provides runtime validation for data orchestrators including
Apache Airflow, Dagster, and Prefect. It wraps the griot-core SDK with runtime
features such as registry integration, contract caching, and result reporting.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   getting-started
   api-reference
   airflow
   dagster
   prefect
   error-handling
   examples

Features
--------

- **RuntimeValidator**: Core validation class with registry integration
- **Contract Caching**: TTL-based caching for performance optimization
- **Residency Enforcement**: Auto-detect regions from cloud URIs (S3, Azure, GCS)
- **Masking Verification**: Environment-aware PII masking checks
- **Orchestrator Integrations**:
  - Apache Airflow operators and sensors
  - Dagster resources and decorators
  - Prefect tasks

Quick Example
-------------

.. code-block:: python

   from griot_enforce import RuntimeValidator

   # Validate against a registry contract
   validator = RuntimeValidator(registry_url="https://registry.example.com")
   result = validator.validate("customer-profile", dataframe)

   # Or validate against a local contract file
   result = validator.validate_local("./contracts/customer.yaml", dataframe)

Installation
------------

.. code-block:: bash

   # Core package
   pip install griot-enforce

   # With orchestrator support
   pip install griot-enforce[airflow]   # Apache Airflow
   pip install griot-enforce[dagster]   # Dagster
   pip install griot-enforce[prefect]   # Prefect
   pip install griot-enforce[all]       # All orchestrators

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
