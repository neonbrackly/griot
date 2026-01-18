Schema Definition
=================

This guide covers how to define data schemas using Griot Core.

Basic Schema Definition
-----------------------

Create a schema by subclassing :class:`~griot_core.Schema`:

.. code-block:: python

   from griot_core import Schema, Field

   class CustomerSchema(Schema):
       """Customer data schema."""

       customer_id: str = Field("Unique customer identifier", primary_key=True)
       name: str = Field("Customer full name")
       email: str = Field("Contact email address")
       created_at: str = Field("Account creation timestamp", logical_type="datetime")

The metaclass automatically processes type hints and ``Field`` descriptors to
create :class:`~griot_core.FieldInfo` objects.

Schema Metadata
---------------

Add metadata using class variables prefixed with ``_``:

.. code-block:: python

   class OrderSchema(Schema):
       """Order data with full metadata."""

       # Schema-level metadata
       _name = "Orders"
       _description = "Customer order records"
       _physical_name = "orders_tbl"
       _physical_type = "table"
       _tags = ["sales", "transactional"]

       # Fields
       order_id: str = Field("Order ID", primary_key=True)
       # ...

Available metadata attributes:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Attribute
     - Description
   * - ``_name``
     - Human-readable schema name
   * - ``_description``
     - Schema description
   * - ``_physical_name``
     - Actual name in storage (table name, file name)
   * - ``_physical_type``
     - Type of storage (table, view, file)
   * - ``_id``
     - Unique schema identifier
   * - ``_business_name``
     - Business-friendly name
   * - ``_tags``
     - Classification tags
   * - ``_quality``
     - Schema-level quality rules
   * - ``_authoritative_definitions``
     - Reference definitions

Field Definition
----------------

Basic Fields
^^^^^^^^^^^^

Define fields with :class:`~griot_core.Field`:

.. code-block:: python

   from griot_core import Field

   # Simple field
   name: str = Field("Customer name")

   # With all options
   email: str = Field(
       "Email address",  # Description (required)
       logical_type="string",
       physical_type="VARCHAR(255)",
       primary_key=False,
       unique=True,
       nullable=False,
       required=True,
       critical_data_element=True,
       tags=["pii", "contact"],
   )

Field Options
^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Option
     - Type
     - Description
   * - ``description``
     - str
     - Human-readable description (required, first arg)
   * - ``logical_type``
     - str
     - ODCS logical type (auto-inferred from Python type)
   * - ``physical_type``
     - str
     - Storage-specific type (e.g., "VARCHAR(36)")
   * - ``primary_key``
     - bool
     - Whether this is the primary key
   * - ``unique``
     - bool
     - Whether values must be unique
   * - ``nullable``
     - bool
     - Whether null values are allowed (default: True)
   * - ``required``
     - bool
     - Whether field is required
   * - ``partitioned``
     - bool
     - Whether used for partitioning
   * - ``partition_key_position``
     - int
     - Position in partition key
   * - ``critical_data_element``
     - bool
     - Whether this is a critical field
   * - ``tags``
     - list[str]
     - Classification tags
   * - ``quality``
     - list[dict]
     - Quality rules (see :doc:`quality_rules`)
   * - ``relationships``
     - list[dict]
     - Foreign key relationships
   * - ``custom_properties``
     - dict
     - Extension properties
   * - ``default``
     - Any
     - Default value
   * - ``default_factory``
     - Callable
     - Factory function for default value

Type Inference
^^^^^^^^^^^^^^

Logical types are automatically inferred from Python type hints:

.. code-block:: python

   class AutoTypedSchema(Schema):
       # string
       name: str = Field("Name")

       # integer
       age: int = Field("Age")

       # float
       price: float = Field("Price")

       # boolean
       is_active: bool = Field("Active status")

       # array
       tags: list = Field("Tags")

       # object
       metadata: dict = Field("Metadata")

       # Optional makes nullable=True
       nickname: str | None = Field("Optional nickname")

Primary Keys
^^^^^^^^^^^^

Designate a primary key:

.. code-block:: python

   class UserSchema(Schema):
       user_id: str = Field("User ID", primary_key=True)
       # ...

   # Access the primary key
   pk = UserSchema.get_primary_key()  # Returns 'user_id'

Default Values
^^^^^^^^^^^^^^

Specify default values:

.. code-block:: python

   class ConfigSchema(Schema):
       # Static default
       status: str = Field("Status", default="pending")

       # Factory default (for mutable objects)
       tags: list = Field("Tags", default_factory=list)

       # Default with validation
       priority: int = Field("Priority", default=5)

.. warning::

   Don't use mutable defaults directly. Use ``default_factory`` instead:

   .. code-block:: python

      # Bad - shared mutable default
      items: list = Field("Items", default=[])

      # Good - factory creates new list each time
      items: list = Field("Items", default_factory=list)

Schema Inheritance
------------------

Schemas support inheritance:

.. code-block:: python

   class BaseEntity(Schema):
       """Base schema with common fields."""
       id: str = Field("Unique identifier", primary_key=True)
       created_at: str = Field("Creation timestamp", logical_type="datetime")
       updated_at: str = Field("Last update timestamp", logical_type="datetime")


   class CustomerSchema(BaseEntity):
       """Customer inherits from BaseEntity."""
       name: str = Field("Customer name")
       email: str = Field("Email address")


   class OrderSchema(BaseEntity):
       """Order inherits from BaseEntity."""
       customer_id: str = Field("Customer ID")
       total: float = Field("Order total")

   # CustomerSchema has: id, created_at, updated_at, name, email

Data-Driven Schemas
-------------------

Create schemas dynamically from dictionaries:

.. code-block:: python

   from griot_core import Schema, FieldInfo

   # From ODCS dictionary
   data = {
       "name": "Products",
       "properties": [
           {"name": "product_id", "logicalType": "string", "primary_key": True},
           {"name": "name", "logicalType": "string"},
           {"name": "price", "logicalType": "float"},
       ]
   }

   schema = Schema.from_dict(data)

   # Or create programmatically
   schema = Schema(
       name="Products",
       properties=[
           FieldInfo(name="product_id", logical_type="string", primary_key=True),
           FieldInfo(name="name", logical_type="string"),
           FieldInfo(name="price", logical_type="float"),
       ]
   )

Accessing Schema Information
----------------------------

.. code-block:: python

   class ProductSchema(Schema):
       product_id: str = Field("Product ID", primary_key=True)
       name: str = Field("Product name")
       price: float = Field("Price")

   # Get all field names
   names = ProductSchema.field_names()
   # ('product_id', 'name', 'price')

   # Get primary key field name
   pk = ProductSchema.get_primary_key()
   # 'product_id'

   # Get specific field info
   field = ProductSchema.get_field('name')
   print(field.description)  # 'Product name'
   print(field.logical_type)  # 'string'

   # List all fields as FieldInfo objects
   fields = ProductSchema.list_fields()

   # For instances
   schema = ProductSchema()
   all_fields = schema.fields  # dict of name -> FieldInfo

Serialization
-------------

Export to ODCS format:

.. code-block:: python

   schema = ProductSchema()

   # To dictionary (camelCase keys)
   data = schema.to_dict()
   print(data)
   # {
   #     'name': 'ProductSchema',
   #     'properties': [
   #         {'name': 'product_id', 'logicalType': 'string', 'primary_key': True},
   #         ...
   #     ]
   # }

Best Practices
--------------

1. **Always add descriptions** - Every field should have a meaningful description
2. **Define primary keys** - Identify the unique identifier for each record
3. **Use type hints** - Let Python infer logical types when possible
4. **Add quality rules** - Define validation constraints upfront
5. **Use inheritance** - Share common fields across related schemas
6. **Tag critical fields** - Mark PII and sensitive data

.. code-block:: python

   class BestPracticeSchema(Schema):
       """Example following best practices."""

       _name = "Transactions"
       _description = "Financial transaction records"
       _tags = ["finance", "sensitive"]

       transaction_id: str = Field(
           "Unique transaction identifier (UUID format)",
           primary_key=True,
           quality=[QualityRule.null_values(must_be=0)]
       )
       amount: float = Field(
           "Transaction amount in USD",
           critical_data_element=True,
           quality=[QualityRule.invalid_values(must_be=0, min_value=0)]
       )
       customer_id: str = Field(
           "Reference to customer record",
           tags=["pii"],
           relationships=[{"target": "customers.customer_id"}]
       )

Next Steps
----------

- Learn about :doc:`quality_rules` for validation
- Create :doc:`contracts` to manage schemas
- See :doc:`validation` for data validation
