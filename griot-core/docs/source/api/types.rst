Types API
=========

The types module provides enumerations and type definitions for Griot Core.

Enums
-----

ContractStatus
^^^^^^^^^^^^^^

.. class:: griot_core.ContractStatus

   Contract lifecycle status based on ODCS specification.

   .. attribute:: DRAFT
      :value: "draft"

      Contract is under development, not for production use.

   .. attribute:: ACTIVE
      :value: "active"

      Contract is production-ready, consumers can depend on it.

   .. attribute:: DEPRECATED
      :value: "deprecated"

      Contract is being phased out, consumers should migrate.

   .. attribute:: RETIRED
      :value: "retired"

      Contract is no longer available.

   **Example**

   .. code-block:: python

      from griot_core import Contract, ContractStatus

      # Create a draft contract
      contract = Contract(
          id="my-contract",
          status=ContractStatus.DRAFT
      )

      # Promote to active
      contract.status = ContractStatus.ACTIVE

      # Mark for deprecation
      contract.status = ContractStatus.DEPRECATED

DataType
^^^^^^^^

.. class:: griot_core.DataType

   Supported logical data types for contract fields.

   .. attribute:: STRING
      :value: "string"

      Text data (Python ``str``).

   .. attribute:: INTEGER
      :value: "integer"

      Whole numbers (Python ``int``).

   .. attribute:: FLOAT
      :value: "float"

      Decimal numbers (Python ``float``).

   .. attribute:: BOOLEAN
      :value: "boolean"

      True/False values (Python ``bool``).

   .. attribute:: DATE
      :value: "date"

      Date values (ISO format string).

   .. attribute:: DATETIME
      :value: "datetime"

      Date and time values (ISO format string).

   .. attribute:: ARRAY
      :value: "array"

      Lists/arrays (Python ``list``).

   .. attribute:: OBJECT
      :value: "object"

      Nested objects (Python ``dict``).

   .. attribute:: ANY
      :value: "any"

      Any type.

   **Methods**

   .. method:: from_python_type(python_type: type | str) -> DataType
      :classmethod:

      Convert a Python type to a DataType.

      :param python_type: Python type or type name string
      :returns: Corresponding DataType

      .. code-block:: python

         DataType.from_python_type(str)      # DataType.STRING
         DataType.from_python_type(int)      # DataType.INTEGER
         DataType.from_python_type("date")   # DataType.DATE

   .. method:: to_python_type() -> type

      Convert DataType to Python type.

      :returns: Python type

      .. code-block:: python

         DataType.STRING.to_python_type()   # str
         DataType.INTEGER.to_python_type()  # int

Severity
^^^^^^^^

.. class:: griot_core.Severity

   Error/issue severity levels.

   .. attribute:: ERROR
      :value: "error"

      Critical issue that must be fixed.

   .. attribute:: WARNING
      :value: "warning"

      Potential issue that should be reviewed.

   .. attribute:: INFO
      :value: "info"

      Informational message.

   **Example**

   .. code-block:: python

      from griot_core import lint_contract, Severity

      issues = lint_contract(contract)
      errors = [i for i in issues if i.severity == Severity.ERROR]
      warnings = [i for i in issues if i.severity == Severity.WARNING]

DataFrameType
^^^^^^^^^^^^^

.. class:: griot_core.DataFrameType

   Supported DataFrame backend types.

   .. attribute:: PANDAS
      :value: "pandas"

      pandas DataFrame.

   .. attribute:: POLARS
      :value: "polars"

      polars DataFrame.

   .. attribute:: SPARK
      :value: "spark"

      PySpark DataFrame.

   .. attribute:: DASK
      :value: "dask"

      Dask DataFrame.

Quality Rule Enums
------------------

QualityCheckType
^^^^^^^^^^^^^^^^

.. class:: griot_core.QualityCheckType

   Types of validation checks based on ODCS specification.

   .. attribute:: LIBRARY
      :value: "library"

      Executable checks using standard metrics (nullValues, etc.).

   .. attribute:: TEXT
      :value: "text"

      Human-readable rules for documentation.

   .. attribute:: SQL
      :value: "sql"

      SQL-based validation queries.

   .. attribute:: CUSTOM
      :value: "custom"

      Vendor-specific custom checks.

QualityMetric
^^^^^^^^^^^^^

.. class:: griot_core.QualityMetric

   ODCS quality metrics for library-type checks.

   **Property-Level Metrics** (operate on a single column):

   .. attribute:: NULL_VALUES
      :value: "nullValues"

      Count of null/None values in a column.

   .. attribute:: MISSING_VALUES
      :value: "missingValues"

      Count of values considered missing (null, empty string, N/A, etc.).

   .. attribute:: INVALID_VALUES
      :value: "invalidValues"

      Count of values failing validation rules.

   .. attribute:: DUPLICATE_VALUES
      :value: "duplicateValues"

      Count of duplicate values in a column.

   **Schema-Level Metrics** (operate on entire dataset):

   .. attribute:: ROW_COUNT
      :value: "rowCount"

      Total number of rows in the dataset.

   .. attribute:: DUPLICATE_ROWS
      :value: "duplicateRows"

      Count of duplicate rows across specified columns.

   **Properties**

   .. attribute:: is_property_level
      :type: bool

      ``True`` if this metric operates at the property/column level.

   .. attribute:: is_schema_level
      :type: bool

      ``True`` if this metric operates at the schema/table level.

   **Example**

   .. code-block:: python

      from griot_core import QualityMetric

      metric = QualityMetric.NULL_VALUES
      print(metric.is_property_level)  # True
      print(metric.is_schema_level)    # False

      metric = QualityMetric.ROW_COUNT
      print(metric.is_property_level)  # False
      print(metric.is_schema_level)    # True

