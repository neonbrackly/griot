griot pull
==========

Pull a contract from the Griot Registry.

Synopsis
--------

.. code-block:: bash

   griot pull [OPTIONS] CONTRACT_NAME

Description
-----------

The ``pull`` command downloads a contract from the Griot Registry server,
allowing you to use centrally managed contracts for local validation.

Arguments
---------

``CONTRACT_NAME``
   Name of the contract in the registry.

Options
-------

``--registry``, ``-r``
   Registry server URL. Overrides configuration.

``--version``
   Specific version to pull. Defaults to latest version.

``--output``, ``-o``
   Output file path. Defaults to ``<contract_name>.yaml``.

``--format``, ``-f``
   Output format. Choices: ``yaml``, ``json``. Default: ``yaml``.

``--api-key``
   API key for authentication. Can also be set via ``GRIOT_API_KEY`` env var.

Examples
--------

Basic Pull
~~~~~~~~~~

.. code-block:: bash

   # Pull latest version of a contract
   griot pull Customer

   # Pull from specific registry
   griot pull Customer --registry https://registry.example.com

   # Pull specific version
   griot pull Customer --version 1.2.0

Output Options
~~~~~~~~~~~~~~

.. code-block:: bash

   # Save to custom filename
   griot pull Customer -o contracts/customer.yaml

   # Pull as JSON
   griot pull Customer -f json -o customer.json

   # Print to stdout (don't save to file)
   griot pull Customer -o -

Authentication
~~~~~~~~~~~~~~

.. code-block:: bash

   # Using environment variable (recommended)
   export GRIOT_API_KEY=your-api-key
   griot pull Customer

   # Using command-line option
   griot pull Customer --api-key your-api-key

Output
------

Successful Pull
~~~~~~~~~~~~~~~

.. code-block:: text

   Pulling contract from registry...
   Registry: https://registry.example.com
   Contract: Customer
   Version: 1.2.0 (latest)

   Contract saved to: Customer.yaml

List Available Versions
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Show available versions (via registry API)
   curl https://registry.example.com/api/contracts/Customer/versions

Not Found
~~~~~~~~~

.. code-block:: text

   Pulling contract from registry...
   Error: Contract 'UnknownContract' not found in registry

Configuration
-------------

The registry URL can be configured in multiple ways (priority order):

1. ``--registry`` command-line option
2. ``GRIOT_REGISTRY_URL`` environment variable
3. ``registry_url`` in configuration file

Example configuration:

.. code-block:: yaml

   # .griot.yaml
   registry_url: https://registry.example.com

Exit Codes
----------

.. list-table::
   :header-rows: 1

   * - Code
     - Meaning
   * - 0
     - Success
   * - 1
     - Contract not found
   * - 2
     - Error (authentication failed, network error, etc.)

Workflow Examples
-----------------

Sync Contracts for CI
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Pull all required contracts before validation
   griot pull Customer -o contracts/customer.yaml
   griot pull Order -o contracts/order.yaml
   griot pull Product -o contracts/product.yaml

   # Validate data
   griot validate contracts/customer.yaml data/customers.csv

Version Pinning
~~~~~~~~~~~~~~~

.. code-block:: bash

   # Pin to specific version for reproducibility
   griot pull Customer --version 1.2.0 -o customer_v1.2.0.yaml

CI/CD Integration
-----------------

.. code-block:: yaml

   # GitHub Actions
   - name: Pull Contracts
     env:
       GRIOT_API_KEY: ${{ secrets.GRIOT_API_KEY }}
       GRIOT_REGISTRY_URL: ${{ secrets.GRIOT_REGISTRY_URL }}
     run: |
       griot pull Customer -o contracts/customer.yaml
       griot pull Order -o contracts/order.yaml

   - name: Validate Data
     run: |
       griot validate contracts/customer.yaml data/customers.csv

See Also
--------

- :doc:`push` - Push contracts to registry
- :doc:`validate` - Validate data against contract
