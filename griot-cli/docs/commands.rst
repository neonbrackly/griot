Commands Overview
=================

griot-cli provides the following commands for data contract management:

Contract Creation & Migration
-----------------------------

.. versionadded:: 0.6.0

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Command
     - Description
   * - :doc:`commands/init`
     - Initialize a new ODCS-format data contract
   * - :doc:`commands/migrate`
     - Migrate old contracts to ODCS v1.0.0 format

Core Commands
-------------

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Command
     - Description
   * - :doc:`commands/validate`
     - Validate data against a contract
   * - :doc:`commands/lint`
     - Check a contract for quality issues (supports ODCS rules)
   * - :doc:`commands/diff`
     - Compare two contracts and detect breaking changes
   * - :doc:`commands/mock`
     - Generate mock data from a contract

Export Commands
---------------

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Command
     - Description
   * - :doc:`commands/manifest`
     - Export contract as JSON-LD, Markdown, or LLM context

Report Commands
---------------

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Command
     - Description
   * - :doc:`commands/report`
     - Generate analytics, AI readiness, audit, and combined reports

Compliance Commands
-------------------

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Command
     - Description
   * - :doc:`commands/residency`
     - Check data residency compliance for regions

Registry Commands
-----------------

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Command
     - Description
   * - :doc:`commands/push`
     - Push a contract to the registry
   * - :doc:`commands/pull`
     - Pull a contract from the registry

Global Options
--------------

All commands support these global options:

``--config``, ``-c``
   Path to configuration file.

``--version``
   Show version and exit.

``--help``
   Show help message and exit.

Output Formats
--------------

Many commands support multiple output formats via the ``--format`` / ``-f`` option:

``table``
   Human-readable table format (default). Best for interactive use.

``json``
   Machine-readable JSON format. Best for scripting and CI/CD.

``github``
   GitHub Actions annotation format. Integrates with GitHub's UI.

``markdown``
   Markdown format. Best for documentation and reports.

Exit Codes
----------

All commands use consistent exit codes:

.. list-table::
   :header-rows: 1

   * - Code
     - Meaning
     - When Used
   * - 0
     - Success
     - Command completed successfully
   * - 1
     - Failure
     - Validation failed, threshold not met, breaking changes detected
   * - 2
     - Error
     - Invalid arguments, file not found, unexpected error

Command Reference
-----------------

.. toctree::
   :maxdepth: 1

   commands/init
   commands/migrate
   commands/validate
   commands/lint
   commands/diff
   commands/mock
   commands/manifest
   commands/report
   commands/residency
   commands/push
   commands/pull

Additional References
---------------------

.. toctree::
   :maxdepth: 1

   odcs_quality_rules
