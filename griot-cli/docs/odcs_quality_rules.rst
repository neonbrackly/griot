ODCS Quality Rules Reference
============================

.. versionadded:: 0.6.0

This document provides a complete reference for all ODCS (Open Data Contract Standard)
quality rules checked by the ``griot lint`` command.

Overview
--------

ODCS quality rules are divided into two categories:

1. **Schema Rules (G001-G005)**: Basic schema validation rules
2. **ODCS Rules (G006-G015)**: ODCS-specific compliance rules

Use ``griot lint --odcs-only`` to check only ODCS rules, or ``griot lint --summary``
to see a breakdown by category.

Schema Rules (G001-G005)
------------------------

These rules check basic schema quality and field definitions.

G001: No Primary Key Defined
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Severity:** Warning

**Description:** The contract has no field marked as ``primary_key: true``.

**Impact:** Without a primary key, it's harder to identify unique records,
perform joins, or track data lineage.

**How to Fix:**

.. code-block:: yaml

   schema:
     - name: customer
       properties:
         - name: id
           primary_key: true  # Add this
           logicalType: string

G002: Field Has No Meaningful Description
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Severity:** Warning

**Description:** A field lacks a description or has a generic description.

**Impact:** Poor documentation makes the contract harder to understand for consumers.

**How to Fix:**

.. code-block:: yaml

   properties:
     - name: customer_segment
       description: "Customer market segment (enterprise, mid-market, smb)"  # Add meaningful description

G003: String Field Without Constraints
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Severity:** Info

**Description:** A string field has no ``max_length`` or ``pattern`` constraints.

**Impact:** Unbounded strings can cause storage issues and validation gaps.

**How to Fix:**

.. code-block:: yaml

   properties:
     - name: email
       logicalType: string
       constraints:
         max_length: 255
         pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"

G004: Numeric Field Without Range Constraints
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Severity:** Info

**Description:** A numeric field has no ``ge`` (greater than or equal) or ``le``
(less than or equal) constraints.

**Impact:** Unbounded numbers can indicate missing business rules.

**How to Fix:**

.. code-block:: yaml

   properties:
     - name: age
       logicalType: integer
       constraints:
         ge: 0
         le: 150

G005: Field Name Should Be snake_case
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Severity:** Warning

**Description:** Field name doesn't follow snake_case convention.

**Impact:** Inconsistent naming makes the schema harder to use.

**How to Fix:**

.. code-block:: yaml

   # Bad
   - name: CustomerID
   - name: customer-id

   # Good
   - name: customer_id

ODCS Rules (G006-G015)
----------------------

These rules check ODCS-specific sections for completeness and correctness.

G006: No Quality Rules Defined
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Severity:** Info

**Description:** The contract has no ``quality`` section or the section is empty.

**Impact:** Without quality rules, data quality cannot be automatically validated.

**How to Fix:**

.. code-block:: yaml

   schema:
     - name: customer
       properties: [...]
       quality:
         - rule: completeness
           min_percent: 99.0
           critical_fields:
             - id
             - email
         - rule: freshness
           max_age: PT24H
           timestamp_field: updated_at

G007: Completeness Rule Missing min_percent
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Severity:** Warning

**Description:** A completeness rule is defined but has no ``min_percent`` threshold.

**Impact:** Without a threshold, completeness checks cannot determine pass/fail.

**How to Fix:**

.. code-block:: yaml

   quality:
     - rule: completeness
       min_percent: 99.0  # Required
       critical_fields:
         - id

G008: Freshness Rule Missing timestamp_field
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Severity:** Warning

**Description:** A freshness rule is defined but has no ``timestamp_field`` reference.

**Impact:** Without knowing which field to check, freshness validation cannot work.

**How to Fix:**

.. code-block:: yaml

   quality:
     - rule: freshness
       max_age: PT24H
       timestamp_field: updated_at  # Required - which field to check

G009: Custom Check Missing Definition
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Severity:** Error

**Description:** A custom check is defined but lacks ``definition`` or ``type``.

**Impact:** The custom check cannot be executed without these required fields.

**How to Fix:**

.. code-block:: yaml

   quality:
     - rule: custom
       name: check_email_domain
       type: sql  # Required
       definition: |  # Required
         SELECT COUNT(*) = 0
         FROM {table}
         WHERE email NOT LIKE '%@example.com'