QualityOperator
^^^^^^^^^^^^^^^

.. class:: griot_core.QualityOperator

   ODCS comparison operators for quality rule thresholds.

   .. attribute:: MUST_BE
      :value: "mustBe"

      Equals (==).

   .. attribute:: MUST_NOT_BE
      :value: "mustNotBe"

      Not equals (!=).

   .. attribute:: MUST_BE_GREATER_THAN
      :value: "mustBeGreaterThan"

      Greater than (>).

   .. attribute:: MUST_BE_GREATER_OR_EQUAL_TO
      :value: "mustBeGreaterOrEqualTo"

      Greater than or equal (>=).

   .. attribute:: MUST_BE_LESS_THAN
      :value: "mustBeLessThan"

      Less than (<).

   .. attribute:: MUST_BE_LESS_OR_EQUAL_TO
      :value: "mustBeLessOrEqualTo"

      Less than or equal (<=).

   .. attribute:: MUST_BE_BETWEEN
      :value: "mustBeBetween"

      Between two values (exclusive).

   .. attribute:: MUST_NOT_BE_BETWEEN
      :value: "mustNotBeBetween"

      Not between two values.

   **Properties**

   .. attribute:: comparison_type
      :type: str

      Internal comparison type code (eq, ne, gt, ge, lt, le, between, not_between).

   **Methods**

   .. method:: compare(value: float, threshold: Any) -> bool

      Compare a metric value against a threshold.

      :param value: The calculated metric value
      :param threshold: The comparison threshold (number or list for between)
      :returns: True if comparison passes

      .. code-block:: python

         op = QualityOperator.MUST_BE_LESS_THAN
         op.compare(5, 10)   # True (5 < 10)
         op.compare(15, 10)  # False (15 < 10)

         op = QualityOperator.MUST_BE_BETWEEN
         op.compare(5, [1, 10])  # True (1 < 5 < 10)

QualityUnit
^^^^^^^^^^^

.. class:: griot_core.QualityUnit

   Units for quality metric values.

   .. attribute:: ROWS
      :value: "rows"

      Absolute count of rows.

   .. attribute:: PERCENT
      :value: "percent"

      Percentage of total rows.

   **Methods**

   .. method:: calculate_metric(count: int, total: int) -> float

      Calculate the metric value based on the unit.

      :param count: The raw count value
      :param total: The total number of rows
      :returns: Metric value in appropriate unit

      .. code-block:: python

         unit = QualityUnit.ROWS
         unit.calculate_metric(10, 100)  # 10.0

         unit = QualityUnit.PERCENT
         unit.calculate_metric(10, 100)  # 10.0 (10%)

QualityRule Builder
-------------------

