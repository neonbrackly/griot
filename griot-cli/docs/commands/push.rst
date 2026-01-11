griot push
==========

Push a contract to the Griot Registry.

.. versionchanged:: 0.6.0
   Added breaking change validation with ``--allow-breaking`` and enhanced ``--dry-run``.

Synopsis
--------

.. code-block:: bash

   griot push [OPTIONS] CONTRACT

Description
-----------

The ``push`` command uploads a contract to the Griot Registry server,
making it available for discovery, validation, and version management.

**Breaking Change Validation (v0.6.0+):**

Before pushing, the command automatically checks for breaking changes by
comparing against the existing contract in the registry. If breaking changes
are detected, the push is **blocked** unless ``--allow-breaking`` is specified.

This prevents accidental breaking changes from being published and ensures
downstream consumers are notified before schema changes take effect.

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

``--major``
   Force major version bump.

``--dry-run``
   Show what would be pushed, including breaking change analysis.
   Does not actually push to registry.

``--allow-breaking``
   Allow push even if breaking changes are detected. Use with caution.
   This flag acknowledges that you understand the impact on downstream consumers.

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

Breaking Change Validation
--------------------------

.. versionadded:: 0.6.0

When pushing an update to an existing contract, Griot automatically detects
breaking changes that could affect downstream consumers.

Breaking Change Types
~~~~~~~~~~~~~~~~~~~~~

The following changes are considered breaking:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Change Type
     - Description
   * - ``field_removed``
     - A field was removed from the schema
   * - ``field_renamed``
     - A field was renamed (detected via similarity)
   * - ``type_changed_incompatible``
     - Field type changed to incompatible type
   * - ``required_field_added``
     - New non-nullable field without default added
   * - ``enum_values_removed``
     - Allowed enum values were removed
   * - ``constraint_tightened``
     - Constraints made more restrictive (e.g., reduced max_length)
   * - ``nullable_to_required``
     - Field changed from nullable to non-nullable
   * - ``pattern_changed``
     - Regex pattern changed in incompatible way
   * - ``primary_key_changed``
     - Primary key field was changed

Example: Blocked Push
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   $ griot push customer.yaml -m "Updated schema"

   # Output:
   BREAKING CHANGES DETECTED (3):
     [field_removed] on 'legacy_id'
       Field 'legacy_id' was removed from schema
       Migration: Add legacy_id back or migrate consumers first
     [type_changed_incompatible] on 'age'
       Field type changed from integer to string
       Migration: Update all consumers to handle string type
     [constraint_tightened] on 'email'
       max_length reduced from 255 to 100
       Migration: Ensure no existing data exceeds 100 characters

   Push blocked. Use --allow-breaking to force push.

Example: Dry Run with Breaking Changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   $ griot push customer.yaml --dry-run

   # Output:
   Dry run - would push:
     Contract: customer.yaml
     Name: Customer
     Registry: https://registry.example.com
     Message: (none)
     Major bump: False

   Breaking changes detected (2):
     [field_removed] on 'legacy_id'
       Field 'legacy_id' was removed from schema
       Migration: Add legacy_id back or migrate consumers first
     [nullable_to_required] on 'email'
       Field changed from nullable to non-nullable
       Migration: Ensure all records have email values

   Push would be BLOCKED. Use --allow-breaking to force.

Example: Force Push with Breaking Changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   $ griot push customer.yaml --allow-breaking -m "Breaking: removed legacy_id"

   # Output:
   Proceeding with 1 breaking change(s)...
   Pushed customer.yaml to https://registry.example.com

Exit Codes
----------

.. list-table::
   :header-rows: 1

   * - Code
     - Meaning
   * - 0
     - Success
   * - 1
     - Breaking changes detected (without ``--allow-breaking``)
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
