Dataclasses
===========

Dataclass types used for configuration and results.

Residency Configuration
-----------------------

ResidencyConfig
^^^^^^^^^^^^^^^

Top-level residency configuration for a contract.

.. code-block:: python

   from griot_core import ResidencyConfig, ResidencyRule, DataRegion

   residency = ResidencyConfig(
       default_rule=ResidencyRule(
           allowed_regions=[DataRegion.US, DataRegion.EU]
       ),
       field_rules={
           "email": ResidencyRule(
               allowed_regions=[DataRegion.EU],
               required_encryption=True
           )
       }
   )

**Fields:**

- ``default_rule`` (ResidencyRule) - Default rule for all fields
- ``field_rules`` (dict[str, ResidencyRule]) - Field-specific overrides

ResidencyRule
^^^^^^^^^^^^^

Individual residency rule definition.

.. code-block:: python

   from griot_core import ResidencyRule, DataRegion

   rule = ResidencyRule(
       allowed_regions=[DataRegion.EU],
       prohibited_regions=[DataRegion.CN, DataRegion.RU],
       required_encryption=True
   )

**Fields:**

- ``allowed_regions`` (list[DataRegion]) - Regions where data can be stored
- ``prohibited_regions`` (list[DataRegion]) - Regions where data cannot be stored
- ``required_encryption`` (bool) - Whether encryption is required

Lineage Configuration
---------------------

LineageConfig
^^^^^^^^^^^^^

Data lineage configuration for a contract.

.. code-block:: python

   from griot_core import LineageConfig, Source, Transformation, Consumer

   lineage = LineageConfig(
       sources=[Source(name="db", type="database")],
       transformations=[
           Transformation(
               name="transform",
               input_fields=["a"],
               output_fields=["b"]
           )
       ],
       consumers=[Consumer(name="warehouse", type="warehouse")]
   )

**Fields:**

- ``sources`` (list[Source]) - Data sources
- ``transformations`` (list[Transformation]) - Data transformations
- ``consumers`` (list[Consumer]) - Data consumers

Source
^^^^^^

Data source definition.

.. code-block:: python

   from griot_core import Source

   source = Source(
       name="orders_db",
       type="database",
       description="PostgreSQL orders database",
       connection="postgresql://orders.internal/db"
   )

**Fields:**

- ``name`` (str) - Unique source identifier
- ``type`` (str) - Source type: database, api, file, stream, manual, external
- ``description`` (str, optional) - Human-readable description
- ``connection`` (str, optional) - Connection string or URL

Transformation
^^^^^^^^^^^^^^

Data transformation definition.

.. code-block:: python

   from griot_core import Transformation

   transform = Transformation(
       name="calculate_total",
       description="Calculate order total with tax",
       input_fields=["subtotal", "tax_rate"],
       output_fields=["total"]
   )

**Fields:**

- ``name`` (str) - Unique transformation identifier
- ``description`` (str, optional) - Human-readable description
- ``input_fields`` (list[str]) - Names of input fields
- ``output_fields`` (list[str]) - Names of output fields

Consumer
^^^^^^^^

Data consumer definition.

.. code-block:: python

   from griot_core import Consumer

   consumer = Consumer(
       name="analytics_warehouse",
       type="warehouse",
       description="BigQuery analytics tables",
       connection="bigquery://project.analytics"
   )

**Fields:**

- ``name`` (str) - Unique consumer identifier
- ``type`` (str) - Consumer type: warehouse, dashboard, api, application, ml, export, archive
- ``description`` (str, optional) - Human-readable description
- ``connection`` (str, optional) - Connection string or URL

Validation Results
------------------

ValidationResult
^^^^^^^^^^^^^^^^

Result of validating data against a contract.

.. code-block:: python

   result = Model.validate(data)

   if not result.passed:
       print(f"Failed: {result.failed_rows}/{result.total_rows}")
       for error in result.errors:
           print(f"  {error.field}: {error.message}")

**Fields:**

- ``passed`` (bool) - True if all data passed validation
- ``total_rows`` (int) - Total rows validated
- ``valid_rows`` (int) - Rows that passed
- ``failed_rows`` (int) - Rows that failed
- ``errors`` (list[FieldValidationError]) - List of errors
- ``field_stats`` (dict[str, FieldStats]) - Per-field statistics

**Methods:**

- ``to_dict()`` - Convert to dictionary
- ``to_json()`` - Convert to JSON string
- ``summary()`` - Human-readable summary

FieldValidationError
^^^^^^^^^^^^^^^^^^^^

Individual field validation error.

**Fields:**

- ``row_index`` (int) - Index of the row with error
- ``field`` (str) - Field name
- ``value`` (Any) - The invalid value
- ``message`` (str) - Error message
- ``constraint_type`` (ConstraintType) - Type of constraint violated
- ``severity`` (Severity) - Error severity

FieldStats
^^^^^^^^^^

Per-field validation statistics.

**Fields:**

- ``total_count`` (int) - Total values checked
- ``valid_count`` (int) - Valid values
- ``invalid_count`` (int) - Invalid values
- ``null_count`` (int) - Null values
- ``error_rate`` (float) - Percentage invalid

Contract Operations
-------------------

ContractDiff
^^^^^^^^^^^^

Result of comparing two contracts.

.. code-block:: python

   diff = NewContract.diff(OldContract)

   if diff.has_breaking_changes:
       print("Breaking changes detected!")

**Fields:**

- ``added_fields`` (list[str]) - New fields in new contract
- ``removed_fields`` (list[str]) - Fields removed
- ``type_changes`` (list[TypeChange]) - Fields with type changes
- ``constraint_changes`` (list[ConstraintChange]) - Fields with constraint changes
- ``has_breaking_changes`` (bool) - True if any breaking changes

TypeChange
^^^^^^^^^^

Record of a field type change.

**Fields:**

- ``field`` (str) - Field name
- ``old_type`` (str) - Previous type
- ``new_type`` (str) - New type
- ``breaking`` (bool) - Whether breaking

ConstraintChange
^^^^^^^^^^^^^^^^

Record of a constraint change.

**Fields:**

- ``field`` (str) - Field name
- ``constraint`` (str) - Constraint name
- ``old_value`` (Any) - Previous value
- ``new_value`` (Any) - New value
- ``breaking`` (bool) - Whether breaking

LintIssue
^^^^^^^^^

Contract linting issue.

**Fields:**

- ``field`` (str | None) - Field name or None for contract-level
- ``code`` (str) - Issue code (W001, E001, etc.)
- ``message`` (str) - Human-readable message
- ``severity`` (Severity) - Issue severity
