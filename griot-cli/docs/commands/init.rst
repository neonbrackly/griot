griot init
==========

Initialize a new ODCS-format data contract.

.. versionadded:: 0.6.0

Synopsis
--------

.. code-block:: bash

   griot init [OPTIONS] NAME

Description
-----------

The ``init`` command scaffolds a new data contract following the Open Data
Contract Standard (ODCS) v1.0.0 format. It generates a complete contract
template with all ODCS sections pre-populated with smart defaults.

This is the recommended way to create new contracts, as it ensures:

- Proper ODCS structure with all required sections
- Audit-ready default values for compliance
- Privacy-preserving defaults for sensitive settings
- Consistent contract format across your organization

Arguments
---------

``NAME``
   Human-readable name for the contract (e.g., "Customer Profile", "Order Events").
   Used to generate the contract ID and schema name.

Options
-------

``--output``, ``-o``
   Output file path. Defaults to ``<contract-id>.yaml`` in current directory.

``--id``
   Contract ID. Defaults to name converted to kebab-case (e.g., "Customer Profile" becomes "customer-profile").

``--purpose``, ``-p``
   Purpose description for the contract. Appears in the description.purpose field.

``--team``, ``-t``
   Team responsible for this contract. Defaults to "Data Team".

``--contact``
   Contact email for the team. Defaults to "team@example.com".

``--jurisdiction``, ``-j``
   Primary legal jurisdiction (e.g., US, EU, UK). Defaults to "US".

``--force``, ``-f``
   Overwrite existing file without prompting.

Examples
--------

Basic Usage
~~~~~~~~~~~

.. code-block:: bash

   # Create a new contract
   griot init "Customer Profile"

   # Output:
   # Created contract: customer-profile.yaml
   #   ID: customer-profile
   #   Name: Customer Profile
   #   Team: Data Team
   #
   # Next steps:
   #   1. Edit customer-profile.yaml to add your schema fields
   #   2. Run 'griot lint' to check for issues
   #   3. Run 'griot push' to publish to registry

Custom Output Location
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Save to specific path
   griot init "Order Events" -o contracts/orders.yaml

   # Save with custom ID
   griot init "User Activity Log" --id user-activity-v2

Team and Jurisdiction
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Set team and jurisdiction
   griot init "User Data" --team "Analytics" --jurisdiction EU

   # Full configuration
   griot init "Payment Transactions" \
     --team "Payments Team" \
     --contact "payments@example.com" \
     --jurisdiction US \
     --purpose "Payment processing transaction records for audit and reconciliation"

Overwriting Existing Files
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Fails if file exists
   griot init "Customer Profile"
   # Error: File already exists: customer-profile.yaml
   # Use --force to overwrite.

   # Force overwrite
   griot init "Customer Profile" --force

Generated Contract Structure
----------------------------

The generated contract includes all ODCS sections:

.. code-block:: yaml

   # Contract metadata
   api_version: v1.0.0
   kind: DataContract
   id: customer-profile
   name: Customer Profile
   version: 1.0.0
   status: draft

   # Description section
   description:
     purpose: Your purpose description
     usage: |
       Describe how this data should be used.
     limitations: |
       Document any known limitations or caveats.

   # Schema with example field
   schema:
     - name: customer_profile
       physicalType: table
       properties:
         - name: id
           description: Primary identifier
           logicalType: string
           primary_key: true
           # ... constraints, semantic, privacy sections

       # Pre-configured quality rules
       quality:
         - rule: completeness
           min_percent: 99.0
         - rule: freshness
           max_age: PT24H

   # Legal and compliance
   legal:
     jurisdiction:
       - US
     basis: legitimate_interest

   compliance:
     data_classification: internal
     audit_requirements:
       logging: true
       log_retention: P365D

   # SLA definitions
   sla:
     availability:
       target_percent: 99.0
     freshness:
       target: P1D

   # Governance structure
   governance:
     producer:
       team: Data Team
       contact: team@example.com
     review:
       cadence: quarterly
     change_management:
       breaking_change_notice: P30D
       deprecation_notice: P90D

   # Team and timestamps
   team:
     name: Data Team
   timestamps:
     created_at: 2026-01-11T12:00:00Z
     updated_at: 2026-01-11T12:00:00Z

Default Values
--------------

The following audit-ready defaults are applied:

**Privacy Defaults:**

- ``contains_pii: false`` - Explicit opt-in required for PII
- ``sensitivity_level: internal`` - Safe default classification

**Compliance Defaults:**

- ``data_classification: internal``
- ``audit_requirements.logging: true``
- ``audit_requirements.log_retention: P365D`` (1 year)

**SLA Defaults:**

- ``availability.target_percent: 99.0``
- ``freshness.target: P1D`` (daily updates expected)

**Governance Defaults:**

- ``review.cadence: quarterly``
- ``breaking_change_notice: P30D`` (30 days notice)
- ``deprecation_notice: P90D`` (90 days notice)

Exit Codes
----------

.. list-table::
   :header-rows: 1

   * - Code
     - Meaning
   * - 0
     - Success
   * - 1
     - File already exists (use ``--force`` to overwrite)
   * - 2
     - Error (permission denied, invalid path, etc.)

Workflow
--------

Typical workflow for creating and publishing a contract:

.. code-block:: bash

   # 1. Scaffold new contract
   griot init "Customer Profile" -o contracts/customer.yaml

   # 2. Edit the contract to add your schema fields
   $EDITOR contracts/customer.yaml

   # 3. Validate the contract structure
   griot lint contracts/customer.yaml

   # 4. Push to registry
   griot push contracts/customer.yaml -m "Initial version"

See Also
--------

- :doc:`lint` - Check contract for quality issues
- :doc:`migrate` - Migrate old contracts to ODCS format
- :doc:`push` - Push contract to registry
- :doc:`../odcs_quality_rules` - ODCS quality rules reference
