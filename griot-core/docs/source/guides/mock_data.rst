Mock Data Generation
====================

Griot Core can generate mock data from your schemas for testing and development.

Basic Usage
-----------

Generate a DataFrame from a schema:

.. code-block:: python

   import pandas as pd
   from griot_core import Schema, Field, generate_mock_data

   class ProductSchema(Schema):
       product_id: str = Field("Product ID", primary_key=True)
       name: str = Field("Product name")
       price: float = Field("Price")
       in_stock: bool = Field("Stock status")

   # Generate mock DataFrame
   df = generate_mock_data(ProductSchema, num_rows=100)

   print(df.head())
   #    product_id       name     price  in_stock
   # 0    a1b2c3d4  Product_0     45.23      True
   # 1    e5f6g7h8  Product_1     12.99     False
   # ...

Controlling Row Count
---------------------

Specify the number of rows to generate:

.. code-block:: python

   # Small dataset for unit tests
   small_df = generate_mock_data(schema, num_rows=10)

   # Large dataset for performance testing
   large_df = generate_mock_data(schema, num_rows=100000)

Type-Aware Generation
---------------------

Mock data is generated based on field types:

.. code-block:: python

   class TypedSchema(Schema):
       # Strings: random alphanumeric
       name: str = Field("Name")

       # Integers: random integers
       count: int = Field("Count")

       # Floats: random decimals
       amount: float = Field("Amount")

       # Booleans: True/False
       active: bool = Field("Active")

       # Dates: ISO format date strings
       created_date: str = Field("Created date", logical_type="date")

       # Datetime: ISO format datetime strings
       updated_at: str = Field("Updated at", logical_type="datetime")

   df = generate_mock_data(TypedSchema, num_rows=5)

Primary Key Handling
--------------------

Primary key fields generate unique values:

.. code-block:: python

   class UserSchema(Schema):
       user_id: str = Field("User ID", primary_key=True)  # Unique values
       email: str = Field("Email")

   df = generate_mock_data(UserSchema, num_rows=100)

   # All user_id values are unique
   assert df['user_id'].nunique() == 100

Unique Fields
-------------

Fields marked as unique also generate unique values:

.. code-block:: python

   class AccountSchema(Schema):
       account_id: str = Field("Account ID", primary_key=True)
       email: str = Field("Email", unique=True)  # Unique values
       status: str = Field("Status")

   df = generate_mock_data(AccountSchema, num_rows=50)
   assert df['email'].nunique() == 50

Nullable Fields
---------------

Nullable fields include some null values:

.. code-block:: python

   class OptionalSchema(Schema):
       id: str = Field("ID", primary_key=True)
       required_field: str = Field("Required", nullable=False)  # No nulls
       optional_field: str | None = Field("Optional", nullable=True)  # Some nulls

   df = generate_mock_data(OptionalSchema, num_rows=100)

   # required_field has no nulls
   assert df['required_field'].isna().sum() == 0

   # optional_field may have some nulls
   print(f"Null count: {df['optional_field'].isna().sum()}")

Default Values
--------------

Fields with defaults use those values:

.. code-block:: python

   class ConfigSchema(Schema):
       id: str = Field("ID", primary_key=True)
       status: str = Field("Status", default="active")
       priority: int = Field("Priority", default=5)

   df = generate_mock_data(ConfigSchema, num_rows=10)

   # Default values may be used
   print(df['status'].value_counts())

Quality Rule Constraints
------------------------

Mock data respects quality rule constraints:

.. code-block:: python

   from griot_core import QualityRule

   class ConstrainedSchema(Schema):
       id: str = Field("ID", primary_key=True)

       # Enum constraint - values from the list
       status: str = Field(
           "Status",
           quality=[
               QualityRule.invalid_values(
                   must_be=0,
                   valid_values=['pending', 'active', 'completed']
               )
           ]
       )

       # Range constraint - values within range
       age: int = Field(
           "Age",
           quality=[
               QualityRule.invalid_values(
                   must_be=0,
                   min_value=18,
                   max_value=100
               )
           ]
       )

       # Pattern constraint - values matching regex
       code: str = Field(
           "Code",
           quality=[
               QualityRule.invalid_values(
                   must_be=0,
                   pattern=r'^[A-Z]{3}-\d{4}$'
               )
           ]
       )

   df = generate_mock_data(ConstrainedSchema, num_rows=100)

   # status values are from the valid list
   assert set(df['status'].unique()).issubset({'pending', 'active', 'completed'})

   # age values are in range
   assert df['age'].between(18, 100).all()

Reproducible Generation
-----------------------

Set a random seed for reproducible data:

.. code-block:: python

   # Same seed = same data
   df1 = generate_mock_data(schema, num_rows=100, seed=42)
   df2 = generate_mock_data(schema, num_rows=100, seed=42)

   assert df1.equals(df2)

   # Different seed = different data
   df3 = generate_mock_data(schema, num_rows=100, seed=123)
   assert not df1.equals(df3)

