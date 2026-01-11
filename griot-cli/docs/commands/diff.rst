griot diff
==========

Compare two contracts and detect breaking changes.

.. versionchanged:: 0.6.0
   Enhanced output with detailed breaking change information and migration hints.

Synopsis
--------

.. code-block:: bash

   griot diff [OPTIONS] OLD_CONTRACT NEW_CONTRACT

Description
-----------

The ``diff`` command compares two contract versions and identifies changes,
particularly breaking changes that could affect downstream consumers.

**Enhanced Breaking Change Detection (v0.6.0+):**

The diff output now includes:

- Detailed breaking change descriptions
- Migration hints for each breaking change
- Categorized breaking change types
- Support for all ODCS schema sections

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

.. versionchanged:: 0.6.0
   Now includes detailed breaking changes section with migration hints.

.. code-block:: text

   BREAKING CHANGES DETECTED

   Breaking Changes:
   ------------------------------------------------------------
     [field_removed] on 'legacy_id'
       Field 'legacy_id' was removed from schema
       Migration: Add legacy_id back or migrate consumers first

     [type_changed_incompatible] on 'age'
       Field type changed from string to integer
       Migration: Update all consumers to handle integer type

     [constraint_tightened] on 'email'
       max_length reduced from 255 to 100
       Migration: Ensure no existing data exceeds 100 characters

   Added fields:
     + loyalty_tier
     + last_purchase_date

   Removed fields (BREAKING):
     - legacy_id

   Type changes:
     age: string -> integer (BREAKING)

   Constraint changes:
     email.max_length: 255 -> 100 (BREAKING)

JSON Format
~~~~~~~~~~~

.. versionchanged:: 0.6.0
   Now includes ``breaking_changes`` array with full details.

.. code-block:: json

   {
     "has_breaking_changes": true,
     "added_fields": ["loyalty_tier", "last_purchase_date"],
     "removed_fields": ["legacy_id"],
     "type_changes": [...],
     "constraint_changes": [...],
     "breaking_changes": [
       {
         "change_type": "field_removed",
         "field": "legacy_id",
         "description": "Field 'legacy_id' was removed from schema",
         "from_value": "legacy_id",
         "to_value": null,
         "migration_hint": "Add legacy_id back or migrate consumers first"
       },
       {
         "change_type": "type_changed_incompatible",
         "field": "age",
         "description": "Field type changed from string to integer",
         "from_value": "string",
         "to_value": "integer",
         "migration_hint": "Update all consumers to handle integer type"
       }
     ]
   }

Markdown Format
~~~~~~~~~~~~~~~

.. versionchanged:: 0.6.0
   Now includes structured breaking change sections.

.. code-block:: markdown

   # Contract Diff Report

   **:warning: BREAKING CHANGES DETECTED**

   ## Breaking Changes

   ### field_removed (`legacy_id`)
   - **Description:** Field 'legacy_id' was removed from schema
   - **From:** `legacy_id`
   - **Migration:** Add legacy_id back or migrate consumers first

   ### type_changed_incompatible (`age`)
   - **Description:** Field type changed from string to integer
   - **From:** `string`
   - **To:** `integer`
   - **Migration:** Update all consumers to handle integer type

   ## Added Fields
   - `loyalty_tier`
   - `last_purchase_date`

   ## Removed Fields (BREAKING)
   - `legacy_id`

Change Types
------------

**Non-Breaking Changes:**

- Adding new optional fields
- Relaxing constraints (increasing max_length, expanding enum values)
- Adding new optional constraints

**Breaking Changes:**

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
     - Constraints made more restrictive
   * - ``nullable_to_required``
     - Field changed from nullable to non-nullable
   * - ``pattern_changed``
     - Regex pattern changed incompatibly
   * - ``primary_key_changed``
     - Primary key field was changed

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
