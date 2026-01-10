griot-cli Documentation
=======================

**griot-cli** is the command-line interface for the Griot data contract management system.
It provides commands for validating data, linting contracts, generating reports, and
interacting with the Griot Registry.

.. note::

   All business logic is handled by ``griot-core``. The CLI is a thin wrapper that
   provides argument parsing, output formatting, and exit codes suitable for CI/CD pipelines.

Quick Start
-----------

.. code-block:: bash

   # Install griot-cli
   pip install griot-cli

   # Validate data against a contract
   griot validate customer.yaml data.csv

   # Lint a contract for issues
   griot lint customer.yaml

   # Generate an AI readiness report
   griot report ai customer.yaml

Contents
--------

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   installation
   configuration
   commands
   ci_cd

.. toctree::
   :maxdepth: 2
   :caption: Reference

   commands/validate
   commands/lint
   commands/diff
   commands/mock
   commands/manifest
   commands/report
   commands/residency
   commands/push
   commands/pull

Features
--------

- **Data Validation**: Validate CSV, JSON, or Parquet data against contracts
- **Contract Linting**: Check contracts for quality issues and best practices
- **Contract Diffing**: Detect breaking changes between contract versions
- **Mock Data Generation**: Generate realistic test data from contracts
- **Manifest Export**: Export contracts as JSON-LD, Markdown, or LLM-optimized formats
- **Report Generation**: Analytics, AI readiness, compliance audit, and combined reports
- **Residency Checking**: Verify data residency compliance for regions
- **Registry Integration**: Push and pull contracts from a central registry

Exit Codes
----------

All commands use consistent exit codes for CI/CD integration:

.. list-table::
   :header-rows: 1

   * - Exit Code
     - Meaning
   * - 0
     - Success
   * - 1
     - Validation/check failed (data issues, threshold not met)
   * - 2
     - Error (invalid arguments, file not found, etc.)

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
