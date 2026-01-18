Quality Rules
=============

Quality rules define data validation constraints following the ODCS specification.
Griot Core provides type-safe builders for creating quality rules.

Overview
--------

Quality rules can be applied at two levels:

1. **Property-level**: Validate individual columns/fields
2. **Schema-level**: Validate the entire dataset

Each rule specifies:

- **Metric**: What to measure (null count, duplicate count, etc.)
- **Operator**: How to compare (must be, must be less than, etc.)
- **Threshold**: The comparison value
- **Unit**: Rows (absolute count) or percent

Using QualityRule Builders
--------------------------

The :class:`~griot_core.QualityRule` class provides type-safe factory methods:

.. code-block:: python

   from griot_core import QualityRule, QualityUnit

   # Create quality rules using builders
   rule1 = QualityRule.null_values(must_be=0)
   rule2 = QualityRule.missing_values(must_be_less_than=5, unit=QualityUnit.PERCENT)
   rule3 = QualityRule.invalid_values(must_be=0, valid_values=['A', 'B', 'C'])

The builders produce ODCS-compliant dictionaries:

.. code-block:: python

   print(rule1)
   # {'metric': 'nullValues', 'mustBe': 0}

   print(rule2)
   # {'metric': 'missingValues', 'mustBeLessThan': 5, 'unit': 'percent'}

   print(rule3)
   # {'metric': 'invalidValues', 'mustBe': 0, 'arguments': {'validValues': ['A', 'B', 'C']}}

Property-Level Metrics
----------------------

Null Values
^^^^^^^^^^^

Count of null/None values in a column:

.. code-block:: python

   from griot_core import Field, QualityRule

   # No nulls allowed
   required_field: str = Field(
       "Required field",
       quality=[QualityRule.null_values(must_be=0)]
   )

   # Allow up to 5% nulls
   optional_field: str = Field(
       "Optional field",
       quality=[
           QualityRule.null_values(
               must_be_less_or_equal_to=5,
               unit=QualityUnit.PERCENT
           )
       ]
   )

   # At least 10 nulls (unusual but valid)
   special_field: str = Field(
       "Special field",
       quality=[QualityRule.null_values(must_be_greater_than=10)]
   )

Missing Values
^^^^^^^^^^^^^^

Count of values considered "missing" (null, empty string, N/A, etc.):

.. code-block:: python

   # Default missing values: [None, '', 'N/A', 'n/a']
   QualityRule.missing_values(must_be=0)

   # Custom missing values list
   QualityRule.missing_values(
       must_be=0,
       missing_values_list=[None, '', 'N/A', 'NULL', '-']
   )

   # Allow up to 10% missing
   QualityRule.missing_values(
       must_be_less_or_equal_to=10,
       unit=QualityUnit.PERCENT
   )

Invalid Values
^^^^^^^^^^^^^^

Count of values failing validation rules:

**Enum validation** (values must be in a set):

.. code-block:: python

   status: str = Field(
       "Order status",
       quality=[
           QualityRule.invalid_values(
               must_be=0,
               valid_values=['pending', 'processing', 'shipped', 'delivered']
           )
       ]
   )

**Pattern validation** (values must match regex):

.. code-block:: python

   email: str = Field(
       "Email address",
       quality=[
           QualityRule.invalid_values(
               must_be=0,
               pattern=r'^[\w.-]+@[\w.-]+\.\w+$'
           )
       ]
   )

   phone: str = Field(
       "Phone number",
       quality=[
           QualityRule.invalid_values(
               must_be=0,
               pattern=r'^\+?[1-9]\d{1,14}$'  # E.164 format
           )
       ]
   )

**Range validation** (numeric values):

.. code-block:: python

   age: int = Field(
       "Customer age",
       quality=[
           QualityRule.invalid_values(
               must_be=0,
               min_value=0,
               max_value=150
           )
       ]
   )

   price: float = Field(
       "Product price",
       quality=[
           QualityRule.invalid_values(
               must_be=0,
               min_value=0.01,
               max_value=1000000.00
           )
       ]
   )

**Length validation** (string length):

.. code-block:: python

   username: str = Field(
       "Username",
       quality=[
           QualityRule.invalid_values(
               must_be=0,
               min_length=3,
               max_length=50
           )
       ]
   )

Duplicate Values
^^^^^^^^^^^^^^^^

Count of duplicate values in a column:

.. code-block:: python

   # No duplicates allowed (unique values)
   email: str = Field(
       "Email address",
       unique=True,
       quality=[QualityRule.duplicate_values(must_be=0)]
   )

   # Allow some duplicates (e.g., status field)
   status: str = Field(
       "Status",
       quality=[
           QualityRule.duplicate_values(
               must_be_less_than=90,
               unit=QualityUnit.PERCENT
           )
       ]
   )

Schema-Level Metrics
--------------------

Schema-level rules apply to the entire dataset:

.. code-block:: python

   class OrderSchema(Schema):
       """Schema with schema-level quality rules."""

       _quality = [
           QualityRule.row_count(must_be_greater_than=0),
           QualityRule.duplicate_rows(
               must_be=0,
               properties=['order_id', 'line_number']
           ),
       ]

       order_id: str = Field("Order ID", primary_key=True)
       line_number: int = Field("Line number")
       # ...

