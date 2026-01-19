API Reference
=============

This page provides detailed API documentation for griot-enforce.

RuntimeValidator
----------------

.. py:class:: RuntimeValidator(registry_url=None, api_key=None, cache_ttl=300, report_results=True)

   Core validator for runtime data validation.

   Wraps griot-core SDK validation with runtime features including registry
   integration, contract caching, and result reporting.

   :param registry_url: Registry URL. Can also be set via ``GRIOT_REGISTRY_URL`` env var.
   :type registry_url: str | None
   :param api_key: API key for registry. Can also be set via ``GRIOT_API_KEY`` env var.
   :type api_key: str | None
   :param cache_ttl: Contract cache TTL in seconds. Default: 300 (5 minutes).
   :type cache_ttl: int
   :param report_results: Whether to report validation results to registry. Default: True.
   :type report_results: bool

   **Example:**

   .. code-block:: python

      validator = RuntimeValidator(
          registry_url="https://registry.example.com",
          cache_ttl=600,  # 10 minute cache
      )

Methods
^^^^^^^

.. py:method:: RuntimeValidator.validate(contract_id, data, version=None, fail_on_error=True, verify_masking=False, environment=None)

   Validate data against a contract from the registry.

   :param contract_id: Contract ID in the registry.
   :type contract_id: str
   :param data: Data to validate. Can be a pandas DataFrame or list of dicts.
   :type data: pd.DataFrame | list[dict]
   :param version: Specific contract version. Default: latest.
   :type version: str | None
   :param fail_on_error: Raise ``RuntimeValidationError`` on validation failure. Default: True.
   :type fail_on_error: bool
   :param verify_masking: Also verify PII masking compliance (FR-ENF-009). Default: False.
   :type verify_masking: bool
   :param environment: Environment name for masking checks (e.g., "staging", "dev").
   :type environment: str | None
   :returns: ValidationResult from griot-core.
   :rtype: ValidationResult
   :raises RuntimeValidationError: If validation fails and ``fail_on_error=True``.
   :raises MaskingViolationError: If masking verification fails and ``fail_on_error=True``.

   **Example:**

   .. code-block:: python

      result = validator.validate(
          "customer-profile",
          dataframe,
          verify_masking=True,
          environment="staging",
      )

.. py:method:: RuntimeValidator.validate_local(contract_path, data, fail_on_error=True)

   Validate data against a local contract file.

   :param contract_path: Path to YAML contract file.
   :type contract_path: str | Path
   :param data: Data to validate.
   :type data: pd.DataFrame | list[dict]
   :param fail_on_error: Raise exception on failure. Default: True.
   :type fail_on_error: bool
   :returns: ValidationResult from griot-core.
   :rtype: ValidationResult
   :raises RuntimeValidationError: If validation fails and ``fail_on_error=True``.
   :raises FileNotFoundError: If contract file doesn't exist.

.. py:method:: RuntimeValidator.get_contract(contract_id, version=None)

   Fetch contract from registry with caching.

   :param contract_id: Contract ID in the registry.
   :type contract_id: str
   :param version: Specific contract version. Default: latest.
   :type version: str | None
   :returns: GriotModel subclass representing the contract.
   :rtype: GriotModel
   :raises ValueError: If ``registry_url`` is not configured.
   :raises RuntimeError: If contract fetch fails.

