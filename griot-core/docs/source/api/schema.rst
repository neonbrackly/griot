Schema API
==========

The schema module provides classes for defining data schemas.

Schema
------

.. class:: griot_core.Schema

   Base class for defining data schemas with typed fields.

   Create schemas by subclassing and adding typed fields:

   .. code-block:: python

      from griot_core import Schema, Field

      class CustomerSchema(Schema):
          customer_id: str = Field("Customer ID", primary_key=True)
          name: str = Field("Customer name")
          email: str = Field("Email address")

   **Class Attributes (Metadata)**

   Use underscore-prefixed class variables for schema metadata:

   .. list-table::
      :header-rows: 1
      :widths: 25 75

      * - Attribute
        - Description
      * - ``_name``
        - Human-readable schema name (defaults to class name)
      * - ``_description``
        - Schema description
      * - ``_physical_name``
        - Physical storage name (e.g., table name)
      * - ``_physical_type``
        - Type of storage (table, view, file)
      * - ``_id``
        - Unique schema identifier
      * - ``_business_name``
        - Business-friendly name
      * - ``_tags``
        - Classification tags (list of strings)
      * - ``_quality``
        - Schema-level quality rules (list of dicts)
      * - ``_authoritative_definitions``
        - Reference definitions (list of dicts)

   **Class Methods**

   .. method:: field_names() -> tuple[str, ...]
      :classmethod:

      Get names of all fields defined in the schema.

      :returns: Tuple of field names

      .. code-block:: python

         names = CustomerSchema.field_names()
         # ('customer_id', 'name', 'email')

   .. method:: get_primary_key() -> str | None
      :classmethod:

      Get the name of the primary key field.

      :returns: Primary key field name, or None if not defined

      .. code-block:: python

         pk = CustomerSchema.get_primary_key()
         # 'customer_id'

   .. method:: get_field(name: str) -> FieldInfo | None
      :classmethod:

      Get field information by name.

      :param name: Field name
      :returns: FieldInfo object or None

      .. code-block:: python

         field = CustomerSchema.get_field('email')
         print(field.description)  # 'Email address'

   .. method:: list_fields() -> list[FieldInfo]
      :classmethod:

      Get list of all field information objects.

      :returns: List of FieldInfo objects

   .. method:: from_dict(data: dict) -> Schema
      :classmethod:

      Create a schema instance from an ODCS dictionary.

      :param data: ODCS-format schema dictionary
      :returns: Schema instance

      .. code-block:: python

         data = {
             "name": "Products",
             "properties": [
                 {"name": "id", "logicalType": "string", "primary_key": True}
             ]
         }
         schema = Schema.from_dict(data)

   **Instance Properties**

   .. attribute:: name
      :type: str

      Schema name (from ``_name`` or class name).

   .. attribute:: description
      :type: str | None

      Schema description.

   .. attribute:: physical_name
      :type: str | None

      Physical storage name.

   .. attribute:: fields
      :type: dict[str, FieldInfo]

      Dictionary mapping field names to FieldInfo objects.

   .. attribute:: quality
      :type: list[dict]

      Schema-level quality rules.

   **Instance Methods**

   .. method:: to_dict(camel_case: bool = True) -> dict

      Convert schema to ODCS dictionary format.

      :param camel_case: Use camelCase keys (default True)
      :returns: Dictionary representation

      .. code-block:: python

         data = schema.to_dict()
         # {'name': 'CustomerSchema', 'properties': [...]}

Field
-----