Row Count
^^^^^^^^^

Validate total number of rows:

.. code-block:: python

   # At least 1 row
   QualityRule.row_count(must_be_greater_than=0)

   # Exactly 1000 rows
   QualityRule.row_count(must_be=1000)

   # Between 100 and 10000 rows
   QualityRule.row_count(must_be_between=[100, 10000])

   # Not empty
   QualityRule.row_count(must_not_be=0)

Duplicate Rows
^^^^^^^^^^^^^^

Check for duplicate rows across specified columns:

.. code-block:: python

   # No duplicate rows on composite key
   QualityRule.duplicate_rows(
       must_be=0,
       properties=['order_id', 'line_number']
   )

   # No completely duplicate rows (all columns)
   QualityRule.duplicate_rows(must_be=0)

   # Allow up to 1% duplicates
   QualityRule.duplicate_rows(
       must_be_less_or_equal_to=1,
       unit=QualityUnit.PERCENT,
       properties=['customer_id', 'product_id']
   )

Comparison Operators
--------------------

All rules support these operators:

.. list-table::
   :header-rows: 1
   :widths: 30 30 40

   * - Parameter
     - ODCS Operator
     - Description
   * - ``must_be``
     - ``mustBe``
     - Equals
   * - ``must_not_be``
     - ``mustNotBe``
     - Not equals
   * - ``must_be_greater_than``
     - ``mustBeGreaterThan``
     - Greater than (exclusive)
   * - ``must_be_greater_or_equal_to``
     - ``mustBeGreaterOrEqualTo``
     - Greater than or equal
   * - ``must_be_less_than``
     - ``mustBeLessThan``
     - Less than (exclusive)
   * - ``must_be_less_or_equal_to``
     - ``mustBeLessOrEqualTo``
     - Less than or equal
   * - ``must_be_between``
     - ``mustBeBetween``
     - Between two values (exclusive)
   * - ``must_not_be_between``
     - ``mustNotBeBetween``
     - Not between two values

Units
-----

Use :class:`~griot_core.QualityUnit` to specify units:

.. code-block:: python

   from griot_core import QualityUnit

   # Absolute row count (default)
   QualityRule.null_values(must_be_less_than=10)
   QualityRule.null_values(must_be_less_than=10, unit=QualityUnit.ROWS)

   # Percentage of total rows
   QualityRule.null_values(must_be_less_than=5, unit=QualityUnit.PERCENT)

Rule Naming
-----------

Add identifiers for tracking:

.. code-block:: python

   QualityRule.null_values(
       must_be=0,
       rule_id="email_not_null",
       name="Email field cannot be null"
   )

Advanced Examples
-----------------

**Complex field with multiple rules**:

.. code-block:: python

   class TransactionSchema(Schema):
       amount: float = Field(
           "Transaction amount",
           critical_data_element=True,
           quality=[
               QualityRule.null_values(
                   must_be=0,
                   rule_id="amount_required"
               ),
               QualityRule.invalid_values(
                   must_be=0,
                   min_value=0.01,
                   rule_id="amount_positive"
               ),
               QualityRule.invalid_values(
                   must_be=0,
                   max_value=1000000,
                   rule_id="amount_reasonable"
               ),
           ]
       )

**Schema with comprehensive rules**:

.. code-block:: python

   class CustomerSchema(Schema):
       _quality = [
           QualityRule.row_count(must_be_greater_than=0),
           QualityRule.duplicate_rows(must_be=0, properties=['customer_id']),
       ]

       customer_id: str = Field(
           "Customer ID",
           primary_key=True,
           quality=[
               QualityRule.null_values(must_be=0),
               QualityRule.duplicate_values(must_be=0),
               QualityRule.invalid_values(must_be=0, pattern=r'^CUST-\d{6}$'),
           ]
       )

       email: str = Field(
           "Email address",
           unique=True,
           quality=[
               QualityRule.null_values(must_be=0),
               QualityRule.invalid_values(
                   must_be=0,
                   pattern=r'^[\w.-]+@[\w.-]+\.\w+$'
               ),
           ]
       )

       status: str = Field(
           "Account status",
           quality=[
               QualityRule.invalid_values(
                   must_be=0,
                   valid_values=['active', 'inactive', 'suspended']
               ),
           ]
       )

       age: int = Field(
           "Customer age",
           nullable=True,
           quality=[
               QualityRule.null_values(must_be_less_than=10, unit=QualityUnit.PERCENT),
               QualityRule.invalid_values(must_be=0, min_value=0, max_value=150),
           ]
       )

Using Raw Dictionaries
----------------------

You can also use raw ODCS dictionaries:

.. code-block:: python

   quality=[
       {
           "metric": "nullValues",
           "mustBe": 0,
           "id": "no_nulls"
       },
       {
           "metric": "invalidValues",
           "mustBe": 0,
           "arguments": {
               "validValues": ["A", "B", "C"]
           }
       }
   ]

.. tip::

   Prefer using ``QualityRule`` builders for type safety and autocompletion.

Next Steps
----------

- See :doc:`validation` to validate data against rules
- Learn about :doc:`contracts` management
- Check the :doc:`../api/types` for type definitions
