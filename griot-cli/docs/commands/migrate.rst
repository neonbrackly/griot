griot migrate
=============

Migrate old contracts to ODCS v1.0.0 format.

.. versionadded:: 0.6.0

Synopsis
--------

.. code-block:: bash

   griot migrate [OPTIONS] CONTRACT

Description
-----------

The ``migrate`` command converts contracts from the legacy v0 format to the
Open Data Contract Standard (ODCS) v1.0.0 format. This is essential for
upgrading existing contracts to take advantage of new ODCS features.

The migration process:

1. **Detects** the current schema version (v0 or v1.0.0)
2. **Transforms** the contract structure to ODCS format
3. **Preserves** all existing field definitions and metadata
4. **Adds** new ODCS sections with sensible defaults
5. **Reports** all changes and warnings

Arguments
---------

``CONTRACT``
   Path to a contract YAML file in legacy (v0) format.

Options
-------

``--output``, ``-o``
   Output file path. If not specified, migrated contract is printed to stdout.

``--in-place``, ``-i``
   Modify the input file in place. Cannot be used with ``--output``.

``--dry-run``
   Show what would be changed without writing any files.

``--format``, ``-f``
   Output format: ``yaml`` (default) or ``json``.

``--verbose``, ``-v``
   Show detailed change log during migration.

Examples
--------

Basic Migration
~~~~~~~~~~~~~~~

.. code-block:: bash

   # Migrate and output to stdout
   griot migrate contracts/old_customer.yaml

   # Sample output:
   # Detected schema version: v0
   # Migration: v0 -> v1.0.0
   # Changes: 15
   # Warnings: 2
   #
   # --- Migrated contract ---
   # api_version: v1.0.0
   # kind: DataContract
   # ...

Save to File
~~~~~~~~~~~~

.. code-block:: bash

   # Save migrated contract to new file
   griot migrate contracts/old_customer.yaml -o contracts/customer_v1.yaml

   # Output:
   # Detected schema version: v0
   # Migration: v0 -> v1.0.0
   # Changes: 15
   # Warnings: 2
   # Migrated contract written to: contracts/customer_v1.yaml

In-Place Migration
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Overwrite the original file
   griot migrate contracts/customer.yaml --in-place

   # Output:
   # Detected schema version: v0
   # Migration: v0 -> v1.0.0
   # Changes: 15
   # Warnings: 2
   # Migrated contract written to: contracts/customer.yaml

Dry Run with Verbose Output
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Preview changes without writing
   griot migrate contracts/old_customer.yaml --dry-run -v

   # Output:
   # Detected schema version: v0
   # Migration: v0 -> v1.0.0
   # Changes: 15
   # Warnings: 2
   #
   # Changes made:
   #   + Added api_version: v1.0.0
   #   + Added kind: DataContract
   #   + Added default status: active
   #   + Converted string description to structured format
   #   + Created privacy section for email
   #   + Created privacy section for phone
   #   ...
   #
   # Warnings:
   #   ! Preserved unknown key: custom_metadata
   #   ! No name found, using 'MigratedContract'
   #
   # --- Dry run - showing migrated output ---
   # api_version: v1.0.0
   # ...

JSON Output
~~~~~~~~~~~

.. code-block:: bash

   # Output as JSON format
   griot migrate contracts/old_customer.yaml -f json

Migration Details
-----------------

Schema Version Detection
~~~~~~~~~~~~~~~~~~~~~~~~

The migration automatically detects the schema version:

- **v1.0.0**: Has ``api_version: v1.0.0`` or ``kind: DataContract``
- **v0**: Legacy format without ODCS metadata

Transformations Applied
~~~~~~~~~~~~~~~~~~~~~~~

**Metadata Additions:**

- ``api_version: v1.0.0``
- ``kind: DataContract``
- ``status: active`` (for existing contracts)
- ``timestamps`` section with created/updated timestamps

**Field Structure Changes:**

- Flat constraints moved to ``constraints`` section
- PII fields moved to ``privacy`` section
- Metadata fields moved to ``semantic`` section
- ``glossary_term`` renamed to ``business_term``

**Example Transformation:**

.. code-block:: yaml

   # v0 format (before)
   name: Customer
   description: Customer data
   fields:
     - name: email
       type: string
       pii_category: email
       sensitivity_level: confidential
       max_length: 255
       pattern: "^[a-z@.]+$"

   # v1.0.0 format (after)
   api_version: v1.0.0
   kind: DataContract
   name: Customer
   status: active
   description:
     purpose: Customer data
   fields:
     - name: email
       type: string
       constraints:
         max_length: 255
         pattern: "^[a-z@.]+$"
       privacy:
         contains_pii: true
         pii_category: email
         sensitivity_level: confidential
   timestamps:
     created_at: 2026-01-11T12:00:00Z
     updated_at: 2026-01-11T12:00:00Z

Preserved Data
~~~~~~~~~~~~~~

The following elements are preserved during migration:

- All field definitions and types
- Lineage configuration
- Residency configuration
- Custom metadata (with warning)
- All constraint values

Exit Codes
----------

.. list-table::
   :header-rows: 1

   * - Code
     - Meaning
   * - 0
     - Migration successful
   * - 1
     - Already at target version (no migration needed)
   * - 2
     - Error (file not found, parse error, no migration path)

Batch Migration
---------------

To migrate multiple contracts, use shell scripting:

.. code-block:: bash

   # Migrate all v0 contracts in a directory
   for file in contracts/*.yaml; do
     echo "Migrating $file..."
     griot migrate "$file" --in-place
   done

   # Or with find for recursive directories
   find contracts/ -name "*.yaml" -exec griot migrate {} --in-place \;

CI/CD Integration
-----------------

.. code-block:: yaml

   # GitHub Actions - Migrate and commit
   - name: Migrate Contracts
     run: |
       for file in contracts/*.yaml; do
         version=$(griot migrate "$file" --dry-run 2>&1 | grep "Detected" | awk '{print $4}')
         if [ "$version" = "v0" ]; then
           griot migrate "$file" --in-place
           echo "Migrated: $file"
         fi
       done

   - name: Commit Migrations
     run: |
       git add contracts/
       git diff --staged --quiet || git commit -m "chore: migrate contracts to ODCS v1.0.0"

Troubleshooting
---------------

**"Already at target version"**

The contract is already in ODCS v1.0.0 format. No migration needed.

**"No migration path"**

The detected version doesn't have a migration path to the target version.
Check the contract format and ensure it's a valid Griot contract.

**"YAML parse error"**

The input file has invalid YAML syntax. Fix the syntax errors before migrating.

See Also
--------

- :doc:`init` - Create new ODCS contracts
- :doc:`lint` - Validate contract structure
- :doc:`diff` - Compare contract versions
