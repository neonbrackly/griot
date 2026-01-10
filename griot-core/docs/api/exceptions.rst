Exceptions
==========

Exception classes for error handling.

GriotError
----------

.. py:exception:: griot_core.GriotError

   Base exception for all griot-core errors.

   All griot-core exceptions inherit from this class, making it easy to catch
   any library error:

   .. code-block:: python

      from griot_core import GriotError

      try:
          result = Customer.validate(data)
      except GriotError as e:
          print(f"Griot error: {e}")

ValidationError
---------------

.. py:exception:: griot_core.ValidationError

   Raised when validation fails critically.

   This is raised for critical validation failures that prevent processing,
   not for individual field errors (which are returned in ValidationResult).

   .. code-block:: python

      from griot_core import ValidationError

      try:
          result = Customer.validate(invalid_data)
      except ValidationError as e:
          print(f"Validation failed: {e}")

ContractNotFoundError
---------------------

.. py:exception:: griot_core.ContractNotFoundError

   Raised when a contract file cannot be found.

   .. code-block:: python

      from griot_core import load_contract, ContractNotFoundError

      try:
          Contract = load_contract("missing.yaml")
      except ContractNotFoundError as e:
          print(f"Contract not found: {e}")

ContractParseError
------------------

.. py:exception:: griot_core.ContractParseError

   Raised when a contract file cannot be parsed.

   This can occur due to invalid YAML syntax or invalid contract structure.

   .. code-block:: python

      from griot_core import load_contract, ContractParseError

      try:
          Contract = load_contract("invalid.yaml")
      except ContractParseError as e:
          print(f"Parse error: {e}")
          print(f"Line: {e.line}")
          print(f"Column: {e.column}")

   **Attributes:**

   .. py:attribute:: line
      :type: int | None

      Line number where error occurred.

   .. py:attribute:: column
      :type: int | None

      Column number where error occurred.

BreakingChangeError
-------------------

.. py:exception:: griot_core.BreakingChangeError

   Raised when a breaking contract change is detected.

   .. code-block:: python

      from griot_core import BreakingChangeError

      try:
          diff = NewContract.diff(OldContract)
          if diff.has_breaking_changes:
              raise BreakingChangeError(diff)
      except BreakingChangeError as e:
          print(f"Breaking changes: {e.diff}")

   **Attributes:**

   .. py:attribute:: diff
      :type: ContractDiff

      The contract diff with breaking changes.

ConstraintError
---------------

.. py:exception:: griot_core.ConstraintError

   Raised when a constraint definition is invalid.

   .. code-block:: python

      from griot_core import GriotModel, Field, ConstraintError

      try:
          class Invalid(GriotModel):
              value: int = Field(
                  description="Invalid range",
                  ge=100,
                  le=50  # Error: ge > le
              )
      except ConstraintError as e:
          print(f"Invalid constraint: {e}")

Exception Hierarchy
-------------------

.. code-block:: text

   GriotError
   ├── ValidationError
   ├── ContractNotFoundError
   ├── ContractParseError
   ├── BreakingChangeError
   └── ConstraintError

Error Handling Patterns
-----------------------

Comprehensive error handling:

.. code-block:: python

   from griot_core import (
       GriotError,
       ValidationError,
       ContractNotFoundError,
       ContractParseError,
       load_contract
   )

   def process_contract(path, data):
       """Process data with comprehensive error handling."""
       try:
           # Load contract
           Contract = load_contract(path)

           # Validate data
           result = Contract.validate(data)

           if not result.passed:
               print(f"Validation failed: {result.failed_rows} errors")
               for error in result.errors[:10]:
                   print(f"  {error.field}: {error.message}")
               return False

           return True

       except ContractNotFoundError:
           print(f"Contract file not found: {path}")
           return False

       except ContractParseError as e:
           print(f"Invalid contract at line {e.line}: {e}")
           return False

       except ValidationError as e:
           print(f"Critical validation error: {e}")
           return False

       except GriotError as e:
           print(f"Unexpected griot error: {e}")
           return False
