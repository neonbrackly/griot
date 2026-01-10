Data Validation
===============

griot-core provides a comprehensive validation engine that checks data against contract constraints.

Basic Validation
----------------

Validate data using the ``validate()`` class method:

.. code-block:: python

   from griot_core import GriotModel, Field

   class User(GriotModel):
       user_id: str = Field(description="User ID", primary_key=True)
       email: str = Field(description="Email", format="email")
       age: int = Field(description="Age", ge=0, le=150)

   # Data to validate
   data = [
       {"user_id": "U001", "email": "john@example.com", "age": 30},
       {"user_id": "U002", "email": "invalid-email", "age": 25},
       {"user_id": "U003", "email": "jane@example.com", "age": -5},
   ]

   # Validate
   result = User.validate(data)

ValidationResult
----------------

The ``validate()`` method returns a :class:`~griot_core.ValidationResult`:

.. code-block:: python

   result = User.validate(data)

   # Overall result
   print(f"Passed: {result.passed}")        # False (has errors)
   print(f"Total rows: {result.total_rows}")  # 3
   print(f"Valid rows: {result.valid_rows}")  # 1
   print(f"Failed rows: {result.failed_rows}")  # 2

   # Error details
   for error in result.errors:
       print(f"Row {error.row_index}: {error.field} - {error.message}")
       # Row 1: email - Invalid email format
       # Row 2: age - Value -5 is less than minimum 0

   # Field statistics
   for field_name, stats in result.field_stats.items():
       print(f"{field_name}: {stats.valid_count}/{stats.total_count} valid")

FieldValidationError
--------------------

Each error is a :class:`~griot_core.FieldValidationError`:

.. code-block:: python

   for error in result.errors:
       print(f"Row index: {error.row_index}")
       print(f"Field name: {error.field}")
       print(f"Invalid value: {error.value}")
       print(f"Error message: {error.message}")
       print(f"Constraint type: {error.constraint_type}")
       print(f"Severity: {error.severity}")
       print("---")

Constraint Types
^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Constraint
     - Description
   * - ``REQUIRED``
     - Field is missing or null
   * - ``TYPE``
     - Wrong data type
   * - ``PATTERN``
     - Regex pattern mismatch
   * - ``FORMAT``
     - Format validation failed (email, uuid, etc.)
   * - ``ENUM``
     - Value not in allowed enum
   * - ``MIN_LENGTH``
     - String too short
   * - ``MAX_LENGTH``
     - String too long
   * - ``MINIMUM``
     - Number below minimum (ge/gt)
   * - ``MAXIMUM``
     - Number above maximum (le/lt)
   * - ``MIN_ITEMS``
     - Array too short
   * - ``MAX_ITEMS``
     - Array too long
   * - ``UNIQUE_ITEMS``
     - Array has duplicates
   * - ``MULTIPLE_OF``
     - Number not divisible by value

Severity Levels
^^^^^^^^^^^^^^^

.. code-block:: python

   from griot_core import Severity

   for error in result.errors:
       if error.severity == Severity.ERROR:
           print(f"ERROR: {error.message}")
       elif error.severity == Severity.WARNING:
           print(f"WARNING: {error.message}")
       elif error.severity == Severity.INFO:
           print(f"INFO: {error.message}")

Field Statistics
----------------

Access per-field validation statistics:

.. code-block:: python

   for field_name, stats in result.field_stats.items():
       print(f"Field: {field_name}")
       print(f"  Total: {stats.total_count}")
       print(f"  Valid: {stats.valid_count}")
       print(f"  Invalid: {stats.invalid_count}")
       print(f"  Null: {stats.null_count}")
       print(f"  Error rate: {stats.error_rate:.2%}")

Validate Single Value
---------------------

Validate a single value against a field:

.. code-block:: python

   from griot_core import validate_value

   # Get field info
   fields = User.get_fields()
   email_field = fields["email"]

   # Validate single value
   errors = validate_value("invalid-email", email_field)
   for error in errors:
       print(error.message)

Validation Options
------------------

Configure validation behavior:

.. code-block:: python

   # Stop on first error
   result = User.validate(data, fail_fast=True)

   # Limit number of errors reported
   result = User.validate(data, max_errors=100)

   # Skip certain fields
   result = User.validate(data, skip_fields=["metadata"])

   # Validate subset of fields
   result = User.validate(data, fields=["user_id", "email"])

Handling Large Datasets
-----------------------

For large datasets, validate in batches:

.. code-block:: python

   def validate_batched(model, data, batch_size=10000):
       """Validate data in batches."""
       all_errors = []
       total_valid = 0
       total_rows = 0

       for i in range(0, len(data), batch_size):
           batch = data[i:i + batch_size]
           result = model.validate(batch)

           # Adjust row indices
           for error in result.errors:
               error.row_index += i
               all_errors.append(error)

           total_valid += result.valid_rows
           total_rows += result.total_rows

       return {
           "passed": len(all_errors) == 0,
           "total_rows": total_rows,
           "valid_rows": total_valid,
           "errors": all_errors
       }

Custom Validation
-----------------

Add custom validation logic:

.. code-block:: python

   class Order(GriotModel):
       order_id: str = Field(description="Order ID", primary_key=True)
       subtotal: float = Field(description="Subtotal", ge=0)
       tax: float = Field(description="Tax", ge=0)
       total: float = Field(description="Total", ge=0)

       @classmethod
       def validate(cls, data, **kwargs):
           # Run standard validation
           result = super().validate(data, **kwargs)

           # Add custom validation
           for i, row in enumerate(data):
               expected_total = row.get("subtotal", 0) + row.get("tax", 0)
               actual_total = row.get("total", 0)

               if abs(expected_total - actual_total) > 0.01:
                   result.errors.append(FieldValidationError(
                       row_index=i,
                       field="total",
                       value=actual_total,
                       message=f"Total {actual_total} doesn't match subtotal + tax ({expected_total})",
                       constraint_type=ConstraintType.CUSTOM,
                       severity=Severity.ERROR
                   ))

           result.passed = len(result.errors) == 0
           return result

Export Validation Results
-------------------------

Export results for reporting:

.. code-block:: python

   result = User.validate(data)

   # As dictionary
   result_dict = result.to_dict()

   # As JSON
   result_json = result.to_json()

   # Summary for logging
   print(result.summary())
   # "Validation: 98/100 rows passed (2 errors)"

Integration with Pandas
-----------------------

Validate pandas DataFrames:

.. code-block:: python

   import pandas as pd

   # DataFrame to validate
   df = pd.DataFrame([
       {"user_id": "U001", "email": "john@example.com", "age": 30},
       {"user_id": "U002", "email": "invalid", "age": 25},
   ])

   # Convert to list of dicts and validate
   result = User.validate(df.to_dict("records"))

   # Get invalid row indices
   invalid_indices = [e.row_index for e in result.errors]

   # Filter to invalid rows
   invalid_df = df.iloc[invalid_indices]
