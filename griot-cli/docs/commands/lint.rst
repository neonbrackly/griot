griot lint
==========

Check a contract for quality issues and best practices.

.. versionchanged:: 0.6.0
   Added ``--odcs-only`` and ``--summary`` flags for ODCS quality rule filtering.

Synopsis
--------

.. code-block:: bash

   griot lint [OPTIONS] CONTRACT

Description
-----------

The ``lint`` command analyzes a contract for potential issues, missing best practices,
and improvement suggestions. Issues are categorized by severity: error, warning, and info.

**ODCS Quality Rules (v0.6.0+):**

In addition to schema validation rules (G001-G005), the lint command now checks
for ODCS-specific quality rules (G006-G015) that ensure contracts follow the
Open Data Contract Standard best practices.

Arguments
---------

``CONTRACT``
   Path to a contract file (YAML) or Python module containing a GriotModel.

Options
-------

``--format``, ``-f``
   Output format. Choices: ``table``, ``json``, ``github``. Default: ``table``.

``--min-severity``
   Minimum severity level to report. Choices: ``error``, ``warning``, ``info``. Default: ``info``.

``--strict``
   Exit with code 1 if any issues are found (including warnings and info).

``--odcs-only``
   Show only ODCS-specific issues (rule codes G006-G015). Useful for checking
   ODCS compliance separately from schema validation.

``--summary``
   Show a summary of issues by category (schema vs ODCS) and severity before
   the detailed issue list.

Examples
--------

Basic Linting
~~~~~~~~~~~~~

.. code-block:: bash

   # Lint a contract
   griot lint customer.yaml

   # Lint and show only errors and warnings
   griot lint customer.yaml --severity warning

   # Lint and show only errors
   griot lint customer.yaml --severity error

Output Formats
~~~~~~~~~~~~~~

.. code-block:: bash

   # Table format (default)
   griot lint customer.yaml -f table

   # JSON format
   griot lint customer.yaml -f json

   # GitHub Actions format
   griot lint customer.yaml -f github

Strict Mode
~~~~~~~~~~~

.. code-block:: bash

   # Fail if any issues found
   griot lint customer.yaml --strict

ODCS-Only Mode
~~~~~~~~~~~~~~

.. versionadded:: 0.6.0

.. code-block:: bash

   # Show only ODCS quality issues (G006-G015)
   griot lint customer.yaml --odcs-only

   # Output:
   # Found 2 ODCS issue(s):
   # [G006] [info]: No quality rules defined
   # [G010] [warning]: No description.purpose defined

Summary Mode
~~~~~~~~~~~~

.. versionadded:: 0.6.0

.. code-block:: bash

   # Show summary before detailed issues
   griot lint customer.yaml --summary

   # Output:
   # === Lint Summary ===
   # Total issues: 5
   #
   # By Severity:
   #   Warnings: 3
   #   Info:     2
   #
   # By Category:
   #   Schema Rules (G001-G005): 2
   #   ODCS Rules (G006-G015):   3
   #
   # Found 5 issue(s):
   # ...

Combined Options
~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Strict mode with ODCS-only filtering
   griot lint customer.yaml --strict --odcs-only

   # Summary with minimum severity
   griot lint contracts/ --summary --min-severity warning

Output
------

Table Format
~~~~~~~~~~~~

.. code-block:: text

   Found 3 issue(s):
   --------------------------------------------------------------------------------
   [MISSING_DESCRIPTION] [warning] (email): Field has no description
       Suggestion: Add a description to improve documentation
   [NO_PRIMARY_KEY] [info]: Contract has no primary key defined
       Suggestion: Consider adding primary_key=True to an identifier field
   [BROAD_TYPE] [warning] (metadata): Field uses generic 'object' type
       Suggestion: Define a more specific type or use nested fields

Issue Codes
-----------

Schema Rules (G001-G005)
~~~~~~~~~~~~~~~~~~~~~~~~

Basic schema validation rules:

.. list-table::
   :header-rows: 1
   :widths: 15 15 70

   * - Code
     - Severity
     - Description
   * - ``G001``
     - warning
     - No primary key defined
   * - ``G002``
     - warning
     - Field has no meaningful description
   * - ``G003``
     - info
     - String field without constraints (max_length, pattern)
   * - ``G004``
     - info
     - Numeric field without range constraints (ge, le)
   * - ``G005``
     - warning
     - Field name should be snake_case

ODCS Quality Rules (G006-G015)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. versionadded:: 0.6.0

ODCS-specific quality rules for Open Data Contract Standard compliance:

.. list-table::
   :header-rows: 1
   :widths: 15 15 70

   * - Code
     - Severity
     - Description
   * - ``G006``
     - info
     - No quality rules defined in contract
   * - ``G007``
     - warning
     - Completeness rule missing ``min_percent`` threshold
   * - ``G008``
     - warning
     - Freshness rule missing ``timestamp_field`` reference
   * - ``G009``
     - error
     - Custom check missing ``definition`` or ``type``
   * - ``G010``
     - warning
     - No ``description.purpose`` defined
   * - ``G011``
     - info
     - No SLA section defined
   * - ``G012``
     - warning
     - No ``governance.producer`` defined
   * - ``G013``
     - info
     - Missing team information
   * - ``G014``
     - warning
     - No ``legal.jurisdiction`` defined
   * - ``G015``
     - warning
     - No ``compliance.data_classification`` defined

Legacy Issue Codes
~~~~~~~~~~~~~~~~~~

These legacy codes are also supported for backwards compatibility:

.. list-table::
   :header-rows: 1
   :widths: 30 15 55

   * - Code
     - Severity
     - Description
   * - ``MISSING_DESCRIPTION``
     - warning
     - Field lacks a description (alias for G002)
   * - ``NO_PRIMARY_KEY``
     - info
     - Contract has no primary key (alias for G001)
   * - ``BROAD_TYPE``
     - warning
     - Field uses overly broad type (e.g., ``object``, ``any``)
   * - ``MISSING_CONSTRAINTS``
     - info
     - Field has no constraints (alias for G003/G004)
   * - ``PII_NO_MASKING``
     - error
     - PII field lacks masking strategy
   * - ``SENSITIVE_NO_LEGAL_BASIS``
     - warning
     - Sensitive field lacks legal basis

Exit Codes
----------

.. list-table::
   :header-rows: 1

   * - Code
     - Meaning
   * - 0
     - No issues found, or only info-level issues (without ``--strict``)
   * - 1
     - Errors or warnings found, or any issues with ``--strict``
   * - 2
     - Error (file not found, invalid contract, etc.)

See Also
--------

- :doc:`validate` - Validate data against contract
- :doc:`diff` - Compare contract versions