Backend Selection
-----------------

Generate data for different DataFrame backends:

.. code-block:: python

   # pandas (default)
   pandas_df = generate_mock_data(schema, num_rows=100, backend='pandas')

   # polars
   polars_df = generate_mock_data(schema, num_rows=100, backend='polars')

   # Return as dict (for any backend)
   data_dict = generate_mock_data(schema, num_rows=100, backend='dict')

Contract-Based Generation
-------------------------

Generate mock data for all schemas in a contract:

.. code-block:: python

   from griot_core import Contract, generate_mock_contract_data

   contract = Contract(
       id="sales-contract",
       schemas=[OrderSchema(), ProductSchema(), CustomerSchema()]
   )

   # Generate data for all schemas
   mock_data = generate_mock_contract_data(contract, num_rows=100)

   orders_df = mock_data['Orders']
   products_df = mock_data['Products']
   customers_df = mock_data['Customers']

Custom Generators
-----------------

Override default generation for specific fields:

.. code-block:: python

   from griot_core import generate_mock_data
   import random

   def email_generator():
       domains = ['example.com', 'test.org', 'mock.net']
       return f"user{random.randint(1000, 9999)}@{random.choice(domains)}"

   def price_generator():
       return round(random.uniform(0.99, 999.99), 2)

   custom_generators = {
       'email': email_generator,
       'price': price_generator,
   }

   df = generate_mock_data(
       schema,
       num_rows=100,
       custom_generators=custom_generators
   )

Testing Workflows
-----------------

Unit Testing
^^^^^^^^^^^^

.. code-block:: python

   import pytest
   from griot_core import generate_mock_data, validate_dataframe

   class TestDataProcessing:
       def test_process_valid_data(self):
           """Test with valid mock data."""
           df = generate_mock_data(OrderSchema, num_rows=10, seed=42)

           result = process_orders(df)

           assert result is not None
           assert len(result) == 10

       def test_validation_passes(self):
           """Mock data should pass validation."""
           df = generate_mock_data(OrderSchema, num_rows=100, seed=42)

           result = validate_dataframe(df, OrderSchema)

           assert result.is_valid

Integration Testing
^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   def test_end_to_end_pipeline():
       """Test full pipeline with realistic data."""
       # Generate test data
       orders = generate_mock_data(OrderSchema, num_rows=1000)
       products = generate_mock_data(ProductSchema, num_rows=100)

       # Run pipeline
       result = run_etl_pipeline(orders, products)

       # Validate output
       assert validate_dataframe(result, OutputSchema).is_valid

Performance Testing
^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   import time

   def test_performance_with_large_dataset():
       """Test processing speed with large data."""
       df = generate_mock_data(schema, num_rows=1_000_000)

       start = time.time()
       result = process_data(df)
       elapsed = time.time() - start

       assert elapsed < 60  # Should complete in under 60 seconds

Edge Case Testing
^^^^^^^^^^^^^^^^^

.. code-block:: python

   def test_handles_nulls():
       """Test handling of null values."""
       # Schema with nullable fields
       class NullableSchema(Schema):
           id: str = Field("ID", primary_key=True)
           value: str | None = Field("Value", nullable=True)

       df = generate_mock_data(NullableSchema, num_rows=100)

       # Ensure some nulls exist
       assert df['value'].isna().sum() > 0

       # Process should handle nulls
       result = process_with_nulls(df)
       assert result is not None

Best Practices
--------------

1. **Use seeds in tests** - Ensure reproducible test data
2. **Match production volumes** - Test with realistic data sizes
3. **Validate generated data** - Ensure it passes your own schemas
4. **Test edge cases** - Generate data with nulls, boundaries
5. **Don't hardcode test data** - Use generated data for flexibility

.. code-block:: python

   # Good: Reproducible, validated test data
   @pytest.fixture
   def sample_data():
       df = generate_mock_data(OrderSchema, num_rows=100, seed=42)
       result = validate_dataframe(df, OrderSchema)
       assert result.is_valid
       return df

   # Use in tests
   def test_order_processing(sample_data):
       result = process_orders(sample_data)
       assert len(result) == 100

Limitations
-----------

- Complex relationships between fields are not automatically maintained
- Foreign key references need custom generators
- Very specific patterns may need custom generators

For complex scenarios, combine mock generation with manual adjustments:

.. code-block:: python

   # Generate base data
   df = generate_mock_data(schema, num_rows=100)

   # Adjust for specific test cases
   df.loc[0, 'status'] = 'error'  # Add specific edge case
   df.loc[1:5, 'amount'] = 0  # Add boundary case

Next Steps
----------

- Learn about :doc:`validation` for data validation
- See :doc:`contracts` for contract management
- Check the :doc:`../api/validation` for full API reference
