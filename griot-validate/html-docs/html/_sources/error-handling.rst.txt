Error Handling
==============

griot-enforce provides specific exception types for different failure scenarios,
allowing you to handle errors appropriately in your pipelines.

Exception Hierarchy
-------------------

.. code-block:: text

   Exception
   ├── RuntimeValidationError      # Data validation failures
   ├── ResidencyViolationError     # Data residency violations
   └── MaskingViolationError       # PII masking violations

RuntimeValidationError
----------------------

Raised when data validation fails against a contract.

**Attributes:**

- ``contract_id`` (str | None): The contract ID that failed validation
- ``error_count`` (int): Number of validation errors
- ``error_rate`` (float): Error rate as a decimal (errors / total rows)

**Example:**

.. code-block:: python

   from griot_enforce import RuntimeValidator, RuntimeValidationError

   validator = RuntimeValidator(registry_url="https://registry.example.com")

   try:
       result = validator.validate(
           "customer-profile",
           dataframe,
           fail_on_error=True,
       )
   except RuntimeValidationError as e:
       print(f"Validation failed for contract: {e.contract_id}")
       print(f"Total errors: {e.error_count}")
       print(f"Error rate: {e.error_rate:.2%}")

       # Access detailed errors from the validation result
       # (you may need to run validation again with fail_on_error=False)

**Handling in Pipelines:**

.. code-block:: python

   # Airflow
   from airflow.exceptions import AirflowException

   try:
       result = validator.validate("contract", data, fail_on_error=True)
   except RuntimeValidationError as e:
       raise AirflowException(f"Validation failed: {e}") from e

   # Dagster
   from dagster import Failure

   try:
       result = griot.validate("contract", data, fail_on_error=True)
   except RuntimeValidationError as e:
       raise Failure(f"Validation failed: {e}") from e

   # Prefect
   from prefect import get_run_logger

   try:
       result = validate_task("contract", data, fail_on_error=True)
   except RuntimeValidationError as e:
       logger = get_run_logger()
       logger.error(f"Validation failed: {e}")
       raise

ResidencyViolationError
-----------------------

Raised when data residency requirements are violated.

**Attributes:**

- ``contract_id`` (str | None): The contract ID
- ``violations`` (list[dict]): List of violation details
- ``detected_region`` (str | None): Region detected from URI
- ``allowed_regions`` (list[str]): List of allowed regions

**Example:**

.. code-block:: python

   from griot_enforce import RuntimeValidator, ResidencyViolationError

   validator = RuntimeValidator(registry_url="https://registry.example.com")

   try:
       result = validator.check_residency(
           "customer-profile",
           destination="s3://bucket-us-east-1/data/",
           fail_on_violation=True,
       )
   except ResidencyViolationError as e:
       print(f"Residency violation for contract: {e.contract_id}")
       print(f"Detected region: {e.detected_region}")
       print(f"Allowed regions: {e.allowed_regions}")

       for violation in e.violations:
           print(f"  - {violation}")

**Preventing Writes to Non-Compliant Regions:**

.. code-block:: python

   def write_to_s3(data, destination: str, contract_id: str):
       """Write data to S3 only if residency requirements are met."""
       validator = RuntimeValidator(registry_url="https://registry.example.com")

       try:
           validator.check_residency(
               contract_id,
               destination=destination,
               fail_on_violation=True,
           )
       except ResidencyViolationError as e:
           # Log and alert
           log_residency_violation(contract_id, destination, e.allowed_regions)
           raise

       # Safe to write
       upload_to_s3(data, destination)

MaskingViolationError
---------------------

Raised when PII masking requirements are violated.

**Attributes:**

- ``contract_id`` (str | None): The contract ID
- ``violations`` (list[dict]): List of masking violations with field details

**Example:**

.. code-block:: python

   from griot_enforce import RuntimeValidator, MaskingViolationError

   validator = RuntimeValidator(registry_url="https://registry.example.com")

   try:
       result = validator.verify_masking(
           "customer-profile",
           dataframe,
           environment="staging",
           fail_on_violation=True,
       )
   except MaskingViolationError as e:
       print(f"Masking violation for contract: {e.contract_id}")

       for violation in e.violations:
           print(f"  Field: {violation['field']}")
           print(f"  Expected strategy: {violation['expected_strategy']}")
           print(f"  Message: {violation['message']}")

**Enforcing Masking in Non-Production:**

