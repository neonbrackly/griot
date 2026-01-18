.. Griot Core documentation master file

Griot Core Documentation
========================

**Griot Core** is a Python library for defining, validating, and managing data contracts
based on the `Open Data Contract Standard (ODCS) <https://github.com/bitol-io/open-data-contract-standard>`_.

.. note::

   Griot Core provides a type-safe, Pythonic way to define data contracts that can be
   validated against DataFrames (pandas, polars, spark, dask) using Pandera.

Quick Example
-------------

.. code-block:: python

   from griot_core import Schema, Field, QualityRule, Contract

   class EmployeeSchema(Schema):
       """Employee data schema with quality rules."""

       employee_id: int = Field(
           "Employee ID",
           primary_key=True,
           quality=[QualityRule.null_values(must_be=0)]
       )
       name: str = Field("Employee name")
       email: str = Field(
           "Email address",
           unique=True,
           quality=[
               QualityRule.invalid_values(
                   must_be=0,
                   pattern=r'^[\w.-]+@[\w.-]+\.\w+$'
               )
           ]
       )

   # Create a contract
   contract = Contract(
       id="employee-contract",
       name="Employee Data Contract",
       schemas=[EmployeeSchema()]
   )

Key Features
------------

- **ODCS Compliant**: Full support for the Open Data Contract Standard
- **Type-Safe Schema Definitions**: Define schemas using Python type hints and descriptors
- **Quality Rules**: Built-in support for data quality validation
- **Multi-Backend Validation**: Validate against pandas, polars, PySpark, or Dask DataFrames
- **Contract Linting**: Check contracts for issues and best practices
- **Mock Data Generation**: Generate synthetic data conforming to schemas
- **Report Generation**: Create contract documentation and manifests

Installation
------------

.. code-block:: bash

   # Core library (no DataFrame validation)
   pip install griot-core

   # With pandas support
   pip install griot-core[pandas]

   # With multiple backends
   pip install griot-core[pandas,polars]

   # All backends
   pip install griot-core[all]

Documentation Contents
----------------------

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   guides/quickstart
   guides/installation
   guides/concepts

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   guides/schema_definition
   guides/quality_rules
   guides/contracts
   guides/validation
   guides/mock_data

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/index

.. toctree::
   :maxdepth: 1
   :caption: Additional Resources

   changelog
   contributing


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
