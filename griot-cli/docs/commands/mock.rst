griot mock
==========

Generate mock data from a contract.

Synopsis
--------

.. code-block:: bash

   griot mock [OPTIONS] CONTRACT

Description
-----------

The ``mock`` command generates realistic test data based on a contract's schema
and constraints. Generated data respects all field types, formats, enums,
and numeric constraints.

Arguments
---------

``CONTRACT``
   Path to a contract file (YAML) or Python module containing a GriotModel.

Options
-------

``--rows``, ``-n``
   Number of rows to generate. Default: ``10``.

``--output``, ``-o``
   Output file path. If not specified, prints to stdout.

``--format``, ``-f``
   Output format. Choices: ``csv``, ``json``, ``parquet``. Default: ``csv``.

``--seed``
   Random seed for reproducible output.

Examples
--------

Basic Generation
~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Generate 10 rows (default) as CSV to stdout
   griot mock customer.yaml

   # Generate 100 rows
   griot mock customer.yaml --rows 100

   # Generate with specific seed for reproducibility
   griot mock customer.yaml --rows 50 --seed 42

Output Formats
~~~~~~~~~~~~~~

.. code-block:: bash

   # CSV format (default)
   griot mock customer.yaml -f csv -o test_data.csv

   # JSON format
   griot mock customer.yaml -f json -o test_data.json

   # Parquet format (requires pyarrow)
   griot mock customer.yaml -f parquet -o test_data.parquet

Output
------

CSV Format
~~~~~~~~~~

.. code-block:: text

   customer_id,email,age,status
   CUST-000001,john.smith@example.com,34,active
   CUST-000002,jane.doe@test.org,28,inactive
   CUST-000003,bob.wilson@company.net,45,active

JSON Format
~~~~~~~~~~~

.. code-block:: json

   [
     {
       "customer_id": "CUST-000001",
       "email": "john.smith@example.com",
       "age": 34,
       "status": "active"
     },
     {
       "customer_id": "CUST-000002",
       "email": "jane.doe@test.org",
       "age": 28,
       "status": "inactive"
     }
   ]

Constraint Handling
-------------------

The mock generator respects contract constraints:

- **Enums**: Values are randomly selected from allowed values
- **Numeric ranges**: Values respect ``ge``, ``le``, ``gt``, ``lt``
- **String lengths**: Strings respect ``min_length``, ``max_length``
- **Patterns**: Strings match specified regex patterns
- **Formats**: Email, UUID, date, datetime, URI, IPv4 are properly formatted
- **Unique fields**: Primary keys and unique fields have unique values
- **Nullable fields**: May include null values (configurable probability)

Example Contract
~~~~~~~~~~~~~~~~

.. code-block:: yaml

   name: Customer
   fields:
     customer_id:
       type: string
       primary_key: true
       pattern: "^CUST-\\d{6}$"
     email:
       type: string
       format: email
     age:
       type: integer
       ge: 18
       le: 120
     status:
       type: string
       enum: [active, inactive, pending]

Generated Data
~~~~~~~~~~~~~~

All generated data will:

- Have unique ``customer_id`` values matching the pattern
- Have valid email addresses
- Have ages between 18 and 120
- Have status from the allowed enum values

Exit Codes
----------

.. list-table::
   :header-rows: 1

   * - Code
     - Meaning
   * - 0
     - Success
   * - 2
     - Error (invalid contract, file write error, etc.)

See Also
--------

- :doc:`validate` - Validate generated data
- :doc:`lint` - Check contract quality
