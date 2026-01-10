.. Griot documentation master file

======================================
Griot: Data Contracts for AI Pipelines
======================================

**Griot** is a comprehensive data contract framework designed for AI/ML pipelines.
It provides schema definition, validation, privacy compliance, and runtime enforcement
across your entire data ecosystem.

.. note::
   Griot follows a **Core-First** architecture: all business logic lives in ``griot-core``,
   with other components (CLI, Enforce, Registry, Hub) as thin wrappers.

Quick Links
-----------

.. grid:: 2
   :gutter: 3

   .. grid-item-card:: Getting Started
      :link: getting-started/index
      :link-type: doc

      New to Griot? Start here to learn the basics.

   .. grid-item-card:: API Reference
      :link: api-reference/index
      :link-type: doc

      Detailed API documentation for all modules.

   .. grid-item-card:: User Guides
      :link: guides/index
      :link-type: doc

      In-depth guides for common use cases.

   .. grid-item-card:: CLI Reference
      :link: api-reference/cli
      :link-type: doc

      Command-line tool documentation.


Features
--------

* **Schema Definition**: Define data contracts using Python classes or YAML
* **Validation Engine**: Validate data against contracts with detailed error reporting
* **Privacy Compliance**: Built-in PII tracking, sensitivity levels, and masking strategies
* **Data Residency**: Enforce regional data storage requirements
* **Lineage Tracking**: Document data sources, transformations, and consumers
* **AI Readiness**: Generate reports on contract quality for AI/ML consumption
* **Runtime Enforcement**: Integrate with Airflow, Dagster, and Prefect
* **Contract Registry**: Central repository for contract management


Package Overview
----------------

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Package
     - Description
   * - ``griot-core``
     - Core library with models, validation, and all business logic
   * - ``griot-cli``
     - Command-line interface for contract operations
   * - ``griot-enforce``
     - Runtime validation for data orchestrators
   * - ``griot-registry``
     - FastAPI server for contract storage and versioning
   * - ``griot-hub``
     - Web UI for contract management and monitoring


Installation
------------

Install the core library:

.. code-block:: bash

   pip install griot-core

Install with CLI:

.. code-block:: bash

   pip install griot-cli

Install with specific orchestrator support:

.. code-block:: bash

   pip install griot-enforce[airflow]
   pip install griot-enforce[dagster]
   pip install griot-enforce[prefect]


Quick Example
-------------

Define a data contract:

.. code-block:: python

   from griot_core import GriotModel, Field

   class Customer(GriotModel):
       """Customer data contract."""

       customer_id: str = Field(
           description="Unique customer identifier",
           primary_key=True,
           pattern=r"^CUST-\d{6}$",
       )
       email: str = Field(
           description="Customer email address",
           format="email",
           pii_category="email",
           sensitivity_level="confidential",
       )
       age: int = Field(
           description="Customer age in years",
           ge=0,
           le=150,
       )

Validate data:

.. code-block:: python

   data = [
       {"customer_id": "CUST-000001", "email": "alice@example.com", "age": 30},
       {"customer_id": "CUST-000002", "email": "bob@example.com", "age": 25},
   ]

   result = Customer.validate(data)
   print(result.summary())


Contents
--------

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   getting-started/index
   getting-started/installation
   getting-started/quickstart
   getting-started/first-contract

.. toctree::
   :maxdepth: 2
   :caption: User Guides

   guides/index
   guides/defining-contracts
   guides/validation
   guides/privacy-compliance
   guides/reports

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api-reference/index
   api-reference/core
   api-reference/cli
   api-reference/enforce
   api-reference/registry


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
