Data Validation
===============

Griot Core provides powerful data validation capabilities using schemas.
This guide covers how to validate DataFrames against your contracts.

Prerequisites
-------------

Install a DataFrame backend:

.. code-block:: bash

   pip install griot-core[pandas]  # or polars, spark, dask

Basic Validation
----------------

Validate a pandas DataFrame against a schema:

.. code-block:: python

   import pandas as pd
   from griot_core import Schema, Field, validate_dataframe

   class ProductSchema(Schema):
       product_id: str = Field("Product ID", primary_key=True)
       name: str = Field("Product name")
       price: float = Field("Price")

   # Create sample data
   df = pd.DataFrame({
       'product_id': ['P001', 'P002', 'P003'],
       'name': ['Widget', 'Gadget', 'Gizmo'],
       'price': [9.99, 19.99, 29.99]
   })

   # Validate
   result = validate_dataframe(df, ProductSchema)

   print(f"Valid: {result.is_valid}")
   print(f"Errors: {len(result.errors)}")

ValidationResult
----------------

The :class:`~griot_core.ValidationResult` contains validation results:

.. code-block:: python

   result = validate_dataframe(df, schema)

   # Check overall validity
   if result.is_valid:
       print("Data is valid!")
   else:
       print(f"Found {len(result.errors)} errors")

   # Access individual errors
   for error in result.errors:
       print(f"Field: {error.field}")
       print(f"Message: {error.message}")
       print(f"Severity: {error.severity}")

   # Get summary
   print(result.summary())

   # Convert to dictionary
   report = result.to_dict()

Validation Errors
-----------------

Each :class:`~griot_core.ValidationError` contains:

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Attribute
     - Description
   * - ``field``
     - The field name that failed validation (or None for schema-level)
   * - ``message``
     - Human-readable error description
   * - ``severity``
     - ``Severity.ERROR`` or ``Severity.WARNING``
   * - ``error_type``
     - Type of validation failure
   * - ``details``
     - Additional error details (dict)

Example:

.. code-block:: python

   for error in result.errors:
       if error.severity == Severity.ERROR:
           print(f"ERROR in {error.field}: {error.message}")
       else:
           print(f"WARNING in {error.field}: {error.message}")

Validating with Quality Rules
-----------------------------

Property-Level Rules
^^^^^^^^^^^^^^^^^^^^

Quality rules on fields are automatically validated:

.. code-block:: python

   from griot_core import Schema, Field, QualityRule, QualityUnit

   class StrictSchema(Schema):
       email: str = Field(
           "Email address",
           quality=[
               QualityRule.null_values(must_be=0),
               QualityRule.duplicate_values(must_be=0),
           ]
       )
       age: int = Field(
           "Customer age",
           quality=[
               QualityRule.null_values(must_be_less_than=5, unit=QualityUnit.PERCENT),
               QualityRule.invalid_values(must_be=0, min_value=0, max_value=150),
           ]
       )

   # Validation will check all quality rules
   result = validate_dataframe(df, StrictSchema)

Schema-Level Rules
^^^^^^^^^^^^^^^^^^

Schema-level rules validate the entire dataset:

.. code-block:: python

   class OrderSchema(Schema):
       _quality = [
           QualityRule.row_count(must_be_greater_than=0),
           QualityRule.duplicate_rows(must_be=0, properties=['order_id']),
       ]

       order_id: str = Field("Order ID", primary_key=True)
       product_id: str = Field("Product ID")
       quantity: int = Field("Quantity")

   result = validate_dataframe(df, OrderSchema)

Type Validation
---------------

Griot validates that column types match the schema:

.. code-block:: python

   class TypedSchema(Schema):
       id: str = Field("ID")
       count: int = Field("Count")
       amount: float = Field("Amount")
       active: bool = Field("Active flag")

   # This will fail if types don't match
   df = pd.DataFrame({
       'id': [1, 2, 3],  # Wrong! Should be string
       'count': [10, 20, 30],
       'amount': [1.5, 2.5, 3.5],
       'active': [True, False, True]
   })

   result = validate_dataframe(df, TypedSchema)
   # Will report type mismatch for 'id' column

Nullable Validation
-------------------

Fields marked as non-nullable will fail if they contain nulls:

.. code-block:: python

   class RequiredSchema(Schema):
       required_field: str = Field("Required", nullable=False)
       optional_field: str | None = Field("Optional", nullable=True)

   df = pd.DataFrame({
       'required_field': ['a', None, 'c'],  # Will fail!
       'optional_field': ['x', None, 'z'],  # OK
   })

   result = validate_dataframe(df, RequiredSchema)

Coerce Types
------------

Enable type coercion to automatically convert types:

.. code-block:: python

   result = validate_dataframe(df, schema, coerce=True)