.. class:: griot_core.QualityRule

   Builder class for creating ODCS-compliant quality rules.

   Provides type-safe factory methods to build quality rules using enums
   instead of raw strings, reducing errors when defining contracts.

   **Property-Level Rules** (for field quality):

   .. method:: null_values(*, must_be=None, must_not_be=None, must_be_less_than=None, must_be_less_or_equal_to=None, must_be_greater_than=None, must_be_greater_or_equal_to=None, must_be_between=None, unit=QualityUnit.ROWS, rule_id=None, name=None) -> dict
      :classmethod:

      Create a null values quality rule.

      :param must_be: Exact count of null values allowed
      :param must_not_be: Count that null values must not equal
      :param must_be_less_than: Maximum null values (exclusive)
      :param must_be_less_or_equal_to: Maximum null values (inclusive)
      :param must_be_greater_than: Minimum null values (exclusive)
      :param must_be_greater_or_equal_to: Minimum null values (inclusive)
      :param must_be_between: Range [min, max] for null values
      :param unit: ROWS for absolute count, PERCENT for percentage
      :param rule_id: Unique identifier for the rule
      :param name: Human-readable name
      :returns: ODCS-compliant quality rule dictionary

      .. code-block:: python

         # No nulls allowed
         QualityRule.null_values(must_be=0)
         # {'metric': 'nullValues', 'mustBe': 0}

         # Less than 5% nulls
         QualityRule.null_values(
             must_be_less_than=5,
             unit=QualityUnit.PERCENT
         )
         # {'metric': 'nullValues', 'mustBeLessThan': 5, 'unit': 'percent'}

   .. method:: missing_values(*, must_be=None, must_not_be=None, must_be_less_than=None, must_be_less_or_equal_to=None, must_be_greater_than=None, must_be_greater_or_equal_to=None, must_be_between=None, unit=QualityUnit.ROWS, missing_values_list=None, rule_id=None, name=None) -> dict
      :classmethod:

      Create a missing values quality rule.

      :param missing_values_list: Custom list of values considered missing
      :returns: ODCS-compliant quality rule dictionary

      .. code-block:: python

         # No missing values (default: null, empty, N/A)
         QualityRule.missing_values(must_be=0)

         # Custom missing values
         QualityRule.missing_values(
             must_be=0,
             missing_values_list=[None, '', 'N/A', 'NULL', '-']
         )

   .. method:: invalid_values(*, must_be=None, must_not_be=None, must_be_less_than=None, must_be_less_or_equal_to=None, unit=QualityUnit.ROWS, valid_values=None, pattern=None, min_value=None, max_value=None, min_length=None, max_length=None, rule_id=None, name=None) -> dict
      :classmethod:

      Create an invalid values quality rule.

      :param valid_values: List of allowed values (enum constraint)
      :param pattern: Regex pattern values must match
      :param min_value: Minimum numeric value allowed
      :param max_value: Maximum numeric value allowed
      :param min_length: Minimum string length
      :param max_length: Maximum string length
      :returns: ODCS-compliant quality rule dictionary

      .. code-block:: python

         # Enum validation
         QualityRule.invalid_values(
             must_be=0,
             valid_values=['active', 'inactive', 'pending']
         )

         # Pattern validation
         QualityRule.invalid_values(
             must_be=0,
             pattern=r'^[\w.-]+@[\w.-]+\.\w+$'
         )

         # Range validation
         QualityRule.invalid_values(
             must_be=0,
             min_value=0,
             max_value=150
         )

         # Length validation
         QualityRule.invalid_values(
             must_be=0,
             min_length=3,
             max_length=50
         )

   .. method:: duplicate_values(*, must_be=None, must_not_be=None, must_be_less_than=None, must_be_less_or_equal_to=None, unit=QualityUnit.ROWS, rule_id=None, name=None) -> dict
      :classmethod:

      Create a duplicate values quality rule for a single column.

      .. code-block:: python

         # No duplicates (unique values)
         QualityRule.duplicate_values(must_be=0)

   **Schema-Level Rules** (for schema quality):

   .. method:: row_count(*, must_be=None, must_not_be=None, must_be_greater_than=None, must_be_greater_or_equal_to=None, must_be_less_than=None, must_be_less_or_equal_to=None, must_be_between=None, rule_id=None, name=None) -> dict
      :classmethod:

      Create a row count quality rule (schema-level).

      .. code-block:: python

         # At least 1 row
         QualityRule.row_count(must_be_greater_than=0)

         # Exactly 1000 rows
         QualityRule.row_count(must_be=1000)

         # Between 100 and 10000 rows
         QualityRule.row_count(must_be_between=[100, 10000])

   .. method:: duplicate_rows(*, must_be=None, must_not_be=None, must_be_less_than=None, must_be_less_or_equal_to=None, unit=QualityUnit.ROWS, properties=None, rule_id=None, name=None) -> dict
      :classmethod:

      Create a duplicate rows quality rule (schema-level).

      :param properties: List of column names to check. If None, checks all columns.

      .. code-block:: python

         # No duplicate rows on composite key
         QualityRule.duplicate_rows(
             must_be=0,
             properties=['order_id', 'line_number']
         )

         # No completely duplicate rows
         QualityRule.duplicate_rows(must_be=0)

   **Complete Example**

   .. code-block:: python

      from griot_core import Schema, Field, QualityRule, QualityUnit

      class CustomerSchema(Schema):
          # Schema-level quality rules
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

          age: int = Field(
              "Customer age",
              nullable=True,
              quality=[
                  QualityRule.null_values(
                      must_be_less_than=10,
                      unit=QualityUnit.PERCENT
                  ),
                  QualityRule.invalid_values(
                      must_be=0,
                      min_value=0,
                      max_value=150
                  ),
              ]
          )

Validation Types
----------------

FieldValidationError
^^^^^^^^^^^^^^^^^^^^

.. class:: griot_core.FieldValidationError

   Single field validation error.

   .. attribute:: field
      :type: str

      Field name that failed validation.

   .. attribute:: row
      :type: int | None

      Row number (0-indexed) or None for column-level errors.

   .. attribute:: value
      :type: Any

      The value that failed validation.

   .. attribute:: constraint
      :type: str

      The constraint that was violated.

   .. attribute:: message
      :type: str

      Human-readable error message.

   .. attribute:: severity
      :type: Severity

      Error severity (default: ERROR).

   **Methods**

   .. method:: to_dict() -> dict

      Convert to dictionary representation.

   **Example**

   .. code-block:: python

      error = FieldValidationError(
          field="email",
          row=5,
          value="invalid-email",
          constraint="pattern",
          message="Value does not match email pattern"
      )

      print(error)  # "email[row 5]: Value does not match email pattern"
      print(error.to_dict())
