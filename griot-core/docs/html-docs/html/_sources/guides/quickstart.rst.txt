Quickstart
==========

This guide will help you get started with Griot Core in just a few minutes.

Installation
------------

Install Griot Core with your preferred DataFrame backend:

.. code-block:: bash

   # Core library only
   pip install griot-core

   # With pandas support (most common)
   pip install griot-core[pandas]

   # With polars support
   pip install griot-core[polars]

   # With all backends
   pip install griot-core[all]

Your First Schema
-----------------

Create a data schema by subclassing :class:`~griot_core.Schema`:

.. code-block:: python

   from griot_core import Schema, Field

   class UserSchema(Schema):
       """Schema for user data."""

       user_id: int = Field(
           "Unique user identifier",
           primary_key=True
       )
       username: str = Field(
           "User's username",
           unique=True
       )
       email: str = Field("User's email address")
       is_active: bool = Field("Whether the user is active")

Check your schema:

.. code-block:: python

   # View field names
   print(UserSchema.field_names())
   # Output: ('user_id', 'username', 'email', 'is_active')

   # Get primary key
   print(UserSchema.get_primary_key())
   # Output: 'user_id'

   # Get field info
   field = UserSchema.get_field('email')
   print(f"{field.name}: {field.logical_type}")
   # Output: 'email: string'

Adding Quality Rules
--------------------

Use :class:`~griot_core.QualityRule` to add data quality constraints:

.. code-block:: python

   from griot_core import Schema, Field, QualityRule, QualityUnit

   class ProductSchema(Schema):
       """Schema for product data with quality rules."""

       product_id: str = Field(
           "Product SKU",
           primary_key=True,
           quality=[
               QualityRule.null_values(must_be=0),
               QualityRule.duplicate_values(must_be=0),
           ]
       )
       name: str = Field(
           "Product name",
           quality=[QualityRule.null_values(must_be=0)]
       )
       price: float = Field(
           "Product price",
           quality=[
               QualityRule.invalid_values(
                   must_be=0,
                   min_value=0,
                   max_value=1000000
               )
           ]
       )
       category: str = Field(
           "Product category",
           quality=[
               QualityRule.invalid_values(
                   must_be=0,
                   valid_values=['Electronics', 'Clothing', 'Food', 'Other']
               )
           ]
       )

Schema-Level Quality Rules
--------------------------

For rules that apply to the entire dataset:

.. code-block:: python

   class OrderSchema(Schema):
       """Order schema with schema-level quality rules."""

       # Schema-level quality rules
       _quality = [
           QualityRule.row_count(must_be_greater_than=0),
           QualityRule.duplicate_rows(
               must_be=0,
               properties=['order_id', 'line_number']
           ),
       ]

       order_id: str = Field("Order ID", primary_key=True)
       line_number: int = Field("Line item number")
       product_id: str = Field("Product ID")
       quantity: int = Field("Quantity ordered")

Creating a Contract
-------------------

Wrap your schema in a :class:`~griot_core.Contract`:

.. code-block:: python

   from griot_core import Contract, ContractStatus

   contract = Contract(
       id="user-data-v1",
       name="User Data Contract",
       version="1.0.0",
       status=ContractStatus.ACTIVE,
       schemas=[UserSchema()]
   )

   # Export to YAML
   yaml_content = contract.to_yaml()
   print(yaml_content)

Generating Mock Data
--------------------

Generate test data that conforms to your schema:

.. code-block:: python

   from griot_core import generate_mock_data

   # Generate 100 rows of mock data
   data = generate_mock_data(ProductSchema, rows=100, seed=42)

   # Convert to pandas DataFrame
   import pandas as pd
   df = pd.DataFrame(data)
   print(df.head())

Validating Data
---------------

Validate a DataFrame against your schema (requires pandas backend):

.. code-block:: python

   from griot_core import validate_dataframe

   # Your data
   df = pd.DataFrame({
       'product_id': ['SKU001', 'SKU002', 'SKU003'],
       'name': ['Widget', 'Gadget', 'Gizmo'],
       'price': [9.99, 19.99, 29.99],
       'category': ['Electronics', 'Electronics', 'Other']
   })

   # Validate
   result = validate_dataframe(df, ProductSchema)

   if result.is_valid:
       print("Data is valid!")
   else:
       print("Validation errors:")
       for error in result.errors:
           print(f"  - {error}")

Generating Reports
------------------

Create documentation for your schema:

.. code-block:: python

   from griot_core import generate_contract_report

   report = generate_contract_report(ProductSchema)

   # Get markdown report
   print(report.to_markdown())

   # Get JSON report
   print(report.to_json())

Next Steps
----------

- Learn about :doc:`concepts` to understand the architecture
- Explore :doc:`schema_definition` for advanced schema features
- Read about :doc:`quality_rules` for comprehensive validation
- Check the :doc:`../api/schema` for complete API reference