This will attempt to convert columns to the expected types before validation.

.. warning::

   Type coercion may cause data loss. For example, converting ``1.9`` to
   an integer yields ``1``.

Handling Missing Columns
------------------------

By default, validation fails if the DataFrame is missing required columns:

.. code-block:: python

   class FullSchema(Schema):
       col_a: str = Field("Column A")
       col_b: str = Field("Column B")
       col_c: str = Field("Column C")

   # Only has 2 of 3 columns
   df = pd.DataFrame({
       'col_a': ['x'],
       'col_b': ['y'],
   })

   result = validate_dataframe(df, FullSchema)
   # Will report missing 'col_c' column

Partial Validation
------------------

To validate only specific columns:

.. code-block:: python

   from griot_core import validate_dataframe_partial

   # Only validate columns that exist in the DataFrame
   result = validate_dataframe_partial(df, schema)

Validation with Contracts
-------------------------

Validate data against a contract's schemas:

.. code-block:: python

   from griot_core import Contract, validate_contract_data

   contract = Contract(
       id="my-contract",
       schemas=[OrderSchema(), ProductSchema()]
   )

   # Validate multiple DataFrames against contract schemas
   data = {
       'Orders': orders_df,
       'Products': products_df,
   }

   results = validate_contract_data(contract, data)

   for schema_name, result in results.items():
       print(f"{schema_name}: {'Valid' if result.is_valid else 'Invalid'}")

Error Handling
--------------

Raise on Validation Failure
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from griot_core import validate_dataframe, ValidationException

   try:
       result = validate_dataframe(df, schema, raise_on_error=True)
   except ValidationException as e:
       print(f"Validation failed: {e}")
       for error in e.errors:
           print(f"  - {error.message}")

Custom Error Handling
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   result = validate_dataframe(df, schema)

   if not result.is_valid:
       # Log errors
       for error in result.errors:
           logger.error(f"Validation error: {error.field} - {error.message}")

       # Decide what to do
       if result.error_count > 10:
           raise ValueError("Too many validation errors")

Validation Reports
------------------

Generate detailed validation reports:

.. code-block:: python

   from griot_core import generate_validation_report

   result = validate_dataframe(df, schema)
   report = generate_validation_report(result, schema)

   print(report['summary'])
   for field_report in report['field_reports']:
       print(f"{field_report['field']}: {field_report['status']}")

Backend Support
---------------

Griot Core supports multiple DataFrame backends:

pandas
^^^^^^

.. code-block:: python

   import pandas as pd
   from griot_core import validate_dataframe

   df = pd.DataFrame(...)
   result = validate_dataframe(df, schema)

polars
^^^^^^

.. code-block:: python

   import polars as pl
   from griot_core import validate_dataframe

   df = pl.DataFrame(...)
   result = validate_dataframe(df, schema)

PySpark
^^^^^^^

.. code-block:: python

   from pyspark.sql import SparkSession
   from griot_core import validate_dataframe

   spark = SparkSession.builder.getOrCreate()
   df = spark.createDataFrame(...)
   result = validate_dataframe(df, schema)

Dask
^^^^

.. code-block:: python

   import dask.dataframe as dd
   from griot_core import validate_dataframe

   df = dd.from_pandas(pandas_df, npartitions=4)
   result = validate_dataframe(df, schema)

Performance Tips
----------------

1. **Use appropriate backends** - polars is faster for large datasets
2. **Validate samples first** - Test with a sample before full validation
3. **Limit quality rules** - More rules = longer validation time
4. **Use type coercion sparingly** - It adds overhead

.. code-block:: python

   # Sample-based validation for large datasets
   sample_df = df.sample(n=1000)
   result = validate_dataframe(sample_df, schema)

   if result.is_valid:
       # Proceed with full validation or processing
       full_result = validate_dataframe(df, schema)

Best Practices
--------------

1. **Define quality rules upfront** - Include them in schema definitions
2. **Validate early** - Check data at ingestion points
3. **Log all errors** - For debugging and auditing
4. **Handle errors gracefully** - Don't crash on invalid data
5. **Test with edge cases** - Include nulls, empty strings, boundary values

.. code-block:: python

   def ingest_data(df: pd.DataFrame, schema: type[Schema]) -> pd.DataFrame:
       """Safe data ingestion with validation."""
       result = validate_dataframe(df, schema)

       if not result.is_valid:
           # Log issues
           for error in result.errors:
               logger.warning(f"Data quality issue: {error.message}")

           # Filter to valid rows or handle errors
           if result.error_count > df.shape[0] * 0.1:  # >10% errors
               raise ValueError("Too many data quality issues")

       return df

Next Steps
----------

- Generate :doc:`mock_data` for testing
- Learn about :doc:`contracts` management
- See the :doc:`../api/validation` for full API reference
