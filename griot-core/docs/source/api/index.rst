API Reference
=============

This section provides complete API documentation for all public classes,
functions, and constants in Griot Core.

.. toctree::
   :maxdepth: 2
   :caption: API Modules

   schema
   contract
   types
   validation
   reports
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
   * - :class:`~griot_core.Schema`
     - Base class for defining data schemas
   * - :class:`~griot_core.Field`
     - Field descriptor for schema properties
   * - :class:`~griot_core.FieldInfo`
     - Runtime field metadata
   * - :class:`~griot_core.Contract`
     - Top-level data contract container
   * - :class:`~griot_core.QualityRule`
     - Type-safe quality rule builder

Enums
^^^^^

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Enum
     - Description
   * - :class:`~griot_core.ContractStatus`
     - Contract lifecycle states (draft, active, deprecated, retired)
   * - :class:`~griot_core.DataType`
     - Logical data types (string, integer, float, etc.)
   * - :class:`~griot_core.Severity`
     - Error severity levels (error, warning, info)
   * - :class:`~griot_core.QualityMetric`
     - Quality rule metrics (nullValues, rowCount, etc.)
   * - :class:`~griot_core.QualityOperator`
     - Comparison operators (mustBe, mustBeLessThan, etc.)
   * - :class:`~griot_core.QualityUnit`
     - Metric units (rows, percent)

Functions
^^^^^^^^^

**Contract Operations**

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Function
     - Description
   * - :func:`~griot_core.load_contract`
     - Load contract from YAML file
   * - :func:`~griot_core.load_contract_from_string`
     - Load contract from YAML string
   * - :func:`~griot_core.load_contract_from_dict`
     - Load contract from dictionary
   * - :func:`~griot_core.contract_to_yaml`
     - Export contract to YAML string
   * - :func:`~griot_core.contract_to_dict`
     - Export contract to dictionary
   * - :func:`~griot_core.lint_contract`
     - Check contract for issues
   * - :func:`~griot_core.validate_contract_structure`
     - Validate contract structure

**DataFrame Validation**

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Function
     - Description
   * - :func:`~griot_core.validate_dataframe`
     - Validate DataFrame against schema
   * - :func:`~griot_core.validate_list_of_dicts`
     - Validate list of dictionaries
   * - :func:`~griot_core.validate_schema_data`
     - Validate data against schema instance
   * - :func:`~griot_core.get_available_backends`
     - List available DataFrame backends

**Utilities**

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Function
     - Description
   * - :func:`~griot_core.generate_mock_data`
     - Generate mock data from schema
   * - :func:`~griot_core.generate_contract_report`
     - Generate contract documentation
   * - :func:`~griot_core.export_manifest`
     - Export contract manifest

Exceptions
^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Exception
     - Description
   * - :class:`~griot_core.GriotError`
     - Base exception for all Griot errors
   * - :class:`~griot_core.ValidationError`
     - Data validation failure
   * - :class:`~griot_core.ContractNotFoundError`
     - Contract file not found
   * - :class:`~griot_core.ContractParseError`
     - Contract parsing failure
   * - :class:`~griot_core.ConstraintError`
     - Constraint violation
