Core Concepts
=============

This page explains the key concepts and architecture of Griot Core.

Open Data Contract Standard (ODCS)
----------------------------------

Griot Core is built on the `Open Data Contract Standard (ODCS) <https://github.com/bitol-io/open-data-contract-standard>`_,
an open-source specification for defining data contracts.

ODCS provides a standardized way to describe:

- **Data structure** - Fields, types, and relationships
- **Data quality** - Validation rules and expectations
- **Metadata** - Descriptions, ownership, and governance
- **SLAs** - Service level agreements for data delivery

Architecture Overview
---------------------

.. code-block:: text

   ┌─────────────────────────────────────────────────────────────┐
   │                         Contract                             │
   │  ┌─────────────────────────────────────────────────────────┐│
   │  │ Metadata: id, version, status, team, SLAs...            ││
   │  └─────────────────────────────────────────────────────────┘│
   │  ┌─────────────────────────────────────────────────────────┐│
   │  │                      Schema 1                            ││
   │  │  ┌────────────┐ ┌────────────┐ ┌────────────┐          ││
   │  │  │  Field 1   │ │  Field 2   │ │  Field 3   │   ...    ││
   │  │  │  (quality) │ │  (quality) │ │  (quality) │          ││
   │  │  └────────────┘ └────────────┘ └────────────┘          ││
   │  │  Schema-level quality rules                             ││
   │  └─────────────────────────────────────────────────────────┘│
   │  ┌─────────────────────────────────────────────────────────┐│
   │  │                      Schema 2                            ││
   │  │  ...                                                     ││
   │  └─────────────────────────────────────────────────────────┘│
   └─────────────────────────────────────────────────────────────┘

Key Components
--------------

Contract
^^^^^^^^

A :class:`~griot_core.Contract` is the top-level entity representing a data agreement.
It contains:

- **Identification**: ``id``, ``version``, ``status``
- **Ownership**: ``team``, ``roles``, ``support``
- **Technical details**: ``servers``, ``sla_properties``
- **Schemas**: One or more data schemas

.. code-block:: python

   from griot_core import Contract, ContractStatus

   contract = Contract(
       id="sales-data-v1",
       name="Sales Data Contract",
       version="1.0.0",
       status=ContractStatus.ACTIVE,
       schemas=[OrderSchema(), ProductSchema()]
   )

Schema
^^^^^^

A :class:`~griot_core.Schema` defines the structure of a single data table/file.
It contains:

- **Metadata**: ``name``, ``description``, ``physical_name``
- **Fields**: Column definitions with types and constraints
- **Quality rules**: Schema-level validation rules

.. code-block:: python

   from griot_core import Schema, Field

   class OrderSchema(Schema):
       _name = "Orders"
       _description = "Sales order data"
       _physical_name = "orders_tbl"

       order_id: str = Field("Order ID", primary_key=True)
       customer_id: str = Field("Customer ID")
       total: float = Field("Order total")

Field
^^^^^

A :class:`~griot_core.Field` descriptor defines a single column/property:

- **Type information**: ``logical_type``, ``physical_type``
- **Constraints**: ``primary_key``, ``unique``, ``nullable``, ``required``
- **Metadata**: ``description``, ``tags``
- **Quality rules**: Field-level validation

.. code-block:: python

   from griot_core import Field, QualityRule

   email: str = Field(
       "User email address",
       unique=True,
       nullable=False,
       quality=[
           QualityRule.null_values(must_be=0),
           QualityRule.invalid_values(
               must_be=0,
               pattern=r'^[\w.-]+@[\w.-]+\.\w+$'
           )
       ]
   )

FieldInfo
^^^^^^^^^

:class:`~griot_core.FieldInfo` is the runtime representation of a field,
containing all metadata. It's created automatically from ``Field`` descriptors.

Quality Rules
^^^^^^^^^^^^^

Quality rules define data validation constraints. They can be:

**Property-level** (on individual columns):

- ``nullValues`` - Count of null values
- ``missingValues`` - Count of missing values
- ``invalidValues`` - Count of invalid values
- ``duplicateValues`` - Count of duplicates

**Schema-level** (on the entire dataset):

- ``rowCount`` - Total row count
- ``duplicateRows`` - Duplicate rows across columns

.. code-block:: python

   from griot_core import QualityRule, QualityUnit

   # Property-level rules
   QualityRule.null_values(must_be=0)
   QualityRule.missing_values(must_be_less_than=5, unit=QualityUnit.PERCENT)
   QualityRule.invalid_values(must_be=0, valid_values=['A', 'B', 'C'])

   # Schema-level rules
   QualityRule.row_count(must_be_between=[100, 10000])
   QualityRule.duplicate_rows(must_be=0, properties=['id', 'date'])

Type System
-----------

Logical Types
^^^^^^^^^^^^^

ODCS logical types represent abstract data types:

.. list-table::
   :header-rows: 1
   :widths: 20 30 50

   * - Logical Type
     - Python Type
     - Description
   * - ``string``
     - ``str``
     - Text data
   * - ``integer``
     - ``int``
     - Whole numbers
   * - ``float``
     - ``float``
     - Decimal numbers
   * - ``boolean``
     - ``bool``
     - True/False values
   * - ``date``
     - ``str``
     - Date (ISO format)
   * - ``datetime``
     - ``str``
     - Date and time (ISO format)
   * - ``array``
     - ``list``
     - Lists/arrays
   * - ``object``
     - ``dict``
     - Nested objects

Physical Types
^^^^^^^^^^^^^^

Physical types represent storage-specific types:

.. code-block:: python

   email: str = Field(
       "Email address",
       logical_type="string",
       physical_type="VARCHAR(255)"  # Database-specific
   )

Contract Lifecycle
------------------

Contracts have a status that indicates their lifecycle stage:

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Status
     - Description
   * - ``draft``
     - Under development, not for production use
   * - ``active``
     - Production-ready, consumers can depend on it
   * - ``deprecated``
     - Being phased out, consumers should migrate
   * - ``retired``
     - No longer available

Validation Pipeline
-------------------

When you validate data against a schema:

1. **Schema generation**: Griot schema → Pandera schema
2. **Type checking**: Verify column types
3. **Null checking**: Apply nullable constraints
4. **Quality rules**: Execute quality rule checks
5. **Schema-level checks**: Run schema-level validations
6. **Result aggregation**: Collect all errors

.. code-block:: python

   from griot_core import validate_dataframe

   result = validate_dataframe(df, MySchema)

   if not result.is_valid:
       for error in result.errors:
           print(f"Field: {error.field}, Error: {error.message}")

Next Steps
----------

- Learn :doc:`schema_definition` in depth
- Master :doc:`quality_rules` for validation
- Understand :doc:`contracts` management
