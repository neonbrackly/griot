Models
======

Core model classes for defining data contracts.

GriotModel
----------

.. py:class:: griot_core.GriotModel

   Base class for all data contracts. Inherit from this class to define your schema.

   **Class Attributes:**

   .. py:attribute:: Meta
      :type: class

      Optional inner class for contract metadata (description, version, owner, residency, lineage).

   **Class Methods:**

   .. py:classmethod:: get_fields() -> dict[str, FieldInfo]

      Get all field definitions for this model.

      :returns: Dictionary mapping field names to FieldInfo objects
      :rtype: dict[str, FieldInfo]

   .. py:classmethod:: get_primary_keys() -> list[str]

      Get the names of primary key fields.

      :returns: List of primary key field names
      :rtype: list[str]

   .. py:classmethod:: pii_inventory() -> list[FieldInfo]

      Get all fields marked as PII.

      :returns: List of FieldInfo objects for PII fields
      :rtype: list[FieldInfo]

   .. py:classmethod:: validate(data, **kwargs) -> ValidationResult

      Validate data against this contract.

      :param data: List of dictionaries to validate
      :type data: list[dict]
      :param fail_fast: Stop on first error (default: False)
      :type fail_fast: bool
      :param max_errors: Maximum errors to collect (default: unlimited)
      :type max_errors: int
      :returns: Validation result with errors and statistics
      :rtype: ValidationResult

   .. py:classmethod:: mock(rows=10, seed=None, null_rate=0.1) -> list[dict]

      Generate mock data that satisfies this contract.

      :param rows: Number of rows to generate
      :type rows: int
      :param seed: Random seed for reproducibility
      :type seed: int | None
      :param null_rate: Rate of null values for nullable fields
      :type null_rate: float
      :returns: List of generated dictionaries
      :rtype: list[dict]

   .. py:classmethod:: to_manifest(format="llm_context", **kwargs) -> str

      Export contract as manifest.

      :param format: Export format ("llm_context", "json_ld", "markdown")
      :type format: str
      :param include_pii: Include PII metadata (default: False)
      :type include_pii: bool
      :param include_lineage: Include lineage info (default: False)
      :type include_lineage: bool
      :returns: Manifest string
      :rtype: str

   .. py:classmethod:: to_yaml() -> str

      Export contract as YAML string.

      :returns: YAML representation
      :rtype: str

   .. py:classmethod:: to_yaml_file(path)

      Save contract to YAML file.

      :param path: File path to save to
      :type path: str | Path

   .. py:classmethod:: diff(other) -> ContractDiff

      Compare this contract to another.

      :param other: Contract to compare against
      :type other: type[GriotModel]
      :returns: Differences between contracts
      :rtype: ContractDiff

   .. py:classmethod:: lint() -> list[LintIssue]

      Check contract for common issues.

      :returns: List of lint issues found
      :rtype: list[LintIssue]

   .. py:classmethod:: check_residency(region, field=None) -> bool

      Check if a region is allowed for this contract.

      :param region: Data region to check
      :type region: DataRegion
      :param field: Specific field to check (optional)
      :type field: str | None
      :returns: True if region is allowed
      :rtype: bool

   **Example:**

   .. code-block:: python

      from griot_core import GriotModel, Field

      class Customer(GriotModel):
          """Customer data contract."""

          class Meta:
              description = "Customer master data"
              version = "1.0.0"
              owner = "data-team@company.com"

          customer_id: str = Field(
              description="Unique customer identifier",
              primary_key=True
          )
          email: str = Field(
              description="Customer email",
              format="email"
          )

      # Use the contract
      result = Customer.validate(data)
      mock = Customer.mock(rows=100)

Field Function
--------------

.. py:function:: griot_core.Field(description, **kwargs) -> FieldInfo

   Create a field definition with constraints.

   :param description: Human-readable field description
   :type description: str
   :param primary_key: Mark as primary key (default: False)
   :type primary_key: bool
   :param nullable: Allow null values (default: False)
   :type nullable: bool
   :param default: Default value
   :param pattern: Regex pattern for string validation
   :type pattern: str
   :param format: String format (email, uuid, date, datetime, etc.)
   :type format: str
   :param enum: List of allowed values
   :type enum: list
   :param min_length: Minimum string length
   :type min_length: int
   :param max_length: Maximum string length
   :type max_length: int
   :param ge: Greater than or equal (numeric)
   :type ge: float
   :param gt: Greater than (numeric)
   :type gt: float
   :param le: Less than or equal (numeric)
   :type le: float
   :param lt: Less than (numeric)
   :type lt: float
   :param multiple_of: Value must be divisible by this
   :type multiple_of: float
   :param min_items: Minimum array length
   :type min_items: int
   :param max_items: Maximum array length
   :type max_items: int
   :param unique_items: Array must have unique items
   :type unique_items: bool
   :param examples: Example values
   :type examples: list
   :param unit: Unit of measurement
   :type unit: str
   :param aggregation: Aggregation type hint
   :type aggregation: AggregationType
   :param pii_category: PII classification
   :type pii_category: PIICategory
   :param sensitivity: Sensitivity level
   :type sensitivity: SensitivityLevel
   :param masking_strategy: How to mask this field
   :type masking_strategy: MaskingStrategy
   :param legal_basis: Legal basis for processing
   :type legal_basis: LegalBasis
   :param retention_days: Retention period in days
   :type retention_days: int
   :returns: Field information object
   :rtype: FieldInfo

   **Example:**

   .. code-block:: python

      from griot_core import Field, PIICategory, SensitivityLevel

      email: str = Field(
          description="Customer email address",
          format="email",
          max_length=255,
          pii_category=PIICategory.EMAIL,
          sensitivity=SensitivityLevel.CONFIDENTIAL,
          examples=["john@example.com"]
      )

FieldInfo
---------

.. py:class:: griot_core.FieldInfo

   Dataclass containing field metadata and constraints.

   **Attributes:**

   .. py:attribute:: name
      :type: str

      Field name.

   .. py:attribute:: description
      :type: str

      Human-readable description.

   .. py:attribute:: type_name
      :type: str

      Python type name (str, int, float, bool, list, dict).

   .. py:attribute:: primary_key
      :type: bool

      Whether this is a primary key field.

   .. py:attribute:: nullable
      :type: bool

      Whether null values are allowed.

   .. py:attribute:: default
      :type: Any

      Default value if any.

   .. py:attribute:: pattern
      :type: str | None

      Regex pattern for validation.

   .. py:attribute:: format
      :type: str | None

      Format type (email, uuid, date, etc.).

   .. py:attribute:: enum
      :type: list | None

      List of allowed values.

   .. py:attribute:: min_length
      :type: int | None

      Minimum string length.

   .. py:attribute:: max_length
      :type: int | None

      Maximum string length.

   .. py:attribute:: ge
      :type: float | None

      Minimum value (inclusive).

   .. py:attribute:: gt
      :type: float | None

      Minimum value (exclusive).

   .. py:attribute:: le
      :type: float | None

      Maximum value (inclusive).

   .. py:attribute:: lt
      :type: float | None

      Maximum value (exclusive).

   .. py:attribute:: pii_category
      :type: PIICategory | None

      PII classification.

   .. py:attribute:: sensitivity
      :type: SensitivityLevel | None

      Sensitivity level.

   .. py:attribute:: masking_strategy
      :type: MaskingStrategy | None

      Masking strategy.

   .. py:attribute:: legal_basis
      :type: LegalBasis | None

      Legal basis for processing.

   .. py:attribute:: retention_days
      :type: int | None

      Retention period in days.