.. function:: griot_core.Field(description: str, **kwargs) -> FieldDescriptor

   Create a field descriptor for schema properties.

   The ``Field`` function creates a descriptor that captures field metadata
   and is processed by the Schema metaclass.

   :param description: Human-readable field description (required)
   :param logical_type: ODCS logical type (auto-inferred from type hint)
   :param physical_type: Storage-specific type (e.g., "VARCHAR(255)")
   :param primary_key: Whether this is the primary key (default: False)
   :param unique: Whether values must be unique (default: False)
   :param nullable: Whether null values are allowed (default: True)
   :param required: Whether field is required (default: False)
   :param partitioned: Whether used for partitioning (default: False)
   :param partition_key_position: Position in partition key
   :param critical_data_element: Whether this is a critical field (default: False)
   :param tags: Classification tags (list of strings)
   :param quality: Quality rules (list of dicts)
   :param relationships: Foreign key relationships (list of dicts)
   :param custom_properties: Extension properties (dict)
   :param default: Default value
   :param default_factory: Factory function for default value

   :returns: Field descriptor

   **Basic Usage**

   .. code-block:: python

      from griot_core import Schema, Field

      class ProductSchema(Schema):
          # Simple field with description
          name: str = Field("Product name")

          # Primary key field
          product_id: str = Field("Product ID", primary_key=True)

          # Field with all options
          price: float = Field(
              "Product price in USD",
              nullable=False,
              required=True,
              critical_data_element=True,
              tags=["financial"],
          )

   **Type Inference**

   Logical types are automatically inferred from Python type hints:

   .. code-block:: python

      class AutoTypedSchema(Schema):
          text_field: str = Field("String")    # logical_type="string"
          int_field: int = Field("Integer")    # logical_type="integer"
          float_field: float = Field("Float")  # logical_type="float"
          bool_field: bool = Field("Boolean")  # logical_type="boolean"
          list_field: list = Field("Array")    # logical_type="array"
          dict_field: dict = Field("Object")   # logical_type="object"

   **Nullable Fields**

   .. code-block:: python

      class NullableSchema(Schema):
          # Nullable (default)
          optional: str = Field("Optional field")

          # Not nullable
          required: str = Field("Required field", nullable=False)

          # Nullable via type hint
          also_optional: str | None = Field("Also optional")

   **Quality Rules**

   .. code-block:: python

      from griot_core import Field, QualityRule

      email: str = Field(
          "Email address",
          quality=[
              QualityRule.null_values(must_be=0),
              QualityRule.invalid_values(
                  must_be=0,
                  pattern=r'^[\w.-]+@[\w.-]+\.\w+$'
              ),
          ]
      )

   **Default Values**

   .. code-block:: python

      # Static default
      status: str = Field("Status", default="pending")

      # Factory default (for mutable objects)
      tags: list = Field("Tags", default_factory=list)

FieldInfo
---------

.. class:: griot_core.FieldInfo

   Runtime representation of a schema field with all metadata.

   ``FieldInfo`` objects are created automatically from ``Field`` descriptors
   by the Schema metaclass. They contain all field metadata in a structured format.

   **Attributes**

   .. attribute:: name
      :type: str

      Field name (column name).

   .. attribute:: description
      :type: str

      Human-readable description.

   .. attribute:: logical_type
      :type: str

      ODCS logical type (string, integer, float, etc.).

   .. attribute:: physical_type
      :type: str | None

      Storage-specific type.

   .. attribute:: primary_key
      :type: bool

      Whether this is the primary key.

   .. attribute:: unique
      :type: bool

      Whether values must be unique.

   .. attribute:: nullable
      :type: bool

      Whether null values are allowed.

   .. attribute:: required
      :type: bool

      Whether field is required.

   .. attribute:: critical_data_element
      :type: bool

      Whether this is a critical field.

   .. attribute:: tags
      :type: list[str]

      Classification tags.

   .. attribute:: quality
      :type: list[dict]

      Quality rules.

   .. attribute:: relationships
      :type: list[dict]

      Foreign key relationships.

   .. attribute:: default
      :type: Any

      Default value.

   **Methods**

   .. method:: to_dict(camel_case: bool = True) -> dict

      Convert to ODCS dictionary format.

      :param camel_case: Use camelCase keys (default True)
      :returns: Dictionary representation

   **Example**

   .. code-block:: python

      # Access field info from schema
      class ProductSchema(Schema):
          product_id: str = Field("Product ID", primary_key=True)
          price: float = Field("Price", nullable=False)

      # Get field info
      field = ProductSchema.get_field('price')

      print(field.name)          # 'price'
      print(field.description)   # 'Price'
      print(field.logical_type)  # 'float'
      print(field.nullable)      # False
      print(field.to_dict())     # {'name': 'price', 'logicalType': 'float', ...}
