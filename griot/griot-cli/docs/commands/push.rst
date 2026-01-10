griot push
==========

Push a contract to the Griot Registry.

Synopsis
--------

.. code-block:: bash

   griot push [OPTIONS] CONTRACT

Description
-----------

The ``push`` command uploads a contract to the Griot Registry server,
making it available for discovery, validation, and version management.

Arguments
---------

``CONTRACT``
   Path to a contract file (YAML) or Python module containing a GriotModel.

Options
-------

``--registry``, ``-r``
   Registry server URL. Overrides configuration.

``--name``
   Contract name in registry. Defaults to model class name.

``--version``
   Version string. Defaults to auto-incrementing version.

``--description``
   Contract description.

``--message``, ``-m``
   Commit message describing the changes.

``--force``
   Overwrite existing version without confirmation.

``--api-key``
   API key for authentication. Can also be set via ``GRIOT_API_KEY`` env var.

Examples
--------

Basic Push
~~~~~~~~~~

.. code-block:: bash

   # Push contract to configured registry
   griot push customer.yaml

   # Push with explicit registry URL
   griot push customer.yaml --registry https://registry.example.com

   # Push with version and message
   griot push customer.yaml --version 2.1.0 --message "Added loyalty fields"

Authentication
~~~~~~~~~~~~~~

.. code-block:: bash

   # Using environment variable (recommended)
   export GRIOT_API_KEY=your-api-key
   griot push customer.yaml

   # Using command-line option
   griot push customer.yaml --api-key your-api-key

Custom Names
~~~~~~~~~~~~

.. code-block:: bash

   # Push with custom name
   griot push customer.yaml --name CustomerContract

   # Push with description
   griot push customer.yaml --description "Customer profile data contract"

Output
------

Successful Push
~~~~~~~~~~~~~~~

.. code-block:: text

   Pushing contract to registry...
   Registry: https://registry.example.com
   Contract: Customer
   Version: 1.2.0

   Contract pushed successfully!
   URL: https://registry.example.com/contracts/Customer/versions/1.2.0

Version Conflict
~~~~~~~~~~~~~~~~

.. code-block:: text

   Pushing contract to registry...
   Error: Version 1.2.0 already exists

   Use --force to overwrite, or specify a new version with --version

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
     - Version conflict (without ``--force``)
   * - 2
     - Error (authentication failed, network error, etc.)

CI/CD Integration
-----------------

.. code-block:: yaml

   # GitHub Actions
   - name: Push Contract
     env:
       GRIOT_API_KEY: ${{ secrets.GRIOT_API_KEY }}
       GRIOT_REGISTRY_URL: ${{ secrets.GRIOT_REGISTRY_URL }}
     run: |
       griot push customer.yaml --version ${{ github.sha }}

See Also
--------

- :doc:`pull` - Pull contracts from registry
- :doc:`validate` - Validate data against contract
