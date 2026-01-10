Configuration
=============

griot-cli can be configured using configuration files and environment variables.
Configuration priority (highest to lowest):

1. Command-line options
2. Environment variables (``GRIOT_*``)
3. Configuration file
4. Default values

Configuration File
------------------

griot-cli searches for configuration files in the following order:

1. ``.griot.yaml``
2. ``.griot.yml``
3. ``griot.yaml``
4. ``griot.yml``

The search starts from the current directory and moves upward to parent directories
until a configuration file is found.

File Format
~~~~~~~~~~~

.. code-block:: yaml

   # .griot.yaml

   # Griot Registry server URL
   registry_url: https://registry.example.com

   # Default output format: table, json, or github
   default_format: table

   # Maximum number of errors to display
   max_errors: 100

   # Enable colored output
   color: true

Configuration Options
---------------------

registry_url
~~~~~~~~~~~~

URL of the Griot Registry server for ``push`` and ``pull`` commands.

- **Type**: string
- **Default**: ``null`` (not configured)
- **Environment**: ``GRIOT_REGISTRY_URL``

.. code-block:: yaml

   registry_url: https://registry.example.com

default_format
~~~~~~~~~~~~~~

Default output format for commands that support multiple formats.

- **Type**: string
- **Default**: ``table``
- **Options**: ``table``, ``json``, ``github``, ``markdown``
- **Environment**: ``GRIOT_DEFAULT_FORMAT``

.. code-block:: yaml

   default_format: json

max_errors
~~~~~~~~~~

Maximum number of validation errors to display.

- **Type**: integer
- **Default**: ``100``
- **Environment**: ``GRIOT_MAX_ERRORS``

.. code-block:: yaml

   max_errors: 50

color
~~~~~

Enable or disable colored output in the terminal.

- **Type**: boolean
- **Default**: ``true``
- **Environment**: ``GRIOT_COLOR``

.. code-block:: yaml

   color: false

Environment Variables
---------------------

All configuration options can be set via environment variables with the ``GRIOT_`` prefix:

.. list-table::
   :header-rows: 1

   * - Variable
     - Description
     - Example
   * - ``GRIOT_REGISTRY_URL``
     - Registry server URL
     - ``https://registry.example.com``
   * - ``GRIOT_DEFAULT_FORMAT``
     - Default output format
     - ``json``
   * - ``GRIOT_MAX_ERRORS``
     - Maximum errors to display
     - ``50``
   * - ``GRIOT_COLOR``
     - Enable colored output
     - ``true``, ``false``, ``1``, ``0``

Example Usage
~~~~~~~~~~~~~

.. code-block:: bash

   # Set registry URL for the session
   export GRIOT_REGISTRY_URL=https://registry.example.com

   # Disable colored output for CI
   export GRIOT_COLOR=0

   # Now commands will use these settings
   griot push customer.yaml
   griot validate customer.yaml data.csv

Command-Line Configuration
--------------------------

The ``--config`` / ``-c`` option allows specifying an explicit configuration file:

.. code-block:: bash

   griot -c /path/to/config.yaml validate customer.yaml data.csv

This overrides the automatic configuration file discovery.

Per-Project Configuration
-------------------------

For project-specific settings, create a ``.griot.yaml`` file in your project root:

.. code-block:: yaml

   # Project: customer-analytics
   registry_url: https://internal-registry.company.com
   default_format: json
   max_errors: 200

This file will be automatically discovered when running griot commands from
within the project directory.

CI/CD Configuration
-------------------

For CI/CD pipelines, environment variables are recommended:

.. code-block:: yaml

   # GitHub Actions example
   env:
     GRIOT_REGISTRY_URL: ${{ secrets.GRIOT_REGISTRY_URL }}
     GRIOT_COLOR: "0"  # Disable colors for cleaner logs

See :doc:`ci_cd` for more CI/CD integration examples.
