Changelog
=========

All notable changes to Griot Core are documented here.

The format is based on `Keep a Changelog <https://keepachangelog.com/>`_,
and this project adheres to `Semantic Versioning <https://semver.org/>`_.

[Unreleased]
------------

Added
^^^^^

- Type-safe quality rule builders with ``QualityRule`` class
- Comprehensive enums: ``QualityMetric``, ``QualityOperator``, ``QualityUnit``, ``QualityCheckType``
- Schema-level quality rule support via ``_quality`` class attribute
- Mock data generation from schemas
- Contract linting and validation
- Multi-backend DataFrame support (pandas, polars, spark, dask)
- ODCS-compliant YAML serialization

Changed
^^^^^^^

- Quality rules now use enum-based operators for type safety
- Pandera schema generation uses new enum system
- Improved error messages for validation failures

Fixed
^^^^^

- Schema inheritance properly merges parent fields
- Quality rule unit calculations (rows vs percent)
- Contract serialization handles all ODCS fields

[0.8.0] - 2024-XX-XX
--------------------

Added
^^^^^

- Initial public release
- Core schema definition with ``Schema`` and ``Field``
- Contract management with ``Contract`` class
- ODCS-compliant quality rules
- DataFrame validation with Pandera
- YAML import/export
- Documentation with Sphinx

API Stability
-------------

Griot Core follows semantic versioning:

- **Major version** (1.0.0): Breaking API changes
- **Minor version** (0.1.0): New features, backwards compatible
- **Patch version** (0.0.1): Bug fixes, backwards compatible

During the 0.x phase, the API may change between minor versions.
After 1.0.0, we commit to backwards compatibility within major versions.

Deprecation Policy
------------------

When features are deprecated:

1. A deprecation warning is added
2. The feature continues to work for at least one minor version
3. Documentation is updated with migration guidance
4. The feature is removed in the next major version

Migration Guides
----------------

Migrating to 0.8.0
^^^^^^^^^^^^^^^^^^

**Quality Rules**

Old style (raw dictionaries):

.. code-block:: python

   # Old
   quality=[{"metric": "nullValues", "mustBe": 0}]

New style (type-safe builders):

.. code-block:: python

   # New
   from griot_core import QualityRule
   quality=[QualityRule.null_values(must_be=0)]

Both styles continue to work, but the new style is recommended.

**Enum Usage**

Use enums instead of string literals:

.. code-block:: python

   # Old
   status = "active"

   # New
   from griot_core import ContractStatus
   status = ContractStatus.ACTIVE
