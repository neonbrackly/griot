griot lint
==========

Check a contract for quality issues and best practices.

Synopsis
--------

.. code-block:: bash

   griot lint [OPTIONS] CONTRACT

Description
-----------

The ``lint`` command analyzes a contract for potential issues, missing best practices,
and improvement suggestions. Issues are categorized by severity: error, warning, and info.

Arguments
---------

``CONTRACT``
   Path to a contract file (YAML) or Python module containing a GriotModel.

Options
-------

``--format``, ``-f``
   Output format. Choices: ``table``, ``json``, ``github``. Default: ``table``.

``--severity``
   Minimum severity level to report. Choices: ``error``, ``warning``, ``info``. Default: ``info``.

``--strict``
   Exit with code 1 if any issues are found (including warnings and info).

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

Common issue codes:

.. list-table::
   :header-rows: 1

   * - Code
     - Severity
     - Description
   * - ``MISSING_DESCRIPTION``
     - warning
     - Field lacks a description
   * - ``NO_PRIMARY_KEY``
     - info
     - Contract has no primary key
   * - ``BROAD_TYPE``
     - warning
     - Field uses overly broad type (e.g., ``object``, ``any``)
   * - ``MISSING_CONSTRAINTS``
     - info
     - Field has no constraints
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
