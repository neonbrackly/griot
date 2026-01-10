Validation
==========

Classes and functions for data validation.

ValidationResult
----------------

.. py:class:: griot_core.ValidationResult

   Result of validating data against a contract.

   **Attributes:**

   .. py:attribute:: passed
      :type: bool

      True if all data passed validation.

   .. py:attribute:: total_rows
      :type: int

      Total number of rows validated.

   .. py:attribute:: valid_rows
      :type: int

      Number of rows that passed validation.

   .. py:attribute:: failed_rows
      :type: int

      Number of rows that failed validation.

   .. py:attribute:: errors
      :type: list[FieldValidationError]

      List of validation errors.

   .. py:attribute:: field_stats
      :type: dict[str, FieldStats]

      Per-field validation statistics.

   **Methods:**

   .. py:method:: to_dict() -> dict

      Convert result to dictionary.

   .. py:method:: to_json() -> str

      Convert result to JSON string.

   .. py:method:: summary() -> str

      Get human-readable summary.

   **Example:**

   .. code-block:: python

      result = Customer.validate(data)

      if not result.passed:
          print(f"Failed: {result.failed_rows}/{result.total_rows} rows")
          for error in result.errors:
              print(f"  Row {error.row_index}: {error.message}")

FieldValidationError
--------------------

.. py:class:: griot_core.FieldValidationError

   Individual field validation error.

   **Attributes:**

   .. py:attribute:: row_index
      :type: int

      Index of the row with the error.

   .. py:attribute:: field
      :type: str

      Name of the field that failed validation.

   .. py:attribute:: value
      :type: Any

      The invalid value.

   .. py:attribute:: message
      :type: str

      Human-readable error message.

   .. py:attribute:: constraint_type
      :type: ConstraintType

      Type of constraint that was violated.

   .. py:attribute:: severity
      :type: Severity

      Error severity level.

   **Example:**

   .. code-block:: python

      for error in result.errors:
          print(f"Row {error.row_index}")
          print(f"  Field: {error.field}")
          print(f"  Value: {error.value}")
          print(f"  Error: {error.message}")
          print(f"  Type: {error.constraint_type}")
          print(f"  Severity: {error.severity}")

FieldStats
----------

.. py:class:: griot_core.FieldStats

   Statistics for a single field's validation.

   **Attributes:**

   .. py:attribute:: total_count
      :type: int

      Total values checked.

   .. py:attribute:: valid_count
      :type: int

      Number of valid values.

   .. py:attribute:: invalid_count
      :type: int

      Number of invalid values.

   .. py:attribute:: null_count
      :type: int

      Number of null values.

   .. py:attribute:: error_rate
      :type: float

      Percentage of invalid values.

validate_data Function
----------------------

.. py:function:: griot_core.validate_data(data, model, **kwargs) -> ValidationResult

   Validate data against a model.

   :param data: List of dictionaries to validate
   :type data: list[dict]
   :param model: Model class to validate against
   :type model: type[GriotModel]
   :param fail_fast: Stop on first error
   :type fail_fast: bool
   :param max_errors: Maximum errors to collect
   :type max_errors: int
   :returns: Validation result
   :rtype: ValidationResult

   **Example:**

   .. code-block:: python

      from griot_core import validate_data

      result = validate_data(data, Customer)
      print(f"Valid: {result.passed}")

validate_value Function
-----------------------

.. py:function:: griot_core.validate_value(value, field_info) -> list[FieldValidationError]

   Validate a single value against field constraints.

   :param value: Value to validate
   :type value: Any
   :param field_info: Field definition
   :type field_info: FieldInfo
   :returns: List of validation errors (empty if valid)
   :rtype: list[FieldValidationError]

   **Example:**

   .. code-block:: python

      from griot_core import validate_value

      fields = Customer.get_fields()
      errors = validate_value("invalid-email", fields["email"])

      for error in errors:
          print(error.message)
