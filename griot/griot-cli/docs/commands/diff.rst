griot diff
==========

Compare two contracts and detect breaking changes.

Synopsis
--------

.. code-block:: bash

   griot diff [OPTIONS] OLD_CONTRACT NEW_CONTRACT

Description
-----------

The ``diff`` command compares two contract versions and identifies changes,
particularly breaking changes that could affect downstream consumers.

Arguments
---------

``OLD_CONTRACT``
   Path to the older contract version.

``NEW_CONTRACT``
   Path to the newer contract version.

Options
-------

``--format``, ``-f``
   Output format. Choices: ``table``, ``json``, ``markdown``. Default: ``table``.

``--fail-on-breaking``
   Exit with code 1 if breaking changes are detected.

Examples
--------

Basic Diff
~~~~~~~~~~

.. code-block:: bash

   # Compare two contract versions
   griot diff customer_v1.yaml customer_v2.yaml

   # Fail if breaking changes found
   griot diff customer_v1.yaml customer_v2.yaml --fail-on-breaking

Output Formats
~~~~~~~~~~~~~~

.. code-block:: bash

   # Table format (default)
   griot diff old.yaml new.yaml -f table

   # JSON format (for automation)
   griot diff old.yaml new.yaml -f json

   # Markdown format (for documentation)
   griot diff old.yaml new.yaml -f markdown

Output
------

Table Format
~~~~~~~~~~~~

.. code-block:: text

   BREAKING CHANGES DETECTED

   Added fields:
     + loyalty_tier
     + last_purchase_date

   Removed fields (BREAKING):
     - legacy_id

   Type changes:
     age: string -> integer (BREAKING)

   Constraint changes:
     email.max_length: 100 -> 255
     status.enum: ['active', 'inactive'] -> ['active', 'inactive', 'pending'] (BREAKING)

Change Types
------------

**Non-Breaking Changes:**

- Adding new optional fields
- Relaxing constraints (increasing max_length, expanding enum values)
- Adding new optional constraints

**Breaking Changes:**

- Removing fields
- Adding required fields
- Changing field types incompatibly
- Tightening constraints (decreasing max_length, removing enum values)
- Renaming fields

Exit Codes
----------

.. list-table::
   :header-rows: 1

   * - Code
     - Meaning
   * - 0
     - No breaking changes (or ``--fail-on-breaking`` not specified)
   * - 1
     - Breaking changes detected (with ``--fail-on-breaking``)
   * - 2
     - Error (file not found, invalid contract, etc.)

CI/CD Integration
-----------------

Use in pull request checks:

.. code-block:: bash

   # Fail the build if breaking changes are introduced
   griot diff main:customer.yaml feature:customer.yaml --fail-on-breaking

See Also
--------

- :doc:`lint` - Check contract quality
- :doc:`validate` - Validate data against contract