.. code-block:: python

   import os

   def process_data_safely(data, contract_id: str):
       """Process data with masking enforcement in non-prod."""
       validator = RuntimeValidator(registry_url="https://registry.example.com")
       environment = os.environ.get("ENVIRONMENT", "development")

       # Verify masking in non-production environments
       if environment != "production":
           try:
               validator.verify_masking(
                   contract_id,
                   data,
                   environment=environment,
                   fail_on_violation=True,
               )
           except MaskingViolationError as e:
               # Alert security team
               alert_security_team(contract_id, e.violations)
               raise

       return process(data)

Combined Error Handling
-----------------------

Handle all griot-enforce exceptions:

.. code-block:: python

   from griot_enforce import (
       RuntimeValidator,
       RuntimeValidationError,
       ResidencyViolationError,
       MaskingViolationError,
   )

   def validate_and_write(data, contract_id: str, destination: str, env: str):
       validator = RuntimeValidator(registry_url="https://registry.example.com")

       try:
           # Validate data
           validator.validate(
               contract_id,
               data,
               verify_masking=(env != "production"),
               environment=env,
               fail_on_error=True,
           )

           # Check residency
           validator.check_residency(
               contract_id,
               destination=destination,
               fail_on_violation=True,
           )

           # Safe to write
           write_to_storage(data, destination)

       except RuntimeValidationError as e:
           log_error("validation_failed", {
               "contract_id": e.contract_id,
               "error_count": e.error_count,
               "error_rate": e.error_rate,
           })
           raise

       except ResidencyViolationError as e:
           log_error("residency_violation", {
               "contract_id": e.contract_id,
               "detected_region": e.detected_region,
               "allowed_regions": e.allowed_regions,
           })
           raise

       except MaskingViolationError as e:
           log_error("masking_violation", {
               "contract_id": e.contract_id,
               "violations": e.violations,
           })
           raise

Graceful Degradation
--------------------

For non-critical validation, you may want to log errors without failing:

.. code-block:: python

   def validate_with_fallback(data, contract_id: str):
       """Validate data but don't fail the pipeline on errors."""
       validator = RuntimeValidator(registry_url="https://registry.example.com")

       try:
           result = validator.validate(
               contract_id,
               data,
               fail_on_error=False,  # Don't raise exception
           )

           if not result.passed:
               # Log warning but continue
               log_warning(f"Validation issues: {result.error_count} errors")
               send_alert_to_data_quality_team(contract_id, result)

           return data

       except Exception as e:
           # Handle unexpected errors (network issues, etc.)
           log_error(f"Validation service unavailable: {e}")
           # Decide whether to fail or continue
           return data

Retry Strategies
----------------

Implement retries for transient failures:

.. code-block:: python

   import time
   from griot_enforce import RuntimeValidator

   def validate_with_retry(data, contract_id: str, max_retries: int = 3):
       """Validate with exponential backoff retry."""
       validator = RuntimeValidator(registry_url="https://registry.example.com")

       for attempt in range(max_retries):
           try:
               return validator.validate(
                   contract_id,
                   data,
                   fail_on_error=True,
               )
           except RuntimeValidationError:
               # Data validation errors should not be retried
               raise
           except Exception as e:
               # Transient errors (network, etc.) can be retried
               if attempt < max_retries - 1:
                   wait_time = 2 ** attempt  # Exponential backoff
                   log_warning(f"Attempt {attempt + 1} failed, retrying in {wait_time}s")
                   time.sleep(wait_time)
               else:
                   raise

Circuit Breaker Pattern
-----------------------

Implement circuit breaker for service reliability:

.. code-block:: python

   class ValidationCircuitBreaker:
       def __init__(self, failure_threshold: int = 5, reset_timeout: int = 60):
           self.failure_count = 0
           self.failure_threshold = failure_threshold
           self.reset_timeout = reset_timeout
           self.last_failure_time = None
           self.state = "closed"  # closed, open, half-open

       def validate(self, validator, contract_id, data):
           if self.state == "open":
               if time.time() - self.last_failure_time > self.reset_timeout:
                   self.state = "half-open"
               else:
                   raise Exception("Circuit breaker is open")

           try:
               result = validator.validate(contract_id, data, fail_on_error=True)
               self._on_success()
               return result
           except Exception as e:
               self._on_failure()
               raise

       def _on_success(self):
           self.failure_count = 0
           self.state = "closed"

       def _on_failure(self):
           self.failure_count += 1
           self.last_failure_time = time.time()
           if self.failure_count >= self.failure_threshold:
               self.state = "open"
