API Reference
=============

Complete API documentation for griot-core, auto-generated from source code docstrings.

.. toctree::
   :maxdepth: 2

   models
   validation
   types
   contract
   reports
   mock
   manifest
   exceptions

Quick Reference
---------------

Core Classes
^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Class
     - Description
   * - :class:`~griot_core.GriotModel`
     - Base class for all data contracts
   * - :class:`~griot_core.FieldInfo`
     - Field metadata and constraints
   * - :class:`~griot_core.ValidationResult`
     - Result of data validation
   * - :class:`~griot_core.FieldValidationError`
     - Individual field validation error

Core Functions
^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Function
     - Description
   * - :func:`~griot_core.Field`
     - Create field definition with constraints
   * - :func:`~griot_core.validate_data`
     - Validate data against a model
   * - :func:`~griot_core.generate_mock_data`
     - Generate mock data for a model
   * - :func:`~griot_core.export_manifest`
     - Export model as manifest
   * - :func:`~griot_core.load_contract`
     - Load contract from YAML file

Report Functions
^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Function
     - Description
   * - :func:`~griot_core.generate_analytics_report`
     - Generate analytics report
   * - :func:`~griot_core.generate_ai_readiness_report`
     - Generate AI readiness report
   * - :func:`~griot_core.generate_audit_report`
     - Generate compliance audit report
   * - :func:`~griot_core.generate_readiness_report`
     - Generate combined readiness report
