griot validate
==============

Validate data against a contract.

Synopsis
--------

.. code-block:: bash

   griot validate [OPTIONS] CONTRACT DATA

Description
-----------

The ``validate`` command checks that data conforms to a contract's schema,
types, and constraints. It reports all validation errors found in the data.

Arguments
---------

``CONTRACT``
   Path to a contract file (YAML) or Python module containing a GriotModel.

``DATA``
   Path to data file (CSV, JSON, or Parquet) to validate.

Options
-------

``--format``, ``-f``
   Output format. Choices: ``table``, ``json``, ``github``. Default: ``table``.

``--max-errors``
   Maximum number of errors to display. Default: ``100``.

``--fail-on-warning``
   Exit with code 1 if any warnings are present (not just errors).

``--strict``
   Enable strict mode. All warnings are treated as errors.

``--sample``
   Number of rows to validate. Use for large datasets. Default: all rows.

Examples
--------

Basic Validation
~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Validate CSV data against a contract
   griot validate customer.yaml customers.csv

   # Validate JSON data
   griot validate order.yaml orders.json

   # Validate Parquet data
   griot validate product.yaml products.parquet

Output Formats
~~~~~~~~~~~~~~

.. code-block:: bash

   # Table format (default, human-readable)
   griot validate customer.yaml data.csv -f table

   # JSON format (machine-readable)
   griot validate customer.yaml data.csv -f json

   # GitHub Actions annotations
   griot validate customer.yaml data.csv -f github

Strict Mode
~~~~~~~~~~~

.. code-block:: bash

   # Fail on any warnings
   griot validate customer.yaml data.csv --fail-on-warning

   # Strict mode (all warnings as errors)
   griot validate customer.yaml data.csv --strict

Sampling Large Datasets
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Validate only first 1000 rows
   griot validate customer.yaml large_file.csv --sample 1000

Output
------

Table Format
~~~~~~~~~~~~

.. code-block:: text

   Validation PASSED

   Rows validated: 1000
   Errors: 0
   Error rate: 0.00%
   Duration: 45.23ms

When validation fails:

.. code-block:: text

   Validation FAILED

   Rows validated: 1000
   Errors: 15
   Error rate: 1.50%
   Duration: 52.17ms

   Errors:
   --------------------------------------------------------------------------------
     [row 42] email: Invalid email format 'not-an-email'
     [row 156] age: Value -5 is less than minimum 0
     [row 789] status: Value 'unknown' not in allowed values ['active', 'inactive']
     ... and 12 more errors

JSON Format
~~~~~~~~~~~

.. code-block:: json

   {
     "passed": false,
     "row_count": 1000,
     "error_count": 15,
     "error_rate": 0.015,
     "duration_ms": 52.17,
     "errors": [
       {
         "field": "email",
         "row": 42,
         "value": "not-an-email",
         "message": "Invalid email format",
         "severity": "error"
       }
     ]
   }

GitHub Format
~~~~~~~~~~~~~

.. code-block:: text

   ::error::Row 42 - email: Invalid email format 'not-an-email'
   ::error::Row 156 - age: Value -5 is less than minimum 0
   ::warning::Row 200 - name: Field is empty (recommended to have value)

Exit Codes
----------

.. list-table::
   :header-rows: 1

   * - Code
     - Meaning
   * - 0
     - Validation passed
   * - 1
     - Validation failed (errors found, or warnings with ``--fail-on-warning``)
   * - 2
     - Error (file not found, invalid contract, etc.)

See Also
--------

- :doc:`lint` - Check contract quality
- :doc:`mock` - Generate test data
