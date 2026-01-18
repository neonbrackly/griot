Exceptions API
==============

The exceptions module provides custom exception classes for Griot Core.

Exception Hierarchy
-------------------

.. code-block:: text

   Exception
   └── GriotError (base for all Griot exceptions)
       ├── ValidationError
       ├── ContractNotFoundError
       ├── ContractParseError
       └── ConstraintError

   Exception
   ├── ValidatorNotFoundError
   └── PanderaNotInstalledError

Base Exception
--------------

GriotError
^^^^^^^^^^

.. exception:: griot_core.GriotError

   Base exception for all Griot Core errors.

   All Griot-specific exceptions inherit from this class, making it easy
   to catch any Griot-related error.

   .. code-block:: python

      from griot_core import GriotError, load_contract

      try:
          contract = load_contract("contract.yaml")
      except GriotError as e:
          print(f"Griot error: {e}")

Contract Exceptions
-------------------

ContractNotFoundError
^^^^^^^^^^^^^^^^^^^^^

.. exception:: griot_core.ContractNotFoundError

   Raised when a contract file cannot be found.

   Inherits from :class:`GriotError`.

   .. code-block:: python

      from griot_core import ContractNotFoundError, load_contract

      try:
          contract = load_contract("nonexistent.yaml")
      except ContractNotFoundError as e:
          print(f"File not found: {e}")

ContractParseError
^^^^^^^^^^^^^^^^^^

.. exception:: griot_core.ContractParseError

   Raised when a contract cannot be parsed.

   This can occur due to:
   - Invalid YAML syntax
   - Missing required fields
   - Invalid field values

   Inherits from :class:`GriotError`.

   .. code-block:: python

      from griot_core import ContractParseError, load_contract_from_string

      invalid_yaml = "invalid: [unclosed bracket"

      try:
          contract = load_contract_from_string(invalid_yaml)
      except ContractParseError as e:
          print(f"Parse error: {e}")

Validation Exceptions
---------------------

ValidationError
^^^^^^^^^^^^^^^

.. exception:: griot_core.ValidationError

   Raised when data validation fails.

   Inherits from :class:`GriotError`.

   **Attributes**

   .. attribute:: errors
      :type: list

      List of validation errors (if available).

   .. code-block:: python

      from griot_core import ValidationError, validate_data

      try:
          validate_data(data, schema, raise_on_error=True)
      except ValidationError as e:
          print(f"Validation failed: {e}")
          if hasattr(e, 'errors'):
              for error in e.errors:
                  print(f"  - {error}")

ConstraintError
^^^^^^^^^^^^^^^

.. exception:: griot_core.ConstraintError

   Raised when a constraint is violated.

   Inherits from :class:`GriotError`.

   Typically raised when:
   - A field value violates its constraints
   - A quality rule check fails
   - A schema constraint is violated

   .. code-block:: python

      from griot_core import ConstraintError

      try:
          # Some operation that might violate constraints
          pass
      except ConstraintError as e:
          print(f"Constraint violated: {e}")

Backend Exceptions
------------------

ValidatorNotFoundError
^^^^^^^^^^^^^^^^^^^^^^

.. exception:: griot_core.ValidatorNotFoundError

   Raised when no validator is found for a DataFrame type.

   .. code-block:: python

      from griot_core import ValidatorNotFoundError, get_validator

      try:
          validator = get_validator("unknown_type")
      except ValidatorNotFoundError as e:
          print(f"No validator available: {e}")

PanderaNotInstalledError
^^^^^^^^^^^^^^^^^^^^^^^^

.. exception:: griot_core.PanderaNotInstalledError

   Raised when Pandera is required but not installed.

   This occurs when attempting to use DataFrame validation without
   having installed a backend (pandas, polars, etc.).

   **Solution**

   Install a DataFrame backend:

   .. code-block:: bash

      pip install griot-core[pandas]
      # or
      pip install griot-core[polars]

   .. code-block:: python

      from griot_core import PanderaNotInstalledError, validate_dataframe

      try:
          result = validate_dataframe(df, schema)
      except PanderaNotInstalledError:
          print("Please install a DataFrame backend:")
          print("  pip install griot-core[pandas]")

Error Handling Patterns
-----------------------

Catching Specific Exceptions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from griot_core import (
       load_contract,
       validate_dataframe,
       GriotError,
       ContractNotFoundError,
       ContractParseError,
       ValidationError,
   )

   def process_contract(path: str, df):
       """Process a contract with proper error handling."""
       try:
           # Load contract
           contract = load_contract(path)

           # Get first schema
           schema = contract.get_schema(0)

           # Validate data
           result = validate_dataframe(df, type(schema))

           return result

       except ContractNotFoundError:
           print(f"Contract file not found: {path}")
           return None

       except ContractParseError as e:
           print(f"Invalid contract format: {e}")
           return None

       except ValidationError as e:
           print(f"Data validation failed: {e}")
           return None

       except GriotError as e:
           print(f"Unexpected Griot error: {e}")
           return None

Catching All Griot Errors
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from griot_core import GriotError

   try:
       # Any Griot operation
       contract = load_contract("contract.yaml")
       result = validate_dataframe(df, schema)
   except GriotError as e:
       # Handle any Griot-specific error
       logger.error(f"Griot operation failed: {e}")
       raise

Graceful Degradation
^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from griot_core import (
       validate_dataframe,
       PanderaNotInstalledError,
       get_available_backends,
   )

   def safe_validate(df, schema):
       """Validate with graceful fallback."""
       # Check if any backend is available
       backends = get_available_backends()
       available = [k for k, v in backends.items() if v['available']]

       if not available:
           print("Warning: No validation backend available")
           print("Install one with: pip install griot-core[pandas]")
           return None

       try:
           return validate_dataframe(df, schema)
       except PanderaNotInstalledError:
           print("Validation backend not properly configured")
           return None

Logging Errors
^^^^^^^^^^^^^^

.. code-block:: python

   import logging
   from griot_core import GriotError, validate_dataframe

   logger = logging.getLogger(__name__)

   def validate_with_logging(df, schema):
       """Validate and log any errors."""
       try:
           result = validate_dataframe(df, schema)

           if not result.is_valid:
               for error in result.errors:
                   logger.warning(
                       f"Validation error in {error.field}: {error.message}"
                   )

           return result

       except GriotError as e:
           logger.exception(f"Validation failed: {e}")
           raise

Creating Custom Exceptions
--------------------------

Extend Griot exceptions for domain-specific errors:

.. code-block:: python

   from griot_core import GriotError

   class DataQualityError(GriotError):
       """Raised when data quality thresholds are not met."""

       def __init__(self, schema_name: str, failed_rules: list[str]):
           self.schema_name = schema_name
           self.failed_rules = failed_rules
           message = (
               f"Data quality check failed for {schema_name}: "
               f"{', '.join(failed_rules)}"
           )
           super().__init__(message)


   class ContractVersionError(GriotError):
       """Raised when contract version is incompatible."""

       def __init__(self, expected: str, actual: str):
           self.expected = expected
           self.actual = actual
           message = f"Expected contract version {expected}, got {actual}"
           super().__init__(message)


   # Usage
   try:
       if result.error_count > threshold:
           raise DataQualityError(
               schema_name="Orders",
               failed_rules=["null_check", "duplicate_check"]
           )
   except DataQualityError as e:
       print(f"Quality error for {e.schema_name}")
       print(f"Failed rules: {e.failed_rules}")
