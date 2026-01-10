Type Reference
==============

Complete reference for all enumeration types and dataclasses in griot-core.

.. toctree::
   :maxdepth: 2

   enums
   dataclasses

Quick Type Lookup
-----------------

Validation Types
^^^^^^^^^^^^^^^^

- :class:`~griot_core.ConstraintType` - Validation constraint types
- :class:`~griot_core.Severity` - Error severity levels
- :class:`~griot_core.FieldFormat` - Built-in string formats
- :class:`~griot_core.DataType` - Supported data types

PII/Privacy Types
^^^^^^^^^^^^^^^^^

- :class:`~griot_core.PIICategory` - PII classification categories
- :class:`~griot_core.SensitivityLevel` - Data sensitivity levels
- :class:`~griot_core.MaskingStrategy` - Masking strategies
- :class:`~griot_core.LegalBasis` - GDPR legal basis

Residency Types
^^^^^^^^^^^^^^^

- :class:`~griot_core.DataRegion` - Geographic regions
- :class:`~griot_core.ResidencyConfig` - Residency configuration
- :class:`~griot_core.ResidencyRule` - Residency rule definition

Lineage Types
^^^^^^^^^^^^^

- :class:`~griot_core.LineageConfig` - Lineage configuration
- :class:`~griot_core.Source` - Data source
- :class:`~griot_core.Transformation` - Data transformation
- :class:`~griot_core.Consumer` - Data consumer

Analytics Types
^^^^^^^^^^^^^^^

- :class:`~griot_core.AggregationType` - Aggregation hints

Report Types
^^^^^^^^^^^^

- :class:`~griot_core.AnalyticsReport` - Analytics report
- :class:`~griot_core.AIReadinessReport` - AI readiness report
- :class:`~griot_core.AuditReport` - Compliance audit report
- :class:`~griot_core.ReadinessReport` - Combined readiness report