G010: No description.purpose Defined
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Severity:** Warning

**Description:** The contract has no ``description.purpose`` field.

**Impact:** Consumers don't know what the data is for or how to use it.

**How to Fix:**

.. code-block:: yaml

   description:
     purpose: |
       Customer profile data for personalization,
       marketing segmentation, and support.
     usage: |
       Use for customer analytics and targeting.

G011: No SLA Section Defined
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Severity:** Info

**Description:** The contract has no ``sla`` section.

**Impact:** No formal service level agreement for availability or freshness.

**How to Fix:**

.. code-block:: yaml

   sla:
     availability:
       target_percent: 99.0
       measurement_window: P30D
     freshness:
       target: P1D
     completeness:
       target_percent: 99.5

G012: No governance.producer Defined
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Severity:** Warning

**Description:** The contract has no ``governance.producer`` section.

**Impact:** No clear ownership or contact information for the data.

**How to Fix:**

.. code-block:: yaml

   governance:
     producer:
       team: Customer Data Team
       contact: customer-data@example.com
       responsibilities:
         - Maintain data quality
         - Respond to consumer questions

G013: Missing Team Information
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Severity:** Info

**Description:** The contract has no ``team`` section.

**Impact:** No organizational context for the contract.

**How to Fix:**

.. code-block:: yaml

   team:
     name: Customer Data Team
     department: Data Engineering
     steward:
       name: Jane Doe
       email: jane.doe@example.com

G014: No legal.jurisdiction Defined
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Severity:** Warning

**Description:** The contract has no ``legal.jurisdiction`` field.

**Impact:** Unclear which legal frameworks apply to the data.

**How to Fix:**

.. code-block:: yaml

   legal:
     jurisdiction:
       - US
       - EU
     basis: legitimate_interest
     regulations:
       - GDPR
       - CCPA

G015: No compliance.data_classification Defined
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Severity:** Warning

**Description:** The contract has no ``compliance.data_classification`` field.

**Impact:** Data handling requirements are unclear.

**How to Fix:**

.. code-block:: yaml

   compliance:
     data_classification: internal  # Or: public, confidential, restricted
     regulatory_scope:
       - GDPR
     audit_requirements:
       logging: true
       log_retention: P365D

Quick Reference Table
---------------------

.. list-table::
   :header-rows: 1
   :widths: 10 15 50 25

   * - Code
     - Severity
     - Description
     - Fix
   * - G001
     - Warning
     - No primary key defined
     - Add ``primary_key: true``
   * - G002
     - Warning
     - Field has no description
     - Add ``description`` field
   * - G003
     - Info
     - String without constraints
     - Add ``max_length``/``pattern``
   * - G004
     - Info
     - Numeric without range
     - Add ``ge``/``le`` constraints
   * - G005
     - Warning
     - Not snake_case
     - Rename to snake_case
   * - G006
     - Info
     - No quality rules
     - Add ``quality`` section
   * - G007
     - Warning
     - Completeness missing threshold
     - Add ``min_percent``
   * - G008
     - Warning
     - Freshness missing field
     - Add ``timestamp_field``
   * - G009
     - Error
     - Custom check incomplete
     - Add ``type`` and ``definition``
   * - G010
     - Warning
     - No purpose defined
     - Add ``description.purpose``
   * - G011
     - Info
     - No SLA defined
     - Add ``sla`` section
   * - G012
     - Warning
     - No producer defined
     - Add ``governance.producer``
   * - G013
     - Info
     - No team info
     - Add ``team`` section
   * - G014
     - Warning
     - No jurisdiction
     - Add ``legal.jurisdiction``
   * - G015
     - Warning
     - No classification
     - Add ``compliance.data_classification``

CI/CD Integration
-----------------

Check ODCS compliance in your pipeline:

.. code-block:: yaml

   # GitHub Actions
   - name: Check ODCS Compliance
     run: |
       griot lint contracts/ --odcs-only --strict

   - name: Full Lint Check
     run: |
       griot lint contracts/ --summary --min-severity warning

See Also
--------

- :doc:`commands/lint` - Full lint command reference
- :doc:`commands/init` - Create ODCS-compliant contracts
- :doc:`commands/migrate` - Migrate legacy contracts to ODCS format
