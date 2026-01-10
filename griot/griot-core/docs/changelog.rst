Changelog
=========

All notable changes to griot-core.

[0.4.0] - 2026-01-10
--------------------

Added
^^^^^

**Phase 2: Compliance Features**

- PII classification with ``PIICategory`` enum
- Sensitivity levels with ``SensitivityLevel`` enum
- Masking strategies with ``MaskingStrategy`` enum
- Legal basis tracking with ``LegalBasis`` enum
- Data residency with ``ResidencyConfig`` and ``DataRegion``
- Data lineage with ``LineageConfig``, ``Source``, ``Transformation``, ``Consumer``
- ``pii_inventory()`` method on GriotModel
- ``check_residency()`` method on GriotModel

**Report Generation**

- ``AnalyticsReport`` - Contract analytics and statistics
- ``AIReadinessReport`` - AI/LLM readiness assessment
- ``AuditReport`` - Compliance and privacy audit
- ``ReadinessReport`` - Combined readiness assessment
- ``generate_analytics_report()`` function
- ``generate_ai_readiness_report()`` function
- ``generate_audit_report()`` function
- ``generate_readiness_report()`` function

[0.3.0] - 2026-01-10
--------------------

Added
^^^^^

**Phase 1: Foundation**

- ``GriotModel`` base class for defining contracts
- ``Field()`` function for field definitions
- ``FieldInfo`` dataclass for field metadata
- Comprehensive validation engine
- ``ValidationResult`` and ``FieldValidationError`` classes
- Contract diffing with ``ContractDiff``
- Contract linting with ``LintIssue``
- Mock data generation with ``generate_mock_data()``
- Manifest export (JSON-LD, Markdown, LLM context)
- YAML contract loading with ``load_contract()``

**Validation Constraints**

- Type validation (str, int, float, bool, list, dict)
- Pattern validation (regex)
- Format validation (email, uuid, date, datetime, uri, etc.)
- Enum validation
- String length constraints (min_length, max_length)
- Numeric range constraints (ge, gt, le, lt)
- Multiple of constraint
- Array constraints (min_items, max_items, unique_items)

**Enums**

- ``ConstraintType`` - Validation constraint types
- ``Severity`` - Error severity levels
- ``FieldFormat`` - Built-in string formats
- ``DataType`` - Supported data types
- ``AggregationType`` - Aggregation hints

**Exceptions**

- ``GriotError`` - Base exception
- ``ValidationError`` - Validation failure
- ``ContractNotFoundError`` - Missing contract file
- ``ContractParseError`` - Invalid YAML
- ``BreakingChangeError`` - Breaking contract change
- ``ConstraintError`` - Invalid constraint definition

[0.2.0] - 2026-01-08
--------------------

Added
^^^^^

- Initial project structure
- Basic GriotModel implementation
- Simple validation

[0.1.0] - 2026-01-05
--------------------

Added
^^^^^

- Project initialization
- Requirements documentation