.. py:method:: RuntimeValidator.check_residency(contract_id, region=None, destination=None, version=None, fail_on_violation=False)

   Check if data can be stored in a given region (FR-ENF-008).

   Auto-detects region from cloud URIs including AWS S3, Azure Blob, and GCP GCS.

   :param contract_id: Contract ID in the registry.
   :type contract_id: str
   :param region: Explicit target region for data storage.
   :type region: str | None
   :param destination: Cloud URI to auto-detect region from (e.g., ``s3://bucket-eu-west-1/``).
   :type destination: str | None
   :param version: Specific contract version.
   :type version: str | None
   :param fail_on_violation: Raise ``ResidencyViolationError`` if not compliant. Default: False.
   :type fail_on_violation: bool
   :returns: Dictionary with compliance status and violations.
   :rtype: dict[str, Any]
   :raises ResidencyViolationError: If not compliant and ``fail_on_violation=True``.
   :raises ValueError: If neither ``region`` nor ``destination`` is provided.

   **Supported URI Patterns:**

   - **AWS S3**: ``s3://bucket-eu-west-1/path`` or ``s3://bucket.s3.eu-west-1.amazonaws.com/``
   - **Azure Blob**: ``https://account.blob.core.windows.net/container``
   - **GCP GCS**: ``gs://bucket-us-central1/path``

   **Example:**

   .. code-block:: python

      # Auto-detect from S3 URI
      result = validator.check_residency(
          "customer-profile",
          destination="s3://my-bucket-eu-west-1/data/",
          fail_on_violation=True,
      )

      # Response includes:
      # {
      #     "compliant": True,
      #     "detected_region": "eu-west-1",
      #     "destination": "s3://my-bucket-eu-west-1/data/",
      #     "target_region": "eu-west-1",
      #     "allowed_regions": ["eu-west-1", "eu-central-1"],
      # }

.. py:method:: RuntimeValidator.verify_masking(contract_id, data, version=None, environment=None, fail_on_violation=False)

   Verify that PII fields are properly masked (FR-ENF-009).

   :param contract_id: Contract ID in the registry.
   :type contract_id: str
   :param data: Data to check for masking compliance.
   :type data: pd.DataFrame | list[dict]
   :param version: Specific contract version.
   :type version: str | None
   :param environment: Environment name. Skips verification in "prod"/"production".
   :type environment: str | None
   :param fail_on_violation: Raise ``MaskingViolationError`` if not compliant. Default: False.
   :type fail_on_violation: bool
   :returns: Dictionary with masking verification results.
   :rtype: dict[str, Any]
   :raises MaskingViolationError: If not compliant and ``fail_on_violation=True``.

   **Masking Strategies Checked:**

   - ``redact``: Expects ``[REDACTED]`` in value
   - ``partial``: Expects ``*`` characters (e.g., ``****1234``)
   - ``hash``: Expects 32+ character hex string

   **Example:**

   .. code-block:: python

      result = validator.verify_masking(
          "customer-profile",
          dataframe,
          environment="staging",
      )

      # Response:
      # {
      #     "compliant": False,
      #     "environment": "staging",
      #     "pii_fields_checked": ["email", "phone", "ssn"],
      #     "violations": [
      #         {
      #             "field": "email",
      #             "expected_strategy": "partial",
      #             "message": "Field 'email' does not appear to be properly masked",
      #             "pii_category": "contact_info",
      #         }
      #     ],
      # }

.. py:method:: RuntimeValidator.clear_cache()

   Clear the contract cache.

   **Example:**

   .. code-block:: python

      validator.clear_cache()

.. py:method:: RuntimeValidator.close()

   Close HTTP client and release resources.

   **Example:**

   .. code-block:: python

      validator.close()

Exceptions
----------

.. py:exception:: RuntimeValidationError(message, contract_id=None, error_count=0, error_rate=0.0)

   Raised when runtime validation fails.

   :param message: Error message.
   :type message: str
   :param contract_id: Contract ID that failed validation.
   :type contract_id: str | None
   :param error_count: Number of validation errors.
   :type error_count: int
   :param error_rate: Error rate (errors / total rows).
   :type error_rate: float

   **Attributes:**

   - ``contract_id`` (str | None): Contract ID
   - ``error_count`` (int): Number of errors
   - ``error_rate`` (float): Error rate as decimal

.. py:exception:: ResidencyViolationError(message, contract_id=None, violations=None, detected_region=None, allowed_regions=None)

   Raised when data residency requirements are violated.

   :param message: Error message.
   :type message: str
   :param contract_id: Contract ID.
   :type contract_id: str | None
   :param violations: List of violation details.
   :type violations: list[dict] | None
   :param detected_region: Region detected from URI.
   :type detected_region: str | None
   :param allowed_regions: List of allowed regions.
   :type allowed_regions: list[str] | None

   **Attributes:**

   - ``contract_id`` (str | None): Contract ID
   - ``violations`` (list[dict]): Violation details
   - ``detected_region`` (str | None): Detected region
   - ``allowed_regions`` (list[str]): Allowed regions

.. py:exception:: MaskingViolationError(message, contract_id=None, violations=None)

   Raised when PII masking requirements are violated.

   :param message: Error message.
   :type message: str
   :param contract_id: Contract ID.
   :type contract_id: str | None
   :param violations: List of masking violations.
   :type violations: list[dict] | None

   **Attributes:**

   - ``contract_id`` (str | None): Contract ID
   - ``violations`` (list[dict]): List of violations with field, expected_strategy, message

Module Exports
--------------

The following are exported from ``griot_enforce``:

.. code-block:: python

   from griot_enforce import (
       RuntimeValidator,
       RuntimeValidationError,
       ResidencyViolationError,
       MaskingViolationError,
   )

Submodule imports:

.. code-block:: python

   # Airflow
   from griot_enforce.airflow import (
       GriotValidateOperator,
       GriotResidencyOperator,
       GriotFreshnessSensor,
   )

   # Dagster
   from griot_enforce.dagster import (
       GriotResource,
       griot_asset,
       griot_op,
   )

   # Prefect
   from griot_enforce.prefect import (
       validate_task,
       validate_local_task,
       check_residency_task,
       verify_masking_task,
       griot_validate,
       griot_validate_local,
       griot_check_residency,
       griot_verify_masking,
   )
